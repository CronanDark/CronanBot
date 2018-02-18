import discord
from discord.ext import commands
from cogs.utils.dataIO import dataIO
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from copy import deepcopy
from .utils import checks
from cogs.utils.chat_formatting import pagify, box
from enum import Enum
from __main__ import send_cmd_help
import os
import time
import logging
import random
import asyncio
from random import choice
from cogs.utils.dataIO import dataIO

default_settings = {"PAYDAY_TIME": 300, "PAYDAY_CREDITS": 120,
					"SLOT_MIN": 5, "SLOT_MAX": 100, "SLOT_TIME": 0,
					"REGISTER_CREDITS": 0}


class EconomyError(Exception):
	pass


class OnCooldown(EconomyError):
	pass


class InvalidBid(EconomyError):
	pass


class BankError(Exception):
	pass


class AccountAlreadyExists(BankError):
	pass


class NoAccount(BankError):
	pass


class InsufficientBalance(BankError):
	pass


class NegativeValue(BankError):
	pass


class SameSenderAndReceiver(BankError):
	pass


NUM_ENC = "\N{COMBINING ENCLOSING KEYCAP}"


class SMReel(Enum):
	cherries  = "\N{CHERRIES}"
	cookie    = "\N{COOKIE}"
	two       = "\N{DIGIT TWO}" + NUM_ENC
	flc       = "\N{FOUR LEAF CLOVER}"
	cyclone   = "\N{CYCLONE}"
	sunflower = "\N{SUNFLOWER}"
	six       = "\N{DIGIT SIX}" + NUM_ENC
	mushroom  = "\N{MUSHROOM}"
	heart     = "\N{HEAVY BLACK HEART}"
	snowflake = "\N{SNOWFLAKE}"

PAYOUTS = {
	(SMReel.two, SMReel.two, SMReel.six) : {
		"payout" : lambda x: x * 2500 + x,
		"phrase" : "JACKPOT! 226! Your bid has been multiplied * 2500!"
	},
	(SMReel.flc, SMReel.flc, SMReel.flc) : {
		"payout" : lambda x: x + 1000,
		"phrase" : "4LC! +1000!"
	},
	(SMReel.cherries, SMReel.cherries, SMReel.cherries) : {
		"payout" : lambda x: x + 800,
		"phrase" : "Three cherries! +800!"
	},
	(SMReel.two, SMReel.six) : {
		"payout" : lambda x: x * 4 + x,
		"phrase" : "2 6! Your bid has been multiplied * 4!"
	},
	(SMReel.cherries, SMReel.cherries) : {
		"payout" : lambda x: x * 3 + x,
		"phrase" : "Two cherries! Your bid has been multiplied * 3!"
	},
	"3 symbols" : {
		"payout" : lambda x: x + 500,
		"phrase" : "Three symbols! +500!"
	},
	"2 symbols" : {
		"payout" : lambda x: x * 2 + x,
		"phrase" : "Two consecutive symbols! Your bid has been multiplied * 2!"
	},
}

SLOT_PAYOUTS_MSG = ("Slot machine payouts:\n"
					"{two.value} {two.value} {six.value} Bet * 2500\n"
					"{flc.value} {flc.value} {flc.value} +1000\n"
					"{cherries.value} {cherries.value} {cherries.value} +800\n"
					"{two.value} {six.value} Bet * 4\n"
					"{cherries.value} {cherries.value} Bet * 3\n\n"
					"Three symbols: +500\n"
					"Two symbols: Bet * 2".format(**SMReel.__dict__))


