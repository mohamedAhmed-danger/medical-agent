# parsers/facebook.py

import logging
import traceback

from service.message_processor import IncomingMessage

logger = logging.getLogger(__name__)


def parse_facebook_message(
    messaging,
    page_id,
    platform_id,
    platform_name: str = "Facebook",
) -> IncomingMessage | None:

    try:

        # ─────────────────────────────────────
        # Ignore delivery events
        # ─────────────────────────────────────
        if "delivery" in messaging:
            return None

        # ─────────────────────────────────────
        # Ignore read events
        # ─────────────────────────────────────
        if "read" in messaging:
            return None

        # ─────────────────────────────────────
        # Ignore non-message events
        # ─────────────────────────────────────
        if "message" not in messaging:
            return None

        msg = messaging["message"]

        # ─────────────────────────────────────
        # Ignore bot echo messages
        # ─────────────────────────────────────
        if msg.get("is_echo", False):
            return None

        # ─────────────────────────────────────
        # Sender
        # ─────────────────────────────────────
        sender_id = messaging.get("sender", {}).get("id")

        if not sender_id:
            return None

        # ─────────────────────────────────────
        # Text message
        # ─────────────────────────────────────
        text = msg.get("text")

        if text:

            return IncomingMessage(
                sender_id=sender_id,
                page_id=page_id,
                platform_id=platform_id,
                platform_name=platform_name,
                msg_type="text",
                text=text,
            )

        # ─────────────────────────────────────
        # Attachments
        # ─────────────────────────────────────
        attachments = msg.get("attachments")

        if attachments:

            attachment = attachments[0]

            return IncomingMessage(
                sender_id=sender_id,
                page_id=page_id,
                platform_id=platform_id,
                platform_name=platform_name,
                msg_type=attachment.get("type", "media"),
                media=attachment.get("payload"),
            )

        return None

    except Exception:

        logger.critical(
            "Fatal error in parse_facebook_message:\n"
            f"{traceback.format_exc()}"
        )

        return None