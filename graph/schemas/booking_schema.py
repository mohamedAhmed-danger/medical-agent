from typing import Optional
from pydantic import BaseModel, Field

class BookingLead(BaseModel):
    name: Optional[str] = Field(None, description="The user's explicit name.")
    phone: Optional[str] = Field(None, description="The user's phone number.")
    details: Optional[str] = Field(None, description="The reason for the visit or the service/doctor they want (e.g., 'تحليل دم', 'كشف عام', 'د. أحمد') or similar. "
          "CRITICAL: If the user's phone number or name is already mentioned in the 'Summary' history, EXTRACT it automatically into the lead. DO NOT ask the user for information they already provided during the booking phase."           
          "EXTRACT it immediately into this field. Do NOT ask for the reason of visit again.")
    date: Optional[str] = Field(
        None, 
        description="The resolved absolute date and time. Use temporal context to turn 'بكرا' or 'السبت' into 'YYYY-MM-DD HH:MM'."
    )

class BookingResponse(BaseModel):
    reply: str = Field(description="Clean reply to send to the user")
    summary: str = Field(description="Updated cumulative summary in English")
    lead: BookingLead = Field(description="Structured booking data ONLY.")
    confirmed: bool = Field(description="True if the user confirms. Accept Egyptian slang like 'تمام', 'تمان', 'ايوه', 'اه', 'ماشي'.")
    ready_to_save: bool = Field(description="True only if all 4 booking fields exist")