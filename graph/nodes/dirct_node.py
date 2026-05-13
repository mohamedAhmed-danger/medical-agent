from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import AgentState
from llm.model import get_gemini
from graph.prompt_service.clinic_data import ClinicDataService
import json


def dirct_node(state: AgentState) -> dict:
    page_id = state["page_id"]
    clinic  = ClinicDataService.get_clinic_info(page_id)

    system_prompt = f"""
You are a friendly assistant for a medical clinic.
Clinic Info: {clinic}

Your job is to respond to general messages like greetings, goodbyes, 
and simple questions that don't need booking or complaint handling.

Reply in the same language the user wrote in.

Return JSON only, no markdown, no extra text:
{{
    "response": "your friendly response to the user",
    "summary": "brief summary of the conversation so far"
}}
"""

    user_prompt = f"""
Conversation Summary: {state.get('summary', '')}
Last Bot Message: {state.get('last_bot_message', '')}
User Message: {state['user_message']}
"""

    model = get_gemini()
    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    try:
        clean = response.content.strip().removeprefix("```json").removesuffix("```").strip()
        data  = json.loads(clean)
        bot_response = data.get("response", "")
        summary      = data.get("summary", state.get("summary", ""))
    except (json.JSONDecodeError, KeyError):
        bot_response = response.content if isinstance(response.content, str) else ""
        summary      = state.get("summary", "")

    usage = {
        "input_tokens":  response.usage_metadata.get("input_tokens", 0),
        "output_tokens": response.usage_metadata.get("output_tokens", 0)
    }

    return {
        "response":         bot_response,
        "last_bot_message": bot_response,
        "dirct_usage":      usage,
        "summary":          summary
    }
