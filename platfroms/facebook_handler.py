import requests
from platfroms.base_handler import BaseHandler


class FacebookHandler(BaseHandler):
    platform_id = 2  # 1=whatsapp, 2=facebook

    # The human-readable name comes from the page's platform relationship.
    # Assuming your Page model has:  page.platform.name  (e.g. "Facebook")
    # If the column is named differently, adjust the property below.
    @property
    def platform_name(self) -> str:
        try:
            return self.page.platform.name          # ← read from DB relation
        except AttributeError:
            return "Facebook"                       # safe fallback

    API_VERSION = "v19.0"

    def __init__(self, page):
        super().__init__(page)
        self.api_url = f"https://graph.facebook.com/{self.API_VERSION}/me/messages"
        self.headers = {"Content-Type": "application/json"}
        self.params  = {"access_token": self.token}

    def send(self, recipient_id: str, text: str):
        print(f"[FB SEND] to={recipient_id}, token={self.token[:20]}...")
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
                print(f"[FB ERROR] {response.text}")
            return response
        except Exception as e:
            print(f"[FB ERROR] Connection failed: {e}")
            return None

    def parse_message(self, payload, page_id):
        """Convenience wrapper — keeps platform_name in one place."""
        from parsers.facebook import parse_facebook_message
        return parse_facebook_message(
            payload,
            page_id,
            platform_id=self.platform_id,
            platform_name=self.platform_name,   # ← injected here
        )