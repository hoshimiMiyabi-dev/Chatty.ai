import os
import re
import json
import discord
from PIL import ImageFont
import config

def load_json_safely(filepath, default_value):
    """Loads a JSON file safely, returning default_value if the file doesn't exist or is corrupt."""
    if not os.path.exists(filepath):
        return default_value
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Utils] Failed to load {filepath}: {e}")
        return default_value

def get_font(size: int):
    """Loads custom TTF font if available, falling back to PIL default font."""
    font_path = config.LOCAL_FONT_NAME
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def clean_ai_response(text: str) -> str:
    """Strips out internal thought tags like <think>...</think> from reasoning models."""
    if not text:
        return ""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()

async def send_split_message(channel, content: str, reference=None):
    """Splits messages longer than Discord's 2000 character limit cleanly."""
    if len(content) <= 2000:
        if reference:
            await reference.reply(content)
        else:
            await channel.send(content)
        return

    # Split long text into chunks under 2000 chars
    chunks = []
    while len(content) > 0:
        if len(content) <= 2000:
            chunks.append(content)
            break
        
        # Try to find a newline or space near the limit
        split_at = content.rfind('\n', 0, 1900)
        if split_at == -1:
            split_at = content.rfind(' ', 0, 1900)
        if split_at == -1:
            split_at = 1900

        chunks.append(content[:split_at])
        content = content[split_at:].lstrip()

    for idx, chunk in enumerate(chunks):
        if idx == 0 and reference:
            await reference.reply(chunk)
        else:
            await channel.send(chunk)
