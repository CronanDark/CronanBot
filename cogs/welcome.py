import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from .utils.chat_formatting import pagify
from __main__ import send_cmd_help
from copy import deepcopy
import os
import aiohttp
from random import choice as rand_choice
try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageOps
except:
    raise RuntimeError("Can't load pillow. Do 'pip3 install pillow'.")


default_greeting = "Welcome {0.name} to {1.name}!"
default_settings = {"GREETING": [default_greeting], "ON": False,
                    "CHANNEL": None, "WHISPER": False,
                    "BOTS_MSG": None, "BOTS_ROLE": None}
settings_path = "data/welcome/settings.json"
default_goodbye = "Goodbye {0.name}!"
default_goodbyeset = {"GOODBYE": [default_goodbye], "ON": False,
                      "CHANNEL": None, "BOTS_MSG": None,
                      "BOTS_ROLE": None}
goodbye_path = "data/welcome/goodbye.json"
font_file = "data/welcome/Font/njnaruto.ttf"
default_avatar_url = "http://i.imgur.com/XPDO9VH.jpg"


class Welcome:
    """Welcomes new members to the server in the default channel"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json(settings_path)
        self.goodbye = dataIO.load_json(goodbye_path)

    @commands.group(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def welcomeset(self, ctx):
        """Sets welcome module settings"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = deepcopy(default_settings)
            self.settings[server.id]["CHANNEL"] = server.default_channel.id
            dataIO.save_json(settings_path, self.settings)
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = ""
            msg += "**__Random GREETING:__** *{}*\n".format(rand_choice(self.settings[server.id]["GREETING"]))
            msg += "**__CHANNEL:__** *#{}*\n".format(self.get_welcome_channel(server))
            msg += "**__ON:__** *{}*\n".format(self.settings[server.id]["ON"])
            msg += "**__WHISPER:__** *{}*\n".format(self.settings[server.id]["WHISPER"])
            msg += "**__BOTS_MSG:__** *{}*\n".format(self.settings[server.id]["BOTS_MSG"])
            msg += "**__BOTS_ROLE:__** *{}*\n".format(self.settings[server.id]["BOTS_ROLE"])
            await self.bot.say(msg)

    @welcomeset.group(pass_context=True, name="msg")
    async def welcomeset_msg(self, ctx):
        """Manage welcome messages
        """
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)
            return

    @welcomeset_msg.command(pass_context=True, name="add", no_pm=True)
    async def welcomeset_msg_add(self, ctx, *, format_msg):
        """Adds a welcome message format for the server to be chosen at random

        {0} is user
        {1} is server
        Default is set to:
            Welcome {0.name} to {1.name}!

        Example formats:
            {0.mention}.. What are you doing here?
            {1.name} has a new member! {0.name}#{0.discriminator} - {0.id}
            Someone new joined! Who is it?! D: IS HE HERE TO HURT US?!"""
        server = ctx.message.server
        self.settings[server.id]["GREETING"].append(format_msg)
        dataIO.save_json(settings_path, self.settings)
        await self.bot.say("Welcome message added for the server.")
        await self.send_testing_msg(ctx, msg=format_msg)

    @welcomeset_msg.command(pass_context=True, name="del", no_pm=True)
    async def welcomeset_msg_del(self, ctx):
        """Removes a welcome message from the random message list
        """
        server = ctx.message.server
        author = ctx.message.author
        msg = '**__Choose a welcome message to delete:__**\n\n'
        for c, m in enumerate(self.settings[server.id]["GREETING"]):
            msg += "  **{}.** *{}*\n".format(c, m)
        for page in pagify(msg, ['\n', ' '], shorten_by=20):
            await self.bot.say("{}".format(page))
        answer = await self.bot.wait_for_message(timeout=120, author=author)
        try:
            num = int(answer.content)
            choice = self.settings[server.id]["GREETING"].pop(num)
        except:
            await self.bot.say("That's not a number in the list :/")
            return
        if not self.settings[server.id]["GREETING"]:
            self.settings[server.id]["GREETING"] = [default_greeting]
        dataIO.save_json(settings_path, self.settings)
        await self.bot.say("**This message was deleted:**\n{}".format(choice))

    @welcomeset_msg.command(pass_context=True, name="list", no_pm=True)
    async def welcomeset_msg_list(self, ctx):
        """Lists the welcome messages of this server
        """
        server = ctx.message.server
        msg = '**__Welcome messages:__**\n\n'
        for c, m in enumerate(self.settings[server.id]["GREETING"]):
            msg += "  **{}.** *{}*\n".format(c, m)
        for page in pagify(msg, ['\n', ' '], shorten_by=20):
            await self.bot.say("{}".format(page))

    @welcomeset.command(pass_context=True, name="toggle")
    async def welcometoggle(self, ctx):
        """Turns on/off welcoming new users to the server"""
        server = ctx.message.server
        self.settings[server.id]["ON"] = not self.settings[server.id]["ON"]
        if self.settings[server.id]["ON"]:
            await self.bot.say("I will now welcome new users to the server.")
            await self.send_testing_msg(ctx)
        else:
            await self.bot.say("I will no longer welcome new users.")
        dataIO.save_json(settings_path, self.settings)

    @welcomeset.command(pass_context=True, name="channel")
    async def welcomechannel(self, ctx, channel : discord.Channel=None):
        """Sets the channel to send the welcome message

        If channel isn't specified, the server's default channel will be used"""
        server = ctx.message.server
        if channel is None:
            channel = ctx.message.server.default_channel
        if not server.get_member(self.bot.user.id
                                 ).permissions_in(channel).send_messages:
            await self.bot.say("I do not have permissions to send "
                               "messages to {0.mention}".format(channel))
            return
        self.settings[server.id]["CHANNEL"] = channel.id
        dataIO.save_json(settings_path, self.settings)
        channel = self.get_welcome_channel(server)
        await self.bot.send_message(channel, "I will now send welcome "
                                    "messages to {0.mention}".format(channel))
        await self.send_testing_msg(ctx)

    @welcomeset.group(pass_context=True, name="bot", no_pm=True)
    async def welcomeset_bot(self, ctx):
        """Special welcome for bots"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)
            return

    @welcomeset_bot.command(pass_context=True, name="msg", no_pm=True)
    async def welcomeset_bot_msg(self, ctx, *, format_msg=None):
        """Set the welcome msg for bots.

        Leave blank to reset to regular user welcome"""
        server = ctx.message.server
        self.settings[server.id]["BOTS_MSG"] = format_msg
        dataIO.save_json(settings_path, self.settings)
        if format_msg is None:
            await self.bot.say("Bot message reset. Bots will now be welcomed as regular users.")
        else:
            await self.bot.say("Bot welcome message set for the server.")
            await self.send_testing_msg(ctx, bot=True)

    # TODO: Check if have permissions
    @welcomeset_bot.command(pass_context=True, name="role", no_pm=True)
    async def welcomeset_bot_role(self, ctx, role: discord.Role=None):
        """Set the role to put bots in when they join.

        Leave blank to not give them a role."""
        server = ctx.message.server
        self.settings[server.id]["BOTS_ROLE"] = role.name if role else role
        dataIO.save_json(settings_path, self.settings)
        await self.bot.say("Bots that join this server will "
                           "now be put into the {} role".format(role.name))

    @welcomeset.command(pass_context=True)
    async def whisper(self, ctx, choice: str=None):
        """Sets whether or not a DM is sent to the new user

        Options:
            off - turns off DMs to users
            only - only send a DM to the user, don't send a welcome to the channel
            both - send a message to both the user and the channel

        If Option isn't specified, toggles between 'off' and 'only'
        DMs will not be sent to bots"""
        options = {"off": False, "only": True, "both": "BOTH"}
        server = ctx.message.server
        if choice is None:
            self.settings[server.id]["WHISPER"] = not self.settings[server.id]["WHISPER"]
        elif choice.lower() not in options:
            await send_cmd_help(ctx)
            return
        else:
            self.settings[server.id]["WHISPER"] = options[choice.lower()]
        dataIO.save_json(settings_path, self.settings)
        channel = self.get_welcome_channel(server)
        if not self.settings[server.id]["WHISPER"]:
            await self.bot.say("I will no longer send DMs to new users")
        elif self.settings[server.id]["WHISPER"] == "BOTH":
            await self.bot.send_message(channel, "I will now send welcome "
                                        "messages to {0.mention} as well as to "
                                        "the new user in a DM".format(channel))
        else:
            await self.bot.send_message(channel, "I will now only send "
                                        "welcome messages to the new user "
                                        "as a DM".format(channel))
        await self.send_testing_msg(ctx)

    def _center(self, start, end, text, font):
        dist = end - start
        width = font.getsize(text)[0]
        start_pos = start + ((dist-width)/2)
        return int(start_pos)

    async def member_join(self, member):
        server = member.server
        user = member
        if str(server.id) == "220297883390443520":
            person = str(member.name)
            profile_url = user.avatar_url
            profile_image = Image
            try:
                async with aiohttp.get(profile_url) as r:
                    image = await r.content.read()
            except:
                async with aiohttp.get(default_avatar_url) as r:
                    image = await r.content.read()
            with open('data/leveler/temp/{}_temp_level_profile.png'.format(user.id),'wb') as f:
                f.write(image)
            profile_image = Image.open('data/leveler/temp/{}_temp_level_profile.png'.format(user.id)).convert('RGBA')

            width = 175
            height = 60
            bg_color = (70,0,0, 255)
            result = Image.new('RGBA', (width, height), bg_color)
            process = Image.new('RGBA', (width, height), bg_color)

            draw = ImageDraw.Draw(process)

            multiplier = 6
            lvl_circle_dia = 60
            circle_left = 4
            circle_top = int((height- lvl_circle_dia)/2)
            raw_length = lvl_circle_dia * multiplier

            mask = Image.new('L', (raw_length, raw_length), 0)
            draw_thumb = ImageDraw.Draw(mask)
            draw_thumb.ellipse((0, 0) + (raw_length, raw_length), fill = 255, outline = 0)

            

            total_gap = 6
            border = int(total_gap/2)
            profile_size = lvl_circle_dia - total_gap
            raw_length = profile_size * multiplier
            output = ImageOps.fit(profile_image, (raw_length, raw_length), centering=(0.5, 0.5))
            output = output.resize((profile_size, profile_size), Image.ANTIALIAS)
            mask = mask.resize((profile_size, profile_size), Image.ANTIALIAS)
            profile_image = profile_image.resize((profile_size, profile_size), Image.ANTIALIAS)
            process.paste(profile_image, (circle_left + border, circle_top + border), mask)

            level_fnt = ImageFont.truetype('data/welcome/Font/njnaruto.ttf', 20)
            level_fnt2 = ImageFont.truetype('data/welcome/Font/njnaruto.ttf', 14)

            white_text = (0, 106, 99, 255)
            dark_text = (0, 248, 219, 255)

            welcome = "WELCOME"

            draw.text((self._center(50, 170, welcome, level_fnt), 20), welcome, font=level_fnt, fill=white_text)
            draw.text((self._center(50, 170, person, level_fnt), 40), person, font=level_fnt2, fill=dark_text)

            result = Image.alpha_composite(result, process)
            filename = 'data/welcome/temp/{}_welcome.png'.format(user.id)
            result.save(filename,'PNG', quality=100)

            channel = self.get_welcome_channel(server) 
            
            await self.bot.send_file(channel, 'data/welcome/temp/{}_welcome.png'.format(user.id))

            
            
        else:
            if server.id not in self.settings:
                self.settings[server.id] = deepcopy(default_settings)
                self.settings[server.id]["CHANNEL"] = server.default_channel.id
                dataIO.save_json(settings_path, self.settings)
            if not self.settings[server.id]["ON"]:
                return
            if server is None:
                print("Server is None. Private Message or some new fangled "
                      "Discord thing?.. Anyways there be an error, "
                      "the user was {}".format(member.name))
                return

            only_whisper = self.settings[server.id]["WHISPER"] is True
            bot_welcome = member.bot and self.settings[server.id]["BOTS_MSG"]
            bot_role = member.bot and self.settings[server.id]["BOTS_ROLE"]
            msg = bot_welcome or rand_choice(self.settings[server.id]["GREETING"])

            # whisper the user if needed
            if not member.bot and self.settings[server.id]["WHISPER"]:
                try:
                    await self.bot.send_message(member, msg.format(member, server))
                except:
                    print("welcome.py: unable to whisper {}. Probably "
                          "doesn't want to be PM'd".format(member))
            # grab the welcome channel
            channel = self.get_welcome_channel(server)
            if channel is None:  # complain even if only whisper
                print('welcome.py: Channel not found. It was most '
                      'likely deleted. User joined: {}'.format(member.name))
                return
            # we can stop here
            if only_whisper and not bot_welcome:
                return
            if not self.speak_permissions(server):
                print("Permissions Error. User that joined: "
                      "{0.name}".format(member))
                print("Bot doesn't have permissions to send messages to "
                      "{0.name}'s #{1.name} channel".format(server, channel))
                return
            # try to add role if needed
            if bot_role:
                try:
                    role = discord.utils.get(server.roles, name=bot_role)
                    await self.bot.add_roles(member, role)
                except:
                    print('welcome.py: unable to add {} role to {}. '
                          'Role was deleted, network error, or lacking '
                          'permissions'.format(bot_role, member))
                else:
                    print('welcome.py: added {} role to '
                          'bot, {}'.format(role, member))
            # finally, welcome them
            await self.bot.send_message(channel, msg.format(member, server))

    def get_welcome_channel(self, server):
        try:
            return server.get_channel(self.settings[server.id]["CHANNEL"])
        except:
            return None

    def speak_permissions(self, server):
        channel = self.get_welcome_channel(server)
        if channel is None:
            return False
        return server.get_member(self.bot.user.id
                                 ).permissions_in(channel).send_messages

    async def send_testing_msg(self, ctx, bot=False, msg=None):
        server = ctx.message.server
        channel = self.get_welcome_channel(server)
        rand_msg = msg or rand_choice(self.settings[server.id]["GREETING"])
        if channel is None:
            await self.bot.send_message(ctx.message.channel,
                                        "I can't find the specified channel. "
                                        "It might have been deleted.")
            return
        await self.bot.send_message(ctx.message.channel,
                                    "`Sending a testing message to "
                                    "`{0.mention}".format(channel))
        if self.speak_permissions(server):
            msg = self.settings[server.id]["BOTS_MSG"] if bot else rand_msg
            if not bot and self.settings[server.id]["WHISPER"]:
                await self.bot.send_message(ctx.message.author,
                        msg.format(ctx.message.author,server))
            if bot or self.settings[server.id]["WHISPER"] is not True:
                await self.bot.send_message(channel,
                        msg.format(ctx.message.author, server))
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "I do not have permissions "
                                        "to send messages to "
                                        "{0.mention}".format(channel))



    @commands.group(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def goodbyeset(self, ctx):
        """Sets goodbye module settings"""
        server = ctx.message.server
        if server.id not in self.goodbye:
            self.goodbye[server.id] = deepcopy(default_goodbyeset)
            self.goodbye[server.id]["CHANNEL"] = server.default_channel.id
            dataIO.save_json(goodbye_path, self.goodbye)
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = ""
            msg += "**__Random GOODBYE:__** *{}*\n".format(rand_choice(self.goodbye[server.id]["GOODBYE"]))
            msg += "**__CHANNEL:__** *#{}*\n".format(self.get_goodbye_channel(server))
            msg += "**__ON:__** *{}*\n".format(self.goodbye[server.id]["ON"])
            msg += "**__BOTS_MSG:__** *{}*\n".format(self.goodbye[server.id]["BOTS_MSG"])
            msg += "**__BOTS_ROLE:__** *{}*\n".format(self.goodbye[server.id]["BOTS_ROLE"])
            await self.bot.say(msg)

    @goodbyeset.group(pass_context=True, name="msg")
    async def goodbyeset_msg(self, ctx):
        """Manage goodbye messages
        """
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)
            return

    @goodbyeset_msg.command(pass_context=True, name="add", no_pm=True)
    async def goodbyeset_msg_add(self, ctx, *, format_msg):
        """Adds a goodbye message format for the server to be chosen at random

        {0} is user
        {1} is server
        Default is set to:
            Goodbye {0.name}!

        Example formats:
            {0.mention}.. What are you doing here?
            {1.name} has lost a member! {0.name}#{0.discriminator} - {0.id}
            Someone left! OH NO!!!!!!!!!"""
        server = ctx.message.server
        self.goodbye[server.id]["GOODBYE"].append(format_msg)
        dataIO.save_json(goodbye_path, self.goodbye)
        await self.bot.say("Goodbye message added for the server.")
        await self.send_testing_byemsg(ctx, msg=format_msg)

    @goodbyeset_msg.command(pass_context=True, name="del", no_pm=True)
    async def goodbyeset_msg_del(self, ctx):
        """Removes a goodbye message from the random message list
        """
        server = ctx.message.server
        author = ctx.message.author
        msg = '**__Choose a goodbye message to delete:__**\n\n'
        for c, m in enumerate(self.goodbye[server.id]["GOODBYE"]):
            msg += "  **{}.** *{}*\n".format(c, m)
        for page in pagify(msg, ['\n', ' '], shorten_by=20):
            await self.bot.say("{}".format(page))
        answer = await self.bot.wait_for_message(timeout=120, author=author)
        try:
            num = int(answer.content)
            choice = self.goodbye[server.id]["GOODBYE"].pop(num)
        except:
            await self.bot.say("That's not a number in the list :/")
            return
        if not self.goodbye[server.id]["GOODBYE"]:
            self.goodbye[server.id]["GOODBYE"] = [default_goodbye]
        dataIO.save_json(goodbye_path, self.goodbye)
        await self.bot.say("**This message was deleted:**\n{}".format(choice))

    @goodbyeset_msg.command(pass_context=True, name="list", no_pm=True)
    async def goodbyeset_msg_list(self, ctx):
        """Lists the goodbye messages of this server
        """
        server = ctx.message.server
        msg = '**__Goodbye messages:__**\n\n'
        for c, m in enumerate(self.goodbye[server.id]["GOODBYE"]):
            msg += "  **{}.** *{}*\n".format(c, m)
        for page in pagify(msg, ['\n', ' '], shorten_by=20):
            await self.bot.say("{}".format(page))

    @goodbyeset.command(pass_context=True, name="toggle")
    async def goodbyetoggle(self, ctx):
        """Turns on/off saying goodbye to users leaving the server"""
        server = ctx.message.server
        self.goodbye[server.id]["ON"] = not self.goodbye[server.id]["ON"]
        if self.goodbye[server.id]["ON"]:
            await self.bot.say("I will now say goodbye to users leaving the server.")
            await self.send_testing_byemsg(ctx)
        else:
            await self.bot.say("I will no longer say goodbye to leaving users.")
        dataIO.save_json(goodbye_path, self.goodbye)

    @goodbyeset.command(pass_context=True, name="channel")
    async def goodbyechannel(self, ctx, channel : discord.Channel=None):
        """Sets the channel to send the goodbye message

        If channel isn't specified, the server's default channel will be used"""
        server = ctx.message.server
        if channel is None:
            channel = ctx.message.server.default_channel
        if not server.get_member(self.bot.user.id
                                 ).permissions_in(channel).send_messages:
            await self.bot.say("I do not have permissions to send "
                               "messages to {0.mention}".format(channel))
            return
        self.goodbye[server.id]["CHANNEL"] = channel.id
        dataIO.save_json(goodbye_path, self.goodbye)
        channel = self.get_goodbye_channel(server)
        await self.bot.send_message(channel, "I will now send goodbye "
                                    "messages to {0.mention}".format(channel))
        await self.send_testing_byemsg(ctx)

    @goodbyeset.group(pass_context=True, name="bot", no_pm=True)
    async def goodbyeset_bot(self, ctx):
        """Special goodbye for bots"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)
            return

    @goodbyeset_bot.command(pass_context=True, name="msg", no_pm=True)
    async def goodbyeset_bot_msg(self, ctx, *, format_msg=None):
        """Set the goodbye msg for bots.

        Leave blank to reset to regular user welcome"""
        server = ctx.message.server
        self.goodbye[server.id]["BOTS_MSG"] = format_msg
        dataIO.save_json(goodbye_path, self.goodbye)
        if format_msg is None:
            await self.bot.say("Bot message reset. Bots will now have the normal goodbye message.")
        else:
            await self.bot.say("Bot goodbye message set for the server.")
            await self.send_testing_byemsg(ctx, bot=True)


    async def member_leave(self, member):
        server = member.server
        if server.id not in self.goodbye:
            self.goodbye[server.id] = deepcopy(default_goodbyeset)
            self.goodbye[server.id]["CHANNEL"] = server.default_channel.id
            dataIO.save_json(goodbye_path, self.goodbye)
        if not self.goodbye[server.id]["ON"]:
            return
        if server is None:
            print("Server is None. Private Message or some new fangled "
                  "Discord thing?.. Anyways there be an error, "
                  "the user was {}".format(member.name))
            return

        bot_goodbye = member.bot and self.goodbye[server.id]["BOTS_MSG"]
        msg = bot_goodbye or rand_choice(self.goodbye[server.id]["GOODBYE"])

        # grab the welcome channel
        channel = self.get_goodbye_channel(server)
        if channel is None:  # complain even if only whisper
            print('welcome.py: Channel not found. It was most '
                  'likely deleted. User joined: {}'.format(member.name))
            return
        # we can stop here
        if not self.speak_permissions(server):
            print("Permissions Error. User that joined: "
                  "{0.name}".format(member))
            print("Bot doesn't have permissions to send messages to "
                  "{0.name}'s #{1.name} channel".format(server, channel))
            return
        # finally, welcome them
        await self.bot.send_message(channel, msg.format(member, server))

    def get_goodbye_channel(self, server):
        try:
            return server.get_channel(self.goodbye[server.id]["CHANNEL"])
        except:
            return None

    def speak_permissions(self, server):
        channel = self.get_goodbye_channel(server)
        if channel is None:
            return False
        return server.get_member(self.bot.user.id
                                 ).permissions_in(channel).send_messages

    async def send_testing_byemsg(self, ctx, bot=False, msg=None):
        server = ctx.message.server
        channel = self.get_goodbye_channel(server)
        rand_msg = msg or rand_choice(self.goodbye[server.id]["GOODBYE"])
        if channel is None:
            await self.bot.send_message(ctx.message.channel,
                                        "I can't find the specified channel. "
                                        "It might have been deleted.")
            return
        await self.bot.send_message(ctx.message.channel,
                                    "`Sending a testing message to "
                                    "`{0.mention}".format(channel))
        if self.speak_permissions(server):
            msg = self.settings[server.id]["BOTS_MSG"] if bot else rand_msg
            if bot is not True:
                await self.bot.send_message(channel,
                        msg.format(ctx.message.author, server))
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "I do not have permissions "
                                        "to send messages to "
                                        "{0.mention}".format(channel))


def check_folders():
    if not os.path.exists("data/welcome"):
        print("Creating data/welcome folder...")
        os.makedirs("data/welcome")


def check_files():
    f = settings_path
    if not dataIO.is_valid_json(f):
        print("Creating welcome settings.json...")
        dataIO.save_json(f, {})
    else:  # consistency check
        current = dataIO.load_json(f)
        for k, v in current.items():
            if v.keys() != default_settings.keys():
                for key in default_settings.keys():
                    if key not in v.keys():
                        current[k][key] = deepcopy(default_settings)[key]
                        print("Adding " + str(key) +
                              " field to welcome settings.json")
        # upgrade. Before GREETING was 1 string
        for server in current.values():
            if isinstance(server["GREETING"], str):
                server["GREETING"] = [server["GREETING"]]
        dataIO.save_json(f, current)


def setup(bot):
    check_folders()
    check_files()
    n = Welcome(bot)
    bot.add_listener(n.member_join, "on_member_join")
    bot.add_listener(n.member_leave, "on_member_remove")
    bot.add_cog(n)
