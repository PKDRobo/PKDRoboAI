import os
import asyncio
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from config import FIREBASE_DB_URL, DEFAULT_FEATURES
from utils import logger

# Initialize Firebase
def init_firebase():
    if not firebase_admin._apps:
        try:
            # Look for Service Account Key to use Admin SDK proper auth
            if os.path.exists("firebase-key.json"):
                cred = credentials.Certificate("firebase-key.json")
            else:
                # Fallback to anonymous credentials (requires public rules in Firebase RTDB)
                logger.warning("No firebase-key.json found. Attempting Anonymous login. Ensure Firebase DB rules allow access.")
                cred = credentials.Anonymous()
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_DB_URL,
                'projectId': 'pkd-robo-ai'
            })
            logger.info("Firebase initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")

init_firebase()

async def get_feature_state(feature: str) -> bool:
    def _get():
        ref = db.reference(f'feature_settings/{feature}')
        val = ref.get()
        if val is None:
            ref.set(DEFAULT_FEATURES.get(feature, False))
            return DEFAULT_FEATURES.get(feature, False)
        return bool(val)
    return await asyncio.to_thread(_get)

async def toggle_feature_state(feature: str) -> bool:
    def _toggle():
        ref = db.reference(f'feature_settings/{feature}')
        val = ref.get()
        new_val = not bool(val)
        ref.set(new_val)
        return new_val
    return await asyncio.to_thread(_toggle)

async def get_all_features() -> dict:
    def _get_all():
        ref = db.reference('feature_settings')
        vals = ref.get() or {}
        # Ensure all defaults exist
        for k, v in DEFAULT_FEATURES.items():
            if k not in vals:
                vals[k] = v
                db.reference(f'feature_settings/{k}').set(v)
        return vals
    return await asyncio.to_thread(_get_all)

async def add_user(user_id: int, first_name: str, username: str):
    def _add():
        ref = db.reference(f'users/{user_id}')
        if not ref.get():
            ref.set({
                "first_name": first_name,
                "username": username,
                "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    await asyncio.to_thread(_add)

async def get_all_users() -> list:
    def _get():
        users = db.reference('users').get()
        return list(users.keys()) if users else[]
    return await asyncio.to_thread(_get)

async def update_stats():
    def _update():
        today = datetime.now().strftime("%Y-%m-%d")
        ref_today = db.reference('stats/messages_today_date')
        ref_count = db.reference('stats/messages_today_count')
        ref_total = db.reference('stats/total_messages')
        
        saved_date = ref_today.get()
        if saved_date != today:
            ref_today.set(today)
            ref_count.set(1)
        else:
            curr = ref_count.get() or 0
            ref_count.set(curr + 1)
            
        total = ref_total.get() or 0
        ref_total.set(total + 1)
    await asyncio.to_thread(_update)

async def get_stats() -> dict:
    def _get():
        users_count = len(db.reference('users').get() or {})
        today = datetime.now().strftime("%Y-%m-%d")
        
        saved_date = db.reference('stats/messages_today_date').get()
        if saved_date == today:
            msg_today = db.reference('stats/messages_today_count').get() or 0
        else:
            msg_today = 0
            
        total_msg = db.reference('stats/total_messages').get() or 0
        return {"users": users_count, "today": msg_today, "total": total_msg}
    return await asyncio.to_thread(_get)

async def get_chat_history(user_id: int) -> list:
    def _get():
        return db.reference(f'chat_history/{user_id}').get() or[]
    return await asyncio.to_thread(_get)

async def append_chat_history(user_id: int, role: str, message: str):
    def _append():
        ref = db.reference(f'chat_history/{user_id}')
        history = ref.get() or[]
        history.append({"role": role, "content": message})
        # Keep only the last 6 messages (3 interactions) to prevent huge context loads
        if len(history) > 6:
            history = history[-6:]
        ref.set(history)
    await asyncio.to_thread(_append)

async def clear_chat_history(user_id: int):
    def _clear():
        db.reference(f'chat_history/{user_id}').delete()
    await asyncio.to_thread(_clear)
