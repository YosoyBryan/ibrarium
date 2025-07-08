#!/usr/bin/env python3
import asyncio
import logging
import os
import json
import sys
from telebot.async_telebot import AsyncTeleBot
from telebot import types

# Dynamically import custom modules from 'scripts' directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# --- Try to import Wi-Fi Plug Control Module ---
try:
    from ibrarium_wifi_plug_generic import WifiPlugGenericControl
    logging.info("Successfully imported WifiPlugGenericControl.")
except ImportError as e:
    logging.error(f"Failed to import WifiPlugGenericControl: {e}. Wi-Fi control features will be unavailable.")
    WifiPlugGenericControl = None

# --- Load Configuration File ---
CONFIG_FILE = 'ibrarium_config.json'
CONFIG = {}

def load_config():
    """Load JSON configuration from disk."""
    global CONFIG
    if not os.path.exists(CONFIG_FILE):
        logging.error(f"Configuration file '{CONFIG_FILE}' not found. Please create it.")
        sys.exit(1)
    try:
        with open(CONFIG_FILE, 'r') as f:
            CONFIG = json.load(f)
        logging.info("Configuration loaded successfully.")
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing configuration file '{CONFIG_FILE}': {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error loading configuration: {e}")
        sys.exit(1)

load_config()

# --- Configure Logging ---
log_level_str = CONFIG.get('system_info', {}).get('log_level', 'INFO').upper()
numeric_level = getattr(logging, log_level_str, None)
if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {log_level_str}')

log_file_path = CONFIG.get('system_info', {}).get('log_file', '/var/log/ibrarium.log')
log_dir = os.path.dirname(log_file_path)

handlers = []
file_logging_enabled = False # Flag to track if file logging is successfully set up

# Attempt to set up file handler
if log_file_path: # Only try if a path is specified
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
            handlers.append(logging.FileHandler(log_file_path))
            file_logging_enabled = True
            logging.info(f"Created log directory and set up file logging to: {log_file_path}") # Log this via stream handler
        except OSError as e:
            # If directory creation fails, log to console and disable file logging
            logging.warning(f"Could not create log directory {log_dir}: {e}. File logging disabled.")
    else: # Directory exists or log_file_path is just a filename (no explicit directory)
        try:
            handlers.append(logging.FileHandler(log_file_path))
            file_logging_enabled = True
            logging.info(f"Set up file logging to: {log_file_path}") # Log this via stream handler
        except Exception as e:
            # If file handler setup fails (e.g., permissions), log to console and disable file logging
            logging.warning(f"Failed to set up file logging to {log_file_path}: {e}. File logging disabled.")

# Always log to console
handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=numeric_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

logging.info(f"IBRARIUM System started with log level: {log_level_str}")
if not file_logging_enabled and log_file_path: # Only warn if file logging was intended but failed
    logging.warning("File logging is disabled. All logs will go to the console.")
elif file_logging_enabled:
    logging.info(f"Logs are being written to: {log_file_path}")


# --- Telegram Bot Setup ---
TELEGRAM_BOT_TOKEN = CONFIG.get('telegram_bot', {}).get('api_token')
ALLOWED_USER_IDS = list(map(int, CONFIG.get('telegram_bot', {}).get('allowed_user_ids', [])))
ADMIN_USER_IDS = list(map(int, CONFIG.get('telegram_bot', {}).get('admin_user_ids', [])))

if not TELEGRAM_BOT_TOKEN or not ALLOWED_USER_IDS:
    logging.error("Telegram bot token or allowed user IDs are not configured. Please check ibrarium_config.json.")
    sys.exit(1)

bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN)

# --- Global State: Initialize Device Controllers ---
wifi_plug_controller = None
if WifiPlugGenericControl:
    try:
        # Pass the full config to the controller, allowing it to read its specific sections
        wifi_plug_controller = WifiPlugGenericControl(CONFIG_FILE)
        logging.info("Wi-Fi Plug Generic Controller initialized.")
    except Exception as e:
        logging.error(f"Failed to initialize WifiPlugGenericControl: {e}. Wi-Fi commands will not work.")

# --- Helper Functions for Permissions ---
def is_allowed_user(message):
    return message.from_user.id in ALLOWED_USER_IDS

