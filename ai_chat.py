import requests
import urllib.parse
import asyncio
from config import API_URL, SYSTEM_PROMPT
from firebase_db import get_chat_history, append_chat_history, get_feature_state
from utils import logger

async def fetch_ai_response(user_id: int, user_message: str) -> str:
    # Check if memory is enabled
    memory_enabled = await get_feature_state("MEMORY")
    
    prompt = SYSTEM_PROMPT + "\n\n"
    
    if memory_enabled:
        history = await get_chat_history(user_id)
        for msg in history:
            role = "User" if msg["role"] == "user" else "PKD AI"
            prompt += f"{role}: {msg['content']}\n"
            
    prompt += f"User: {user_message}\nPKD AI: "
    
    def _request():
        url = API_URL + urllib.parse.quote(prompt)
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI API Error: {e}")
            return "Sorry, I am having trouble connecting to my brain right now. Please try again later."
            
    ai_reply = await asyncio.to_thread(_request)
    
    if memory_enabled and ai_reply and "trouble connecting" not in ai_reply:
        await append_chat_history(user_id, "user", user_message)
        await append_chat_history(user_id, "bot", ai_reply)
        
    return ai_reply
