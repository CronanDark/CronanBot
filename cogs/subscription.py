from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from .utils.chat_formatting import pagify, box
from collections import defaultdict
import os
import re
import discord
import importlib
import traceback
import logging
import asyncio
import threading
import datetime
import glob
import aiohttp
from discord.message import Message
from discord.user import User

class Msger:

    def __init__(self, msger):
        self.msgs = msger

class Subscription:
    """Subscription commands"""

    def __init__(self, bot):
        self.bot = bot
        self.subscribers = dataIO.load_json("data/subscription/subscribers.json")



    @commands.command(pass_context=True)
    async def subscribe(self, ctx):
        """subscribe to bot announcement PM's"""
        user = ctx.message.author
        user1 = str(user)
        person = self.subscribers
        for i, s in enumerate(person):
            if s["NAME"] == person:
                continue

            if user.id in s["ID"]:
                await self.bot.say("You are already subscribed")
                return
        
        data = {"ID": [user.id],
                "NAME": str(user)}
        person.append(data)
        dataIO.save_json("data/subscription/subscribers.json", self.subscribers)
        await self.bot.say("You are now subscribed.")


    @commands.command(pass_context=True)
    async def unsubscribe(self, ctx):
        """unsubscribe to bot announcement PM's"""
        user = ctx.message.author
        user1 = str(user)
        person = self.subscribers
        for i, s in enumerate(person):
            if s["NAME"] == person:
                continue

            
            if user.id in s["ID"]:
                person[i]["ID"].remove(user.id)
                if not s["ID"]:
                    person.remove(s)
                dataIO.save_json("data/subscription/subscribers.json", self.subscribers)
                await self.bot.say("You are now unsubscribed.")
                return

        await self.bot.say("You are already unsubscribed.")



    @commands.command(pass_context=True)
    @checks.is_owner()
    async def pmannounce(self, ctx, *, message : str):
        """PM everyone subscribed an announcement"""
        person = self.subscribers
        for i, s in enumerate(person):
            msger = s["ID"]
            msger = msger[i]
            await self.bot.send_message(discord.User(id=msger), message)



def setup(bot):
    n = Subscription(bot)
    bot.add_cog(n)

