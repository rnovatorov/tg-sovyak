import os


TOKEN = os.environ["TOKEN"]

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
TRIOGRAM_LOGGING_LEVEL = os.getenv("TRIOGRAM_LOGGING_LEVEL", "WARNING")

ROUND_DURATION = 10
CHAT_MEMBERS = list(map(int, os.environ["CHAT_MEMBERS"].split(",")))
PACK = os.environ["PACK"]
