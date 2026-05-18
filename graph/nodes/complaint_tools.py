from langchain_core.tools import tool
from software_services.complaint_services import ComplaintService
from graph.utils import get_platform_name


@tool
def save_complaint_tool(
    phone_number: str,
    complaint_text: str,
    comes_from: str = "unknown",
) -> str:
    """Save a patient complaint to the database so the team can follow up."""
    
    platform_name = get_platform_name(comes_from)
    
    return ComplaintService.save_complaint(
        phone_number=phone_number,
        complaint_text=complaint_text,
        comes_from=platform_name,  # هتباصي الاسم هنا للسيرفيس (بعد ما تزودها في الموديل)
    )