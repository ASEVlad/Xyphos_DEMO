import time
from loguru import logger
from src.telegram_handler import handle_telegram_updates

def main():
    logger.add("logfile.log", rotation="2 MB", level="INFO")
    while True:
        handle_telegram_updates()
        time.sleep(5)


if __name__ == "__main__":
    main()