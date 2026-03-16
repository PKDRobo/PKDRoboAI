import logging

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_admin(username: str) -> bool:
    from config import ADMIN_USERNAMES
    if not username:
        return False
    return username.lstrip("@").lower() in [u.lower() for u in ADMIN_USERNAMES]

def should_reply_in_group(text: str, bot_username: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    trigger_words = ["pkd", "pkd ai", bot_username.lower()]
    return any(trigger in text_lower for trigger in trigger_words)
