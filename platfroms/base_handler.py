from service.message_processor import run_agent


class BaseHandler:
    platform_id = None

    def __init__(self, page):
        self.page        = page
        self.page_id     = page.page_id
        self.token       = page.token

    def handle(self, message) -> str | None:
        if message.type == "text":
            return run_agent(message)
        return self._handle_media(message.type)

    def _handle_media(self, msg_type: str) -> str:
        responses = {
            "image":    "برجاء إرسال رسالة نصية بدلاً من الصورة.",
            "video":    "برجاء إرسال رسالة نصية بدلاً من الفيديو.",
            "audio":    "برجاء إرسال رسالة نصية بدلاً من الملف الصوتي.",
            "voice":    "برجاء إرسال رسالة نصية بدلاً من الرسالة الصوتية.",
            "location": "📍 تم استلام الموقع.",
        }
        return responses.get(msg_type, "برجاء إرسال رسالة نصية.")

    def send(self, recipient_id: str, text: str):
        raise NotImplementedError
