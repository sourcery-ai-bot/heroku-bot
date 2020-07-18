import discord
from discord.ext import commands

import json
from math import floor
from datetime import datetime
from random import choice

from snowflake import to_datetime as to_dt
from json_handler import load_data, dump_data
from main import random_color

level_up_messages = [
    "Niiiiice, {user}, you done leveled up!",
    "Level up, {user}, now get back to spawn point!",
    "Your level has been updated; increased by one, {user}.",
    "Like, ohhhhhmigod, {user}, you like, just leveled, like, up!",
    "Your xp count has caused your level to increase by one, {user}. Good job.",
    "You like chattin', dontcha, {user}! Level up!",
    "Dogs. {user}.",
    "Keep it up, {user}! You just leveled up!",
    "Congrats, {user}. You talked so much you leveled up.",
    "{user}.... * anime noises * 'Nani?!?! Your jitsu level has increased by.... ***one?!?***'",
    "Bro, why would you talk this much? You literally leveled up by talking so much, {user}. Dedication."
]

levels_log = "logs/user_levels.json"
message_dt_log = "logs/message_dt.json"
levels_config = "levels_config.json"

class Levels(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = load_data(levels_config)

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        _id = str(ctx.author.id)
        now = to_dt(ctx.id)

        message_dt = load_data(message_dt_log)

        try:
            then = message_dt[_id]
        except Exception:
            message_dt[_id] = ctx.id

            dump_data(message_dt, message_dt_log)
            return

        then_user_info = self.get_user(ctx.author)

        if (now - to_dt(then)).seconds > self.config["chat_timer"]:
            message_dt[_id] = ctx.id
            self.add_xp(ctx.author, self.config["chat_points"])
            if then_user_info[0] != self.get_user(ctx.author)[0]:
                message = choice(level_up_messages).replace("{user}", ctx.author.mention)
                await ctx.channel.send(message)

        dump_data(message_dt, message_dt_log)

    @commands.command(name='settings')
    @commands.guild_only()
    @commands.has_permissions()
    async def show_level_settings(self, ctx):
        """ View current level configuration settings. """
        embed = discord.Embed(
            title = "Level configuration settings",
            description = "Various level settings for chat and upvote stats.\n"
                f"Update individual settings by using `{self.client.command_prefix[0]}set ""{setting}`.",
                colour = random_color()
        )

        embed.add_field(name='chat_timer', value=self.config["chat_timer"], inline=False)
        embed.add_field(name='chat_points', value=self.config["chat_points"], inline=False)
        embed.add_field(name='upvote_points', value=self.config["upvote_points"], inline=False)
        embed.add_field(name='difficulty', value=self.config["difficulty"], inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=['up', 'props'])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=3600, type=commands.BucketType.user)
    async def upvote(self, ctx, user: discord.Member, *, reason: str=''):
        """ Freely give a user a set amount of points. """
        if ctx.author.id == user.id:
            return await ctx.send("You can't upvote yourself, cheater!")
        self.add_xp(user, self.config["upvote_points"])
        await ctx.send(f"{ctx.author.mention} upvoted {user.mention}{' for ' * bool(reason)}{reason * bool(reason)}!")

    @commands.command(aliases=["lev"])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def level(self, ctx, user: discord.Member = None):
        """ Check a user's level and xp. """
        user = user or ctx.author

        embed = discord.Embed(
            title = f"{user.name}",
            colour = random_color()
        )

        user_level = self.get_user(user)

        embed.add_field(name='level', value=str(user_level[0]), inline=True)
        embed.add_field(name='xp', value=str(user_level[1]), inline=True)
        embed.set_footer(text=f"{user} | {user.id}")

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def give(self, ctx, user: discord.Member, xp: int):
        """ Give user a given amount of xp. """
        if user.id == ctx.author.id:
            return

        if xp < 1:
            xp = 1

        self.add_xp(user, xp)
        await ctx.send(f"Gave {user.mention} {xp} point{'s' * bool(xp - 1)}!")

    @commands.command(aliases=['restart'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reset(self, ctx, user: discord.Member):
        """ Reset user's level and xp to [0, 0] """
        self.update_user(user)
        await ctx.send(f"Reset {user.mention}'s xp and level to 0.")

    @commands.command(name="set")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def update_setting_command(self, ctx, setting: str, updated_setting):
        """ Update a given level configuration setting. """
        original_setting = self.config[setting]
        self.update_config(setting, updated_setting)
        embed = discord.Embed(
            title = "Level configuration update",
            description = f"Altered setting: {setting}",
            colour = random_color()
        )

        embed.add_field(name="Original", value=str(original_setting), inline=True)
        embed.add_field(name="Updated", value=str(updated_setting), inline=True)
        await ctx.send(embed=embed)

    def update_user(self, user, info: list = [0, 0]):
        """ Update user levels in user_levels.json file.
        If user is not found, it will create a new user
        item with a value of [0, 0], AKA the starting point. """
        if user.bot:
            return
        _id = str(user.id)
        user_levels = load_data(levels_log)

        user_levels[_id] = info
        dump_data(user_levels, levels_log)

    def get_user(self, user):
        _id = str(user.id)
        user_levels = load_data(levels_log)

        try:
            return user_levels[_id]
        except Exception:
            self.update_user(user)
            return self.get_user(user)

    def add_xp(self, user: discord.Member, xp: int):
        user_level = self.get_user(user)
        user_level[1] += xp
        user_level[0] = floor((((self.config["difficulty"] ** 2) + 8 * user_level[1] * self.config["difficulty"]) ** 0.5) / (2 * self.config["difficulty"]) + 0.5)

        self.update_user(user, user_level)

    def update_config(self, setting: str, updated_setting: int):
        self.config[setting] = int(updated_setting)
        dump_data(self.config, levels_config)

        print(f"Updated {setting} to {updated_setting}")


def setup(client):
    client.add_cog(Levels(client))
