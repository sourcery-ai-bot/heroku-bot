import discord
from discord.ext import commands

import asyncio as aio

from main import random_color
from cogs.info import get_user

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="embed", aliases=["emb"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def make_embed(self, ctx, title, description, footer, *, fields=None):
        """ Create an embed with specified values. """
        description = bool(description) * description

        embed = discord.Embed(
            title = title,
            description = description,
            colour = random_color()
        )

        if fields:
            fields = fields.split(' |')
            for field in fields:
                name, value = field.split(" : ")
                embed.add_field(name=name, value=value, inline=True)

        if footer != "0":
            embed.set_footer(text=footer)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    async def bane(self, ctx, member: discord.Member):
        """ Bane someone! """
        await ctx.send(f"{member.mention} was baned")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member, *, reason=''):
        """ Kick a given user for an optional reason. """
        member = await get_user(self.client, ctx, member)
        if await self.remove_member_checks(ctx, member):
            pass

        await member.kick()

        await self.remove_member_embed(ctx, member, reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member, *, reason=''):
        """ Ban a given user for an optional reason. """
        member = await get_user(self.client, ctx, member)
        if await self.remove_member_checks(ctx, member):
            pass

        await member.ban()

        await self.remove_member_embed(ctx, member, reason)

    @commands.command(name='delete', aliases=['del', 'clear', 'purge'])
    @commands.has_permissions(manage_messages=True)
    async def delete_messages(self, ctx, amount:int=1):
        """ Delete a given amount < 100 of messages and < 14 days old. Default is 1 message. """
        if amount > 100:
            amount = 100
        elif amount < 1:
            amount = 1

        channel = ctx.channel
        await channel.delete_messages([ctx.message])
        messages = await channel.history(limit=int(amount)).flatten()

        await channel.delete_messages(messages)
        message = await ctx.send(f"{amount} message{'s' * bool(int(amount) - 1)} deleted.")
        await aio.sleep(2)
        await channel.delete_messages([message])

    async def remove_member_checks(self, ctx, member):
        if ctx.author.id == member.id:
            await ctx.send(f"You can't {ctx.command.name} yourself, silly.")
            return True
        return False

    async def remove_member_embed(self, ctx, member, reason):
        n_or_no_n = 'n' if ctx.command.name == 'ban' else ''

        embed = discord.Embed(
            title=f"{member.name} was {ctx.command}{n_or_no_n}ed for:",
            description=f"{'No reason given.' * (not bool(reason))}{reason}",
            colour = random_color()
        )

        embed.set_author(
            name = f"{member}",
            icon_url = member.avatar_url
        )

        embed.set_footer(text=f"UID : {member.id}")

        await ctx.send(embed=embed)

    @kick.error
    @ban.error
    async def remove_member_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            return await ctx.send(f"You must pass in a valid member to {ctx.command} them, {ctx.author.mention}.")


def setup(client):
    client.add_cog(Moderation(client))
