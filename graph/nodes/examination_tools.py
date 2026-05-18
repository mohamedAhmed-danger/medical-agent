from langchain_core.tools import tool
from software_services.examination_services import ExaminationService
from graph.utils import get_platform_name 



@tool
def save_examination_tool(
    phone_number: str,
    symptoms_text: str,
    comes_from: str = "unknown",
) -> str:
    """
    Saves a patient's medical examination or triage request into the database.
    """
    platform_name = get_platform_name(comes_from)
    
    # افترضت إنك هتزود الـ comes_from برضه في دالة الـ Service عندك
    new_exam, message = ExaminationService.create_examination(
        phone_number=phone_number, 
        symptom_text=symptoms_text,
        comes_from=platform_name,
    )
    
    if new_exam:
        return f"Success: {message}"
    else:
        return f"Error: {message}"