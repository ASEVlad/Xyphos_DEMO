import time

from src.telegram_handler import handle_telegram_updates

while True:
    handle_telegram_updates()
    time.sleep(5)