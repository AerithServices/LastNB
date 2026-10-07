import discord
from discord.ext import commands
from typing import Callable, Any
from src.core.managers.usertypes import user_manager


class PremiumCooldown(commands.Cooldown):
    def __init__(self, rate: int, per: float, bucket_type: commands.BucketType):
        super().__init__(rate, per)
        self.bucket_type = bucket_type

    def get_retry_after(self, ctx: commands.Context) -> float:
        retry_after = super().get_retry_after(ctx)
        if retry_after:
            user_type = user_manager.get_user_type(ctx.author.id)
            if user_type == "premium":
                return retry_after * 0.75
        return retry_after


def cooldown(
    rate: int,
    per: float,
    bucket_type: commands.BucketType = commands.BucketType.default
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    cd = PremiumCooldown(rate, per, bucket_type)
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if isinstance(func, commands.Command):
            func.cooldown = cd
        else:
            func.__commands_cooldown__ = cd
        return commands.cooldown(rate, per, bucket_type)(func)
    
    return decorator


def premium_cooldown(
    rate: int,
    per: float,
    bucket_type: commands.BucketType = commands.BucketType.default
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    cd = PremiumCooldown(rate, per, bucket_type)
    return commands.max_concurrency(1, per=bucket_type, wait=False).__call__(commands.cooldown(rate, per, bucket_type))