save_booking_tool = {
    "name": "save_booking",
    "description": (
        "Save the appointment booking to the database after the user has confirmed all their details. "
        "Only call this tool when the user has explicitly confirmed they want to proceed with the booking."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "name":   {"type": "string", "description": "Patient full name"},
            "phone":  {"type": "string", "description": "Patient phone number"},
            "date":   {"type": "string", "description": "Appointment date"},
            "details":{"type": "string", "description": "Doctor preference or any extra details"},
        },
        "required": ["name", "phone", "date", "details"],
    },
}