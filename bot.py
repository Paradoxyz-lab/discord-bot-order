# bot.py
import os
from dotenv import load_dotenv

load_dotenv()
from main import run_bot

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    run_bot(token)
