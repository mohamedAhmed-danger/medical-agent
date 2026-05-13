from typing import Any, TypedDict, Optional


class AgentState(TypedDict):
    page_id:             Optional[str]
    sender_id:           Optional[str]
    platform_id:         Optional[int]
    platform_name:       Optional[str]
    user_message:        str
    summary:             Optional[str]
    last_bot_message:    Optional[str]
    intent:              Optional[str]
    response:            Optional[str]
    intent_usage:        Optional[dict]
    clinic_info_usage:   Optional[dict]
    booking_usage:       Optional[dict]
    complaint_usage:     Optional[dict]
    dirct_usage:         Optional[dict]
    booking_saved:       Optional[bool]
    complaint_saved:     Optional[bool]
    