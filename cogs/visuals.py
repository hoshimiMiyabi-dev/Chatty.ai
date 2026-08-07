import time
import discord
from discord.ext import commands
from discord import app_commands
import config
from image_gen import create_ping_card, create_usercard

class VisualsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_groq_ping(self):
        start = time.perf_counter()
        try:
            await self.bot.groq_client.models.list()
            end = time.perf_counter()
            lat = round((end - start) * 1000)
            config.STATS["latency_history"].append(lat)
            if len(config.STATS["latency_history"]) > 20:
                config.STATS["latency_history"].pop(0)
            return lat
        except Exception:
            return 999

    @commands.command(name="ping")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def prefix_ping(self, ctx):
        ws_ping = round(self.bot.latency * 1000)
        status_msg = await ctx.send("Gathering network telemetry...")
        groq_ping = await self.get_groq_ping()
        avatar_bytes = await self.bot.user.display_avatar.read()

        buf = create_ping_card(avatar_bytes, self.bot.user.name, ws_ping, groq_ping)
        await status_msg.delete()
        await ctx.reply(file=discord.File(fp=buf, filename="ping_card.png"))

    @app_commands.command(name="ping", description="View network latency and API inference metrics")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def slash_ping(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ws_ping = round(self.bot.latency * 1000)
        groq_ping = await self.get_groq_ping()
        avatar_bytes = await self.bot.user.display_avatar.read()

        buf = create_ping_card(avatar_bytes, self.bot.user.name, ws_ping, groq_ping)
        await interaction.followup.send(file=discord.File(fp=buf, filename="ping_card.png"))

    @commands.command(name="usercard")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def prefix_usercard(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        avatar_bytes = await target.display_avatar.read()
        joined_at = target.joined_at.strftime("%Y-%m-%d") if target.joined_at else "N/A"
        created_at = target.created_at.strftime("%Y-%m-%d")
        top_role = target.top_role.name if target.top_role else "None"

        buf = create_usercard(avatar_bytes, target.display_name, joined_at, created_at, top_role)
        await ctx.reply(file=discord.File(fp=buf, filename="usercard.png"))

    @app_commands.command(name="usercard", description="Generate a tactical profile card for a member")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def slash_usercard(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer()
        target = member or interaction.user
        avatar_bytes = await target.display_avatar.read()
        joined_at = target.joined_at.strftime("%Y-%m-%d") if getattr(target, 'joined_at', None) else "N/A"
        created_at = target.created_at.strftime("%Y-%m-%d")
        top_role = target.top_role.name if getattr(target, 'top_role', None) else "None"

        buf = create_usercard(avatar_bytes, target.display_name, joined_at, created_at, top_role)
        await interaction.followup.send(file=discord.File(fp=buf, filename="usercard.png"))

async def setup(bot):
    await bot.add_cog(VisualsCog(bot))
