import discord
from discord.ext.commands import Command
from core.config import EMOJIS


async def send_command_help(ctx, command: Command, premium: bool = False):
    description = command.help or command.description or "No description provided."
    
    cooldown_obj = getattr(command, "cooldown", None)
    cooldown = cooldown_obj is not None
    cooldown_text = ""
    if cooldown:
        cooldown_text = f"{cooldown_obj.per} seconds"
    
    info_parts = []
    if premium:
        info_parts.append(f"{EMOJIS.warn} Is Premium")
    if cooldown:
        info_parts.append(f"{EMOJIS.cooldown} {cooldown_text}")
    
    embed = discord.Embed(
        title=f"Command: {command.name}",
        description=f"{description}\n",
    )
    
    if info_parts:
        embed.add_field(
            name="Information",
            value="\n".join(info_parts),
            inline=True,
        )
    
    await ctx.send(embed=embed)


async def send_bot_help(ctx):
    command_lines = []
    for command in ctx.bot.commands:
        desc = command.help or command.description or "No description"
        command_lines.append(f"-# **`{command.name}`** ➜ {desc}")
    
    commands_text = "\n".join(command_lines) if command_lines else "No commands available."
    
    description = (
        f"Welcome to **Last**󠁯, we are currently serving {len(ctx.bot.commands)} commands\n"
        f"Run `.help <command>` for even more information about that command\n"
        f"-# Made by [AerithServices](https://github.com/AerithServices) 󠁯•󠁏󠁏 Bot is [opensource](https://github.com/AerithServices/LastNB)\n\n"
        f"{commands_text}"
    )
    
    embed = discord.Embed(
        title="Last - Discord's Premier Nuke bot",
        description=description,
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1548399850905665648/2f083276b3588f4dab4545f698a290be.png?size=1024")
    
    await ctx.send(embed=embed)
