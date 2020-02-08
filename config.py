import os


TOKEN = os.environ["TOKEN"]

TRIOGRAM_LOGGING_LEVEL = os.getenv("TRIOGRAM_LOGGING_LEVEL", "INFO")
BOT_LOGGING_LEVEL = os.getenv("BOT_LOGGING_LEVEL", "INFO")

ROUND_DURATION = 10
CHAT_MEMBERS = list(map(int, os.environ["CHAT_MEMBERS"].split(",")))
PACK = os.environ["PACK"]
