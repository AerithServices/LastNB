import discord
from discord.ext.commands import Bot

class Axron(Bot):
    def __init__(self):
        super().__init__(
            command_prefix=".",
            intents=discord.Intents.default(),
            help_command=None,
            allowed_mentions=discord.AllowedMentions(
                everyone=True, roles=True, users=True),
            owner_ids=[
                1470775670262202590, # voby
                1320349118102769767, # dennis
                289206530249719818 # deedhay
            ]
        )

    
bot = Axron()