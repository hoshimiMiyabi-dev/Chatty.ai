import discord
from discord.ext import commands
from discord import app_commands
import config

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prompt")
    async def set_prompt(self, ctx, *, new_prompt: str = None):
        if ctx.author.id != config.OWNER_ID:
            await ctx.reply("Unauthorized action.")
            return
            
        if not new_prompt:
            await ctx.reply(f"**Current Active Prompt:**\n```{config.SYSTEM_PROMPT}```")
            return

        config.SYSTEM_PROMPT = new_prompt
        try:
            with open(config.PROMPT_FILE, "w", encoding="utf-8") as f:
                f.write(new_prompt)
            await ctx.reply("System prompt updated dynamically and saved to `sys_prompt.txt`.")
        except Exception as e:
            await ctx.reply(f"Updated active prompt in memory, but failed saving to file: {e}")

    @commands.command(name="model")
    async def set_model(self, ctx, target: str = None, *, new_model: str = None):
        if ctx.author.id != config.OWNER_ID:
            await ctx.reply("Unauthorized action.")
            return
            
        if not target or target not in config.MODELS:
            await ctx.reply(f"Active Models:\nCore: `{config.MODELS['core']}`\nVision: `{config.MODELS['vision']}`\nUsage: `-model <core|vision> <model_name>`")
            return
            
        if new_model:
            config.MODELS[target] = new_model
            await ctx.reply(f"Updated `{target}` model string to `{new_model}`.")
        else:
            await ctx.reply(f"Current `{target}` model string: `{config.MODELS[target]}`")

    @app_commands.command(name="addchat", description="Authorize current channel for AI responses")
    async def slash_add_chat(self, interaction: discord.Interaction):
        if interaction.user.id != config.OWNER_ID and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("Insufficient permissions.", ephemeral=True)
            return
            
        if interaction.channel_id not in self.bot.active_channels:
            self.bot.active_channels.append(interaction.channel_id)
            self.bot.save_channels()
            await interaction.response.send_message("Channel authorized for AI chat.", ephemeral=True)
        else:
            await interaction.response.send_message("Channel is already authorized.", ephemeral=True)

    @app_commands.command(name="removechat", description="Deauthorize current channel for AI responses")
    async def slash_remove_chat(self, interaction: discord.Interaction):
        if interaction.user.id != config.OWNER_ID and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("Insufficient permissions.", ephemeral=True)
            return
            
        if interaction.channel_id in self.bot.active_channels:
            self.bot.active_channels.remove(interaction.channel_id)
            self.bot.save_channels()
            await interaction.response.send_message("Channel deauthorized.", ephemeral=True)
        else:
            await interaction.response.send_message("Channel is not currently active.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
