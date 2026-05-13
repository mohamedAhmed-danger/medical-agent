from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import AgentState
from llm.model import get_gemini
from graph.prompt_service.clinic_data import ClinicDataService
from graph.nodes.booking_tools import save_booking_tool
from software_services.booking_services import BookingService


def booking_node(state: AgentState) -> dict:
    page_id       = state["page_id"]
    doctors       = ClinicDataService.get_doctors_info(page_id)
    specialties   = ClinicDataService.get_specialties_info(page_id)
    services      = ClinicDataService.get_services_info(page_id)
    platform_name = state.get("platform_name") or str(state.get("platform_id", "unknown"))


    system_prompt="""
 you are a assisent for a clincal you task is make appionment 
 you have a info for the doctor the this clinc have {doctors} and you have also th specialties this clinc have {specialties} and 
 you have th services {services}
     
 
 you should geathirng all this info
 1-name
 2-phone
 3-detials about the servcies or doctor or sepciltiy 
 4-
"""

 