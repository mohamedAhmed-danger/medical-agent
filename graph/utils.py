
import re
from models.models import RequestCounter

def strip_tags(text: str) -> str:
    """Remove all XML-style tags injected by LLM prompts from a reply string."""
    text = re.sub(r"<SUMMARY>.*?</SUMMARY>",                   "", text, flags=re.DOTALL)
    text = re.sub(r"<INTENT>.*?</INTENT>",                     "", text, flags=re.DOTALL)
    text = re.sub(r"<LAST_BOT_MESSAGE>.*?</LAST_BOT_MESSAGE>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>",                                  "", text)
    return text.strip()


def detect_language_fallback(user_message: str, arabic: str, default: str) -> str:
    """
    Return `arabic` if the user message contains Arabic characters,
    otherwise return `default`.
    Used for error/fallback messages in nodes that must match user language.
    """
    if any("\u0600" <= c <= "\u06ff" for c in user_message):
        return arabic
    return default


PLATFORM_MAP = {
    1: "WhatsApp",
    2: "Facebook",
}

def get_platform_name(platform_id) -> str:
    """تحويل الـ platform_id الرقمي أو النصي إلى اسم المنصة صراحة"""
    if not platform_id:
        return "unknown"
    key = int(platform_id) if str(platform_id).isdigit() else platform_id
    return PLATFORM_MAP.get(key, str(platform_id))    






def count_request():
    counter = RequestCounter.query.first()
    if counter:
        counter.decrement()

        