import discord
from discord.ext.commands import Bot
import pkgutil
from pathlib import Path

class Axron(Bot):
    def __init__(self):
        super().__init__(
            command_prefix=".",
            intents=discord.Intents.all(),
            help_command=None,
            allowed_mentions=discord.AllowedMentions(
                everyone=True, roles=True, users=True),
            owner_ids=[
                1470775670262202590, # voby
                1320349118102769767, # dennis
                289206530249719818 # deedhay
            ]
        )

    async def setup_hook(self):
        plugins_dir = Path(__file__).parent.parent / "plugins"
        for _, package_name, is_package in pkgutil.walk_packages([str(plugins_dir)], prefix="src.plugins."):
            if is_package:
                try:
                    await self.load_extension(package_name)
                    print(f"Loaded cog: {package_name}")
                except Exception as e:
                    print(f"Failed to load cog {package_name}: {e}")

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Streaming(name="Last", url="https://twitch.tv/voby7")
        )

bot = Axron()