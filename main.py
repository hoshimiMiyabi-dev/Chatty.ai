import os
import json
import asyncio
import discord
from discord.ext import commands
from groq import AsyncGroq, RateLimitError
import config
from utils import load_json_safely, clean_ai_response, send_split_message

class HelpfulAIBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        activity = discord.Activity(type=discord.ActivityType.listening, name="commands | Chat")
        super().__init__(command_prefix="-", intents=intents, activity=activity)
        
        self.channel_file = "active_channels.json"
        self.active_channels = load_json_safely(self.channel_file, [])
        self.chat_cd = commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.user)
        self.groq_client = AsyncGroq(api_key=config.GROQ_KEY)

    def save_channels(self):
        with open(self.channel_file, "w") as f:
            json.dump(self.active_channels, f, indent=4)

    async def setup_hook(self):
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.stats")
        await self.load_extension("cogs.visuals")
        await self.tree.sync()

    async def on_ready(self):
        print(f"[{self.user.name}] Bot online and operational.")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            config.STATS["rate_limits"] += 1
            await ctx.reply(f"Rate limited. Please wait {round(error.retry_after, 1)}s.", delete_after=5)

    async def on_message(self, message):
        if message.author.bot: return

        if message.content.startswith(self.command_prefix):
            await self.process_commands(message)
            return

        is_active = message.channel.id in self.active_channels
        is_pinged = self.user.mentioned_in(message)

        if is_active or is_pinged:
            bucket = self.chat_cd.get_bucket(message)
            retry_after = bucket.update_rate_limit()
            if retry_after:
                config.STATS["rate_limits"] += 1
                await message.reply(f"Please wait {round(retry_after, 1)}s before messaging again.", delete_after=4)
                return

            async with message.channel.typing():
                file_name = f"chat_{message.channel.id}.json"
                path = os.path.join(config.MEMORY_FOLDER, file_name)
                history = load_json_safely(path, [])
                sender_label = message.author.display_name

                image_url = None
                if message.attachments:
                    for att in message.attachments:
                        if att.content_type and att.content_type.startswith("image/"):
                            image_url = att.url
                            break

                if image_url:
                    current_msg = {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"{sender_label}: {message.content}" if message.content else f"{sender_label}: [Sent an image]"},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                    trimmed_history = history[-2:] if len(history) >= 2 else history
                    selected_model = config.MODELS["vision"]
                else:
                    current_msg = {"role": "user", "content": f"{sender_label}: {message.content}"}
                    trimmed_history = history
                    selected_model = config.MODELS["core"]

                api_messages = [{"role": "system", "content": config.SYSTEM_PROMPT}] + trimmed_history + [current_msg]

                try:
                    chat_completion = await self.groq_client.chat.completions.create(
                        messages=api_messages, model=selected_model
                    )
                    config.STATS["requests"] += 1

                    reply = clean_ai_response(chat_completion.choices[0].message.content) or "I couldn't generate a response."
                    user_entry = f"{sender_label}: {message.content}" if message.content else f"{sender_label}: [Sent an image]"
                    
                    history.append({"role": "user", "content": user_entry})
                    history.append({"role": "assistant", "content": reply})
                    
                    if len(history) > (config.MESSAGE_LIMIT * 2):
                        history = history[-(config.MESSAGE_LIMIT * 2):]

                    with open(path, "w") as f:
                        json.dump(history, f, indent=4)

                    await send_split_message(message.channel, reply, reference=message)

                except RateLimitError:
                    config.STATS["rate_limits"] += 1
                    await message.channel.send("API Rate limit reached. Please try again shortly.")
                except Exception as e:
                    print(f"Error processing request: {e}")
                    await message.channel.send("An error occurred while generating the response.")

bot = HelpfulAIBot()

if __name__ == "__main__":
    if not config.BOT_TOKEN:
        print("[Error] BOT_TOKEN missing in environment variables!")
    else:
        asyncio.run(bot.start(config.BOT_TOKEN))
