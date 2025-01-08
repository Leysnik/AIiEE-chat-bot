import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
FOLDER_ID = os.getenv("FOLDER_ID")
API_KEY = os.getenv("API_KEY")