# noinspection PyUnresolvedReferences
import discord
from discord.ext import commands
from cogs.utils import checks
from random import randint
from random import choice
from cogs.utils.dataIO import dataIO
import asyncio

__author__ = "Cronan"


class Fun:
    """fun random commands"""

    def __init__(self, bot):
        self.bot = bot
        self.points = dataIO.load_json("data/fun/points.json")


    @commands.command(pass_context=True)
    async def rocketship(self, ctx):
        """Launch a Rocket Ship"""
        points = self.points
        user = ctx.message.author
        if ctx.message.channel.is_private:
            correctmsg = False
            await self.bot.say("How heavy will it be(in pounds)")
            while correctmsg is False:
                msg = await self.bot.wait_for_message(author=user, timeout=120, channel=ctx.message.channel)
                if msg is None:
                    correctmsg = True
                try:
                    msg5 = str(msg.content)
                    msg4 = int(msg5)
                    correctmsg = True
                except(IndexError, ValueError, AttributeError):
                    pass
                if correctmsg is True:
                    if msg is None:
                        await self.bot.say("Alright. Nevermind then.")
                        return
                    try:
                        msg7 = str(msg.content)
                        weight = int(msg7)
                    except(IndexError, ValueError, AttributeError):
                        pass
            correctmsg2 = False
            await self.bot.say("How much fuel will be in it(in pounds)")
            while correctmsg2 is False:
                msg2 = await self.bot.wait_for_message(author=user, timeout=120, channel=ctx.message.channel)
                if msg2 is None:
                    correctmsg2 = True
                try:
                    msg6 = str(msg2.content)
                    msg3 = int(msg6)
                    correctmsg2 = True
                except(IndexError, ValueError, AttributeError):
                    pass
                if correctmsg2 is True:
                    if msg2 is None:
                        await self.bot.say("Alright. Nevermind then.")
                        return
                    try:
                        msg8 = str(msg2.content)
                        fuel = int(msg8)
                    except(IndexError, ValueError, AttributeError):
                        pass
            fuelcost = fuel * .19
            weightcost = weight * 27000
            cost = fuelcost + weightcost
            await asyncio.sleep(2)
            await self.bot.say("The cost of your rocket(for the weight and fuel) is $" + str(cost))
            await asyncio.sleep(2)
            count = 10

            themsg = await self.bot.say(str(count))
            for i in range(count):
                await asyncio.sleep(1)
                await self.bot.edit_message(themsg, str(count))
                count = count - 1
                if count == 0:
                    await self.bot.edit_message(themsg, "BLAST OFF!!!")
                    await asyncio.sleep(2)
                    needed = weight * 9
                    if needed > fuel:
                        goodorno = "Failed"
                    elif needed < fuel:
                        goodorno = ["Failed", "Failed", "SUCCESS"]
                        goodorno = choice(goodorno)
                    elif needed == fuel:
                        goodorno = ["Failed", "SUCCESS", "SUCCESS"]
                        goodorno = choice(goodorno)
                    await self.bot.say(goodorno)
                    if goodorno == "Failed":
                        userexist = False
                        for i, s in enumerate(points):
                            if s["USER"] == points:
                                continue

                            if str(user.id) in s["USER"]:
                                ogfailpoints = int(points[i]["FAILS"])
                                ogwinpoints = str(points[i]["WINS"])
                                newfailpoints = ogfailpoints + 1
                                points.remove(s)
                                dataIO.save_json("data/fun/points.json", self.points)
                                data = {"USER": str(user.id),
                                        "FAILS": str(newfailpoints),
                                        "WINS": str(ogwinpoints)}
                                points.append(data)
                                dataIO.save_json("data/fun/points.json", self.points)
                                userexist = True
                                
                        if not userexist:
                            data = {"USER": str(user.id),
                                    "FAILS": str(1),
                                    "WINS": str(0)}
                            points.append(data)
                            dataIO.save_json("data/fun/points.json", self.points)
                    elif goodorno == "SUCCESS":
                        userexist = False
                        for i, s in enumerate(points):
                            if s["USER"] == points:
                                continue

                            if str(user.id) in s["USER"]:
                                ogfailpoints = str(points[i]["FAILS"])
                                ogwinpoints = int(points[i]["WINS"])
                                newwinpoints = ogwinpoints + 1
                                points.remove(s)
                                dataIO.save_json("data/fun/points.json", self.points)
                                data = {"USER": str(user.id),
                                        "FAILS": str(ogfailpoints),
                                        "WINS": str(newwinpoints)}
                                points.append(data)
                                dataIO.save_json("data/fun/points.json", self.points)
                                userexist = True
                        if not userexist:
                            data = {"USER": str(user.id),
                                    "FAILS": str(0),
                                    "WINS": str(1)}
                            points.append(data)
                            dataIO.save_json("data/fun/points.json", self.points)

            asyncio.sleep(2)
            for i, s in enumerate(points):

                if str(user.id) in s["USER"]:
                    failboard = str(points[i]["FAILS"])
                    winboard = str(points[i]["WINS"])


            embedship = discord.Embed(color=discord.Color.red())
            embedship.set_author(name="Scores:")
            embedship.add_field(name="Fails:", value=failboard)
            embedship.add_field(name="Successes:", value=winboard)

            await self.bot.say(embed=embedship)

        else:
            await self.bot.say("I can only do this in private messages")
            


    @commands.command(pass_context=True)
    async def sword(self, ctx, *, user: discord.Member):
        """Sword Duel!"""
        author = ctx.message.author
        if user.id == self.bot.user.id:
            await self.bot.say("I'm not the fighting kind")
        else:
            await self.bot.say(author.mention + " and " + user.mention + " dueled for " + str(randint(2, 120)) +
                               " gruesome hours! It was a long, heated battle, but " +
                               choice([author.mention, user.mention]) + " came out victorious!")

    @commands.command(pass_context=True)
    async def love(self, ctx, user: discord.Member):
        """Found your one true love?"""
        author = ctx.message.author
        if user.id == self.bot.user.id:
            await self.bot.say("I am not capable of loving like you can. I'm sorry." )
        else:
            await self.bot.say(author.mention + " is capable of loving " + user.mention + " a whopping " +
                               str(randint(0, 100)) + "%!")

    @commands.command(pass_context=True)
    async def squat(self, ctx):
        """How is your workout going?"""
        author = ctx.message.author
        await self.bot.say(author.mention + " puts on their game face and does " + str(randint(2, 1000)) +
                           " squats in " + str(randint(4, 90)) + " minutes. Wurk it!")

    @commands.command(pass_context=True)
    async def pizza(self, ctx):
        """How many slices of pizza have you eaten today?"""
        author = ctx.message.author
        await self.bot.say(author.mention + " has eaten " + str(randint(2, 120)) + " slices of pizza today.")

    @commands.command(pass_context=True)
    async def bribe(self, ctx, *, user : discord.Member=None):
        """Find out who is paying under the table"""
        author = ctx.message.author
        if user is None:
            await self.bot.say(author.mention + " has bribed " + self.bot.user.mention + " with " +
                               str(randint(10, 10000)) + " dollars!")
        else:
            await self.bot.say(author.mention + " has bribed " + user.mention + " with " +
                               str(randint(10, 10000)) + " dollars!")




    @commands.command(pass_context=True)
    async def daddy(self, ctx):
        """Pass the salt"""
        author = ctx.message.author
        await self.bot.say("I'm kink shaming you, " + author.mention)

    @commands.command()
    async def calculated(self):
        """That was 100% calculated!"""
        await self.bot.say("That was " + str(randint(0, 100)) + "% calculated!")

    @commands.command()
    async def butts(self):
        """butts"""
        await self.bot.say("ლ(́◉◞౪◟◉‵ლ)")

    @commands.command(name="commands")
    async def _commands(self):
        """Command the bot"""
        await self.bot.say("Don't tell me what to do.")

    @commands.command()
    async def flirt(self):
        """Slide into DMs"""
        await self.bot.say("xoxoxoxoxo ;)) ))) hey b a b e ; ; ;))) ) ;)")

    @commands.command()
    async def updog(self):
        """This is updog"""
        await self.bot.say("What's updog?")



def setup(bot):
    n = Fun(bot)
    bot.add_cog(n)
