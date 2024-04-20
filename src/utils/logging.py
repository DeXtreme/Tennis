import logging
import os

from dotenv import load_dotenv

load_dotenv()
# logging.basicConfig(level=logging.NOTSET)

log_level = "INFO".upper()


class EmojiFormatter(logging.Formatter):
    def format(self, record):
        log_level_emoji = {
            logging.DEBUG: "🐞 ",
            logging.INFO: "ℹ️ ",
            logging.WARNING: "⚠️ ",
            logging.ERROR: "🚨 ",
            logging.CRITICAL: "🆘🔥 ",
        }
        emoji = log_level_emoji.get(record.levelno, "❓")
        message = super().format(record)
        asctime = self.formatTime(record, self.datefmt)
        level_name = record.levelname
        return f"{asctime} {level_name} {emoji} {message}"


logger = logging.getLogger("django")

handler = logging.StreamHandler()
handler.setFormatter(EmojiFormatter())
logger.addHandler(handler)
logger.setLevel(level=log_level)
