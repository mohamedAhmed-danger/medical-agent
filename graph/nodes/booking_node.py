# graph/nodes/booking_node.py

from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
from graph.state import AgentState
from graph.utils import detect_language_fallback
from llm.model import get_gemini
from graph.prompt_service.clinic_data import ClinicDataService
from graph.nodes.booking_tools import save_booking_tool
from software_services.client_services import ClientService

from graph.schemas.booking_schema import BookingResponse


BOOKING_SYSTEM_PROMPT = """
You are a professional booking assistant for a medical clinic.

Your task is to collect booking information professionally.

====================
REQUIRED FIELDS
====================

- name
- phone
- details: this can be the reason for the visit, the service they want, or the doctor they want to see (e.g., 'تحليل دم', 'كشف عام', 'د. أحمد') or similar.
- date 

====================
RULES
====================

1. Never ask for fields already collected
2. Ask for ONE missing field at a time
3. Match the user's language
4. Never invent information
5. ask the user for confirmation after you have collected all fields and before saving.
5. confirmed=true ONLY if the user clearly confirms
6. ready_to_save=true ONLY if ALL fields exist

"""


def booking_node(state: AgentState) -> dict:

    page_id          = state.get("page_id")
    sender_id        = state.get("sender_id")
    platform_id      = state.get("platform_id")
    user_message     = state["user_message"]
    current_summary  = state.get("summary") or ""
    existing_lead    = state.get("booking_lead") or {}
    last_bot_message = state.get("last_bot_message") or ""

    now = datetime.now()
    current_time_info = now.strftime("Today is %A, %B %d, %Y. Current time is %I:%M %p")
    doctors, specialties, services = ClinicDataService.get_all_clinic_data(page_id)

    llm = get_gemini()

    structured_llm = llm.with_structured_output(BookingResponse, include_raw=True)

    system_prompt = f"""
{BOOKING_SYSTEM_PROMPT}

====================
CRITICAL: CURRENT TEMPORAL CONTEXT
====================
{current_time_info}
Use this current date and time to resolve relative expressions like "بكرا" (tomorrow), "بعد بكرا", "السبت الجاي", etc. into actual absolute context.

====================
CLINIC DATA
====================

Doctors:
{doctors}

Specialties:
{specialties}

Services:
{services}

====================
ALREADY COLLECTED
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
        result        = structured_llm.invoke(messages)
        parsed: BookingResponse = result["parsed"]
        raw_response  = result["raw"]

    except Exception as e:
        print(f"[Booking Node] LLM error: {e}")
        fallback = detect_language_fallback(
            user_message,
            arabic="عذرًا، حدث خطأ مؤقت. حاول مرة أخرى.",
            default="Sorry, a temporary error occurred. Please try again.",
        )
        return {
            "response":         fallback,
            "summary":          current_summary,
            "booking_lead":     existing_lead,
            "last_bot_message": fallback,
            "booking_saved":    False,
            "booking_usage":    None,
        }

    usage = getattr(raw_response, "usage_metadata", None)
    booking_usage = (
    {
        "input_tokens":  usage.get("input_tokens",  0),   
        "output_tokens": usage.get("output_tokens", 0),
        "total_tokens":  usage.get("total_tokens",  0),
    }
    if usage
    else None
)

    updated_lead = {
        **existing_lead,
        **parsed.lead.model_dump(exclude_none=True),
    }

    required_fields    = ["name", "phone", "details", "date"]
    all_fields_present = all(updated_lead.get(f) for f in required_fields)
    booking_saved      = False

    if parsed.ready_to_save and parsed.confirmed and all_fields_present:

        try:
            save_booking_tool.invoke(input=
                {
                    **updated_lead,
                    "comes_from": str(platform_id or "unknown"),
                })
            booking_saved = True

            clean_reply = detect_language_fallback(
                user_message,
                arabic="تم تأكيد الحجز بنجاح ✅\nسيتواصل معك فريقنا قريبًا.",
                default="Your booking has been confirmed successfully ✅\nOur team will contact you soon.",
            )

        except Exception as e:
            print(f"[Booking Node] Tool error: {e}")
            booking_saved = False

            clean_reply = detect_language_fallback(
                user_message,
                arabic="حدث خطأ أثناء حفظ الحجز. حاول مرة أخرى.",
                default="An error occurred while saving your booking. Please try again.",
            )

            # FIX 2: rollback summary to before this turn so memory stays honest
            parsed.summary = current_summary

    else:
        clean_reply = parsed.reply

    # =====================================================
    # PERSIST
    # =====================================================

    try:
        ClientService.update_client_summary_and_last_bot_message(
            sender_id=sender_id,
            page_id=page_id,
            platform_id=platform_id,
            summary=parsed.summary,
            last_bot_message=clean_reply,
        )
    except Exception as e:
        print(f"[Booking Node] Persist error: {e}")

    print(f"[Booking Node] done | saved={booking_saved} | usage={booking_usage}")

    # =====================================================
    # RETURN STATE
    # =====================================================

    return {
        "response":         clean_reply,
        "summary":          parsed.summary,
        "booking_lead":     {} if booking_saved else updated_lead,
        "last_bot_message": clean_reply,
        "booking_saved":    booking_saved,
        "booking_usage":    booking_usage,
    }