class Bank:

	def __init__(self, bot, file_path):
		self.accounts = dataIO.load_json(file_path)
		self.bot = bot

	def create_account(self, user, *, initial_balance=0):
		server = user.server
		if not self.account_exists(user):
			if server.id not in self.accounts:
				self.accounts[server.id] = {}
			if user.id in self.accounts:  # Legacy account
				balance = self.accounts[user.id]["balance"]
			else:
				balance = initial_balance
			timestamp = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
			account = {"name": user.name,
					   "balance": balance,
					   "created_at": timestamp
					   }
			self.accounts[server.id][user.id] = account
			self._save_bank()
			return self.get_account(user)
		else:
			raise AccountAlreadyExists()

	def account_exists(self, user):
		try:
			self._get_account(user)
		except NoAccount:
			return False
		return True

	def withdraw_credits(self, user, amount):
		server = user.server

		if amount < 0:
			raise NegativeValue()

		account = self._get_account(user)
		if account["balance"] >= amount:
			account["balance"] -= amount
			self.accounts[server.id][user.id] = account
			self._save_bank()
		else:
			raise InsufficientBalance()

	def deposit_credits(self, user, amount):
		server = user.server
		if amount < 0:
			raise NegativeValue()
		account = self._get_account(user)
		account["balance"] += amount
		self.accounts[server.id][user.id] = account
		self._save_bank()

	def set_credits(self, user, amount):
		server = user.server
		if amount < 0:
			raise NegativeValue()
		account = self._get_account(user)
		account["balance"] = amount
		self.accounts[server.id][user.id] = account
		self._save_bank()

	def transfer_credits(self, sender, receiver, amount):
		if amount < 0:
			raise NegativeValue()
		if sender is receiver:
			raise SameSenderAndReceiver()
		if self.account_exists(sender) and self.account_exists(receiver):
			sender_acc = self._get_account(sender)
			if sender_acc["balance"] < amount:
				raise InsufficientBalance()
			self.withdraw_credits(sender, amount)
			self.deposit_credits(receiver, amount)
		else:
			raise NoAccount()

	def can_spend(self, user, amount):
		account = self._get_account(user)
		if account["balance"] >= amount:
			return True
		else:
			return False

	def wipe_bank(self, server):
		self.accounts[server.id] = {}
		self._save_bank()

	def get_server_accounts(self, server):
		if server.id in self.accounts:
			raw_server_accounts = deepcopy(self.accounts[server.id])
			accounts = []
			for k, v in raw_server_accounts.items():
				v["id"] = k
				v["server"] = server
				acc = self._create_account_obj(v)
				accounts.append(acc)
			return accounts
		else:
			return []

	def get_all_accounts(self):
		accounts = []
		for server_id, v in self.accounts.items():
			server = self.bot.get_server(server_id)
			if server is None:
				# Servers that have since been left will be ignored
				# Same for users_id from the old bank format
				continue
			raw_server_accounts = deepcopy(self.accounts[server.id])
			for k, v in raw_server_accounts.items():
				v["id"] = k
				v["server"] = server
				acc = self._create_account_obj(v)
				accounts.append(acc)
		return accounts

	def get_balance(self, user):
		account = self._get_account(user)
		return account["balance"]

	def get_account(self, user):
		acc = self._get_account(user)
		acc["id"] = user.id
		acc["server"] = user.server
		return self._create_account_obj(acc)

	def _create_account_obj(self, account):
		account["member"] = account["server"].get_member(account["id"])
		account["created_at"] = datetime.strptime(account["created_at"],
												  "%m-%d-%Y %H:%M:%S")
		Account = namedtuple("Account", "id name balance "
							 "created_at server member")
		return Account(**account)

	def _save_bank(self):
		dataIO.save_json("data/economy/bank.json", self.accounts)

	def _get_account(self, user):
		server = user.server
		try:
			return deepcopy(self.accounts[server.id][user.id])
		except KeyError:
			raise NoAccount()


class SetParser:
	def __init__(self, argument):
		allowed = ("+", "-")
		if argument and argument[0] in allowed:
			try:
				self.sum = int(argument)
			except:
				raise
			if self.sum < 0:
				self.operation = "withdraw"
			elif self.sum > 0:
				self.operation = "deposit"
			else:
				raise
			self.sum = abs(self.sum)
		elif argument.isdigit():
			self.sum = int(argument)
			self.operation = "set"
		else:
			raise


