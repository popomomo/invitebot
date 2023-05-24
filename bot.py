from keep_alive import keep_alive
import discord
from discord.ext import commands
import os
import json
import asyncio
import datetime
import traceback
import sys
import io
import aiohttp

keep_alive()

with open("main-config.json", "r") as mc:
    config = json.load(mc)
    token = os.environ['DiscordToken']
    logFile = config["LogFile"]
    delinvos = config["DeleteOwnerCommandsInvos"]

def get_prefix(cl, message):
    try:
        with open(f"configs/{message.guild.id}.json", "r") as gc:
            guild_config = json.load(gc)
            prefix = guild_config["General"]["Prefix"]
    except:
        prefix = config["Prefix"]

    return [f"<@{cl.user.id}> ", prefix]

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = get_prefix, intents = intents)
client.remove_command("help")

@client.event
async def on_ready():
    ascii_art = """
  _   _              _____            _           _
 | \ | |            |_   _|          | |         | |
 |  \| | _____   __   | |  _ ____   _| |__   ___ | |_
 | . ` |/ _ \ \ / /   | | | '_ \ \ / / '_ \ / _ \| __|
 | |\  |  __/\ V /   _| |_| | | \ V /| |_) | (_) | |_
 |_| \_|\___| \_/   |_____|_| |_|\_/ |_.__/ \___/ \__|

    """
    print(f"\033[34m{ascii_art}\033[0m\nThanks for using my bot! If you like it, consider supporting me on kofi - https://ko-fi.com/nevalicjus")
    log("Invitebot started")
    loaded_cogs = await loadall()
    log(f"Cogs named: {loaded_cogs} were loaded")
    client.loop.create_task(status_task())
    log("Status service started")
    log("Invitebot ready")

@client.command()
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} was loaded")
    log(f"{extension} was loaded")

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} was unloaded")
    log(f"{extension} was unloaded")

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    if extension == "all":
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                client.unload_extension(f"cogs.{filename[:-3]}")
                client.load_extension(f"cogs.{filename[:-3]}")
                await ctx.send(f"{filename[:-3]} was reloaded")
                log(f"{filename[:-3]} was reloaded")
    else:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"{extension} was reloaded")
        log(f"{extension} was reloaded")

async def loadall():
    loaded_cogs = ""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")
            loaded_cogs += f"{filename[:-3]} "
    return loaded_cogs[:-1]

def log(log_msg: str):
    print(f"[{datetime.datetime.now()}] [\033[1;31mINTERNAL\033[0;0m]: {log_msg}")
    with open(f"{logFile}", "a") as lf:
        lf.write(f"[{datetime.datetime.now()}] [INTERNAL]: {log_msg}\n")

async def status_task():
    while True:
        members = 0
        try:
            for guild in client.guilds:
                members += guild.member_count
            await client.change_presence(status = discord.Status.online, activity = discord.Activity(type = discord.ActivityType.playing, name = f"on {len(client.guilds)} guilds with {members} members"))
            await asyncio.sleep(30)
            await client.change_presence(status = discord.Status.online, activity = discord.Activity(type = discord.ActivityType.playing, name = "i!help"))
            await asyncio.sleep(30)
        except:
            pass

        
WHEN = datetime.time(3, 0, 0)  # 6:00 PM
channel_id = 829651715502374982 # Put your channel id here
channel_id2 = 936297277679611985 # CWC channel

async def called_once_a_day():  # Fired every day
    await client.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
    channel = client.get_channel(channel_id) # Note: It's more efficient to do bot.get_guild(guild_id).get_channel(channel_id) as there's less looping involved, but just get_channel still works fine
    
    fngUrl = "https://alternative.me/crypto/fear-and-greed-index.png"
    async with aiohttp.ClientSession() as session:
      async with session.get(fngUrl) as resp:
          if resp.status != 200:
              return await channel.send('Could not download file...')
          data = io.BytesIO(await resp.read())
          await channel.send(file=discord.File(data, 'fear-and-greed-index.png'))

async def called_once_a_day2():  # Fired every day
    await client.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
    channel2 = client.get_channel(channel_id2)
    
    fngUrl2 = "https://alternative.me/crypto/fear-and-greed-index.png"
    async with aiohttp.ClientSession() as session:
      async with session.get(fngUrl2) as resp:
          if resp.status != 200:
              return await channel2.send('Could not download file...')
          data = io.BytesIO(await resp.read())
          await channel2.send(file=discord.File(data, 'fear-and-greed-index.png'))

async def background_task():
    now = datetime.datetime.utcnow()
    if now.time() > WHEN:  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
        tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
    while True:
        now = datetime.datetime.utcnow() # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
        target_time = datetime.datetime.combine(now.date(), WHEN)  # 6:00 PM today (In UTC)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
        await called_once_a_day()  # Call the helper function that sends the message
        await called_once_a_day2()
        tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start a new iteration

client.loop.create_task(background_task())

client.run(token)
