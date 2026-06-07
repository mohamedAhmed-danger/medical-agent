"""
graph/nodes/booking_tools.py
"""

from langchain_core.tools import tool

from graph.utils import get_platform_name
from software_services.booking_services import BookingService, BookingSaveResult


@tool
def save_booking_tool(
    name: str,
    phone: str,
    date: str,
    details: str,
    comes_from: str = "unknown",
) -> BookingSaveResult:
    """
    Save a confirmed appointment booking to the database.

    Returns a BookingSaveResult containing:
      - reference_id : unique booking reference string
      - pdf_bytes    : PDF ticket as raw bytes
      - booking_id   : database row id
    """
    platform_name = get_platform_name(comes_from)

    # BookingService.save_booking raises on failure — let the node catch it.
    return BookingService.save_booking(
        name=name,
        phone=phone,
        date=date,
        details=details,
        comes_from=platform_name,
    )