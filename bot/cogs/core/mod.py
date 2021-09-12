# -*- coding: utf-8 -*-

import asyncio
import contextlib
import pprint
import random
import typing

import bot.utils.utilities as tragedy
import discord
import humanize
import nanoid
import pymysql.cursors
from bot.utils.classes import WelcomeNotConfigured
from discord.channel import DMChannel
from discord.colour import Color
from discord.ext import commands, tasks
from discord.ext.commands.converter import TextChannelConverter
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import BadArgument
from discord.permissions import Permissions
from discord_components import *
from discord_components.component import Button, ButtonStyle


class Mod(commands.Cog, description="Commands to moderate your server !"):
    def __init__(self, bot):
        self.bot = bot
        self.snipe_cache = {}
        self.edit_cache = {}
        self.pool = pymysql.connect(
            host=tragedy.DotenvVar("mysqlServer"),
            user="root",
            password=tragedy.DotenvVar("mysqlPassword"),
            port=3306,
            database="tragedy",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            read_timeout=5,
            write_timeout=5,
            connect_timeout=5,
            autocommit=True
        )
        self.mysqlPing.start()
        DiscordComponents(self.bot)

    @tasks.loop(seconds=35)
    async def mysqlPing(self):
        connected = bool(self.pool.open)
        pprint.pprint(
            "Testing connection to mysql database () --> {}".format(str(connected).upper()))
        if connected is False:
            self.pool.ping(reconnect=True)
            pprint.pprint("Reconnecting to database () --> SUCCESS")
        else:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        with self.pool.cursor() as cursor:
            cursor.execute(
                "SELECT channel, message FROM `welcome` WHERE guild=%s", (member.guild.id))
            row: dict = cursor.fetchone()
            try:
                channelID = row.get("channel")
                message = row.get("message")
            except AttributeError:
                return
            try:
                channel = await self.bot.fetch_channel(channelID)
                await channel.send(self.ConvertMessage(member, message))
            except:
                return

    def ConvertMessage(self, member: discord.Member, message: str):
        variables = {
            "user": member,
            "user_ping": member.mention,
            "user_name": member.name,
            "server_name": member.guild.name
        }

        formatted: str = str(message)

        for key in variables.keys():
            try:
                formatted = formatted.replace(key, variables.get(key), -1)
            except:
                pass

        return formatted

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot is False and isinstance(message.channel, DMChannel) is not True:
            self.snipe_cache[message.channel.id] = message

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.author.bot is False and isinstance(after.channel, DMChannel) is not True:
            self.edit_cache[after.channel.id] = {
                "before": before, "after": after
            }

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.bot_has_guild_permissions(send_messages=True, embed_links=True)
    async def snipe(self, ctx):
        if not ctx.channel.id in self.snipe_cache:
            return await ctx.send('Nothing to snipe.')
        data: discord.Message = self.snipe_cache[ctx.channel.id]
        time = data.created_at
        embed = discord.Embed(color=Color.green())
        embed.set_author(name=data.author.display_name,
                         icon_url=data.author.avatar_url)
        if data.content:
            embed.description = data.content
        if data.attachments:
            if str(data.attachments[0].filename).lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                embed.set_image(
                    url="attachment://{}".format(data.attachments[0].filename))
                embed.set_footer(text='Sniped message sent at {}'.format(
                    time.strftime("%I:%M %p")))
                del self.snipe_cache[ctx.channel.id]
                return await ctx.send(embed=embed, file=await data.attachments[0].to_file())
        embed.set_footer(text='Sniped message sent at {}'.format(
            time.strftime("%I:%M %p")))
        del self.snipe_cache[ctx.channel.id]
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.bot_has_guild_permissions(send_messages=True, embed_links=True)
    async def editsnipe(self, ctx):
        if not ctx.channel.id in self.edit_cache:
            return await ctx.send('Nothing to snipe.')

        before: discord.Message = self.edit_cache[ctx.channel.id]["before"]
        after: discord.Message = self.edit_cache[ctx.channel.id]["after"]
        edited_at = after.created_at

        embed = discord.Embed(color=Color.green(), timestamp=edited_at)
        embed.set_author(name=after.author,
                         url=after.jump_url,
                         icon_url=after.author.avatar_url)
        if after.content:
            embed.add_field(
                name="Before", value=before.clean_content, inline=False)
            embed.add_field(
                name="After", value=after.clean_content, inline=False)
        del self.edit_cache[ctx.channel.id]
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True, description="kicks specified member from server",
                      help="kick <member> [reason]")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.cooldown(1, 5, type=BucketType.member)
    async def kick(self, ctx, member: commands.MemberConverter, *, reason: str = None):
        try:
            if not reason:
                try:
                    await member.kick("Kicked by {}".format(ctx.author))
                    await ctx.reply(embed=discord.Embed(title="Member Kicked",
                                                        description="**{}** was kicked by **{}** for an unspecified reason.".format(
                                                            member, ctx.author), color=discord.Color.green()))
                    try:
                        await member.send(embed=discord.Embed(title="You Were Kicked",
                                                              description="You were kicked from **{}** by **{}** for an unspecified reason.".format(
                                                                  ctx.message.guild.name, ctx.author),
                                                              color=discord.Color.green()))
                    except:
                        pass
                    return
                except Exception as exc:
                    tragedy.logError(exc)
            else:
                try:
                    await member.kick(reason="Kicked by {} for \"{}\"".format(ctx.author, reason))
                    await ctx.reply(embed=discord.Embed(title="Member Kicked",
                                                        description="**{}** was kicked by **{}** for \"{}\".".format(member,
                                                                                                                     ctx.author,
                                                                                                                     reason),
                                                        color=discord.Color.green()))
                    try:
                        await member.send(embed=discord.Embed(title="You Were Kicked",
                                                              description="You were kicked from **{}** by **{}** for \"{}\".".format(
                                                                  ctx.guild.name, ctx.author, reason),
                                                              color=discord.Color.green()))
                    except:
                        pass
                    return
                except Exception as exc:
                    tragedy.logError(exc)
        except discord.Forbidden:
            embed = discord.Embed(title="Oops !",
                                  description="I am not high enough in the role heirachy to do that you silly goose.",
                                  color=discord.Color.red())
            await ctx.reply(embed=embed, mention_author=True)

    @commands.command(ignore_extra=True, description="bans specified member from server", help="ban <member> [reason]")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.cooldown(1, 5, type=BucketType.member)
    async def ban(self, ctx, members: commands.Greedy[commands.MemberConverter], *, reason: str = None):
        try:
            for member in members:
                if not reason:
                    await member.ban(reason="Banned by {}".format(ctx.author))
                    embed = discord.Embed(title="You Were Banned",
                                          description="You were banned from {} by {} for an unspecified reason.".format(
                                              ctx.message.guild.name, ctx.author), color=discord.Color.green())
                    await ctx.reply(embed=discord.Embed(title="Member Banned",
                                                        description="**{}** was banned by **{}** for an unspecified reason.".format(
                                                            member, ctx.author), color=discord.Color.green()))
                    with contextlib.suppress(Exception):
                        await member.send(embed=embed)
                else:
                    await member.ban(reason="Banned by {} for \"{}\"".format(ctx.author, reason))
                    await ctx.reply(embed=discord.Embed(title="Member Banned",
                                                        description="{} was banned by {} for \"{}\".".format(member.name,
                                                                                                             ctx.author,
                                                                                                             reason),
                                                        color=discord.Color.green()))
                    with contextlib.suppress(Exception):
                        await member.send(embed=discord.Embed(title="You Were Banned",
                                                              description="You were banned from **{}** by **{}** for \"{}\".".format(
                                                                  ctx.guild.name, ctx.author, reason),
                                                              color=discord.Color.green()))
        except discord.Forbidden:
            embed = discord.Embed(title="Oops !",
                                  description="I am not high enough in the role heirachy to do that you silly goose.",
                                  color=discord.Color.red())
            await ctx.reply(embed=embed, mention_author=True)

    @commands.command(description="lock's specified channel from specified role/everyone", help="lock [channel] [role]")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def lock(self, ctx, channel: commands.TextChannelConverter = None, role: commands.RoleConverter = None):
        channel = channel or ctx.channel
        role = role or ctx.guild.default_role
        try:
            if ctx.guild.default_role not in channel.overwrites:
                overwrites = {
                    role: discord.PermissionOverwrite(send_messages=False)
                }
                await channel.edit(overwrites=overwrites)
                embed = discord.Embed(description='{} has been locked :lock:.'.format(
                    channel.mention), color=Color.green())
                await ctx.send(embed=embed)
            elif channel.overwrites[role].send_messages or channel.overwrites[role].send_messages is None:
                overwrites = channel.overwrites[role]
                overwrites.send_messages = False
                await channel.set_permissions(role, overwrite=overwrites)
                embed = discord.Embed(description='{} has been locked. :lock:'.format(
                    channel.mention), color=Color.green())
                await ctx.send(embed=embed)
            else:
                overwrites = channel.overwrites[role]
                overwrites.send_messages = True
                await channel.set_permissions(role, overwrite=overwrites)
                embed = discord.Embed(description='{} has been unlocked. :unlock:'.format(channel.mention),
                                      color=Color.green())
                await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(title="Oops !",
                                  description="I cannot do that that you silly goose.",
                                  color=discord.Color.red())
            await ctx.reply(embed=embed, mention_author=True)

    @commands.command(description="`warn` will warn specified user", help="warn <member> [reason]")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 15, BucketType.guild)
    async def warn(self, ctx: commands.Context, member: commands.MemberConverter, *, reason: str = None):
        reason = "None Specified." if reason is None else reason
        if member.bot is True or member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot do that.")
        try:
            with self.pool.cursor() as cursor:
                cursor.execute("INSERT INTO warns (id, guild, user, warner, reason) VALUES (%s, %s, %s, %s, %s)", (
                    nanoid.generate(size=10), ctx.guild.id, member.id, ctx.author.id, reason))
            await ctx.send("**{}** has been warned.".format(member.mention))
        except Exception as exc:
            tragedy.logError(exc)

    @commands.command(name='warns', description="Views specified user's warnings in this server", help="warns <member>")
    @commands.guild_only()
    @commands.cooldown(1, 15, BucketType.guild)
    async def _warns(self, ctx, *, member: commands.MemberConverter):
        def check(response):
            return ctx.author == response.user and response.channel == ctx.channel
        try:
            embed = discord.Embed(color=Color.green()).set_author(
                icon_url=member.avatar_url, name=member)
            warns = list()
            ids = list()
            with self.pool.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM warns WHERE guild=%s AND user=%s", (ctx.guild.id, member.id))
                rows = cursor.fetchall()
            if not rows:
                embed.description = "No warnings."
                return await ctx.reply(embed=embed, mention_author=True)
            else:
                for _row in rows:
                    tragedy_warning_id = _row.get("id")
                    warner = _row.get("warner")
                    reason = _row.get("reason")
                    time = humanize.naturaldate(_row.get("time"))
                    ids.append(tragedy_warning_id)
                    warns.append(str("**ID** - `{}` | **Admin** - <@{}> | **Date** - `{}` | **Reason** - `{}`".format(
                        tragedy_warning_id, warner, time, reason)))
                index = 1
                for _warning in warns:
                    embed.add_field(name="Warning {}.".format(
                        index), value=_warning, inline=False)
                    index += 1

                Confirm = await ctx.reply(embed=embed, mention_author=True, components=[
                    [
                        Button(style=ButtonStyle.green,
                               label="Clear warnings"),
                        Button(style=ButtonStyle.green,
                               label="Remove a warning"),
                        Button(style=ButtonStyle.red, label="X")
                    ]
                ])

                try:
                    try:
                        interaction = await self.bot.wait_for("button_click", check=check, timeout=15)
                    except asyncio.exceptions.TimeoutError:
                        await Confirm.edit(embed=embed, components=[])
                    if interaction.component.label == "X":
                        await Confirm.edit(embed=embed, components=[])
                        await ctx.message.delete()
                        await Confirm.delete()
                    elif interaction.component.label == "Clear warnings" and Permissions.manage_guild in ctx.author.guild_permissions:
                        await Confirm.edit(embed=embed, components=[])
                        await ctx.message.delete()
                        await Confirm.delete()
                        with self.pool.cursor() as cursor:
                            cursor.execute(
                                "DELETE FROM warns WHERE guild=%s AND user=%s", (ctx.guild.id, member.id))
                        await ctx.send("Cleared all of {}'s warnings.".format(member.mention), delete_after=5)
                    elif interaction.component.label == "Remove a warning" and Permissions.manage_guild in ctx.author.guild_permissions:
                        await Confirm.edit(embed=embed, components=[])
                        SelectOptions = []
                        for _id in ids:
                            SelectOptions.append(
                                SelectOption(label=_id, value=_id))
                        SelectWarn = await ctx.send(components=[
                            [
                                Select(
                                    placeholder="Select the ID you wish to delete.",
                                    max_values=1,
                                    options=SelectOptions
                                )
                            ]
                        ])
                        try:
                            selectInteraction = await self.bot.wait_for("select_option", check=check, timeout=45)
                        except asyncio.exceptions.TimeoutError:
                            return await SelectWarn.edit(content="Took too long !", embed=None, components=[])
                        await ctx.message.delete()
                        await SelectWarn.delete()
                        with self.pool.cursor() as cursor:
                            cursor.execute("DELETE FROM warns WHERE guild=%s AND user=%s AND id=%s", (
                                ctx.guild.id, member.id, selectInteraction.component[0].label))
                        await ctx.send("Removed warning from {}\nID - **{}**".format(member.mention, selectInteraction.component[0].label), delete_after=5)
                except Exception as exc:
                    tragedy.logError(exc)
        except Exception as exc:
            tragedy.logError(exc)

    @commands.group(ignore_extra=True, invoke_without_command=True, description="`prefix` will show this server's prefix(es)", help="prefix")
    @commands.guild_only()
    @commands.cooldown(1, 15, BucketType.guild)
    async def prefix(self, ctx: commands.Context):
        try:
            prefixes = tragedy.getServerPrefixes(ctx.guild.id)
            numberedList = list()
            for index, value in enumerate(prefixes, 1):
                if value == "xv ":
                    numberedList.append(
                        "{}. `{}` (Default Prefix)".format(index, value))
                else:
                    numberedList.append("{}. `{}`".format(index, value))
            embed = discord.Embed(title="Prefixes", description='\n'.join(numberedList),
                                  color=Color.green())
            embed.set_footer(
                text="{}/5 Custom Prefixes".format(len(prefixes) - 1))
            await ctx.reply(embed=embed)
        except Exception as exc:
            tragedy.logError(exc)

    @prefix.command(name='add', description="Adds new prefix to tragedy's prefix(es) for this server", help="prefix add <prefix>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 60, BucketType.guild)
    async def _add(self, ctx, *, prefix: str):
        try:
            prefixes = tragedy.getServerPrefixes(ctx.guild.id)
            if prefix in prefixes:
                return await ctx.send("That's already one of my prefixes !", delete_after=5)
            if (len(prefixes) - 1) > 4:
                return await ctx.send("You have set too many prefixes (maximum of 5). Remove one to continue adding more !", delete_after=5)
            if len(prefix) > 10:
                return await ctx.send("That's too long for our database ! Try to keep it below 10 characters.", delete_after=5)
            with self.pool.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM prefix WHERE guild=%s", (str(ctx.guild.id)))
                response = cursor.fetchone()
                try:
                    column = list(response.keys())[
                        list(response.values()).index(None)]
                except AttributeError:
                    column = "prefix1"
            with self.pool.cursor() as cursor:
                cursor.execute(
                    "UPDATE prefix SET {0}=%s WHERE guild=%s".format(
                        column), (prefix, str(ctx.guild.id))
                )
            embed = discord.Embed(title="Prefix Added", description='Added `%s` to my prefixes for this server !' % (prefix),
                                  color=Color.green())
            await ctx.reply(embed=embed)
        except Exception as exc:
            tragedy.logError(exc)

    @prefix.command(name='remove', description="Removes prefix from tragedy's prefix(es) for this server", help="prefix remove <prefix>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 60, BucketType.guild)
    async def _remove(self, ctx, *, prefix: str):
        try:
            if prefix in list(["xv ", "xv"]):
                return await ctx.send("You cannot remove default prefix.", delete_after=5)
            prefixes = tragedy.getServerPrefixes(ctx.guild.id)
            if prefix not in prefixes:
                return await ctx.send("That is not currently a prefix for this server.", delete_after=5)
            if (len(prefixes) - 1) < 1:
                return await ctx.send("You have to keep at least 1 prefix.", delete_after=5)
            with self.pool.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM prefix WHERE guild=%s", (str(ctx.guild.id)))
                response = dict(cursor.fetchone())
                column = list(response.keys())[
                    list(response.values()).index(prefix)]
                cursor.execute("UPDATE prefix SET {0}=NULL WHERE guild=%s".format(
                    column), (str(ctx.guild.id)))
            embed = discord.Embed(title="Prefix Removed", description='Removed `%s` from my prefixes for this server !' % (prefix),
                                  color=Color.green())
            await ctx.reply(embed=embed)
        except Exception as exc:
            tragedy.logError(exc)

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.group(ignore_extra=True, invoke_without_command=True, description="Auto-welcome commands", help="welcome")
    async def welcome(self, ctx):
        with self.pool.cursor() as cursor:
            cursor.execute(
                "SELECT channel, message FROM `welcome` WHERE guild=%s", (ctx.guild.id))
            row: dict = cursor.fetchone()
            try:
                channel = row.get("channel")
                message = row.get("message")
            except AttributeError:
                raise WelcomeNotConfigured("Welcome has not been configured")
            channel = await self.bot.fetch_channel(channel)
            embed = discord.Embed(title="Auto-welcome", description="Your auto-welcome is configured to use %s with the message\n```%s```" %
                                  (channel.mention, message), color=Color.green())
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @welcome.group(ignore_extra=True, invoke_without_command=True, description="Set Auto-welcome variables", help="welcome set <variable>")
    @commands.cooldown(1, 45, BucketType.guild)
    async def set(self, ctx):
        embed = discord.Embed(
            title="Auto-welcome Configuration",
            description="Use the following commands to configure auto-welcome for this server",
            color=Color.green()
        )
        embed.add_field(name="welcome set channel",
                        value="Sets the channel to send the welcome messages in", inline=False)
        embed.add_field(name="welcome set message",
                        value="Sets the welcome message", inline=False)
        await ctx.send(embed=embed)

    @set.command()
    @commands.cooldown(1, 35, BucketType.guild)
    async def channel(self, ctx, channel: TextChannelConverter):
        with self.pool.cursor() as cursor:
            cursor.execute("UPDATE `welcome` SET channel=%s WHERE guild=%s", (str(
                channel.id), str(ctx.guild.id)))
        await ctx.send(embed=discord.Embed(
            title="Auto-welcome Configuration",
            description="Welcome channel set to `#%s`" % (channel.name),
            color=Color.green()
        ))

    @set.command()
    @commands.cooldown(1, 35, BucketType.guild)
    async def message(self, ctx, *, message: typing.Optional[str]):
        if not message:
            embed = discord.Embed(
                title="Auto-welcome Configuration",
                description="You can use the following variables in your welcome message",
                color=Color.green()
            )
            embed.add_field(name="user", value="Member's username#descriminator\nExample: Welcome user ! (Welcome %s !)" % (
                ctx.author), inline=False)
            embed.add_field(name="user_ping", value="Ping member\nExample: Welcome user_ping ! (Welcome %s !)" % (
                ctx.author.mention), inline=False)
            embed.add_field(name="user_name", value="Member's username\nExample: Welcome user_name ! (Welcome %s !)" % (
                ctx.author.name), inline=False)
            embed.add_field(name="server_name", value="Server's name\nExample: Welcome to server_name ! (Welcome to %s !)" % (
                ctx.guild.name), inline=False)
            return await ctx.send(embed=embed)
        if len(message) > 1849:
            raise BadArgument("Message cannot be over 1850 characters.")
        else:
            with self.pool.cursor() as cursor:
                cursor.execute("UPDATE `welcome` SET message=%s WHERE guild=%s", (str(
                    message), str(ctx.guild.id)))
            await ctx.send(embed=discord.Embed(
                title="Auto-welcome Configuration",
                description="Welcome message set.",
                color=Color.green()
            ))

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.cooldown(1, 15, type=BucketType.member)
    @commands.group(invoke_without_command=True)
    async def purge(self, ctx, amount: typing.Optional[int] = 5):
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        temp = await ctx.send(">>> Purged `{}` Messages".format(amount))
        await asyncio.sleep(5)
        await temp.delete()

    @purge.command(name='until')
    async def _until(self, ctx, message: commands.MessageConverter):
        await ctx.message.delete()
        await ctx.channel.purge(after=message)

    @purge.command(name='user')
    async def _user(self, ctx, user: commands.MemberConverter, amount: typing.Optional[int] = 100):
        def check(msg):
            return msg.author.id == user.id

        await ctx.channel.purge(limit=amount, check=check, before=None, bulk=True)

    @purge.command(name="all")
    async def _all(self, ctx):
        def check(response):
            return ctx.author == response.user and response.channel == ctx.channel

        Confirm = await ctx.reply(embed=discord.Embed(title="Are you sure?", description="This will delete **every message** in this channel.", color=Color.red()), mention_author=True, components=[
            [
                Button(style=ButtonStyle.green, label="Yes"),
                Button(style=ButtonStyle.red, label="No")
            ]
        ])

        try:
            interaction = await self.bot.wait_for("button_click", check=check, timeout=15)
            if interaction.component.label == "Yes":
                await ctx.message.delete()
                await Confirm.delete()
                await ctx.channel.purge(bulk=True, limit=9999999999999999999999)
                try:
                    await ctx.send(embed=discord.Embed(title="Channel Nuked!",
                                                       description="Type \"{}help\" for commands.".format(
                                                           random.choice(tragedy.getServerPrefixes(ctx.guild.id))),
                                                       color=discord.Color.green()).set_image(
                        url='https://media.giphy.com/media/HhTXt43pk1I1W/source.gif'), delete_after=5)
                except Exception as exc:
                    tragedy.logError(exc)
            else:
                await Confirm.delete()
                await ctx.message.delete()
                return
        except asyncio.exceptions.TimeoutError:
            await Confirm.edit(content="Took too long !", embed=None, components=[])

def setup(bot):
    bot.add_cog(Mod(bot))
