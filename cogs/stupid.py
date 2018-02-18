import discord
from discord.ext import commands
import asyncio
from discord.user import User
from cogs.utils import checks
from cogs.utils.dataIO import dataIO

class Stupid():
	"""Stupid commands Cronan builds in for no reason what so ever"""

	def __init__(self, bot):
		self.bot = bot
		self.confession = dataIO.load_json("data/stupid/settings.json")


	@commands.command()
	async def cronan(self):
		"""why? just why?"""
		await self.bot.say("ew... y do u like that cringy yter who cant even code me right or have me alive 24/7")

	@commands.command(pass_context=True)
	async def annoyme(self, ctx, times : int, minutes : int):
		"""The bot will annoy you
		
		To stop him just say "CronanBot stop"
		trust me... it works... it just wont say anything till the next time it was supposed to mention you"""
		seconds = minutes * 60
		user = ctx.message.author.id
		usermention = "<@" + user + ">"
		for i in range(times):
			await self.bot.say(usermention)
			stop = await self.stop_annoy(seconds)
			if stop:
				await self.bot.say("Ok i'll stop")
				break
	
	async def stop_annoy(self, time):
		answers = ("CronanBot stop")
		correctmsg = False
		while correctmsg is False:
			msg = await self.bot.wait_for_message(timeout=time)
			if msg is None:
				correctmsg = True
			elif msg.content.lower().strip() in answers:
				correctmsg = True
			if correctmsg is True:
				if msg is None:
					return False
				elif msg.content.lower().strip() in answers:
					return True

	@commands.command(pass_context=True)
	@checks.serverowner()
	async def pmconfession(self, ctx, enable : bool):
		"""Set whether or not the spam confession is dmed to you or not"""
		theconfesset = self.confession
		server = ctx.message.server.id
		if enable is True:
			thechoice = "True"
			changefrom = "False"
			for i,s in enumerate(theconfesset):
				if s["SERVER"] == theconfesset:
					continue

				if str(server) in s["SERVER"]:
					if thechoice not in s["CHOICE"]:
						datadel = {"SERVER": [server],
								   "CHOICE": changefrom}
						theconfesset.remove(datadel)
						data = {"SERVER": [server],
								"CHOICE": thechoice}
						theconfesset.append(data)
						dataIO.save_json("data/stupid/settings.json", self.confession)
						await self.bot.say("Confession DMs enabled")
						return
					elif thechoice in s["CHOICE"]:
						await self.bot.say("You already have this set to True")
						return

			
			data = {"SERVER": [server],
					"CHOICE": thechoice}
			theconfesset.append(data)
			dataIO.save_json("data/stupid/settings.json", self.confession)
			await self.bot.say("Confession DMs enabled")


		elif enable is False:
			thechoice = "False"
			changefrom = "True"
			for i,s in enumerate(theconfesset):
				if s["SERVER"] == theconfesset:
					continue

				if str(server) in s["SERVER"]:
					if thechoice not in s["CHOICE"]:
						datadel = {"SERVER": [server],
								   "CHOICE": changefrom}
						theconfesset.remove(datadel)
						data = {"SERVER": [server],
								"CHOICE": thechoice}
						theconfesset.append(data)
						dataIO.save_json("data/stupid/settings.json", self.confession)
						await self.bot.say("Confession DMs disabled")
						return
					elif thechoice in s["CHOICE"]:
						await self.bot.say("You already have this set to False")
						return

			
			data = {"SERVER": [server],
					"CHOICE": thechoice}
			theconfesset.append(data)
			dataIO.save_json("data/stupid/settings.json", self.confession)
			await self.bot.say("Confession DMs disabled")
	  

	@commands.command(pass_context=True)
	async def spam(self, ctx, message, times : int):
		"""spams chat with what u make it say.

		If your message has spaces but them in double quotes
		Note: You will be responsible for any trouble you get into"""
		server = ctx.message.server
		serverid = server.id
		theconfesset = self.confession
		truestr = "True"
		falsestr = "False"
		owner = server.owner.id
		msgdude = str(message)
		user = str(ctx.message.author.name)
		msgdel = ctx.message
		await self.bot.delete_message(msgdel)
		for i in range(times):
			await self.bot.say(msgdude)
			await asyncio.sleep(1)
		await asyncio.sleep(5)
		confess = user + " made me spam ```" + msgdude + "```"
		nosetconfess = user + " made me spam ```" + msgdude + "``` To disable confession DMs do ```->pmconfession False```"
		for i,s in enumerate(theconfesset):
			if s["SERVER"] == theconfesset:
				continue

			if serverid in s["SERVER"]:
				if truestr in s["CHOICE"]:
					await self.bot.send_message(discord.User(id=owner), confess)
					return
				elif falsestr in s["CHOICE"]:
					await self.bot.say(confess)
					return

		await self.bot.send_message(discord.User(id=owner), nosetconfess)


def setup(bot):
	n = Stupid(bot)
	bot.add_cog(n)
