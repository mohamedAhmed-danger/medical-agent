from models.models import Client, db
from graph.agent_graph import get_agent_graph
from graph.agent_response import AgentResponse
from sqlalchemy.exc import IntegrityError
from software_services.client_services import ClientService
from software_services.platform_services import PlatformService


class IncomingMessage:
    def __init__(self, sender_id, page_id, platform_id, msg_type,
                 text=None, media=None, platform_name=None):
        self.sender_id     = sender_id
        self.page_id       = page_id
        self.platform_id   = platform_id
        self.platform_name = platform_name
        self.type          = msg_type
        self.text          = text
        self.media         = media





def run_agent(message: IncomingMessage) -> str:
    client = ClientService.get_or_create_client(message.sender_id, message.page_id, message.platform_id)
    platform=PlatformService.get_platform_by_id(message.platform_id)

   

    state = {
        "page_id":           message.page_id,
        "sender_id":         message.sender_id,
        "platform_id":       message.platform_id,
        "platform_name":     platform.name,
        "user_message":      message.text or "",
        "summary":           client.summary or "",       
        "last_bot_message":  client.last_bot_message or "",
        "intent":            None,
        "response":          None,
        "intent_usage":      None,
        "clinic_info_usage": None,
        "booking_usage":     None,
        "complaint_usage":   None,
        "dirct_usage":       None,
        "booking_saved":     None,
        "complaint_saved":   None,
    }

    result       = get_agent_graph().invoke(state)
    response_obj = AgentResponse.from_result(result)
    bot_response = response_obj.response

  

    return bot_response