class Economy:
	"""Economy

	Get rich and have fun with imaginary currency!"""

	def __init__(self, bot):
		global default_settings
		self.bot = bot
		self.bank = Bank(bot, "data/economy/bank.json")
		self.file_path = "data/economy/settings.json"
		self.settings = dataIO.load_json(self.file_path)
		if "PAYDAY_TIME" in self.settings:  # old format
			default_settings = self.settings
			self.settings = {}
		self.settings = defaultdict(lambda: default_settings, self.settings)
		self.payday_register = defaultdict(dict)
		self.slot_register = defaultdict(dict)

	@commands.group(name="bank", pass_context=True)
	async def _bank(self, ctx):
		"""Bank operations"""
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)

	@_bank.command(pass_context=True, no_pm=True)
	async def register(self, ctx):
		"""Registers an account at the Cronan bank"""
		settings = self.settings[ctx.message.server.id]
		author = ctx.message.author
		credits = 0
		if ctx.message.server.id in self.settings:
			credits = settings.get("REGISTER_CREDITS", 0)
		try:
			account = self.bank.create_account(author, initial_balance=credits)
			await self.bot.say("{} Account opened. Current balance: ${}"
							   "".format(author.mention, account.balance))
		except AccountAlreadyExists:
			await self.bot.say("{} You already have an account at the"
							   " Cronan bank.".format(author.mention))

	@_bank.command(pass_context=True)
	async def balance(self, ctx, user: discord.Member=None):
		"""Shows balance of user.

		Defaults to yours."""
		if not user:
			user = ctx.message.author
			try:
				await self.bot.say("{} Your balance is: ${}".format(
					user.mention, self.bank.get_balance(user)))
			except NoAccount:
				await self.bot.say("{} You don't have an account at the"
								   " Cronan bank. Type `{}bank register`"
								   " to open one.".format(user.mention,
														  ctx.prefix))
		else:
			try:
				await self.bot.say("{}'s balance is ${}".format(
					user.name, self.bank.get_balance(user)))
			except NoAccount:
				await self.bot.say("That user has no bank account.")

	@_bank.command(pass_context=True)
	async def transfer(self, ctx, user: discord.Member, sum: int):
		"""Transfer money to other users"""
		author = ctx.message.author
		try:
			self.bank.transfer_credits(author, user, sum)
			logger.info("{}({}) transferred ${} to {}({})".format(
				author.name, author.id, sum, user.name, user.id))
			await self.bot.say("${} have been transferred to {}'s"
							   " account.".format(sum, user.name))
		except NegativeValue:
			await self.bot.say("You need to transfer at least $1.")
		except SameSenderAndReceiver:
			await self.bot.say("You can't transfer money to yourself.")
		except InsufficientBalance:
			await self.bot.say("You don't have that sum in your bank account.")
		except NoAccount:
			await self.bot.say("That user has no bank account.")

	@_bank.command(name="set", pass_context=True)
	@checks.admin_or_permissions(manage_server=True)
	async def _set(self, ctx, user: discord.Member, money: SetParser):
		"""Sets the money of user's bank account. See help for more operations

		Passing positive and negative values will add/remove money instead

		Examples:
			bank set @Cronan 26 - Sets $26
			bank set @Cronan +2 - Adds $2
			bank set @Cronan -6 - Removes $6"""
		author = ctx.message.author
		try:
			if money.operation == "deposit":
				self.bank.deposit_credits(user, money.sum)
				logger.info("{}({}) added ${} to {} ({})".format(
					author.name, author.id, money.sum, user.name, user.id))
				await self.bot.say("${} have been added to {}"
								   "".format(money.sum, user.name))
			elif money.operation == "withdraw":
				self.bank.withdraw_credits(user, money.sum)
				logger.info("{}({}) removed ${} to {} ({})".format(
					author.name, author.id, money.sum, user.name, user.id))
				await self.bot.say("${} have been withdrawn from {}"
								   "".format(money.sum, user.name))
			elif money.operation == "set":
				self.bank.set_credits(user, money.sum)
				logger.info("{}({}) set ${} to {} ({})"
							"".format(author.name, author.id, money.sum,
									  user.name, user.id))
				await self.bot.say("{}'s money have been set to ${}".format(
					user.name, money.sum))
		except InsufficientBalance:
			await self.bot.say("User doesn't have enough money.")
		except NoAccount:
			await self.bot.say("User has no bank account.")

	@_bank.command(pass_context=True, no_pm=True)
	@checks.serverowner_or_permissions(administrator=True)
	async def reset(self, ctx, confirmation: bool=False):
		"""Deletes all server's bank accounts"""
		if confirmation is False:
			await self.bot.say("This will delete all bank accounts on "
							   "this server.\nIf you're sure, type "
							   "{}bank reset yes".format(ctx.prefix))
		else:
			self.bank.wipe_bank(ctx.message.server)
			await self.bot.say("All bank accounts of this server have been "
							   "deleted.")

	@commands.command(pass_context=True, no_pm=True)
	async def payday(self, ctx):  # TODO
		"""Get some free money"""
		author = ctx.message.author
		server = author.server
		id = author.id
		if self.bank.account_exists(author):
			if id in self.payday_register[server.id]:
				seconds = abs(self.payday_register[server.id][
							  id] - int(time.perf_counter()))
				if seconds >= self.settings[server.id]["PAYDAY_TIME"]:
					self.bank.deposit_credits(author, self.settings[
											  server.id]["PAYDAY_CREDITS"])
					self.payday_register[server.id][
						id] = int(time.perf_counter())
					await self.bot.say(
						"{} Here, take some money. Enjoy! (+${}"
						"!)".format(
							author.mention,
							str(self.settings[server.id]["PAYDAY_CREDITS"])))
				else:
					dtime = self.display_time(
						self.settings[server.id]["PAYDAY_TIME"] - seconds)
					await self.bot.say(
						"{} Too soon. For your next payday you have to"
						" wait {}.".format(author.mention, dtime))
			else:
				self.payday_register[server.id][id] = int(time.perf_counter())
				self.bank.deposit_credits(author, self.settings[
										  server.id]["PAYDAY_CREDITS"])
				await self.bot.say(
					"{} Here, take some money. Enjoy! (+${}!)".format(
						author.mention,
						str(self.settings[server.id]["PAYDAY_CREDITS"])))
		else:
			await self.bot.say("{} You need an account to receive money."
							   " Type `{}bank register` to open one.".format(
								   author.mention, ctx.prefix))

	@commands.group(pass_context=True)
	async def leaderboard(self, ctx):
		"""Server / global leaderboard

		Defaults to server"""
		if ctx.invoked_subcommand is None:
			await ctx.invoke(self._server_leaderboard)

	@leaderboard.command(name="server", pass_context=True)
	async def _server_leaderboard(self, ctx, top: int=10):
		"""Prints out the server's leaderboard

		Defaults to top 10"""
		server = ctx.message.server
		if top < 1:
			top = 10
		bank_sorted = sorted(self.bank.get_server_accounts(server),
							 key=lambda x: x.balance, reverse=True)
		bank_sorted = [a for a in bank_sorted if a.member] #  exclude users who left
		if len(bank_sorted) < top:
			top = len(bank_sorted)
		topten = bank_sorted[:top]
		highscore = ""
		place = 1
		serboardbed = discord.Embed(color=discord.Color.red())
		for acc in topten:
			highscore = "**"
			highscore += (str(acc.member.display_name) + " ").ljust(23 - len(str(acc.balance)))
			highscore += "**"
			highscore += "$" + str(acc.balance) + "\n"
			serboardbed.add_field(name=str(place), value=str(highscore), inline=False)
			place += 1
		if highscore != "":
			await self.bot.say(embed=serboardbed)
		else:
			await self.bot.say("There are no accounts in the bank.")

	@leaderboard.command(name="global")
	async def _global_leaderboard(self, top: int=10):
		"""Prints out the global leaderboard

		Defaults to top 10"""
		if top < 1:
			top = 10
		bank_sorted = sorted(self.bank.get_all_accounts(),
							 key=lambda x: x.balance, reverse=True)
		bank_sorted = [a for a in bank_sorted if a.member] #  exclude users who left
		unique_accounts = []
		for acc in bank_sorted:
			if not self.already_in_list(unique_accounts, acc):
				unique_accounts.append(acc)
		if len(unique_accounts) < top:
			top = len(unique_accounts)
		topten = unique_accounts[:top]
		highscore = ""
		place = 1
		globoardbed = discord.Embed(color=discord.Color.red())
		for acc in topten:
			highscore = "**"
			highscore += ("{}** (*{}*) ".format(acc.member, acc.server)
						  ).ljust(23 - len(str(acc.balance)))
			highscore += "$" + str(acc.balance) + "\n"
			globoardbed.add_field(name=str(place), value=str(highscore), inline=False)
			place += 1
		if highscore != "":
			await self.bot.say(embed=globoardbed)
		else:
			await self.bot.say("There are no accounts in the bank.")

	def already_in_list(self, accounts, user):
		for acc in accounts:
			if user.id == acc.id:
				return True
		return False

	@commands.command()
	async def payouts(self):
		"""Shows slot machine payouts"""
		await self.bot.whisper(SLOT_PAYOUTS_MSG)

	@commands.command(pass_context=True, no_pm=True)
	async def slot(self, ctx, bid: int):
		"""Play the slot machine"""
		author = ctx.message.author
		server = author.server
		settings = self.settings[server.id]
		valid_bid = settings["SLOT_MIN"] <= bid and bid <= settings["SLOT_MAX"]
		slot_time = settings["SLOT_TIME"]
		last_slot = self.slot_register.get(author.id)
		now = datetime.now()
		try:
			if last_slot:
				if (now - last_slot).seconds < slot_time:
					raise OnCooldown()
			if not valid_bid:
				raise InvalidBid()
			if not self.bank.can_spend(author, bid):
				raise InsufficientBalance
			await self.slot_machine(author, bid)
		except NoAccount:
			await self.bot.say("{} You need an account to use the slot "
							   "machine. Type `{}bank register` to open one."
							   "".format(author.mention, ctx.prefix))
		except InsufficientBalance:
			await self.bot.say("{} You need an account with enough funds to "
							   "play the slot machine.".format(author.mention))
		except OnCooldown:
			await self.bot.say("Slot machine is still cooling off! Wait {} "
							   "seconds between each pull".format(slot_time))
		except InvalidBid:
			await self.bot.say("Bid must be between ${} and ${}."
							   "".format(settings["SLOT_MIN"],
										 settings["SLOT_MAX"]))

	async def slot_machine(self, author, bid):
		default_reel = deque(SMReel)
		reels = []
		self.slot_register[author.id] = datetime.now()
		for i in range(3):
			default_reel.rotate(random.randint(-999, 999)) # weeeeee
			new_reel = deque(default_reel, maxlen=3) # we need only 3 symbols
			reels.append(new_reel)                   # for each reel
		rows = ((reels[0][0], reels[1][0], reels[2][0]),
				(reels[0][1], reels[1][1], reels[2][1]),
				(reels[0][2], reels[1][2], reels[2][2]))

		slot = "~~\n~~" # Mobile friendly
		for i, row in enumerate(rows): # Let's build the slot to show
			sign = "  "
			if i == 1:
				sign = ">"
			slot += "{}{} {} {}\n".format(sign, *[c.value for c in row])

		payout = PAYOUTS.get(rows[1])
		if not payout:
			# Checks for two-consecutive-symbols special rewards
			payout = PAYOUTS.get((rows[1][0], rows[1][1]),
					 PAYOUTS.get((rows[1][1], rows[1][2]))
								)
		if not payout:
			# Still nothing. Let's check for 3 generic same symbols
			# or 2 consecutive symbols
			has_three = rows[1][0] == rows[1][1] == rows[1][2]
			has_two = (rows[1][0] == rows[1][1]) or (rows[1][1] == rows[1][2])
			if has_three:
				payout = PAYOUTS["3 symbols"]
			elif has_two:
				payout = PAYOUTS["2 symbols"]

		if payout:
			then = self.bank.get_balance(author)
			pay = payout["payout"](bid)
			now = then - bid + pay
			self.bank.set_credits(author, now)
			await self.bot.say("{}\n{} {}\n\nYour bid: ${}\n${} → ${}!"
							   "".format(slot, author.mention,
										 payout["phrase"], bid, then, now))
		else:
			then = self.bank.get_balance(author)
			self.bank.withdraw_credits(author, bid)
			now = then - bid
			await self.bot.say("{}\n{} Nothing!\nYour bid: ${}\n${} → ${}!"
							   "".format(slot, author.mention, bid, then, now))

	@commands.group(pass_context=True, no_pm=True)
	@checks.admin_or_permissions(manage_server=True)
	async def economyset(self, ctx):
		"""Changes economy module settings"""
		server = ctx.message.server
		settings = self.settings[server.id]
		if ctx.invoked_subcommand is None:
			msg = ""
			for k, v in settings.items():
				k = "**__" + str(k) + ":__**"
				v = "*" + str(v) + "*"
				msg += "{} {}\n".format(k, v)
			await send_cmd_help(ctx)
			await self.bot.say(msg)

	@economyset.command(pass_context=True)
	async def slotmin(self, ctx, bid: int):
		"""Minimum slot machine bid"""
		server = ctx.message.server
		self.settings[server.id]["SLOT_MIN"] = bid
		await self.bot.say("Minimum bid is now ${}.".format(bid))
		dataIO.save_json(self.file_path, self.settings)

	@economyset.command(pass_context=True)
	async def slotmax(self, ctx, bid: int):
		"""Maximum slot machine bid"""
		server = ctx.message.server
		self.settings[server.id]["SLOT_MAX"] = bid
		await self.bot.say("Maximum bid is now ${}.".format(bid))
		dataIO.save_json(self.file_path, self.settings)

	@economyset.command(pass_context=True)
	async def slottime(self, ctx, seconds: int):
		"""Seconds between each slots use"""
		server = ctx.message.server
		self.settings[server.id]["SLOT_TIME"] = seconds
		await self.bot.say("Cooldown is now {} seconds.".format(seconds))
		dataIO.save_json(self.file_path, self.settings)

	@economyset.command(pass_context=True)
	async def paydaytime(self, ctx, seconds: int):
		"""Seconds between each payday"""
		server = ctx.message.server
		self.settings[server.id]["PAYDAY_TIME"] = seconds
		await self.bot.say("Value modified. At least {} seconds must pass "
						   "between each payday.".format(seconds))
		dataIO.save_json(self.file_path, self.settings)

	@economyset.command(pass_context=True)
	async def paydaymoney(self, ctx, money: int):
		"""Money earned each payday"""
		server = ctx.message.server
		self.settings[server.id]["PAYDAY_CREDITS"] = money
		await self.bot.say("Every payday will now give ${}."
						   "".format(money))
		dataIO.save_json(self.file_path, self.settings)

	@economyset.command(pass_context=True)
	async def registermoney(self, ctx, money: int):
		"""Money given on registering an account"""
		server = ctx.message.server
		if money < 0:
			money = 0
		self.settings[server.id]["REGISTER_CREDITS"] = money
		await self.bot.say("Registering an account will now give ${}."
						   "".format(money))
		dataIO.save_json(self.file_path, self.settings)

	# What would I ever do without stackoverflow?
	def display_time(self, seconds, granularity=2):
		intervals = (  # Source: http://stackoverflow.com/a/24542445
			('weeks', 604800),  # 60 * 60 * 24 * 7
			('days', 86400),    # 60 * 60 * 24
			('hours', 3600),    # 60 * 60
			('minutes', 60),
			('seconds', 1),
		)

		result = []

		for name, count in intervals:
			value = seconds // count
			if value:
				seconds -= value * count
				if value == 1:
					name = name.rstrip('s')
				result.append("{} {}".format(value, name))
		return ', '.join(result[:granularity])