def is_admin_user(message):
    return message.from_user.id in ADMIN_USER_IDS

# --- Telegram Command Handlers ---

@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    if not is_allowed_user(message):
        await bot.reply_to(message, CONFIG.get('telegram_bot', {}).get('commands', {}).get('unauthorized', "You are not authorized."))
        return

    help_message = CONFIG.get('telegram_bot', {}).get('commands', {}).get('help',
        "Available commands: /status, /wifi_list, /wifi_on <device>, /wifi_off <device>, /wifi_toggle <device>, /wifi_status <device>")
    await bot.reply_to(message, help_message)

@bot.message_handler(commands=['ping'])
async def handle_ping(message):
    """Health check command."""
    if is_allowed_user(message):
        await bot.reply_to(message, "pong 🟢")

@bot.message_handler(commands=['status'])
async def get_status(message):
    if not is_allowed_user(message):
        await bot.reply_to(message, CONFIG.get('telegram_bot', {}).get('commands', {}).get('unauthorized', "You are not authorized."))
        return

    status_text = "🛠️ IBRARIUM system is running.\n"
    status_text += f"Version: {CONFIG.get('system_info', {}).get('version', 'N/A')}\n"
    status_text += f"Timezone: {CONFIG.get('system_info', {}).get('timezone', 'N/A')}\n"
    status_text += f"Log level: {CONFIG.get('system_info', {}).get('log_level', 'N/A')}\n"

    if wifi_plug_controller:
        status_text += "\nWi-Fi Plug Controller: ✅ Active\n"
        devices_info = wifi_plug_controller.list_devices()
        # wifi_plug_controller.list_devices() returns a string already, no need to join a list
        status_text += devices_info
    else:
        status_text += "\nWi-Fi Plug Controller: ❌ Inactive (module not loaded or failed to initialize)\n"

    await bot.reply_to(message, status_text)

@bot.message_handler(commands=['wifi_list'])
async def wifi_list_devices(message):
    if not is_allowed_user(message):
        await bot.reply_to(message, CONFIG.get('telegram_bot', {}).get('commands', {}).get('unauthorized', "You are not authorized."))
        return

    if wifi_plug_controller:
        devices_info = wifi_plug_controller.list_devices()
        # wifi_plug_controller.list_devices() returns a string already
        if not devices_info.strip(): # Check if the string is empty or just whitespace
            devices_info = "No Wi-Fi devices configured."
        await bot.reply_to(message, f"Configured Wi-Fi devices:\n{devices_info}")
    else:
        await bot.reply_to(message, "Wi-Fi controller is not available. Please check the logs.")

@bot.message_handler(commands=['wifi_on', 'wifi_off', 'wifi_toggle', 'wifi_status'])
async def control_wifi_device(message):
    if not is_allowed_user(message):
        await bot.reply_to(message, CONFIG.get('telegram_bot', {}).get('commands', {}).get('unauthorized', "You are not authorized."))
        return

    if not wifi_plug_controller:
        await bot.reply_to(message, "Wi-Fi controller is not available. Please check the logs.")
        return

    parts = message.text.split(maxsplit=2)
    command = parts[0][1:]  # Remove leading '/'
    if len(parts) < 2:
        await bot.reply_to(message, f"Usage: /{command} <device_name>\nExample: /{command} coffee_machine")
        return

    device_name = parts[1].lower()
    action = command.replace("wifi_", "")  # Extract action: on/off/toggle/status

    logging.info(f"Received command /{command} for device: {device_name}, action: {action}")
    try:
        response = await wifi_plug_controller.control_device(device_name, action)
        await bot.reply_to(message, response)
    except Exception as e:
        logging.error(f"Error handling device '{device_name}': {e}", exc_info=True) # exc_info for full traceback
        await bot.reply_to(message, f"Failed to process command for device '{device_name}'. Error: {e}")

# --- Main Bot Polling Loop ---
async def main_loop():
    logging.info("Starting Telegram bot polling...")
    # The polling method blocks. Make sure any other async tasks are run separately
    await bot.polling(non_stop=True, interval=0)

if __name__ == '__main__':
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user (KeyboardInterrupt).")
    except Exception as e:
        logging.critical(f"An unhandled error occurred: {e}", exc_info=True) # exc_info for full traceback
    
