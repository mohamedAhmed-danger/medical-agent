from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import AgentState
from llm.model import get_gemini
from models.models import db, Complaint
from graph.prompt_service.clinic_data import ClinicDataService
from graph.nodes.complaint_tools import save_complaint_tool
from software_services.complaint_services import ComplaintService


def complaint_node(state: AgentState) -> dict:
    page_id = state["page_id"]
    clinic  = ClinicDataService.get_clinic_info(page_id)

    system_prompt = f"""
"""