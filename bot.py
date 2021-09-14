from keep_alive import keep_alive
import discord
import os
from discord.ext import commands
import json
import asyncio
import datetime
import traceback
import sys
import io
import aiohttp
intents = discord.Intents.default()
intents.members = True

keep_alive()

with open('main-config.json', 'r') as f:
    config = json.load(f)
    prefix = config['Prefix']
    token = os.environ['DiscordToken']
    logfile = config['LogFile']
    delinvos = config['DeleteOwnerCommandsInvos']

def get_prefix(client, message):
    try:
        with open(f'configs/{message.guild.id}.json', 'r') as f:
            config = json.load(f)
            prefix = config['General']['Prefix']
    except:
        prefix = "i!"

    return prefix

client = commands.Bot(command_prefix = get_prefix, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    ascii = """
  _   _              _____            ____        _
 | \ | |            |_   _|          |  _ \      | |
 |  \| | _____   __   | |  _ ____   _| |_) | ___ | |_
 | . ` |/ _ \ \ / /   | | | '_ \ \ / /  _ < / _ \| __|
 | |\  |  __/\ V /   _| |_| | | \ V /| |_) | (_) | |_
 |_| \_|\___| \_/   |_____|_| |_|\_/ |____/ \___/ \__|

    """
    print(f"\033[34m{ascii}\033[0m")
    log("InviteBot started")
    loaded_cogs = await loadall()
    log(f"Cogs named: {loaded_cogs} were loaded")
    client.loop.create_task(status_task())
    log("Status service started")
    log(f"InviteBot ready")

@client.command(help="Loads a cog.")
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} was loaded')
    log(f'{extension} was loaded')

@client.command(help="Unloads a cog.")
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} was unloaded')
    log(f'{extension} was unloaded')

    #deleting invo
    if delinvos == True:
        await ctx.message.delete(delay=5)

@client.command(help="Reloads a cog")
@commands.is_owner()
async def reload(ctx, extension):
    if extension == "all":
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                client.unload_extension(f'cogs.{filename[:-3]}')
                client.load_extension(f'cogs.{filename[:-3]}')
                await ctx.send(f'{filename[:-3]} was reloaded')
                log(f'{filename[:-3]} was reloaded')
    else:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} was reloaded')
        log(f'{extension} was reloaded')
    #deleting invo
    if delinvos == 1:
        await ctx.message.delete(delay=5)

async def loadall():
    loaded_cogs = ""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            loaded_cogs += f"{filename[:-3]} "
    return loaded_cogs

def log(log_msg: str):
    print(f"[{datetime.datetime.now()}] [\033[1;31mINTERNAL\033[0;0m]: " + log_msg)
    with open('log.txt', 'a') as f:
        f.write(f"[{datetime.datetime.now()}] [INTERNAL]: " + log_msg + "\n")

async def status_task():
    while True:
        members = 0
        try:
            for guild in client.guilds:
                members += guild.member_count
            await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=f"on {len(client.guilds)} guilds with {members} members"))
            await asyncio.sleep(30)
            await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="i!help | https://invitebot.xyz"))
            await asyncio.sleep(30)
        except:
            pass
        
WHEN = datetime.time(3, 0, 0)  # 6:00 PM
channel_id = 829651715502374982 # Put your channel id here

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
        tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start a new iteration

client.loop.create_task(background_task())

client.run(token)
