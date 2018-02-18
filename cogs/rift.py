import discord
from discord.ext import commands
from collections import namedtuple, defaultdict
from cogs.utils.chat_formatting import escape, pagify, box
import os
from cogs.utils.dataIO import dataIO
from cogs.utils import checks
import re
import importlib
import traceback
import logging
import asyncio
import threading
import datetime
import glob
import aiohttp
from discord.channel import Channel
from discord.message import Message
import copy
from discord import utils
from discord.permissions import Permissions, PermissionOverwrite
from discord.enums import ChannelType
from discord.mixins import Hashable



OpenRift = namedtuple("Rift", ["source", "destination"])


class DaDudePlace:

    def __init__(self, where):
        self.daplacedude = where

    
class Rift:
    """Message across servers/channels"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json('data/rift/settings.json')


    def save_json(self):
        dataIO.save_json("data/rift/settings.json", self.settings)


    @commands.command(pass_context=True)
    async def channelid(self, ctx, channel):
        """Get the id of a channel"""
        person = ctx.message.author
        place = ctx.message.channel
        theid = await self.getid(person, place, channel)
        if theid is None:
            await self.bot.say("you didnt pick in time")
        else:
            await self.bot.say(theid)


    async def _confirm_rift(self, otherplace):
        answers = ("yes", "y")
        nope = ("no", "n")
        stuff = ("yes", "y", "no", "n")
        dadudeplace = self.bot.get_channel(otherplace)
        await self.bot.send_message(dadudeplace, "Someone wants to form a rift."
                                    "do you accept? (yes/no)")
        correctmsg = False
        while correctmsg is False:
            msg = await self.bot.wait_for_message(timeout=20, channel=dadudeplace)
            if msg is None:
                correctmsg = True
            elif msg.content.lower().strip() in stuff:
                correctmsg = True
            if correctmsg is True:
                if msg is None:
                    await self.bot.send_message(dadudeplace, "I guess not.")
                    return False
                elif msg.content.lower().strip() in answers:
                    return True
                elif msg.content.lower().strip() in nope:
                    await self.bot.send_message(dadudeplace, "Alright then.")
                    return False


    async def getid(self, dauser, daplace, channel):
        author = dauser
        author_channel = daplace

        def check(m):
            try:
                return channels[int(m.content)]
            except:
                return False

        channels = self.bot.get_all_channels()
        channels = [c for c in channels
                    if c.name.lower() == channel or c.id == channel]
        channels = [c for c in channels if c.type == discord.ChannelType.text]


        if not channels:
            await self.bot.say("No channels found. Remember to type just "
                               "the channel name, no `#`.")
            return

        if len(channels) > 1:
            msg = "Multiple results found.\nChoose a server:\n"
            for i, channel in enumerate(channels):
                msg += "{} - {}\n".format(i, channel.server)
            for page in pagify(msg):
                await self.bot.say(page)
            choice = await self.bot.wait_for_message(author=author,
                                                     timeout=30,
                                                     check=check,
                                                     channel=author_channel)
            if choice is None:
                return None
            channel = channels[int(choice.content)]
        else:
            channel = channels[0]

        return channel.id


    @commands.command(pass_context=True)
    async def riftopen(self, ctx, channel):
        """Makes you able to communicate with other channels through Cronan

        This is cross-server. Type only the channel name or the ID."""
        author = ctx.message.author
        author_channel = ctx.message.channel
        rafts = self.settings

        channels = self.bot.get_all_channels()
        channels = [c for c in channels if c.type == discord.ChannelType.text]
        channels = [c.id for c in channels if c.id == channel or c.id == author_channel.id]

        if len(channels) == 2:
            for i, s in enumerate(rafts):
                if s["chan1"] == rafts:
                    continue

                if s["chan2"] == rafts:
                    continue

                if author_channel in s["chan2"]:
                    await self.bot.say("There is already a rift in this channel.")
                    return

                if channel in s["chan1"]:
                    await self.bot.say("There is already a rift in that channel.")
                    return


            confirmation = await self._confirm_rift(channel)
            if confirmation is True:
                data = {"chan1":[channel],
                        "chan2": [author_channel.id]}
                rafts.append(data)
                dataIO.save_json("data/rift/settings.json", self.settings)
                await self.bot.say("Rift opened")
                aceptchan = self.bot.get_channel(channel)
                await self.bot.send_message(aceptchan, "Rift opened")
            else:
                await self.bot.say("Rift has been denied")
        else:
            await self.bot.say("I did not get two unique channel IDs")


    @commands.command(pass_context=True)
    async def exitrift(self, ctx):
        """close a rift"""
        author = ctx.message.author
        author_channel = ctx.message.channel
        rafts = self.settings
        for i, s in enumerate(rafts):
            if s["chan2"] == rafts:
                continue

            
            if author_channel.id in s["chan2"]:
                otherplace = rafts[i]
                otherplace = otherplace["chan1"]
                otherplace = otherplace[i]
                otherplace = str(otherplace)
                otherplace = self.bot.get_channel(otherplace)
                rafts[i]["chan2"].remove(author_channel.id)
                if not s["chan2"]:
                    rafts.remove(s)
                dataIO.save_json("data/rift/settings.json", self.settings)
                await self.bot.send_message(otherplace, "Rift has been closed")
                await self.bot.say("Rift closed")
                return

            if author_channel.id in s["chan1"]:
                otherplace = rafts[i]
                otherplace = otherplace["chan2"]
                otherplace = otherplace[i]
                otherplace = str(otherplace)
                otherplace = self.bot.get_channel(otherplace)
                rafts[i]["chan1"].remove(author_channel.id)
                if not s["chan1"]:
                    rafts.remove(s)
                dataIO.save_json("data/rift/settings.json", self.settings)
                await self.bot.send_message(otherplace, "Rift has been closed")
                await self.bot.say("Rift closed")
                return

        await self.bot.say("There is no rift here.")


    async def on_message(self, message):
        """Do stuff based on settings"""
        valid = message.channel
        raftsvalid = self.settings
        dauser = message.author

        for i, s in enumerate(raftsvalid):
            if s["chan2"] == raftsvalid:
                continue

            if valid.id not in s["chan2"]:
                if valid.id not in s["chan1"]:
                    return
                else:
                    continue


        rafts = self.settings
        for i, s in enumerate(rafts):
            if message.author == self.bot.user:
                return

            channel = message.channel
            rft = rafts[i]
            c1 = rft["chan1"]
            c1 = c1[i]
            c2 = rft["chan2"]
            c2 = c2[i]
            if channel.id == c2:
                destination = c1
            elif channel.id == c1:
                destination = c2

            if destination is not None:
                destination = await self.getid(dauser, valid, destination)
                await self.senderdude(destination, message)



    async def senderdude(self, where, message=None):
        """sends the thing"""

        if message:
            em = self.qform(message)
            where = self.bot.get_channel(where)
            await self.bot.send_message(where, embed=em)



    def qform(self, message):
        channel = message.channel
        server = channel.server
        content = message.clean_content
        author = message.author
        sname = server.name
        cname = channel.name
        timestamp = message.timestamp.strftime('%Y-%m-%d %H:%M')
        avatar = author.avatar_url if author.avatar \
            else author.default_avatar_url
        if message.attachments:
            a = message.attachments[0]
            fname = a['filename']
            url = a['url']
            content += "\nUploaded: [{}]({})".format(fname, url)
        footer = 'Said in {} #{} at {} UTC'.format(sname, cname, timestamp)
        botowner = "Cronan The Dark Gamer"
        if message.author.name == botowner:
            msgcolor = discord.Color.red()
        else:
            msgcolor = discord.Color.gold()
        em = discord.Embed(description=content, color=msgcolor)
        em.set_author(name='{}'.format(author.name), icon_url=avatar)
        em.set_footer(text=footer)
        return em


def check_folder():
    f = 'data/rift'
    if not os.path.exists(f):
        os.makedirs(f)


def check_file():
    f = 'data/rift/settings.json'
    if dataIO.is_valid_json(f) is False:
        dataIO.save_json(f, [])

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Rift(bot))
