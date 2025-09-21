import os
import time
from loguru import logger

import telegram
from dotenv import load_dotenv

from src.messages import welcome_message, repeated_login
from src.message_logic import handle_operation

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSISTENT_USER_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "registered_users.txt")) # File to store chat_ids
UPDATES_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "handled_updates.txt")) # File to store chat_ids

load_dotenv(os.path.abspath(os.path.join(BASE_DIR, "..", ".env")))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


def load_registered_users():
    """Loads registered user chat_ids from a file."""
    try:
        with open(PERSISTENT_USER_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_registered_user(chat_id):
    if not os.path.exists(PERSISTENT_USER_FILE):
        open(PERSISTENT_USER_FILE, "w").close()
    """Saves a new user's chat_id to the file."""
    with open(PERSISTENT_USER_FILE, "a") as f:
        f.write(str(chat_id) + "\n")

def handle_telegram_updates():
    """
    Handles incoming Telegram messages to register new users.
    This function would typically be part of a larger bot framework.
    For simplicity here, we'll show a basic polling mechanism.
    """
    # This is a simplified polling mechanism. For a production bot,
    # you'd use the webhook or the more advanced polling methods from python-telegram-bot.

    # Get the latest update_id
    try:
        updates = bot.get_updates(timeout=10) # Poll for updates
        for update in updates:
            if update.message:
                chat_id = str(update.message.chat_id)
                message_text = update.message.text
                update_id = str(update.update_id)

                handled_updates = retrieve_handled_updates()
                if update_id in handled_updates:
                    continue

                logger.info("There is one more update message to handle!")
                if message_text.lower() == "/start":
                    if chat_id not in load_registered_users():
                        save_registered_user(chat_id)
                        bot.send_message(chat_id=chat_id, text=welcome_message)
                        logger.info(f"New user registered: {chat_id}")
                    else:
                        bot.send_message(chat_id=chat_id, text=repeated_login)
                        logger.info(f"User {chat_id} already registered.")
                else:
                    handle_operation(bot, chat_id, message_text)

                handled_updates.add(update_id)
                save_handled_updates(handled_updates)

    except telegram.error.TelegramError as e:
        logger.error(f"Error getting Telegram updates: {e}")


def send_notification_to_all_users(message):
    """Sends a message to all registered Telegram users."""
    if bot is None:
        print("Telegram bot not initialized.")
        return

    user_ids = load_registered_users()
    if not user_ids:
        print("No registered users to send notifications to.")
        return

    print(f"Sending notification to {len(user_ids)} users...")
    for user_id in user_ids:
        try:
            bot.send_message(chat_id=user_id, text=message)
            print(f"Message sent to {user_id}")
        except telegram.error.TelegramError as e:
            print(f"Failed to send message to {user_id}: {e}")
            # Optionally, you might want to remove users who consistently fail

def send_irritative_notification_to_all_users(message):
    for i in range(5):
        send_notification_to_all_users(message)
        time.sleep(2)

    time.sleep(10)

    for i in range(5):
        send_notification_to_all_users(message)
        time.sleep(2)

    time.sleep(10)

    for i in range(5):
        send_notification_to_all_users(message)
        time.sleep(2)


def save_handled_updates(handled_updates):
    with open(UPDATES_FILE, 'w', encoding='utf-8') as f:
        for dapp in sorted(handled_updates):
            f.write(f"{dapp}\n")


def retrieve_handled_updates():
    if not os.path.exists(UPDATES_FILE):
        return set()
    with open(UPDATES_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())
