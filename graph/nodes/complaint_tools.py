save_complaint_tool = {
    "name": "save_complaint",
    "description": (
        "Save the user's complaint to the database once both the phone number "
        "and complaint text have been collected."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "phone":     {"type": "string", "description": "Patient phone number"},
            "complaint": {"type": "string", "description": "Full complaint text"},
        },
        "required": ["phone", "complaint"],
    },
}