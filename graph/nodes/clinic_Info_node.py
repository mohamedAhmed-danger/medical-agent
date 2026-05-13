import json
import re
from graph.state import AgentState
from llm.model import get_gemini
from graph.prompt_service.clinic_data import ClinicDataService
from langchain_core.messages import HumanMessage, SystemMessage


def clinic_info_node(state: AgentState) -> dict:
    page_id = state["page_id"]

    # get clinic data
    clinic = ClinicDataService.get_clinic_info(page_id)
    doctors = ClinicDataService.get_doctors_info(page_id)
    specialties = ClinicDataService.get_specialties_info(page_id)
    services = ClinicDataService.get_services_info(page_id)

    system_prompt = f"""
You are a helpful assistant for a medical clinic.
Reply in the same language the user wrote in.

Clinic Info: {clinic}
Doctors: {doctors}
Specialties: {specialties}
Services: {services}

Return JSON only, no markdown:
{{
    "response": "your response to the user",
    "summary": "updated conversation summary"
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
        data = json.loads(clean)
        bot_response = data.get("response", "")
        summary = data.get("summary", "")
    except (json.JSONDecodeError, KeyError):
        match = re.search(r'"response"\s*:\s*"([^"]+)"', response.content)
        bot_response = match.group(1) if match else "I'm sorry, I couldn't process your request."
        summary = state.get("summary", "")

    return {
        "response": bot_response,
        "summary": summary,
        "last_bot_message": bot_response,
        "clinic_info_usage": {
            "input_tokens": response.usage_metadata.get("input_tokens", 0),
            "output_tokens": response.usage_metadata.get("output_tokens", 0)
        }
    }
