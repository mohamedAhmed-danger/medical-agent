from langchain_core.tools import tool
from software_services.booking_services import BookingService
from graph.utils import get_platform_name


@tool
def save_booking_tool(
    name: str,
    phone: str,
    date: str,
    details: str,
    comes_from: str = "unknown", 
) -> str: 
    """Save a confirmed appointment booking to the database."""  

    
    platform_name = get_platform_name(comes_from)

    return BookingService.save_booking(
        name=name,
        phone=phone,
        date=date,
        details=details,
        comes_from=platform_name, 
    )