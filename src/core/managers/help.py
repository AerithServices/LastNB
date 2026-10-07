import discord
from discord.ext import commands
from discord.ext.commands import Command
from src.core.config import EMOJIS
from src.core.managers.usertypes import user_manager


async def send_command_help(ctx, command: Command, premium: bool = False):
    description = command.help or command.description or "No description provided."

    cooldown_obj = getattr(command, "cooldown", None)
    cooldown = cooldown_obj is not None
    cooldown_text = ""
    if cooldown:
        base_per = cooldown_obj.per
        user_type = user_manager.get_user_type(ctx.author.id)
        if user_type == "premium":
            base_per = base_per * 0.75
        
        if base_per >= 3600:
            cooldown_text = f"{base_per/3600:.0f} hours"
        elif base_per >= 60:
            cooldown_text = f"{base_per/60:.0f} minutes"
        else:
            cooldown_text = f"{base_per:.0f} seconds"
        
        bucket_type = getattr(cooldown_obj, 'bucket', None)
        if bucket_type == commands.BucketType.guild:
            cooldown_text += " **per-guild**"
        elif bucket_type == commands.BucketType.user:
            cooldown_text += " **per-user**"
        elif bucket_type == commands.BucketType.channel:
            cooldown_text += " **per-channel**"

    cog_name = command.cog_name or "general"

    aliases = command.aliases
    aliases_text = ", ".join(aliases) if aliases else "None"

    info_parts = []
    if cooldown:
        info_parts.append(f"{EMOJIS.cooldown} {cooldown_text}")
    if premium:
        info_parts.append(f"{EMOJIS.warn} Is Premium command only")

    embed = discord.Embed(
        title=f"Command: {command.name}",
        description=description,
    ).set_footer(
        text=f"module: {cog_name}",
    ).add_field(
        name="Aliases",
        value=aliases_text,
        inline=True,
    ).add_field(
        name="Information",
        value="\n".join(info_parts) if info_parts else "None",
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
