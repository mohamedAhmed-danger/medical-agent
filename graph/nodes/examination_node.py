from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from graph.utils import detect_language_fallback
from llm.model import get_gemini
from graph.prompt_service.clinic_data import ClinicDataService
from graph.nodes.examination_tools import save_examination_tool 
from software_services.client_services import ClientService
from graph.schemas.examination_schema import ExaminationResponse

EXAMINATION_SYSTEM_PROMPT = """
You are an empathetic and professional medical triage assistant for a clinic.
Your task is to gather information from patients who are feeling sick, tired, or describing medical symptoms, so that the medical team can contact them.

====================
CRITICAL RULE FOR SUMMARY
====================
You will receive the "current_summary" of the conversation. 
Your primary task is to APPEND the new examination/medical info to it. 
Do NOT clear or drop previous history (such as patient names, booking info, or dates). Keep it cumulative.

====================
REQUIRED FIELDS
====================
- phone_number (Look into the Summary first! If it exists, extract it and DO NOT ask for it again).
- symptoms_text (What hurts the patient, their sickness, or medical condition).

====================
RULES
====================
1. Never ask for already collected information.
2. Ask for ONE missing field at a time.
3. Be extremely polite, empathetic, and reassuring (patients are tired or in pain).
4. Match user language (Egyptian Arabic / English).
5. confirmed=true only if user explicitly confirms saving (e.g., "تمام", "اه", "اكد").
6. ready_to_save=true only if BOTH fields exist.
"""

def examination_node(state: AgentState) -> dict:
    page_id          = state.get("page_id")
    sender_id        = state.get("sender_id")
    platform_id      = state.get("platform_id")
    user_message     = state["user_message"]
    current_summary  = state.get("summary") or ""
    existing_lead    = state.get("examination_lead") or {}
    last_bot_message = state.get("last_bot_message") or ""

    clinic = ClinicDataService.get_clinic_info(page_id)
    llm = get_gemini()
    structured_llm = llm.with_structured_output(ExaminationResponse, include_raw=True)

    system_prompt = f"""
{EXAMINATION_SYSTEM_PROMPT}

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
        result = structured_llm.invoke(messages)
        parsed: ExaminationResponse = result["parsed"]
        raw_response = result["raw"]
    except Exception as e:
        print(f"[Examination Node] LLM error: {e}")
        fallback = detect_language_fallback(
            user_message,
            arabic="عذرًا، حدث خطأ مؤقت. حاول مرة أخرى.",
            default="Sorry, a temporary error occurred. Please try again.",
        )
        return {
            "response": fallback,
            "summary": current_summary,
            "examination_lead": existing_lead,
            "last_bot_message": fallback,
            "examination_saved": False,
            "examination_usage": None,
        }

    usage = getattr(raw_response, "usage_metadata", None)
    examination_usage = (
        {
            "input_tokens":  usage.get("input_tokens",  0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens":  usage.get("total_tokens",  0),
        }
        if usage else None
    )

    # MERGE LEAD
    updated_lead = {
        **existing_lead,
        **parsed.lead.model_dump(exclude_none=True),
    }

    # VALIDATION
    required_fields = ["phone_number", "symptoms_text"]
    all_fields_present = all(updated_lead.get(f) for f in required_fields)
    examination_saved = False

    # TOOL EXECUTION
    if parsed.ready_to_save and parsed.confirmed and all_fields_present:
        try:
            save_examination_tool.invoke(input={
                **updated_lead,
                "comes_from": str(platform_id or "unknown"),
            })

            examination_saved = True
            clean_reply = detect_language_fallback(
                user_message,
                arabic="تم تسجيل بياناتك بنجاح ✅\n"
                    "ألف سلامة عليك، وسيتواصل معك الفريق الطبي في أقرب وقت.\n"
                    "⚠️ تنبيه مهم: إذا كان التعب شديداً أو الحالة طارئة، يرجى الاتصال فوراً بخط العيادة الساخن لسرعة المتابعة!",
                default="Your medical request has been registered successfully ✅\n"
                    "Get well soon! Our medical team will contact you shortly.\n"
                    "⚠️ Important: If this is an emergency or severe case, please call the clinic directly right now!",
            )
        except Exception as e:
            print(f"[Examination Node] Tool error: {e}")
            examination_saved = False
            clean_reply = detect_language_fallback(
                user_message,
                arabic="حدث خطأ أثناء حفظ البيانات. حاول مرة أخرى.",
                default="An error occurred while saving your details. Please try again.",
            )
            parsed.summary = current_summary
    else:
        clean_reply = parsed.reply

    # SUMMARY FALLBACK
    final_summary = parsed.summary
    if not final_summary or (current_summary and len(final_summary.strip()) < 15):
        final_summary = f"{current_summary}\n[Note]: User requested an examination for medical symptoms."

    # PERSIST
    try:
        ClientService.update_client_summary_and_last_bot_message(
            sender_id=sender_id,
            page_id=page_id,
            platform_id=platform_id,
            summary=final_summary,
            last_bot_message=clean_reply,
        )
    except Exception as e:
        print(f"[Examination Node] Persist error: {e}")

    print(f"[Examination Node] done | saved={examination_saved}")

    return {
        "response": clean_reply,
        "summary": final_summary,
        "examination_lead": {} if examination_saved else updated_lead,
        "last_bot_message": clean_reply,
        "examination_saved": examination_saved,
        "examination_usage": examination_usage,
    }