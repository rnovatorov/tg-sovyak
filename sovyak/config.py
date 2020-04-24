import os


TOKEN = os.environ["TOKEN"]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TRIOGRAM_LOG_LEVEL = os.getenv("TRIOGRAM_LOG_LEVEL", "WARNING")

ROUND_DURATION = int(os.getenv("ROUND_DURATION", 30))
CHAT_MEMBERS = list(map(int, os.environ["CHAT_MEMBERS"].split(",")))
PACK = os.environ["PACK"]

try:
    PACK_SAMPLE = int(os.environ["PACK_SAMPLE"])
except KeyError:
    PACK_SAMPLE = None
