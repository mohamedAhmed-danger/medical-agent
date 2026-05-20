# graph/nodes/intent_node.py

import re
from graph.state import AgentState
from llm.model import get_gemini
from langchain_core.messages import HumanMessage, SystemMessage


INTENT_SYSTEM_PROMPT = """
You are an expert intent recognition agent for a medical clinic. Your job is to classify the user's latest message into exactly ONE category.

====================
CATEGORIES
====================
- booking    : User wants to book, reschedule, cancel, OR is providing answers to booking questions (name, phone, date, confirmation).
- clinic_info: User is asking general questions about the clinic (location, doctor names, pricing, working hours, available specialties).
- complaint  : User is expressing ANY form of anger, dissatisfaction, negative feedback, or using profanity/insults (e.g., "الخدمة زبالة" ", "سيئين جداً") this is for complaints about the clinic or the stuff or services not about the user's health.
- direct     : General greetings ("مساء الخير"), goodbyes ("مع السلامة"), or clear system interactions or if the user is representing themselves as a medical representative or salesperson.
- examination : user is talking about being sick, tired, expressing physical pain, medical symptoms (e.g., "تعبان", "بموت", "بطني بتوجعني", "عندي كشف") or responding to questions about their sickness this for medical inquiries foucs on the user health.
====================
CRITICAL ROUTING RULES (ORDER OF PRIORITY)
====================
1. PROFANITY & ANGER SUPREMACY (CRITICAL):
   If the user's latest message contains ANY insults, swear words, or clear expressions of anger (like , "زفت", "فاشلين"), you MUST classify the intent as 'complaint' IMMEDIATELY. 
   This rule OVERRIDES all other rules, even if there is an active booking in the summary.

2. CONTEXT AWARENESS FOR SHORT REPLIES:
   If the user's message is a short confirmation or generic reply (e.g., "اه", "تمام", "تمان", "ok", "yes", "لا") or similar:
   - If the last_bot_message was asking for a booking detail or confirmation -> classify as 'booking'.
   - If the last_bot_message was asking for complaint details -> classify as 'complaint'.

3. FLOW BIAS:
   If the message is ambiguous but the conversation summary shows an active uncompleted booking flow, lean toward 'booking'. But remember, Rule 1 overrides this completely.

You MUST end every reply with this exact tag — no exceptions:
<INTENT>[one of: booking | clinic_info | complaint | direct | examination]</INTENT>
"""

_VALID_INTENTS = {"booking", "clinic_info", "complaint", "direct","examination"}


def intent_node(state: AgentState) -> dict:

    current_summary  = state.get("summary") or ""
    last_bot_message = state.get("last_bot_message") or ""
    user_message     = state["user_message"]

    user_prompt = (
        f"Conversation summary:\n{current_summary}\n\n"
        f"Last bot message: {last_bot_message}\n"
        f"User message: {user_message}"
    )

    model = get_gemini()

    try:
        response = model.invoke([
            SystemMessage(content=INTENT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])

      
    except Exception as e:
        print(f"[Intent Node] LLM error: {e}")
        return {
            "intent":       "direct",
            "intent_usage": None,
        }

    raw = response.content or ""

    match  = re.search(r"<INTENT>(.*?)</INTENT>", raw, re.DOTALL)
    intent = match.group(1).strip().lower() if match else "direct"

    if intent not in _VALID_INTENTS:
        print(f"[Intent Node] WARNING: unrecognised intent '{intent}', defaulting to direct")
        intent = "direct"

    usage = getattr(response, "usage_metadata", None)
    intent_usage = (
        {
            "input_tokens":  usage.get("input_tokens",  0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens":  usage.get("total_tokens",  0),
        }
        if usage
        else None
    )

    print(f"[Intent Node] intent={intent}")

    return {
        "intent":       intent,
        "intent_usage": intent_usage,
    }