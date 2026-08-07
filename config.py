import os
import time
from dotenv import load_dotenv

load_dotenv()

OWNER_ID = int(os.getenv('OWNER_ID', id here))
MEMORY_FOLDER = 'memory'
PROMPT_FILE = 'sys_prompt.txt'
GROQ_KEY = os.getenv('GROQ_API_KEY')
BOT_TOKEN = os.getenv('DISCORD_TOKEN') or os.getenv('BOT_TOKEN')
MESSAGE_LIMIT = 5
LOCAL_FONT_NAME = "Font.ttf"

START_TIME = time.time()

MODELS = {
    "core": "llama-3.3-70b-versatile",
    "vision": "qwen/qwen3.6-27b"
}

def load_system_prompt():
    if os.path.exists(PROMPT_FILE):
        try:
            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception as e:
            print(f"[Config] Error loading {PROMPT_FILE}: {e}")
            
    # Default fallback prompt
    return (
        "You are a helpful, intelligent, and versatile AI assistant. "
        "Provide accurate, clear, and concise responses. "
        "Be polite, engaging, and direct while adapting to the user's tone."
    )

SYSTEM_PROMPT = load_system_prompt()

STATS = {
    "requests": 0,
    "rate_limits": 0,
    "latency_history": []
}

if not os.path.exists(MEMORY_FOLDER):
    os.makedirs(MEMORY_FOLDER)
