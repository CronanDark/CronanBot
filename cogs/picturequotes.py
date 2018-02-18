import discord
from discord.ext import commands
from random import choice
import asyncio
from .utils.dataIO import dataIO
import os
from numpy import random
from __main__ import user_allowed, send_cmd_help



class PictureQuotes:
    def __init__(self, bot):
        self.bot = bot
        self.quotes = dataIO.load_json("data/quotes/quotes.json")



    @commands.group(name="quotes", pass_context=True, no_pm=True)
    async def _quotes(self, ctx):
        """Save retrieve or delete screenshots of chat"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @_quotes.command(pass_context=True, no_pm=True)
    async def save(self, ctx, url):
        """saves a quote"""
        thequotes = self.quotes
        quoteowner = ctx.message.author
        if "http" not in url:
            await self.bot.say("I need an image link")
            return
        else:
            for i, s in enumerate(thequotes):
                if s["OWNER"] == thequotes:
                    continue

                if url in s["URL"]:
                    await self.bot.say("There is already a quote with that image")
                    return
            
            data = {"OWNER": [quoteowner.id],
                    "URL": url}
            thequotes.append(data)
            dataIO.save_json("data/quotes/quotes.json", self.quotes)
            await self.bot.say("Quote saved")


    @_quotes.command(pass_context=True, no_pm=True)
    async def delete(self, ctx, url):
        """deletes a quote"""
        thequotes = self.quotes
        quoteowner = ctx.message.author
        if "http" not in url:
            await self.bot.say("I need an image link")
            return
        else:
            for i, s in enumerate(thequotes):
                if s["OWNER"] == thequotes:
                    continue


                if quoteowner.id in s["OWNER"]:
                    if url in s["URL"]:
                        thequotes[i]["OWNER"].remove(quoteowner.id)
                        if not s["OWNER"]:
                            thequotes.remove(s)
                        dataIO.save_json("data/quotes/quotes.json", self.quotes)
                        await self.bot.say("Quote Deleted")
                        return
                if url in s["URL"]:
                    if quoteowner.id in s["OWNER"]:
                        thequotes[i]["OWNER"].remove(quoteowner.id)
                        if not s["OWNER"]:
                            thequotes.remove(s)
                        dataIO.save_json("data/quotes/quotes.json", self.quotes)
                        await self.bot.say("Quote Deleted")
                        return
                    else:
                        await self.bot.say("You don't own this quote")
                        return

            await self.bot.say("That quote doesnt exist")


    @_quotes.command(pass_context=True, no_pm=True)
    async def show(self, ctx):
        """Shows a quote"""
        thequotes = self.quotes
        addhere = []
        for i, s in enumerate(thequotes):
            quoteadd = s["URL"]
            addhere.append(str(quoteadd))

        quoteyes = random.choice(addhere)
        quoteyes = ''.join(quoteyes)
        await self.bot.say(str(quoteyes))



def setup(bot):
    bot.add_cog(PictureQuotes(bot))
