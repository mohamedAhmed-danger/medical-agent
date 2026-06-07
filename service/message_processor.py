# service/message_processor.py

from graph.agent_graph import get_agent_graph
from graph.agent_response import AgentResponse
from software_services.client_services import ClientService


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


def _calc_total_usage(result: dict) -> dict:
    nodes = [
        "intent_usage",
        "clinic_info_usage",
        "booking_usage",
        "complaint_usage",
        "direct_usage",        
    ]
    total_in = total_out = total = 0
    breakdown = {}

    for key in nodes:
        u = result.get(key) or {}
        i = u.get("input_tokens",  0) or 0
        o = u.get("output_tokens", 0) or 0
        t = u.get("total_tokens",  0) or 0
        if i or o:
            breakdown[key] = {"input": i, "output": o, "total": t or i + o}
            total_in  += i
            total_out += o
            total     += t or i + o

    return {
        "breakdown":    breakdown,
        "total_input":  total_in,
        "total_output": total_out,
        "total_tokens": total,
    }


def run_agent(message: IncomingMessage) -> tuple[str, bytes | None]:
    client = ClientService.get_or_create_client(
        message.sender_id, message.page_id, message.platform_id
    )

   
    platform_name = message.platform_name or str(message.platform_id)

    state = {
        "page_id":           message.page_id,
        "sender_id":         message.sender_id,
        "platform_id":       message.platform_id,
        "platform_name":     platform_name,
        "user_message":      message.text or "",
        "summary":           client.summary          or "",
        "last_bot_message":  client.last_bot_message or "",
        "intent":            None,
        "response":          None,
        "intent_usage":      None,
        "clinic_info_usage": None,
        "booking_usage":     None,
        "complaint_usage":   None,
        "direct_usage":      None,   
        "booking_saved":     None,
        "complaint_saved":   None,
    }

    try:
        result       = get_agent_graph().invoke(state)
        response_obj = AgentResponse.from_result(result)
    except Exception as e:
        print(f"[run_agent] Error: {e}")
        return "Sorry, something went wrong. Please try again in a moment."

    usage = _calc_total_usage(result)
    print(
        f"\n📊 TOTAL USAGE"
        f" | intent={result.get('intent')}"
        f" | in={usage['total_input']}"
        f" | out={usage['total_output']}"
        f" | total={usage['total_tokens']}"
    )
    for node, u in usage["breakdown"].items():
        print(f"   └─ {node:<22} in={u['input']:>5} | out={u['output']:>5} | total={u['total']:>6}")

    return response_obj.response, result.get("booking_pdf")