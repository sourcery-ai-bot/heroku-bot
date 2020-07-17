import discord
from discord.ext import commands

token = process.env.BOT_TOKEN
prefix = "."

client = commands.Bot(command_prefix=prefix)

@client.command()
async def echo(ctx, *, words):
    await ctx.send(words)

print(f"{client.user} brought online")

client.run(token)
