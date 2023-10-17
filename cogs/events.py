import discord
from discord.ext import commands

from datetime import datetime

from main import random_color

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.client.user.name} brought online at {datetime.now()}.")

        @commands.Cog.listener()
        async def on_command_error(self, ctx, error):
            if isinstance(
                error, (commands.CommandNotFound, commands.NoPrivateMessage)
            ):
                return

            if isinstance(error, commands.CommandOnCooldown):
                embed = discord.Embed(
                    title = "Command cooldown",
                    description = f"Please wait {error.retry_after:.1f} seconds before using `{ctx.command}` again.",
                    colour = 0xAA0000
                )

                await ctx.send(embed=embed)
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send(f"You don't have permission to do that, {ctx.author.mention}!")
            elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument) and ctx.command not in ["kick", "ban"]:
                await ctx.send(f"Please send `{self.client.command_prefix[0]}help {ctx.command.name}` to see how to use it correctly, {ctx.author.mention}.")


def setup(client):
    client.add_cog(Events(client))
