from typing import Any, TypedDict, Optional


class AgentState(TypedDict):

    # platform
    page_id: Optional[str]
    sender_id: Optional[str]
    platform_id: Optional[int]
    platform_name: Optional[str]

    # conversation
    user_message: str
    response: Optional[str]

    # routing
    intent: Optional[str]

    # memory
    summary: Optional[str]
    last_bot_message: Optional[str]

    # structured business data
    booking_lead: Optional[dict]
    complaint_lead: Optional[dict]
    examination_lead: Optional[dict]


    # status flags
    booking_saved: Optional[bool]
    complaint_saved: Optional[bool]
    examination_saved: Optional[bool]

    # usage
    intent_usage: Optional[dict]
    clinic_info_usage: Optional[dict]
    booking_usage: Optional[dict]
    complaint_usage: Optional[dict]
    direct_usage: Optional[dict]