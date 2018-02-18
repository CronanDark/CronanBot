import discord
from discord.ext import commands
import os
import sys
import shutil
from .utils import checks

class Chatter:
    """Chatter cog: talk as your bot using the console."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def chatter(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @chatter.command(pass_context=True)
    @checks.is_owner()
    async def here(self, ctx):
        """Start talk mode to send messages to the current channel as your bot via the console.

           Console commands:
           ~~exit to exit this mode
           ~~switch to start sending messages to another channel. Only lets you send 1 message in the channel you specify using this command.

           Errors:
           HTTPException (discord.HTTPException): either you tried to send an empty message or something messed up
           Forbidden (discord.Forbidden): Your bot does not have the permission to delete messages.
           Other: not really sure
        """
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            await self.bot.say("Not allowed to delete messages.")
        except discord.HTTPException:
            await self.bot.say("Failed to delete message.")
        except:
            await self.bot.say("Unknown error encountered, failed to delete message.")
        while True:
            print("Message to say: ")
            hereInput = input("")

            if hereInput == "~~exit":
                break
            elif hereInput == "~~switch":
                toChannel = input("ID of channel to switch to: ")
                toInput = input("Message to say: ")
                getChannelObj = self.bot.get_channel(toChannel)
                await self.bot.send_message(getChannelObj, toInput)
            elif hereInput is not None:
                await self.bot.say(hereInput)

    @chatter.command(pass_context=True)
    @checks.is_owner()
    async def overthere(self, ctx, *, channelid: str):
        """Start talk mode in another channel, must specify the channel ID.

           Console commands:
           ~~exit - Exits talk mode
           ~~switch - Switches channel you are talking in, only lets you send 1 message in the channel you specify with this command.

           Errors:
           HTTPException (discord.HTTPException): either you tried to send an empty message or something messed up
           Forbidden (discord.Forbidden): The bot does not have permissions to delete messages.
           Other: not really sure
        """
        if channelid is None:
            await self.bot.say("Please specify a channel ID.")
        else:
            pass
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            await self.bot.say("No permissions, cannot delete message.")
        except discord.HTTPException:
            await self.bot.say("Failed to delete message.")
        except:
            await self.bot.say("Failed to delete message.")
        while True:
            sendMessage = input("Message to send to channel " + channelid + ": ")
            if sendMessage == "~~exit":
                break
            elif sendMessage == "~~switch":
                switchTo = input("ID of channel to switch to: ")
                inputToSwitch = input("Message to say: ")
                getObjChannel = self.bot.get_channel(switchTo)
                await self.bot.send_message(getObjChannel, inputToSwitch)
            elif sendMessage is not None:
                channelObj = self.bot.get_channel(channelid)
                await self.bot.send_message(channelObj, sendMessage)


def setup(bot):
    n = Chatter(bot)
    bot.add_cog(n)
            

