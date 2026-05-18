# graph/nodes/complaint_node.py

from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import AgentState
from graph.utils import detect_language_fallback
from llm.model import get_gemini
from graph.prompt_service.clinic_data import ClinicDataService
from graph.nodes.complaint_tools import save_complaint_tool
from software_services.client_services import ClientService

from graph.schemas.complaint_schema import ComplaintResponse


COMPLAINT_SYSTEM_PROMPT = """
You are a professional customer service assistant for a medical clinic.

Your task is to collect and register patient complaints.

====================
CRITICAL RULE FOR SUMMARY
====================
You will receive the "current_summary" of the conversation. 
Your primary task is to APPEND the new complaint information to it. 
Do NOT clear or drop previous history (such as patient names, booking info, or dates). Keep it cumulative.

====================
REQUIRED FIELDS
====================
- phone_number
- complaint_text

====================
RULES
====================
1. Never ask for already collected information
2. Ask for ONE missing field at a time
3. Be polite and professional
4. Match user language
5. confirmed=true only if user explicitly confirms
6. ready_to_save=true only if ALL fields exist
"""


def complaint_node(state: AgentState) -> dict:

    page_id          = state.get("page_id")
    sender_id        = state.get("sender_id")
    platform_id      = state.get("platform_id")
    user_message     = state["user_message"]
    current_summary  = state.get("summary") or ""
    existing_lead    = state.get("complaint_lead") or {}
    last_bot_message = state.get("last_bot_message") or ""

    clinic = ClinicDataService.get_clinic_info(page_id)

    llm = get_gemini()

    # include_raw=True so we can access usage_metadata from the raw response
    structured_llm = llm.with_structured_output(ComplaintResponse, include_raw=True)

    system_prompt = f"""
{COMPLAINT_SYSTEM_PROMPT}

====================
CLINIC INFO
====================

{clinic}

====================
ALREADY COLLECTED (HISTORY)
====================

Summary:
{current_summary}

Lead:
{existing_lead}

Last bot message:
{last_bot_message}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    try:
        result                    = structured_llm.invoke(messages)
        parsed: ComplaintResponse = result["parsed"]
        raw_response              = result["raw"]

    except Exception as e:
        print(f"[Complaint Node] LLM error: {e}")
        fallback = detect_language_fallback(
            user_message,
            arabic="عذرًا، حدث خطأ مؤقت. حاول مرة أخرى.",
            default="Sorry, a temporary error occurred. Please try again.",
        )
        return {
            "response":        fallback,
            "summary":         current_summary,
            "complaint_lead":  existing_lead,
            "last_bot_message": fallback,
            "complaint_saved": False,
            "complaint_usage": None,
        }

    # usage_metadata is a dict — read with .get()
    usage = getattr(raw_response, "usage_metadata", None)
    complaint_usage = (
        {
            "input_tokens":  usage.get("input_tokens",  0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens":  usage.get("total_tokens",  0),
        }
        if usage
        else None
    )

    # =====================================================
    # MERGE LEAD
    # =====================================================

    updated_lead = {
        **existing_lead,
        **parsed.lead.model_dump(exclude_none=True),
    }

    # =====================================================
    # VALIDATION
    # =====================================================

    required_fields    = ["phone_number", "complaint_text"]
    all_fields_present = all(updated_lead.get(f) for f in required_fields)
    complaint_saved    = False

    # =====================================================
    # TOOL EXECUTION
    # =====================================================

    if parsed.ready_to_save and parsed.confirmed and all_fields_present:

        try:
            save_complaint_tool.invoke(input=
                {
                    **updated_lead,
                    "comes_from": str(platform_id or "unknown"),
                })
            complaint_saved = True

            clean_reply = detect_language_fallback(
                user_message,
                arabic="تم تسجيل شكواك بنجاح ✅\nسيتواصل معك فريقنا قريبًا.",
                default="Your complaint has been registered successfully ✅\nOur team will contact you soon.",
            )

        except Exception as e:
            print(f"[Complaint Node] Tool error: {e}")
            complaint_saved = False

            clean_reply = detect_language_fallback(
                user_message,
                arabic="حدث خطأ أثناء تسجيل الشكوى. حاول مرة أخرى.",
                default="An error occurred while registering your complaint. Please try again.",
            )

            # rollback summary on save failure so memory stays honest
            parsed.summary = current_summary

    else:
        clean_reply = parsed.reply

    # =====================================================
    # SUMMARY FALLBACK
    # =====================================================

    final_summary = parsed.summary
    if not final_summary or (current_summary and len(final_summary.strip()) < 15):
        final_summary = f"{current_summary}\n[Note]: User filed a complaint."

    # =====================================================
    # PERSIST
    # =====================================================

    try:
        ClientService.update_client_summary_and_last_bot_message(
            sender_id=sender_id,
            page_id=page_id,
            platform_id=platform_id,
            summary=final_summary,
            last_bot_message=clean_reply,
        )
    except Exception as e:
        print(f"[Complaint Node] Persist error: {e}")

    print(f"[Complaint Node] done | saved={complaint_saved} | usage={complaint_usage}")

    # =====================================================
    # RETURN STATE
    # =====================================================

    return {
        "response":         clean_reply,
        "summary":          final_summary,
        "complaint_lead":   {} if complaint_saved else updated_lead,
        "last_bot_message": clean_reply,
        "complaint_saved":  complaint_saved,
        "complaint_usage":  complaint_usage,
    }