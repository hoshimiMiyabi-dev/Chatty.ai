import time
import discord
from discord.ext import commands
from discord import app_commands
import config
from image_gen import create_stats_card

def get_formatted_uptime():
    delta = int(time.time() - config.START_TIME)
    days, remainder = divmod(delta, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cmd_stats(self, ctx):
        avg_lat = round(sum(config.STATS["latency_history"]) / len(config.STATS["latency_history"])) if config.STATS["latency_history"] else 0
        uptime = get_formatted_uptime()
        avatar_bytes = await self.bot.user.display_avatar.read()

        buf = create_stats_card(avatar_bytes, uptime, config.STATS["requests"], config.STATS["rate_limits"], avg_lat)
        await ctx.reply(file=discord.File(fp=buf, filename="stats.png"))

    @app_commands.command(name="stats", description="View operational stats, token usage metrics, and bot uptime")
    @app_checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def slash_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        avg_lat = round(sum(config.STATS["latency_history"]) / len(config.STATS["latency_history"])) if config.STATS["latency_history"] else 0
        uptime = get_formatted_uptime()
        avatar_bytes = await self.bot.user.display_avatar.read()

        buf = create_stats_card(avatar_bytes, uptime, config.STATS["requests"], config.STATS["rate_limits"], avg_lat)
        await interaction.followup.send(file=discord.File(fp=buf, filename="stats.png"))

async def setup(bot):
    await bot.add_cog(StatsCog(bot))
