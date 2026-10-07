import os
from dotenv import load_dotenv
from src.core.axron import bot

load_dotenv()

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
    print(f"Logged in as {bot.user}")
    print("-----")