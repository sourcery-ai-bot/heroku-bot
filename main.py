import discord
from discord.ext import commands

import json
import os
from random import randint

# token = os.environ.get('BOT_TOKEN')
token = "Njg4MTk4MDEwMzQxMDMxOTcx.XxOV2Q.Xg5CPFmD8DvTXblqkcAx-cKPx8U"

with open('config.json', 'r') as file:
    config = json.load(file)
    managers = config["managers"]
    prefix = config["prefix"]

def is_manager(ctx, member=None):
    member = member or ctx.author
    return member.id in managers


random_color = lambda : randint(0, 16**6)


client = commands.Bot(command_prefix=prefix)

@client.command(aliases=['rel'])
@commands.check(is_manager)
async def reload(ctx, extension):
    """ Reload one or all extensions """
    if extension == 'all':
        for cog in os.listdir('./cogs'):
            if cog.endswith('.py'):
                client.reload_extension(f'cogs.{cog[:-3]}')
        return await ctx.send('All cogs reloaded.')
    client.reload_extension(f'cogs.{extension}')
    await ctx.send(f"Cog `{extension}` reloaded.")


@client.command()
@commands.check(is_manager)
async def load(ctx, extension):
    """ Load an extension """
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Cog `{extension}` loaded.")


@client.command(aliases=['unl'])
@commands.check(is_manager)
async def unload(ctx, extension):
    """ Unloads an extension """
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Cog `{extension}` unloaded.")


for cog in os.listdir('./cogs'):
    if cog.endswith('.py'):
        client.load_extension(f"cogs.{cog[:-3]}")

print("All cogs loaded.")

client.run(token)
