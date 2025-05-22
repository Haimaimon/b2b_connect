import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
print("📄 GOOGLE_SHEET_NAME =", GOOGLE_SHEET_NAME)

#STRIPE_SECRET = os.getenv("STRIPE_SECRET")
