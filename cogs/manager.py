import discord
from discord.ext import commands

from main import is_manager

from datetime import datetime

class Manager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check(is_manager)
    async def shutdown(self, ctx):
        name = self.client.user.name
        await ctx.send(f"{name} shut down.")
        print(f"{name} shut down @ {datetime.now()} by {ctx.author.name}.")
        exit()


def setup(client):
    client.add_cog(Manager(client))
