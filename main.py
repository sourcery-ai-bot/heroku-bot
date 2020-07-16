import discord
from discord.ext import commands

token = "NzI5OTA5MjI1NTY3OTQ0NzI0.XwfwqA.yLQaP8cJnr7CtDIKUVoknjrSm-4"
prefix = "."

client = commands.Bot(command_prefix=prefix)

@client.command()
async def echo(ctx, *, words):
    await ctx.send(words)

print(f"{client.user} brought online")

client.run(token)
