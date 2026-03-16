import sys
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    filters, CallbackQueryHandler, ContextTypes
)
from config import BOT_TOKEN
from admin import admin_command, admin_callback, broadcast_command, stats_command
import firebase_db
from ai_chat import fetch_ai_response
from utils import logger, is_admin, should_reply_in_group

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await firebase_db.add_user(user.id, user.first_name, user.username)
    
    welcome_text = (
        f"Hello {user.first_name} 👋\n\n"
        "Welcome to PKD AI 🤖\n"
        "Powered by PKD Robo\n"
        "Developed by Prathik\n\n"
        "Use /newchat to start chatting."
    )
    await update.message.reply_text(welcome_text)

async def newchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await firebase_db.clear_chat_history(user.id)
    await update.message.reply_text("Conversation history cleared. We can start fresh! 🧠")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text
    chat_type = update.message.chat.type

    # 1. Maintenance Check
    is_maintenance = await firebase_db.get_feature_state("MAINTENANCE_MODE")
    if is_maintenance and not is_admin(user.username):
        await update.message.reply_text("PKD AI is currently under maintenance.")
        return

    # 2. Group Mode Check
    if chat_type in ['group', 'supergroup']:
        group_mode = await firebase_db.get_feature_state("GROUP_MODE")
        if not group_mode:
            return
            
        bot_username = context.bot.username
        if not should_reply_in_group(text, bot_username):
            return

    # 3. AI Chat Toggle Check
    ai_enabled = await firebase_db.get_feature_state("AI_CHAT")
    if not ai_enabled:
        await update.message.reply_text("AI Chat is currently disabled by administrators.")
        return

    # Update Statistics
    if await firebase_db.get_feature_state("STATS"):
        await firebase_db.update_stats()

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    # Get Response
    response = await fetch_ai_response(user.id, text)
    await update.message.reply_text(response)

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing! Check your environment variables.")
        sys.exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("newchat", newchat_command))
    
    # Admin Commands
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # Callback Query (Admin Buttons)
    app.add_handler(CallbackQueryHandler(admin_callback))

    # Text Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting PKD AI Bot using Long Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
