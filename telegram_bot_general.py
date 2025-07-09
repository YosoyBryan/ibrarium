"""
telegram_bot_general.py

A general-purpose Telegram bot that dynamically detects and launches Ibrarium modules.
Compatible with all action scripts like ibrarium_coffee.py, ibrarium_garage.py, etc.
Supports immediate, delayed, and scheduled actions.
"""

import os
import subprocess
import logging
import re
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Replace this with your actual bot token
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Directory where the .py scripts are located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Regex patterns
DELAY_PATTERN = re.compile(r"^(\w+)(?:\s+(\d+))?$")
SCHEDULE_PATTERN = re.compile(r"^(\w+)\s+at\s+(\d{1,2}):(\d{2})$")

# Detect available scripts (like ibrarium_coffee.py → command 'coffee')
def get_available_commands():
    commands = {}
    for file in os.listdir(SCRIPT_DIR):
        if file.startswith("ibrarium_") and file.endswith(".py") and file != os.path.basename(__file__):
            cmd = file[len("ibrarium_"):-3]  # remove prefix and suffix
            commands[cmd] = file
    return commands

AVAILABLE_COMMANDS = get_available_commands()

# Execute the script immediately or with subprocess
async def run_script(command: str):
    script = AVAILABLE_COMMANDS.get(command)
    if not script:
        return False
    subprocess.Popen(["python3", os.path.join(SCRIPT_DIR, script)])
    return True

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Welcome! Send a command like 'coffee', 'garage', or 'coffee 10' (in 10 min) or 'coffee at 7:45'."
    )

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = ", ".join(AVAILABLE_COMMANDS.keys())
    await update.message.reply_text(
        f"🤖 Available commands: {commands}\n\nUsage:\n- coffee\n- coffee 10 (in 10 minutes)\n- coffee at 7:45"
    )

# Main message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if m := DELAY_PATTERN.match(text):
        command, delay = m.groups()
        if command in AVAILABLE_COMMANDS:
            delay = int(delay) if delay else 0
            eta = datetime.now() + timedelta(minutes=delay)
            context.job_queue.run_once(
                lambda ctx: asyncio.create_task(run_script(command)),
                when=delay * 60,
                name=command
            )
            await update.message.reply_text(
                f"⏱️ '{command}' scheduled in {delay} minutes (at {eta.strftime('%H:%M')})"
            )
            return

    elif m := SCHEDULE_PATTERN.match(text):
        command, hour, minute = m.groups()
        if command in AVAILABLE_COMMANDS:
            now = datetime.now()
            scheduled_time = now.replace(hour=int(hour), minute=int(minute), second=0)
            if scheduled_time < now:
                scheduled_time += timedelta(days=1)
            delay_sec = (scheduled_time - now).total_seconds()
            context.job_queue.run_once(
                lambda ctx: asyncio.create_task(run_script(command)),
                when=delay_sec,
                name=command
            )
            await update.message.reply_text(
                f"📅 '{command}' scheduled at {scheduled_time.strftime('%H:%M')}"
            )
            return

    await update.message.reply_text("❌ Unknown or invalid command. Use /help to see available actions.")

# Main function
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
