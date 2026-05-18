from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ComplaintLead(BaseModel):
    phone_number: Optional[str] = Field(
        None,
        description=(
            "The patient's phone number. CRITICAL: If the user says 'موجود في الحجز' or refers to past info, "
            "look at the 'Summary' section, extract the phone number from there (e.g., 01208140337) or similar, and fill this field. "
            "Do NOT ask for it again if it exists in the Summary."
        )
    )
    complaint_text: Optional[str] = Field(
        None,
        description=(
            "The customer's complaint. Accept ANY expression of dissatisfaction, anger, or negative feedback "
            "(e.g., 'المعاملة زبالة', 'الخدمة سيئة') or similar. Consider even a short phrase or single sentence as a complete complaint_text. "
            "Do NOT wait for a detailed essay."
        )
    )

    


class ComplaintResponse(BaseModel):
    reply: str = Field(
        description="Clean, polite reply to the user. If ALL fields (phone_number and complaint_text) are collected, ask the user to CONFIRM saving the complaint."
    )

    summary: str = Field(
        description="Updated cumulative conversation summary in English. Append new complaint facts at the end without clearing history."
    )

    lead: ComplaintLead = Field(
        description="Structured complaint data ONLY."
    )

    confirmed: bool = Field(
        description="True only if user explicitly confirmed saving the complaint (e.g., 'اكد', 'تمام', 'يس')."
    )

    ready_to_save: bool = Field(
        description="True IF AND ONLY IF both phone_number and complaint_text are not null/empty."
    )