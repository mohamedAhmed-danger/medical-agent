from typing import Optional
from pydantic import BaseModel, Field

class ExaminationLead(BaseModel):
    phone_number: Optional[str] = Field(
        None,
        description=(
            "The patient's phone number. CRITICAL: If the user refers to past info, "
            "or if a phone number already exists in the 'Summary' section (e.g., from a previous booking attempt), "
            "extract that phone number and fill this field automatically. Do NOT ask for it again if it exists in the Summary."
        )
    )
    symptoms_text: Optional[str] = Field(
        None,
        description=(
            "The patient's medical symptoms, condition, or what hurts them (e.g., 'بطني بتوجعني', 'عندي سخونية'). "
            "Extract any medical complaint or symptoms the user describes."
        )
    )

class ExaminationResponse(BaseModel):
    reply: str = Field(
        description="Clean, empathetic, and professional reply to the patient. If ALL fields (phone_number and symptoms_text) are collected, ask the patient to CONFIRM saving their request for examination."
    )
    summary: str = Field(
        description="An updated English summary of the patient's medical context. "
            "Incorporate new symptoms by condensing the medical history into a single sentence "
            "(e.g., 'Patient has a booking history, previously reported back pain, and is now reporting testicular pain'). "
            "Never append message logs; always re-summarize the total current state tightly.")
    
    lead: ExaminationLead = Field(
        description="Structured examination data ONLY."
    )
    confirmed: bool = Field(
        description="True only if user explicitly confirmed saving the examination/consultation request (e.g., 'اكد', 'تمام', 'اه', 'يا ريت')."
    )
    ready_to_save: bool = Field(
        description="True IF AND ONLY IF both phone_number and symptoms_text are not null/empty."
    )