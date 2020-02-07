import os


TOKEN = os.environ["TOKEN"]

TRIOGRAM_LOGGING_LEVEL = os.getenv("TRIOGRAM_LOGGING_LEVEL", "INFO")
BOT_LOGGING_LEVEL = os.getenv("BOT_LOGGING_LEVEL", "INFO")

CHAT_MEMBERS = os.environ["CHAT_MEMBERS"].split(",")
PACK = os.environ["PACK"]
