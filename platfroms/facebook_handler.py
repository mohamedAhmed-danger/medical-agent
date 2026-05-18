import logging
import requests
from platfroms.base_handler import BaseHandler

logger = logging.getLogger(__name__)


class FacebookHandler(BaseHandler):
    platform_id = 2  

    @property
    def platform_name(self) -> str:
        try:
            return self.page.platform.name
        except AttributeError:
            return "Facebook"

    API_VERSION = "v19.0"

    def __init__(self, page):
        super().__init__(page)
        self.api_url = f"https://graph.facebook.com/{self.API_VERSION}/me/messages"
        self.headers = {"Content-Type": "application/json"}
        self.params  = {"access_token": self.token}

    def send(self, recipient_id: str, text: str):
        logger.debug("[FB SEND] to=%s", recipient_id)

        if not text or not text.strip():
            return None

        payload = {
            "recipient": {"id": recipient_id},
            "message":   {"text": text},
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                params=self.params,
                timeout=10,
            )
            if response.status_code not in [200, 201]:
                logger.error("[FB ERROR] status=%s body=%s",
                             response.status_code, response.text)
            return response
        except Exception as e:
            logger.error("[FB ERROR] Connection failed: %s", e)
            return None

    def parse_message(self, payload, page_id):
        from parsers.facebook import parse_facebook_message
        return parse_facebook_message(
            payload,
            page_id,
            platform_id=self.platform_id,
            platform_name=self.platform_name,
        )