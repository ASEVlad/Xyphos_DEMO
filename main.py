import time
from loguru import logger
from src.telegram_handler import handle_telegram_updates

def main():
    logger.add("logfile.log", rotation="2 MB", level="INFO")
    while True:
        try:
            handle_telegram_updates()
        except Exception as e:
            logger.error(e)
        time.sleep(5)


if __name__ == "__main__":
    main()