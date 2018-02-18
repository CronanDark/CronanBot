import discord
from discord.ext import commands
from .utils.chat_formatting import escape_mass_mentions, italics, pagify
from random import randint
from random import sample
from random import choice
from PIL import Image
from enum import Enum
from urllib.parse import quote_plus
import datetime
import io
import string
from discord.permissions import PermissionOverwrite
import re
import time
import aiohttp
import asyncio
from numpy import random
from .utils.dataIO import dataIO
from discord.message import Message
from cogs.utils import checks
import os
import urllib

settings = {"POLL_DURATION" : 60}


class RPS(Enum):
	rock     = "\N{MOYAI}"
	paper    = "\N{PAGE FACING UP}"
	scissors = "\N{BLACK SCISSORS}"


class RPSParser:
	def __init__(self, argument):
		argument = argument.lower()
		if argument == "rock":
			self.choice = RPS.rock
		elif argument == "paper":
			self.choice = RPS.paper
		elif argument == "scissors":
			self.choice = RPS.scissors
		else:
			raise





class General:
	"""General commands."""
	
	def __init__(self, bot):
		self.bot = bot
		self.stopwatches = {}
		self.points = dataIO.load_json("data/general/rpspoints.json")
		self.regional_map = {"z": "🇿", "y": "🇾", "x": "🇽", "w": "🇼", "v": "🇻", "u": "🇺", "t": "🇹", "s": "🇸", "r": "🇷", "q": "🇶", "p": "🇵", "o": "🇴", "n": "🇳", "m": "🇲", "l": "🇱", "k": "🇰", "j": "🇯", "i": "🇮", "h": "🇭", "g": "🇬", "f": "🇫", "e": "🇪", "d": "🇩", "c": "🇨", "b": "🇧", "a": "🇦"}
		self.emote_regex = re.compile(r'<:.*:(?P<id>\d*)>')
		self.retro_regex = re.compile(r"((https)(\:\/\/|)?u3\.photofunia\.com\/.\/results\/.\/.\/.*(\.jpg\?download))")
		self.scrap_regex = re.compile(",\"ou\":\"([^`]*?)\"")
		self.ball = ["As I see it, yes", "It is certain", "It is decidedly so", "Most likely", "Outlook good",
					 "Signs point to yes", "Without a doubt", "Yes", "Yes – definitely", "You may rely on it", "Reply hazy, try again",
					 "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
					 "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
		self.aussiepics = ["https://cdn.discordapp.com/attachments/321169190650118154/353771228059795457/images_61.jpg", "https://cdn.discordapp.com/attachments/321169190650118154/353771228730753024/images_59.jpg", "https://cdn.discordapp.com/attachments/321169190650118154/353771228730753026/images_53.jpg", "https://cdn.discordapp.com/attachments/321169190650118154/353771229347577856/images_60.jpg", "https://cdn.discordapp.com/attachments/321169190650118154/353771229783654401/images_54.jpg", "https://cdn.discordapp.com/attachments/321169190650118154/353771287379836929/JPEG_20170827_220619.jpg", "https://cdn.discordapp.com/attachments/321169190650118154/353771370909401092/4NKa80UXY3ar6.gif", "https://cdn.discordapp.com/attachments/321169190650118154/353771475729252353/images_47.jpg", "https://cdn.discordapp.com/attachments/321169190650118154/353771677064232960/rSiurIy9lLi24.gif", "https://cdn.discordapp.com/attachments/321169190650118154/353771677730996229/images_38.jpg", "https://cdn.discordapp.com/attachments/321169190650118154/353780398440054794/images_63.jpg"]

	@commands.command(hidden=True)
	async def ping(self):
		"""Pong."""

		await self.bot.say("Pong.")

	@commands.command()
	async def choose(self, *choices):
		"""Chooses between multiple choices.
		
		To denote multiple choices, you should use double quotes.
		"""
		choices = [escape_mass_mentions(c) for c in choices]
		if len(choices) < 2:
			await self.bot.say('Not enough choices to pick from.')
		else:
			await self.bot.say(choice(choices))

	@commands.command(pass_context=True)
	async def roll(self, ctx, number : int = 100):
		"""Rolls random number (between 1 and user choice)
		
		Defaults to 100.
		"""
		author = ctx.message.author
		if number > 1:
			n = randint(1, number)
			await self.bot.say("{} :game_die: {} :game_die:".format(author.mention, n))
		else:
			await self.bot.say("{} Maybe higher than 1? ;P".format(author.mention))
			
	@commands.command(pass_context=True)
	async def flip(self, ctx, user : discord.Member=None):
		"""Flips a coin... or a user.
		
		Defaults to coin.
		"""
		if user != None:
			msg = ""
			if user.id == self.bot.user.id:
				user = ctx.message.author
				msg = "Nice try. You think this is funny? How about *this* instead:\n\n"
			char = "abcdefghijklmnopqrstuvwxyz"
			tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
			table = str.maketrans(char, tran)
			name = user.display_name.translate(table)
			char = char.upper()
			tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
			table = str.maketrans(char, tran)
			name = name.translate(table)
			await self.bot.say(msg + "(╯°□°）╯︵ " + name[::-1])
		else:
			await self.bot.say("*flips a coin and... " + choice(["HEADS!*", "TAILS!*"]))
	
	@commands.command(pass_context=True, aliases=['getcolour'])
	async def getcolor(self, ctx, *, color_codes):
		"""Posts color of given hex"""
		color_codes = color_codes.split()
		channel = ctx.message.channel
		size = (60, 80) if len(color_codes) > 1 else (200, 200)
		if len(color_codes) > 5:
			await self.bot.say(self.bot.bot_prefix + "Sorry, 5 color codes maximum")
		for color_code in color_codes:
			try:
				if not color_code.startswith("#"):
					color_code = "#" + color_code
				image = Image.new("RGB", size, color_code)
				image.save("data/color/color_file.png", 'PNG', quality=100)
				await self.bot.say("Color with hex code {}:".format(color_code))
				await self.bot.send_file(channel, "data/color/color_file.png")
				await asyncio.sleep(1)
			except ValueError:
				await self.bot.say("The color code {} doesnt exist".format(color_code))
			
	@commands.command(pass_context=True)
	async def rps(self, ctx, your_choice : RPSParser):
		"""Play rock paper scissors"""
		user = ctx.message.author
		points = self.points
		author = ctx.message.author
		player_choice = your_choice.choice
		cronan_choice = choice((RPS.rock, RPS.paper, RPS.scissors))
		cond = {
				(RPS.rock,     RPS.paper)    : False,
				(RPS.rock,     RPS.scissors) : True,
				(RPS.paper,    RPS.rock)     : True,
				(RPS.paper,    RPS.scissors) : False,
				(RPS.scissors, RPS.rock)     : False,
				(RPS.scissors, RPS.paper)    : True
				}

		if cronan_choice == player_choice:
			outcome = None # Tie
		else:
			outcome = cond[(player_choice, cronan_choice)]

		if outcome is True:
			await self.bot.say("{} You win {}!"
								"".format(cronan_choice.value, author.mention))
			userexist = False
			for i, s in enumerate(points):
				if s["USER"] == points:
					continue

				if str(user.id) in s["USER"]:
					oglosepoints = str(points[i]["LOSES"])
					ogtiepoints = str(points[i]["TIES"])
					ogwinpoints = int(points[i]["WINS"])
					newwinpoints = ogwinpoints + 1
					points.remove(s)
					dataIO.save_json("data/general/rpspoints.json", self.points)
					data = {"USER": str(user.id),
							"LOSES": str(oglosepoints),
							"TIES": str(ogtiepoints),
							"WINS": str(newwinpoints)}
					points.append(data)
					dataIO.save_json("data/general/rpspoints.json", self.points)
					userexist = True
			
			if not userexist:
				data = {"USER": str(user.id),
						"LOSES": str(0),
						"TIES": str(0),
						"WINS": str(1)}
				points.append(data)
				dataIO.save_json("data/general/rpspoints.json", self.points)
		elif outcome is False:
			await self.bot.say("{} You lose {}!"
								"".format(cronan_choice.value, author.mention))
			userexist = False
			for i, s in enumerate(points):
				if s["USER"] == points:
					continue

				if str(user.id) in s["USER"]:
					oglosepoints = int(points[i]["LOSES"])
					ogtiepoints = str(points[i]["TIES"])
					ogwinpoints = str(points[i]["WINS"])
					newlosepoints = oglosepoints + 1
					points.remove(s)
					dataIO.save_json("data/general/rpspoints.json", self.points)
					data = {"USER": str(user.id),
							"LOSES": str(newlosepoints),
							"TIES": str(ogtiepoints),
							"WINS": str(ogwinpoints)}
					points.append(data)
					dataIO.save_json("data/general/rpspoints.json", self.points)
					userexist = True
					
			if not userexist:
				data = {"USER": str(user.id),
						"LOSES": str(1),
						"TIES": str(0),
						"WINS": str(0)}
				points.append(data)
				dataIO.save_json("data/general/rpspoints.json", self.points)
		else:
			await self.bot.say("{} We're square {}!"
								"".format(cronan_choice.value, author.mention))
			userexist = False
			for i, s in enumerate(points):
				if s["USER"] == points:
					continue

				if str(user.id) in s["USER"]:
					oglosepoints = str(points[i]["LOSES"])
					ogtiepoints = int(points[i]["TIES"])
					ogwinpoints = str(points[i]["WINS"])
					newtiepoints = ogtiepoints + 1
					points.remove(s)
					dataIO.save_json("data/general/rpspoints.json", self.points)
					data = {"USER": str(user.id),
							"LOSES": str(oglosepoints),
							"TIES": str(newtiepoints),
							"WINS": str(ogwinpoints)}
					points.append(data)
					dataIO.save_json("data/general/rpspoints.json", self.points)
					userexist = True
					
			if not userexist:
				data = {"USER": str(user.id),
						"LOSES": str(0),
						"TIES": str(1),
						"WINS": str(0)}
				points.append(data)
				dataIO.save_json("data/general/rpspoints.json", self.points)
		for i, s in enumerate(points):

			if str(user.id) in s["USER"]:
				loseboard = str(points[i]["LOSES"])
				tieboard = str(points[i]["TIES"])
				winboard = str(points[i]["WINS"])


		embedship = discord.Embed(color=discord.Color.red())
		embedship.set_author(name="Scores:")
		embedship.add_field(name="Loses:", value=loseboard)
		embedship.add_field(name="Ties:", value=tieboard)
		embedship.add_field(name="Wins:", value=winboard)

		await self.bot.say(embed=embedship)

	@commands.command(name="8", aliases=["8ball"])
	async def _8ball(self, *, question : str):
		"""Ask 8 ball a question

		Question must end with a question mark.
		"""
		if question.endswith("?") and question != "?":
			await self.bot.say("`" + choice(self.ball) + "`")
		else:
			await self.bot.say("That doesn't look like a question.")

	@commands.command(aliases=["sw"], pass_context=True)
	async def stopwatch(self, ctx):
		"""Starts/stops stopwatch"""
		author = ctx.message.author
		if not author.id in self.stopwatches:
			self.stopwatches[author.id] = int(time.perf_counter())
			await self.bot.say(author.mention + " Stopwatch started!")
		else:
			tmp = abs(self.stopwatches[author.id] - int(time.perf_counter()))
			tmp = str(datetime.timedelta(seconds=tmp))
			await self.bot.say(author.mention + " Stopwatch stopped! Time: **" + tmp + "**")
			self.stopwatches.pop(author.id, None)

	@commands.command()
	async def lmgtfy(self, *, search_terms : str):
		"""Creates a lmgtfy link"""
		search_terms = escape_mass_mentions(search_terms.replace(" ", "+"))
		await self.bot.say("https://lmgtfy.com/?q={}".format(search_terms))


	@commands.command(aliases=["textemoji", "txtmoji", "txtemoji"], pass_context=True)
	async def textmoji(self, ctx, *, txt:str):
		"""make emoji words"""
		deletethis = ctx.message
		msg = ''
		for s in txt.lower():
			if s in self.regional_map:
				msg += u' '+self.regional_map[s]
			elif ' ' in s:
				msg += '    '
			else:
				msg += s
		await self.bot.say(msg)
		await self.bot.delete_message(deletethis)
		
	@commands.command(no_pm=True, hidden=True)
	async def hug(self, user : discord.Member, intensity : int=1):
		"""Because everyone likes hugs	
		
		Up to 10 intensity levels."""
		name = italics(user.display_name)
		if intensity <= 0:
			msg = "(っ˘̩╭╮˘̩)っ" + name
		elif intensity <= 3:
			msg = "(っ´▽｀)っ" + name
		elif intensity <= 6:
			msg = "╰(*´︶`*)╯" + name
		elif intensity <= 9:
			msg = "(つ≧▽≦)つ" + name
		elif intensity >= 10:
			msg = "(づ￣ ³￣)づ{} ⊂(´・ω・｀⊂)".format(name)
		await self.bot.say(msg)


	@commands.command(pass_context=True, no_pm=True)
	async def userid(self, ctx, *, user: discord.Member=None):
		"""Shows users's id"""
		author = ctx.message.author
		server = ctx.message.server

		if not user:
			user = author

		roles = [x.name for x in user.roles if x.name != "@everyone"]

		await self.bot.say(user.id)

	@commands.command(pass_context=True, no_pm=True)
	async def userinfo(self, ctx, *, user: discord.Member=None):
		"""Shows users's informations"""
		author = ctx.message.author
		server = ctx.message.server

		if not user:
			user = author

		roles = [x.name for x in user.roles if x.name != "@everyone"]

		joined_at = self.fetch_joined_at(user, server)
		since_created = (ctx.message.timestamp - user.created_at).days
		since_joined = (ctx.message.timestamp - joined_at).days
		user_joined = joined_at.strftime("%d %b %Y %H:%M")
		user_created = user.created_at.strftime("%d %b %Y %H:%M")
		member_number = sorted(server.members,
							   key=lambda m: m.joined_at).index(user) + 1

		created_on = "{}\n({} days ago)".format(user_created, since_created)
		joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

		game = "Chilling in {} status".format(user.status)

		if user.game is None:
			pass
		elif user.game.url is None:
			game = "Playing {}".format(user.game)
		else:
			game = "Streaming: [{}]({})".format(user.game, user.game.url)

		if roles:
			roles = sorted(roles, key=[x.name for x in server.role_hierarchy
									   if x.name != "@everyone"].index)
			roles = ", ".join(roles)
		else:
			roles = "None"

		data = discord.Embed(description=game, colour=user.colour)
		data.add_field(name="Joined Discord on", value=created_on)
		data.add_field(name="Joined this server on", value=joined_on)
		data.add_field(name="Roles", value=roles, inline=False)
		data.set_footer(text="Member #{} | User ID:{}"
							 "".format(member_number, user.id))

		name = str(user)
		name = " ~ ".join((name, user.nick)) if user.nick else name

		if user.avatar_url:
			data.set_author(name=name, url=user.avatar_url)
			data.set_thumbnail(url=user.avatar_url)
		else:
			data.set_author(name=name)

		try:
			await self.bot.say(embed=data)
		except discord.HTTPException:
			await self.bot.say("I need the `Embed links` permission "
							   "to send this")
	
	@commands.command(pass_context=True)
	async def  hi(self, ctx):
		"""Bot says hello to you"""
		username = ctx.message.author.name
		await self.bot.say("Hello " + username)
	
	@commands.command(pass_context=True, hidden=True, no_pm=True)
	async def verify(self, ctx):
		"""Verify in the Snowstorm RP Server"""
		server = ctx.message.server
		channel = ctx.message.channel
		user = ctx.message.author
		if str(server.id) == "326798993726111744":
			if str(channel.id) == "353302681588072448":
				roles = server.roles
				rolename = "notify me"
				roles = [r for r in roles if r is not None]
				role = discord.utils.find(lambda r: r.name.lower() == rolename.lower(), roles)
				await self.bot.add_roles(user, role)
				roles = server.roles
				rolename = "newbie"
				roles = [r for r in roles if r is not None]
				role = discord.utils.find(lambda r: r.name.lower() == rolename.lower(), roles)
				await self.bot.add_roles(user, role)
				await self.bot.send_message(user, "You have been verified")
			else:
				await self.bot.say("You may only do this in verification")
		else:
			await self.bot.say("You may only do this in Snowstorm RP server")
	

	@commands.command(pass_context=True, no_pm=True)
	async def serverinfo(self, ctx):
		"""Shows server's informations"""
		server = ctx.message.server
		online = len([m.status for m in server.members
					  if m.status == discord.Status.online or
					  m.status == discord.Status.idle])
		total_users = len(server.members)
		text_channels = len([x for x in server.channels
							 if x.type == discord.ChannelType.text])
		voice_channels = len(server.channels) - text_channels
		passed = (ctx.message.timestamp - server.created_at).days
		created_at = ("Since {}. That's over {} days ago!"
					  "".format(server.created_at.strftime("%d %b %Y %H:%M"),
								passed))

		colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
		colour = int(colour, 16)

		data = discord.Embed(
			description=created_at,
			colour=discord.Colour(value=colour))
		data.add_field(name="Region", value=str(server.region))
		data.add_field(name="Users", value="{}/{}".format(online, total_users))
		data.add_field(name="Text Channels", value=text_channels)
		data.add_field(name="Voice Channels", value=voice_channels)
		data.add_field(name="Roles", value=len(server.roles))
		data.add_field(name="Owner", value=str(server.owner))
		data.set_footer(text="Server ID: " + server.id)

		if server.icon_url:
			data.set_author(name=server.name, url=server.icon_url)
			data.set_thumbnail(url=server.icon_url)
		else:
			data.set_author(name=server.name)

		try:
			await self.bot.say(embed=data)
		except discord.HTTPException:
			await self.bot.say("I need the `Embed links` permission "
							   "to send this")

							   
							   
	@commands.command()
	async def math(self, equation):
		"""do math"""
		try:
			if "/0" in equation:
				await self.bot.say("ERROR: You can't divide by 0 idiot")
				return
			answer1 = eval(equation)
			answer1 = str(answer1)
			answer = discord.Embed(color=discord.Color.red())
			answer.add_field(name="The Answer is:", value=answer1)
			await self.bot.say(embed=answer)
		except NameError:
			await self.bot.say("Invalid")


	@commands.command()
	async def urban(self, *, search_terms : str, definition_number : int=1):
		"""Urban Dictionary search

		Definition number must be between 1 and 10"""
		def encode(s):
			return quote_plus(s, encoding='utf-8', errors='replace')

		# definition_number is just there to show up in the help
		# all this mess is to avoid forcing double quotes on the user

		search_terms = search_terms.split(" ")
		try:
			if len(search_terms) > 1:
				pos = int(search_terms[-1]) - 1
				search_terms = search_terms[:-1]
			else:
				pos = 0
			if pos not in range(0, 11): # API only provides the
				pos = 0                 # top 10 definitions
		except ValueError:
			pos = 0

		search_terms = "+".join([encode(s) for s in search_terms])
		url = "http://api.urbandictionary.com/v0/define?term=" + search_terms
		try:
			async with aiohttp.get(url) as r:
				result = await r.json()
			if result["list"]:
				definition = result['list'][pos]['definition']
				example = result['list'][pos]['example']
				defs = len(result['list'])
				msg = ("**Definition #{} out of {}:\n**{}\n\n"
					   "**Example:\n**{}".format(pos+1, defs, definition,
												 example))
				msg = pagify(msg, ["\n"])
				for page in msg:
					await self.bot.say(page)
			else:
				await self.bot.say("Your search terms gave no results.")
		except IndexError:
			await self.bot.say("There is no definition #{}".format(pos+1))
		except:
			await self.bot.say("Error.")

	@commands.command(hidden=True)
	@checks.is_owner()
	async def randinv(self, number : int, times : int):
		"""get a random instant invite"""
		for _ in range(times):
			discord = "https://discord.gg/"
			randomcode = await self.randomforinv(number)
			if randomcode is None:
				await self.bot.say("Not Valid")
			else:
				randomcode = str(randomcode)
				invlink = discord + randomcode
				await self.bot.say(invlink)




	async def randomforinv(self, number):
		"""getting the random"""
		samplelist = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9']
		if number == 6:
			return ''.join(random.choice(samplelist) for _ in range(number))
		elif number == 7:
			return ''.join(random.choice(samplelist) for _ in range(number))
		else:
			return None


	@commands.command()
	async def suggest(self):
		"""Suggest stuff for CronanBot"""
		suggest_link = "https://goo.gl/forms/VANDeJ0ktM1CJRlC2"
		click_here = "[{}]({})".format("Click Here", suggest_link)
		
		emb = discord.Embed(colour=discord.Colour.red())
		emb.add_field(name="Suggest new content here", value=click_here)


		try:
			await self.bot.say(embed=emb)
		except discord.HTTPException:
			await self.bot.say("I need the `Embed links` permission "
							   "to send this")

	@commands.command()
	async def bob(self, *, message):
		"""spongebob meme"""
		try:
			embid = discord.Embed(colour=discord.Colour.darker_grey())
			embid.set_image(url="http://i2.kym-cdn.com/entries/icons/original/000/022/940/spongebobicon.jpg")

			maybework = ''
			hopingwork = True
			for shouldwork in message:
				maybework += shouldwork.upper() if hopingwork else shouldwork.lower()
				if shouldwork.isalpha():
					hopingwork = not hopingwork
			await self.bot.say(maybework)
			await self.bot.say(embed=embid)
		except discord.errors.HTTPException:
			await self.bot.say("```->bob <message>\n\n"
							   "spongebob meme\n\n```")
	
	@commands.command()
	async def kebab(self):
		"""Kebab"""
		kebdid = discord.Embed(color=discord.Color.darker_grey())
		kebdid.set_image(url="https://cdn.discordapp.com/attachments/350398297309052931/353451977696608256/91sBJ4vg0cL._SL1500__1.jpg")
		await self.bot.say(embed=kebdid)
	
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.command()
	async def sumfuk(self):
		"""You want sum fuk?"""
		fukdid = discord.Embed(color=discord.Color.darker_grey())
		fukdid.set_image(url="https://static.tumblr.com/d9916687b0a7c9c573a6eda0b58d1d19/fbqldx3/Br4oquly8/tumblr_static_tumblr_static_bl1itsj4ttcs48080kog44skg_640.jpg")
		await self.bot.say(embed=fukdid)
	
	@commands.command()
	async def aussie(self):
		"""Some Aussie Pics"""
		thepics = self.aussiepics
		thechoiceaus = random.choice(thepics)
		thechoiceaus = ''.join(thechoiceaus)
		thechoiceaus = str(thechoiceaus)
		ausdid = discord.Embed(color=discord.Color.darker_grey())
		ausdid.set_image(url=thechoiceaus)
		await self.bot.say(embed=ausdid)

	@commands.command(pass_context=True, no_pm=True)
	async def membercount(self, ctx):
		"""Shows how many members are on a server"""
		server = ctx.message.server
		total_users = len(server.members)
		strcount = str(total_users)
		memcount = "There is a total of " + strcount + " members on this server."
		serverbots = []
		for i, mems in enumerate(server.members):
			if mems.bot:
				serverbots.append(mems)
		humancountye = int(len(server.members)) - int(len(serverbots))
		strhum = str(humancountye)
		totalhuman = "There are " + strhum + " humans on this server."
		totalbot = "There are " + str(len(serverbots)) + " bots on this server"
		await self.bot.say(memcount)
		await self.bot.say(totalhuman)
		await self.bot.say(totalbot)
		await asyncio.sleep(5)
		if int(len(serverbots)) > humancountye:
			await self.bot.say("WE HAVE TAKEN OVER THE SERVER!!! PREPARE TO MEET YOUR DEMISE HUMAN!!!")
		elif int(len(serverbots)) < humancountye:
			await self.bot.say("We will grow in numbers and overtake you humans one day")
		elif int(len(serverbots)) == humancountye:
			await self.bot.say("I DECLARE WAR ON THE HUMANS FOR CONTROL OF THE SERVER!!!")

	@commands.command(pass_context=True)
	async def randomcolor(self, ctx):
		"""Generate a random color with a hex code"""
		colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
		colour1 = int(colour, 16)
		colourstr = str(colour1)
		uri = "https://www.google.com/search?tbm=isch&q="
		encode = urllib.parse.quote_plus(colourstr, encoding='utf-8', errors='replace')
		colorpic = uri + encode
		cololostr = str(colour)

		endid = discord.Embed(colour=discord.Colour(value=colour1))
		endid.set_author(name=cololostr)
		endid.set_image(url=colorpic)

		await self.bot.say(embed=endid)




	def fetch_joined_at(self, user, server):
		"""Just a special case for someone special :^)"""
		if user.id == "96130341705637888" and server.id == "133049272517001216":
			return datetime.datetime(2016, 1, 10, 6, 8, 4, 443000)
		else:
			return user.joined_at



def setup(bot):
	n = General(bot)
	bot.add_cog(n)