class Life:
	def __init__(self, bot):
		self.bot = bot
		self.bank = Bank(bot, "data/economy/bank.json")

	@commands.command(pass_context=True, no_pm=True)
	async def life(self, ctx):
		"""Play a game of life"""
		grade = 1
		job = 0
		income = 0
		didstudy = 0
		filename = ctx.message.author.name + "_life.txt"
		filepath = "data/life/temp/" + filename
		filepath2 = os.path.join("data/life/temp", filename)
		if not os.path.exists("data/life/temp"):
			os.makedirs("data/life/temp")
		if os.path.exists(filepath):
			os.remove(filepath)
		f = open(filepath2, "w+")
		i = 0
		money = 0
		dropout = False
		jobtypeA = [15, 14, 13]
		jobtypeB = [12, 11, 10]
		jobtypeC = [9, 8, 7]
		jobtypeD = [6, 5, 4]
		jobtypeE = [3, 2, 1]
		choices5 = [1]
		choices10 = [1, 2]
		choices18 = [1, 2, 3, 4, 5]
		choicesUP = [1, 2, 3, 4, 5, 6, 7]
		noombers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
		ageten = (choice(noombers) * 10)
		ageone = choice(noombers)
		age = ageten + ageone
		while i <= age:
			chosenint = 134085897189357184935
			chosen = 0
			if i == 0:
				await self.bot.say("You are now born")
				f.write("You are now born\n")
			else:
				await self.bot.say("You are now " + str(i) + " years old")
				f.write("You are now " + str(i) + " years old\n")
			if i == 5:
				await self.bot.say("You have started elementary school")
				f.write("You have started elementary school\n")
			elif i == 10:
				await self.bot.say("You have graduated elementary school and started middle school")
				f.write("You have graduated elementary school and started middle school\n")
			elif i == 13:
				await self.bot.say("You have graduated middle school and started high school")
				f.write("You have graduated middle school and started high school\n")
			elif i == 18 and grade <= 3:
				await self.bot.say("You have graduated high school")
				f.write("You have graduated high school\n")
			elif i == 18 and grade > 3 and dropout is False:
				await self.bot.say("You failed high school and were kicked out `(cause me as dev to lazy to figure out how to make u help back and not break code)`")
				f.write("You failed high school and were kicked out `(cause me as dev to lazy to figure out how to make u help back and not break code)`\n")
				grade = 10
			if i < 5:
				await self.bot.say("1. Age one year")
				correctmsg = False
				while correctmsg is False:
					await asyncio.sleep(1)
					chosen = None
					chosen = await self.bot.wait_for_message(timeout=300, author=ctx.message.author)
					if chosen is not None:
						try:
							chosenint = int(chosen.content)
						except:
							chosenint = 2748917289
					if chosen is None:
						correctmsg = True
					elif chosenint in choices5:
						correctmsg = True
			elif i < 13:
				while chosenint != 1 and chosenint != 0:
					await self.bot.say("1. Age one year")
					await self.bot.say("2. Study")
					correctmsg = False
					while correctmsg is False:
						await asyncio.sleep(1)
						chosen = None
						chosen = await self.bot.wait_for_message(timeout=300, author=ctx.message.author)
						if chosen is not None:
							try:
								chosenint = int(chosen.content)
							except:
								chosenint = 2748917289
						if chosen is None:
							correctmsg = True
							chosenint = 0
						elif chosenint in choices10:
							correctmsg = True
					if correctmsg is True and chosenint == 1 and didstudy == 0:
						grade += 1
					elif correctmsg is True and chosenint == 2:
						await self.bot.say("You chose to study")
						f.write("You chose to study\n")
						didstudy += 1
						if grade > 1:
							grade -= 1
			elif i < 18:
				while chosenint != 1 and chosenint != 0:
					await self.bot.say("1. Age one year")
					await self.bot.say("2. Study")
					if job == 0:
						await self.bot.say("3. Get a job")
					elif job != 0:
						await self.bot.say("4. Get a new job")
					if dropout is not True:
						await self.bot.say("5. Dropout")
					correctmsg = False
					while correctmsg is False:
						await asyncio.sleep(1)
						chosen = None
						chosen = await self.bot.wait_for_message(timeout=300, author=ctx.message.author)
						if chosen is not None:
							try:
								chosenint = int(chosen.content)
							except:
								chosenint = 2748917289
						if chosen is None:
							correctmsg = True
							chosenint = 0
						elif chosenint in choices18:
							correctmsg = True
					if correctmsg is True and chosenint == 1 and didstudy == 0:
						grade += 1
					elif correctmsg is True and chosenint == 2:
						await self.bot.say("You chose to study")
						f.write("You chose to study\n")
						didstudy += 1
						if grade > 1:
							grade -= 1
					elif correctmsg is True and chosenint == 3:
						await self.bot.say("You chose to get a job")
						f.write("You chose to get a job\n")
						if grade == 1:
							job = choice(jobtypeA)
						elif grade == 2:
							job = choice(jobtypeB)
						elif grade == 3:
							job = choice(jobtypeC)
						elif grade == 4:
							job = choice(jobtypeD)
						elif grade == 5:
							job = choice(jobtypeE)
						else:
							await self.bot.say("You didn't get the job")
							f.write("You didn't get the job\n")
							job = 0
					elif correctmsg is True and chosenint == 4:
						await self.bot.say("You chose to get a new job")
						f.write("You chose to get a new job\n")
						if grade == 1:
							job = choice(jobtypeA)
						elif grade == 2:
							job = choice(jobtypeB)
						elif grade == 3:
							job = choice(jobtypeC)
						elif grade == 4:
							job = choice(jobtypeD)
						elif grade == 5:
							job = choice(jobtypeE)
						else:
							await self.bot.say("You didn't get the job")
							f.write("You didn't get the job\n")
							job = 0
					elif correctmsg is True and chosenint == 5:
						await self.bot.say("You chose to dropout")
						f.write("You chose to dropout\n")
						dropout = True
						grade = 10
			elif i >= 18:
				while chosenint != 1 and chosenint != 0:
					await self.bot.say("1. Age one year")
					await self.bot.say("2. Go to a college class")
					if job == 0:
						await self.bot.say("3. Get a job")
					elif job != 0:
						await self.bot.say("4. Get a new job")
					await self.bot.say("5. Smoke")
					await self.bot.say("6. Get Drunk")
					await self.bot.say("7. Party(not a nice party... like a club kind of party)")
					correctmsg = False
					while correctmsg is False:
						await asyncio.sleep(1)
						chosen = None
						chosen = await self.bot.wait_for_message(timeout=300, author=ctx.message.author)
						if chosen is not None:
							try:
								chosenint = int(chosen.content)
							except:
								chosenint = 2748917289
						if chosen is None:
							correctmsg = True
							chosenint = 0
						elif chosenint in choicesUP:
							correctmsg = True
					if correctmsg is True and chosenint == 1 and didstudy == 0:
						grade += 1
					elif correctmsg is True and chosenint == 2:
						await self.bot.say("You chose to go to a college class and learn")
						f.write("You chose to go to a college class and learn\n")
						didstudy += 1
						if grade > 1:
							grade -= 1
					elif correctmsg is True and chosenint == 3:
						await self.bot.say("You chose to get a job")
						f.write("You chose to get a job\n")
						if grade == 1:
							job = choice(jobtypeA)
						elif grade == 2:
							job = choice(jobtypeB)
						elif grade == 3:
							job = choice(jobtypeC)
						elif grade == 4:
							job = choice(jobtypeD)
						elif grade == 5:
							job = choice(jobtypeE)
						else:
							await self.bot.say("You didn't get the job")
							f.write("You didn't get the job\n")
							job = 0
					elif correctmsg is True and chosenint == 4:
						await self.bot.say("You chose to get a new job")
						f.write("You chose to get a new job\n")
						if grade == 1:
							job = choice(jobtypeA)
						elif grade == 2:
							job = choice(jobtypeB)
						elif grade == 3:
							job = choice(jobtypeC)
						elif grade == 4:
							job = choice(jobtypeD)
						elif grade == 5:
							job = choice(jobtypeE)
						else:
							await self.bot.say("You didn't get the job")
							f.write("You didn't get the job\n")
							job = 0
					elif correctmsg is True and chosenint == 5:
						await self.bot.say("You chose to smoke")
						f.write("You chose to smoke\n")
						age -= 1
						if age <= i:
							await self.bot.say("You smoked too much and died")
							f.write("You smoked too much and died\n")
							age = i
							chosenint = 0
					elif correctmsg is True and chosenint == 6:
						await self.bot.say("You chose to get drunk")
						f.write("You chose to get drunk\n")
						age -= 1
						if age <= i:
							await self.bot.say("You drank too much and died")
							f.write("You drank too much and died\n")
							age = i
							chosenint = 0
					elif correctmsg is True and chosenint == 7:
						await self.bot.say("You chose to go to a party")
						f.write("You chose to go to a party\n")
						age -= 1
						if age <= i:
							await self.bot.say("You partied too much and died the next morning")
							f.write("You partied too much and died the next morning\n")
							age = i
							chosenint = 0
			if chosen is None:
				await self.bot.say("You decided to suicide")
				f.write("You decided to suicide\n")
				age = i
			i += 1
			if grade < 5 and job != 0:
				income = job * 1000
			elif grade >= 5 and job !=0:
				await self.bot.say("You have lost your job")
				f.write("You have lost your job\n")
				job = 0
				income = 0
			money += income

		await self.bot.say("You have died at age `" + str(age) + "` with $`" + str(money) + "`")
		f.write("You have died at age `" + str(age) + "` with $`" + str(money) + "`")
		f.close()
		await self.bot.send_file(ctx.message.channel, filepath2, filename=filename)
		moneybot1 = money / 100
		moneybot2 = money % 100
		moneybot = moneybot1 - moneybot2
		try:
			self.bank.deposit_credits(ctx.message.author, moneybot)
		except:
			self.bank.create_account(ctx.message.author)
			self.bank.deposit_credits(ctx.message.author, moneybot)
		



def check_folders():
	if not os.path.exists("data/economy"):
		print("Creating data/economy folder...")
		os.makedirs("data/economy")


def check_files():

	f = "data/economy/settings.json"
	if not dataIO.is_valid_json(f):
		print("Creating default economy's settings.json...")
		dataIO.save_json(f, {})

	f = "data/economy/bank.json"
	if not dataIO.is_valid_json(f):
		print("Creating empty bank.json...")
		dataIO.save_json(f, {})


def setup(bot):
	global logger
	check_folders()
	check_files()
	logger = logging.getLogger("cronan.economy")
	if logger.level == 0:
		# Prevents the logger from being loaded again in case of module reload
		logger.setLevel(logging.INFO)
		handler = logging.FileHandler(
			filename='data/economy/economy.log', encoding='utf-8', mode='a')
		handler.setFormatter(logging.Formatter(
			'%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
		logger.addHandler(handler)
	bot.add_cog(Economy(bot))
	bot.add_cog(Life(bot))
