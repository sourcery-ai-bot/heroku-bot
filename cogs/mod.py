import discord
from discord.ext import commands

from main import random_color

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="embed", aliases=["emb"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def make_embed(self, ctx, title, description, footer, *, fields=None):
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
    async def kickk(self, ctx, member: discord.Member):
        await ctx.send(f"{member.mention} got kickked! Good riddance!")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason=''):
        """ Kick a given user for an optional reason. """
        if await self.remove_member_checks(ctx, member):
            return

        await member.kick()

        await self.remove_member_embed(ctx, member, reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason=''):
        """ Ban a given user for an optional reason. """
        if await self.remove_member_checks(ctx, member):
            return

        await member.ban()

        await self.remove_member_embed(ctx, member, reason)

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


def setup(client):
    client.add_cog(Moderation(client))
