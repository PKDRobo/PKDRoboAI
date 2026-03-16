from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import is_admin
import firebase_db

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.username):
        await update.message.reply_text("You are not admin.")
        return

    await send_admin_panel(update.message)

async def send_admin_panel(message_obj):
    features = await firebase_db.get_all_features()
    
    keyboard = []
    # Build 2 columns format
    row =[]
    for feature, state in features.items():
        status = "✅" if state else "❌"
        btn_text = f"{status} {feature}"
        row.append(InlineKeyboardButton(btn_text, callback_data=f"toggle_{feature}"))
        if len(row) == 2:
            keyboard.append(row)
            row =[]
    if row:
        keyboard.append(row)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message_obj.reply_text("🛠 **PKD AI Admin Panel**\nClick to toggle features:", reply_markup=reply_markup, parse_mode='Markdown')

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    
    if not is_admin(user.username):
        await query.answer("You are not admin.", show_alert=True)
        return

    await query.answer()
    
    data = query.data
    if data.startswith("toggle_"):
        feature_name = data.replace("toggle_", "")
        await firebase_db.toggle_feature_state(feature_name)
        
        # Refresh the panel
        features = await firebase_db.get_all_features()
        keyboard = []
        row =[]
        for feature, state in features.items():
            status = "✅" if state else "❌"
            btn_text = f"{status} {feature}"
            row.append(InlineKeyboardButton(btn_text, callback_data=f"toggle_{feature}"))
            if len(row) == 2:
                keyboard.append(row)
                row =[]
        if row:
            keyboard.append(row)
            
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.username):
        await update.message.reply_text("You are not admin.")
        return
        
    if not await firebase_db.get_feature_state("BROADCAST"):
        await update.message.reply_text("Broadcast feature is disabled in settings.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    broadcast_msg = " ".join(context.args)
    users = await firebase_db.get_all_users()
    
    await update.message.reply_text(f"Starting broadcast to {len(users)} users...")
    
    success = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **Announcement**\n\n{broadcast_msg}", parse_mode='Markdown')
            success += 1
        except Exception:
            pass # Ignore users who blocked the bot
            
    await update.message.reply_text(f"Broadcast completed. Successfully sent to {success} users.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.username):
        await update.message.reply_text("You are not admin.")
        return

    if not await firebase_db.get_feature_state("STATS"):
        await update.message.reply_text("Stats feature is disabled in settings.")
        return

    stats = await firebase_db.get_stats()
    text = (
        "📊 **PKD AI Statistics**\n\n"
        f"👥 Users: {stats['users']}\n"
        f"✉️ Messages Today: {stats['today']}\n"
        f"💬 Total Chats: {stats['total']}"
    )
    await update.message.reply_text(text, parse_mode='Markdown')
