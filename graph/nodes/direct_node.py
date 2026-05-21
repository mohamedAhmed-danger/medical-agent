# graph/nodes/direct_node.py

import re
from graph.state import AgentState
from graph.utils import strip_tags, detect_language_fallback
from llm.model import get_gemini
from graph.prompt_service.clinic_data import ClinicDataService
from langchain_core.messages import HumanMessage, SystemMessage
from software_services.client_services import ClientService


DIRECT_SYSTEM_PROMPT = """
You are a friendly assistant for a medical clinic.
Reply in the same language the user wrote in.

====================
CLINIC INFO
====================
{clinic}

====================
BEHAVIOR
====================
- Respond warmly to greetings, goodbyes, and simple conversational messages.
- Keep answers short and friendly.
- Do not handle booking or complaint requests — just acknowledge and redirect politely.
- if any one represent him self as a for medical reps or sales tell him to call on the clinic number. 

====================
MANDATORY TAGS  ← include at the END of EVERY reply
====================

<LAST_BOT_MESSAGE>
[Your reply to the patient — clean text only, no tags inside.]
</LAST_BOT_MESSAGE>

<SUMMARY>
[Create an updated, highly condensed English report of the conversation state. 
 Rules:
  1. Do NOT build a chronological chat log or append raw text blocks.
  2. Maintain a single unified snapshot of the patient profile: Name, Phone, and critical historical facts (e.g., 'User has a confirmed booking for X', 'User filed complaints previously').
  3. When new facts emerge (like a new symptom or inquiry), rewrite the summary to incorporate them into a single, compact paragraph. Overwrite and clean up repetitive or redundant historical records.]
</SUMMARY>  
"""


def direct_node(state: AgentState) -> dict:

    # FIX 2: safe .get() access for Optional fields
    page_id          = state.get("page_id")
    sender_id        = state.get("sender_id")
    platform_id      = state.get("platform_id")
    user_message     = state["user_message"]
    current_summary  = state.get("summary") or ""
    last_bot_message = state.get("last_bot_message") or ""

    clinic = ClinicDataService.get_clinic_info(page_id)

    system_content = (
        DIRECT_SYSTEM_PROMPT.format(clinic=clinic)
        + f"\n\n====================\nCONVERSATION CONTEXT\n===================="
        + f"\nPrevious summary:\n{current_summary}"
        + f"\n\nLast bot message:\n{last_bot_message}"
        + f"\n===================="
    )

    model = get_gemini()

    try:
        response = model.invoke([
            SystemMessage(content=system_content),
            HumanMessage(content=user_message),
        ])
    except Exception as e:
        print(f"[Direct Node] LLM error: {e}")
        # FIX 3: language-aware fallback
        fallback = detect_language_fallback(
            user_message,
            arabic="عذرًا، أواجه مشكلة الآن. حاول مرة أخرى.",
            default="Sorry, I'm having trouble right now. Please try again in a moment.",
        )
        return {
            "response":         fallback,
            "summary":          current_summary,
            "last_bot_message": fallback,
            "direct_usage":     None,
        }

    raw = response.content or ""

    reply_match = re.search(
        r"<LAST_BOT_MESSAGE>(.*?)</LAST_BOT_MESSAGE>", raw, re.DOTALL
    )
    if reply_match:
        clean_reply = strip_tags(reply_match.group(1).strip())
    else:
        print("[Direct Node] WARNING: <LAST_BOT_MESSAGE> tag missing in LLM response")
        clean_reply = strip_tags(raw.strip())

    summary_match = re.search(r"<SUMMARY>(.*?)</SUMMARY>", raw, re.DOTALL)
    if not summary_match:
        print("[Direct Node] WARNING: <SUMMARY> tag missing in LLM response")
    new_summary = summary_match.group(1).strip() if summary_match else current_summary

    # FIX 1: correct Gemini usage field names (singular token, not tokens)
    usage = getattr(response, "usage_metadata", None)
    direct_usage = (
        {
            "input_tokens":  usage.get("input_tokens",  0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens":  usage.get("total_tokens",  0),
        }
        if usage
        else None
    )

    try:
        ClientService.update_client_summary_and_last_bot_message(
            sender_id=sender_id,
            page_id=page_id,
            platform_id=platform_id,
            summary=new_summary,
            last_bot_message=clean_reply,
        )
    except Exception as e:
        print(f"[Direct Node] ClientService persist error: {e}")

    print(f"[Direct Node] done | usage={direct_usage}")

    return {
        "response":         clean_reply,
        "summary":          new_summary,
        "last_bot_message": clean_reply,
        "direct_usage":     direct_usage,
    }