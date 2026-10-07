import discord
from discord.ext import commands
from typing import Callable, Any, Union
from src.core.managers.usertypes import user_manager


def cooldown(
    rate: int,
    per: float,
    bucket_type: commands.BucketType = commands.BucketType.default
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def predicate(ctx: commands.Context) -> bool:
        bucket = commands.CooldownMapping.from_cooldown(rate, per, bucket_type)
        retry_after = bucket.get_bucket(ctx.message).update_rate_limit()
        if retry_after:
            user_type = user_manager.get_user_type(ctx.author.id)
            if user_type == "premium":
                retry_after *= 0.75
            if retry_after > 0:
                raise commands.CommandOnCooldown(bucket, retry_after, bucket_type)
        return True

    return commands.check(predicate)


class PremiumCooldown(commands.Cooldown):
    def __init__(self, rate: int, per: float, bucket_type: commands.BucketType):
        super().__init__(rate, per, bucket_type)

    def get_retry_after(self, ctx: commands.Context) -> float:
        retry_after = super().get_retry_after(ctx)
        if retry_after:
            user_type = user_manager.get_user_type(ctx.author.id)
            if user_type == "premium":
                return retry_after * 0.75
        return retry_after


def premium_cooldown(
    rate: int,
    per: float,
    bucket_type: commands.BucketType = commands.BucketType.default
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    cd = PremiumCooldown(rate, per, bucket_type)
    return commands.max_concurrency(1, per=bucket_type, wait=False).__call__(commands.cooldown(rate, per, bucket_type))