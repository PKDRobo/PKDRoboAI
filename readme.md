# PKD AI - Telegram Bot

A production-ready Telegram Bot powered by PKD Robo and developed by Prathik.
This bot talks to the Vercel-based AI API, stores states inside Firebase Realtime Database, and has an interactive Admin Panel.

## Features
- AI Chatting Memory tracking
- Full Admin Panel to toggle features dynamically
- Broadcasting & Live Statistics
- Group Chat support (Mentions only)
- Uses modern Long-Polling (Ideal for Render Free Tier)

## Setup & Deployment on Render.com

### 1. Prerequisites
- Create a bot on Telegram via `@BotFather` and get the **Bot Token**.
- You need a Firebase Project with a **Realtime Database**.
- Get your **Service Account JSON file** from Firebase Console > Project Settings > Service Accounts > Generate New Private Key.

### 2. Local Testing
1. Clone the repository.
2. Install libraries: `pip install -r requirements.txt`
3. Create a `.env` file and add:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
