import os

SYMBOLS = [s.strip().upper() for s in os.getenv("SYMBOLS", "BTC,ETH,SOL").split(",") if s.strip()]

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")

ALERT_1H_PCT = float(os.getenv("ALERT_1H_PCT", "3.0"))
ALERT_24H_PCT = float(os.getenv("ALERT_24H_PCT", "8.0"))
ALERT_RSI_HIGH = float(os.getenv("ALERT_RSI_HIGH", "70"))
ALERT_RSI_LOW = float(os.getenv("ALERT_RSI_LOW", "30"))

QUIET_MODE = os.getenv("QUIET_MODE", "false").lower() == "true"
FORCE_SEND = os.getenv("FORCE_SEND", "false").lower() == "true"
