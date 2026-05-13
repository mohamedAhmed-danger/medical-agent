import logging
import traceback
from service.message_processor import IncomingMessage

logger = logging.getLogger(__name__)


def parse_facebook_message(payload, page_id, platform_id, platform_name: str = "Facebook") -> IncomingMessage | None:
    # ↑ platform_name passed in from the handler so we never hard-code it here
    try:
        if not isinstance(payload, dict):
            return None

        entry     = payload.get("entry", [{}])[0]
        messaging = entry.get("messaging", [{}])[0]

        if "delivery" in messaging or "read" in messaging:
            return None

        sender_id = messaging.get("sender", {}).get("id")

        if not sender_id or sender_id == page_id:
            return None

        if "message" in messaging:
            msg  = messaging["message"]
            text = msg.get("text")

            if text:
                return IncomingMessage(
                    sender_id=sender_id,
                    page_id=page_id,
                    platform_id=platform_id,
                    platform_name=platform_name,   # ← passed through
                    msg_type="text",
                    text=text,
                )

            if "attachments" in msg:
                attachment = msg["attachments"][0]
                return IncomingMessage(
                    sender_id=sender_id,
                    page_id=page_id,
                    platform_id=platform_id,
                    platform_name=platform_name,   # ← passed through
                    msg_type=attachment.get("type", "media"),
                    media=attachment.get("payload"),
                )

        return None

    except Exception:
        logger.critical(f"Fatal error in parse_facebook_message:\n{traceback.format_exc()}")
        return None