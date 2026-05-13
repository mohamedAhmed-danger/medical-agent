import json
from graph.state import AgentState
from langchain_core.messages import HumanMessage, SystemMessage
import re
from llm.model import get_gemini


system_prompt = """
you are an intent recognition agent for a medical clinic.

IMPORTANT RULE: if the last bot message was asking for booking information 
(name, phone, date, doctor), classify as "booking" regardless of what the user said.

Categories:
- booking: user wants to book OR is responding to booking questions
- clinic_info: user asking about clinic, doctors, services, specialties
- complaint: user has a complaint
- direct: greetings, goodbyes, or anything else

Return JSON only:
{"intent": "identified_intent"}
"""
user_prompt = "" \
"summary {summary} \n last bot message {last_bot_message} \n user message {user_message}"


def intent_node(state: AgentState) -> str:
    # Prepare the system and user messages
    system_message = SystemMessage(content=system_prompt)
    user_message = HumanMessage(content=user_prompt.format(
        summary=state.get("summary", ""),
        last_bot_message=state.get("last_bot_message", ""),
        user_message=state["user_message"]
    ))
    
    # Get the model and generate a response
    model = get_gemini()
    response = model.invoke([system_message, user_message])
    print("RAW RESPONSE:", response.content)
    # Extract the intent from the response
    try:
        clean = response.content.strip().removeprefix("```json").removesuffix("```").strip()
        intent_data = json.loads(clean)
        intent = intent_data.get("intent", "direct")
    except (json.JSONDecodeError, KeyError):
        intent = "direct"

    return {
    "intent": intent,
    "intent_usage": {
        "input_tokens": response.usage_metadata.get("input_tokens", 0),
        "output_tokens": response.usage_metadata.get("output_tokens", 0)
    }
}
