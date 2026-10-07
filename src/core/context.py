from __future__ import annotations
import discord

from discord.ext.commands import HelpCommand, Group
from datetime import datetime
from xxhash import xxh32_hexdigest

from discord.ext.commands import Command, Group


from typing import Union
try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

from typing import Any, Dict, List, Optional, TYPE_CHECKING, TypedDict, cast

from discord import (
    AllowedMentions,
    ButtonStyle,
    Color,
    Message,
    MessageReference,
    Embed,
    Role,
    Member,
    ui,
)
from discord.ui import View, Button
from discord.ui import button
from discord.ext.commands import Context as BaseContext
from core.config import *

if TYPE_CHECKING:
    from core.axron import Axron


class FieldDict(TypedDict, total=False):
    name: str
    value: str
    inline: bool


class FooterDict(TypedDict, total=False):
    text: Optional[str]
    icon_url: Optional[str]


class AuthorDict(TypedDict, total=False):
    name: Optional[str]
    icon_url: Optional[str]


class ButtonDict(TypedDict, total=False):
    url: Optional[str]
    emoji: Optional[str]
    style: Optional[ButtonStyle]
    label: Optional[str]


class MessageKwargs(TypedDict, total=False):
    content: Optional[str]
    tts: Optional[bool]
    allowed_mentions: Optional[AllowedMentions]
    reference: Optional[MessageReference]
    mention_author: Optional[bool]
    delete_after: Optional[float]

    # Embed Related
    url: Optional[str]
    title: Optional[str]
    color: Optional[Color]
    image: Optional[str]
    description: Optional[str]
    thumbnail: Optional[str]
    footer: Optional[FooterDict]
    author: Optional[AuthorDict]
    fields: Optional[List[FieldDict]]
    timestamp: Optional[datetime]
    view: Optional[View]
    buttons: Optional[List[ButtonDict]]


class Context(BaseContext):
    bot: "Axron"

    def is_dangerous(self, role: Role) -> bool:
        permissions = role.permissions

        return any(
            [
                permissions.kick_members,
                permissions.ban_members,
                permissions.administrator,
                permissions.manage_channels,
                permissions.manage_guild,
                permissions.manage_messages,
                permissions.manage_roles,
                permissions.manage_webhooks,
                permissions.manage_emojis_and_stickers,
                permissions.manage_threads,
                permissions.mention_everyone,
                permissions.moderate_members,
            ]
        )

    async def approve(self, message: str, **kwargs) -> Message:
        return await self.send(
            embed=Embed(
                color=COLORS.approve,
                description=f"{EMOJIS.APPROVE} {self.author.mention}: {message}",
            ),
            **kwargs,
        )

    async def warn(self, message: str, **kwargs) -> Message:
        return await self.send(
            embed=Embed(
                color=COLORS.warn,
                description=f"{EMOJIS.WARN} {self.author.mention}: {message}",
            ),
            **kwargs,
        )

    async def deny(self, message: str, **kwargs) -> Message:
        return await self.send(
            embed=Embed(
                color=COLORS.deny,
                description=f"{EMOJIS.DENY} {self.author.mention}: {message}",
            ),
            **kwargs,
        )

    async def cooldown(self, message: str, **kwargs) -> Message:
        return await self.send(
            embed=Embed(
                color=0x38A9E1,
                description=f"{EMOJIS.COOLDOWN} {self.author.mention}: {message}",
            )
        )

class Confirmation(View):
    def __init__(self, ctx: Context, user: Member, reason: str, action: str):
        super().__init__()
        self.ctx = ctx
        self.user = user
        self.reason = reason
        self.action = action
        self.message = None

    async def send_confirmation(self):
        embed = Embed(
            title="",
            description=f"Are you sure you want to {self.action} {self.user.mention if self.user else ''}?",
            color=COLORS.neutral,
        )
        self.message = await self.ctx.send(embed=embed, view=self)

    @ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, button: Button, interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "You cannot confirm this action.", ephemeral=True
            )
            return
        if self.action == "ban" and self.user:
            await self.user.ban(reason=self.reason)
            await self.ctx.approve(f"{self.user.mention} has been **banned**.")
        elif self.action == "kick" and self.user:
            await self.user.kick(reason=self.reason)
            await self.ctx.approve(f"{self.user.mention} has been **kicked**.")

        if self.message:
            await self.message.delete()
        self.stop()

    @ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, button: Button, interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "You cannot confirm cancel action.", ephemeral=True
            )
            return
        await self.ctx.approve(
            f"{self.action.capitalize()} action has been **cancelled**."
        )
        if self.message:
            await self.message.delete()
        self.stop()