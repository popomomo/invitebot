import discord
import os
from discord.ext import commands
import json
import datetime
intents = discord.Intents.default()
intents.members = True

with open('config.json', 'r') as f:
    config = json.load(f)
    prefix = config['Prefix']
    token = config['DiscordToken']
    logfile = config['LogFile']

client = commands.Bot(command_prefix=prefix, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="inv!help | https://discord.gg/wsEU32a3ke"))
    log(f"InviteBot ready")

@client.command(help="Loads a cog.")
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} was loaded')
    log(f'{extension} was loaded')

    #deleting invo
    if delinvos == True:
        await ctx.message.delete(delay=5)


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
    if delinvos == True:
        await ctx.message.delete(delay=5)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

def log(string: str):
    print(f"[{datetime.datetime.now()}] : " + string)
    with open(logfile, 'a') as f:
        f.write(f"[{datetime.datetime.now()}] : " + string + "\n")

client.run(token)
