import discord
import os
from discord.ext import commands
import json
import asyncio
import datetime
import traceback
import sys
intents = discord.Intents.default()
intents.members = True

class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

# old
#    @commands.Cog.listener()
#    #------------------------------
#    # Create config file for guild on guild join
#    #------------------------------
#    async def on_guild_join(self, guild):
#        self.log(guild.id, f"Joined new guild - {guild.name} [{guild.id}]")
#        braces = "{}"
#        #creates config file
#        os.system(f"touch configs/{guild.id}.json && echo {braces} > configs/{guild.id}.json")
#        await asyncio.sleep(5)
#        try:
#            with open(f'configs/{guild.id}.json', 'r') as f:
#                config = json.load(f)
#        except FileNotFoundError:
#            self.log(0, f"Config for guild {guild.name}[{guild.id}] couldn't be created.")
#
#        #creates config data
#        config['General'] = {}
#        config['Invites'] = {}
#
#        config['General']['DeleteInvocations'] = 0
#        config['General']['AdminRoles'] = []
#        config['General']['ServerLog'] = 0
#        config['General']['Prefix'] = "i!"
#        config['General']['WelcomeMessage'] = "None"
#
#        for invite in await guild.invites():
#            config['Invites'][f'{invite.code}'] = {}
#            config['Invites'][f'{invite.code}']['name'] = "None"
#            config['Invites'][f'{invite.code}']['roles'] = []
#            config['Invites'][f'{invite.code}']['uses'] = invite.uses
#            config['Invites'][f'{invite.code}']['welcome'] = "None"
#
#        with open(f'configs/{guild.id}.json', 'w') as f:
#            json.dump(config, f, indent = 4)

    @commands.Cog.listener()
    #------------------------------
    # Create config file for guild on guild join
    #------------------------------
    async def on_guild_join(self, guild):
        self.log(guild.id, f"Joined new guild - {guild.name} [{guild.id}]")

        config = {}
        config["General"] = {}
        config["General"]["DeleteInvocations"] = 0
        config["General"]["AdminRoles"] = []
        config["General"]["ServerLog"] = 0
        config["General"]["Prefix"] = "i!"
        config["General"]["WelcomeMessage"] = "None"
        config["General"]["Analytics"] = False
        config["General"]["AnalyticsLog"] = 0

        config["Invites"] = {}

        #creates invites data
        for invite in await guild.invites():
            config["Invites"][f"{invite.code}"] = {}
            config["Invites"][f"{invite.code}"]["name"] = "None"
            config["Invites"][f"{invite.code}"]["roles"] = []
            config["Invites"][f"{invite.code}"]["uses"] = invite.uses
            config["Invites"][f"{invite.code}"]["welcome"] = "None"
            config["Invites"][f"{invite.code}"]["tags"] = {}

        with open(f"configs/{guild.id}.json", 'w') as f:
            json.dump(config, f, indent = 4)

        if f"{guild.id}.json" not in os.listdir("users/"):
            users_blank = {}
            with open(f"users/{guild.id}.json", 'w') as f:
                json.dump(users_blank, f, indent = 4)

    @commands.Cog.listener()
    #------------------------------
    # Delete the config file when leaving guild
    #------------------------------
    async def on_guild_remove(self, guild):
        self.log(guild.id, f"Left guild - {guild.name} [{guild.id}]")

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')
        if str(guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {guild.id}')

        #saves config
        savefp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        os.system(f'cp {os.getenv("PWD")}/configs/{guild.id}.json {os.getenv("PWD")}/saved-configs/{guild.id}/{savefp}.json')

        #removes config file on guild leave
        os.system(f"rm configs/{guild.id}.json")

    @commands.command(aliases = ['savecnfg', 'sconf'])
    #------------------------------
    # Saves the current config
    #------------------------------
    async def saveconfig(self, ctx):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')
        if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')

        with open(f'main-config.json', 'r') as f:
            config = json.load(f)

        if len(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}')) >= config['MaxSavedConfigs']:
            embed = self.constructResponseEmbedBase(f"Saved Config couldn't be created, Max Saved Configurations number: {config['MaxSavedConfigs']} reached.")
            await ctx.send(embed = embed)
            return

        savefp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        os.system(f'cp {os.getenv("PWD")}/configs/{ctx.guild.id}.json {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{savefp}.json')

        await self.serverLog(ctx.guild.id, "cnfg_save", "Saved Config was created, at {0} by {1}[`{2}`]".format(datetime.datetime.now().strftime('%H:%M:%S | %d/%m/%Y'), ctx.author, ctx.author.id))
        embed = self.constructResponseEmbedBase(f"Your Saved Config was created, at {datetime.datetime.now().strftime('%H:%M:%S | %d/%m/%Y')}")
        await ctx.send(embed = embed)

    @commands.command(aliases = ['lscnfgs', 'lsconf'])
    #------------------------------
    # Lists Saved Configs
    #------------------------------
    async def listconfigs(self, ctx, specific: int = -1):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        if specific not in [-1, 0]:
            guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')

            if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
                os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')
                embed = self.constructResponseEmbedBase(f"You had no configurations saved")
                await ctx.send(embed = embed)
                return

            guilds_configs = sorted(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/'), reverse=True)
            fetched_config = guilds_configs[specific - 1]

            with open(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{fetched_config}', 'r') as f:
                saved_config = json.load(f)

            embed = discord.Embed(title = f"**Saved Config\n{fetched_config[17:19]}:{fetched_config[14:16]}:{fetched_config[11:13]} | {fetched_config[8:10]}/{fetched_config[5:7]}/{fetched_config[0:4]}**", color = discord.Colour.from_rgb(119, 137, 218))
            embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
            embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Invitebot made with \u2764\ufe0f by Nevalicjus")

            for setting in saved_config['General']:
                embed.add_field(name = f"{setting}:", value = f"{saved_config['General'][setting]}", inline = False)

            await ctx.send(embed = embed)

            embed = discord.Embed(title = f"**Saved Config's Invites\n{fetched_config[17:19]}:{fetched_config[14:16]}:{fetched_config[11:13]} | {fetched_config[8:10]}/{fetched_config[5:7]}/{fetched_config[0:4]}**", color = discord.Colour.from_rgb(119, 137, 218))
            embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
            embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Invitebot made with \u2764\ufe0f by Nevalicjus")

            no_fields = 0
            for inv in saved_config['Invites']:
                about = ''
                for invrole in saved_config['Invites'][f"{inv}"]["roles"]:
                    try:
                        role = ctx.guild.get_role(invrole)
                        about += f"{role.name}\n"
                    except:
                        about += f"ErrorFetchingRole\n"
                about += f"Uses - {saved_config['Invites'][inv]['uses']}\n"
                if about != '':
                    if saved_config['Invites'][f'{inv}']['name'] != "None":
                        embed.add_field(name = f"{saved_config['Invites'][inv]['name']}", value = about, inline = True)
                    else:
                        embed.add_field(name = f"https://discord.gg/{inv}", value = about, inline = True)
                    no_fields +=1
                if no_fields == 25:
                    await ctx.send(embed = embed)
                    no_fields = 0
                    for i in range(25):
                        embed.remove_field(0)
            if no_fields != 0:
                await ctx.send(embed = embed)

            return

        if specific == 0:

            with open(f'{os.getenv("PWD")}/configs/{ctx.guild.id}.json', 'r') as f:
                config = json.load(f)

            embed = discord.Embed(title = f"**Current Config**", color = discord.Colour.from_rgb(119, 137, 218))
            embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
            embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Invitebot made with \u2764\ufe0f by Nevalicjus")

            for setting in config['General']:
                embed.add_field(name = f"{setting}:", value = f"{config['General'][setting]}", inline = False)

            await ctx.send(embed = embed)

            embed = discord.Embed(title = f"**Current Config's Invites**", color = discord.Colour.from_rgb(119, 137, 218))
            embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
            embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Invitebot made with \u2764\ufe0f by Nevalicjus")

            no_fields = 0
            for inv in config['Invites']:
                about = ''
                for invrole in config['Invites'][f"{inv}"]["roles"]:
                    role = ctx.guild.get_role(invrole)
                    about += f"{role.name}\n"
                about += f"Uses - {config['Invites'][inv]['uses']}\n"
                if about != '':
                    if config['Invites'][f'{inv}']['name'] != "None":
                        embed.add_field(name = f"{config['Invites'][inv]['name']}", value = about, inline = True)
                    else:
                        embed.add_field(name = f"https://discord.gg/{inv}", value = about, inline = True)
                    no_fields +=1
                if no_fields == 25:
                    await ctx.send(embed = embed)
                    no_fields = 0
                    for i in range(25):
                        embed.remove_field(0)
            if no_fields != 0:
                await ctx.send(embed = embed)

            return

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')

        if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')

        embed = discord.Embed(title = f"**Saved Configs**", color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
        embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Invitebot made with \u2764\ufe0f by Nevalicjus")
        embed.add_field(name = f"Config 0", value = f"Currently used Config", inline = False)

        i = 0
        for config in sorted(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/'), reverse=True):
            i += 1
            config_name: str = config
            embed.add_field(name = f"Config {i} saved on:", value = f"{config_name[11:13]}:{config_name[14:16]}:{config_name[17:19]} | {config_name[8:10]}/{config_name[5:7]}/{config_name[0:4]}", inline = False)

        await ctx.send(embed = embed)

    @commands.command(aliases = ['removeconfig', 'delcnfg', 'delconf', 'remconf'])
    #------------------------------
    # Deletes a Saved Config
    #------------------------------
    async def deleteconfig(self, ctx, target_config: int = 0):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        if target_config == 0:
            embed = self.constructResponseEmbedBase(f"You didn't pick any config to delete. To view configs use `i!lscnfgs`")
            await ctx.send(embed = embed)
            return

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')

        if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')
            embed = self.constructResponseEmbedBase(f"You had no configurations saved")
            await ctx.send(embed = embed)
            return

        guilds_configs = sorted(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/'), reverse=True)

        try:
            os.system(f'rm {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{guilds_configs[target_config - 1]}')
            await self.serverLog(ctx.guild.id, "cnfg_del", "Saved Config {0} was deleted by {1}[`{2}`]".format(guilds_configs[target_config - 1], ctx.author, ctx.author.id))
            embed = self.constructResponseEmbedBase(f"Saved Config {guilds_configs[target_config - 1]} was successfully deleted")
            await ctx.send(embed = embed)
            return

        except FileNotFoundError:
            embed = self.constructResponseEmbedBase(f"No Saved Config from this date exists")
            await ctx.send(embed = embed)
            return

    @commands.command(aliases = ['switchcnfg', 'switchconf'])
    #------------------------------
    # Switch the chosen config with the current one
    #------------------------------
    async def switchconfig(self, ctx, target_config: int = 0):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        if target_config == 0:
            embed = self.constructResponseEmbedBase(f"You didn't pick any config to switch. To view configs use `i!lscnfgs`")
            await ctx.send(embed = embed)
            return

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')

        if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')
            embed = self.constructResponseEmbedBase(f"You had no configurations saved")
            await ctx.send(embed = embed)
            return

        guilds_configs = sorted(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/'), reverse=True)

        savefp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        os.system(f'cp {os.getenv("PWD")}/configs/{ctx.guild.id}.json {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{savefp}.json && chmod +r {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{savefp}.json')

        os.system(f'mv {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{guilds_configs[target_config - 1]} {os.getenv("PWD")}/configs/{ctx.guild.id}.json')

        await self.serverLog(ctx.guild.id, "cnfg_switch", "{0}[`{1}`], switched current config for the one created on:\n{2}:{3}:{4} | {5}/{6}/{7}, and the previous config was saved".format(ctx.message.author, ctx.message.author.id, guilds_configs[target_config - 1][11:13], guilds_configs[target_config - 1][14:16], guilds_configs[target_config - 1][17:19], guilds_configs[target_config - 1][8:10], guilds_configs[target_config - 1][5:7], guilds_configs[target_config - 1][0:4]))
        embed = self.constructResponseEmbedBase(f"Your Current Config was switched, for the one created on:\n{guilds_configs[target_config - 1][11:13]}:{guilds_configs[target_config - 1][14:16]}:{guilds_configs[target_config - 1][17:19]} | {guilds_configs[target_config - 1][8:10]}/{guilds_configs[target_config - 1][5:7]}/{guilds_configs[target_config - 1][0:4]},\n and previous Current Config was saved")
        await ctx.send(embed = embed)

    @commands.command()
    #------------------------------
    # Add role.id to adminroles for permission verification
    #------------------------------
    async def addmod(self, ctx, role: discord.Role):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        admin_roles = config['General']['AdminRoles']

        if role.id in admin_roles:
            embed = self.constructResponseEmbedBase("This role was already an admin role")
            await ctx.send(embed = embed)

        admin_roles.append(role.id)
        config['General']['AdminRoles'] = admin_roles
        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)
        embed = self.constructResponseEmbedBase(f"Added role {role.name} as an admin role")
        await ctx.send(embed = embed)
        await self.serverLog(ctx.guild.id, "mod_added", "Admin role <@{0}> added".format(role.id))

    @addmod.error
    async def addmod_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "role":
                await ctx.send("Your command is missing a required argument: a valid Discord role (Role meention or Role ID)")
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("Role you are trying to mention or provide ID of doesn't exist")

        #await self.errorLog()

    @commands.command()
    #------------------------------
    # Remove role.id from adminrole for no further permission verification
    #------------------------------
    async def delmod(self, ctx, role: discord.Role):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        admin_roles = config['General']['AdminRoles']

        if role.id not in admin_roles:
            embed = self.constructResponseEmbedBase("This role wasn't an admin role")
            await ctx.send(embed = embed)

        admin_roles.remove(role.id)
        config['General']['AdminRoles'] = admin_roles
        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)
        embed = self.constructResponseEmbedBase(f"Removed role {role.name} as an admin role")
        await ctx.send(embed = embed)
        await self.serverLog(ctx.guild.id, "mod_deleted", "Admin role <@{0}> removed".format(role.id))

    @delmod.error
    async def delmod_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "role":
                await ctx.send("Your command is missing a required argument: a valid Discord role (Role meention or Role ID)")
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("Role you are trying to mention or provide ID of doesn't exist")

    @commands.command(aliases = ['elog'])
    #------------------------------
    # Enable server logging
    #------------------------------
    async def enablelog(self, ctx, channel: discord.TextChannel):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        config['General']['ServerLog'] = channel.id
        await ctx.send(f"Enabled log on channel {channel}")
        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

    @enablelog.error
    async def enablelog_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "channel":
                await ctx.send("Your command is missing a required argument: a valid channel (Channel mention or Channel ID)")
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send("Channel you are trying to mention or provide ID of doesn't exist")

    @commands.command(aliases = ['dlog'])
    #------------------------------
    # Disable server logging
    #------------------------------
    async def disablelog(self, ctx):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        config['General']['ServerLog'] = 0
        await ctx.send(f"Disabled log")
        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

    @commands.command()
    #------------------------------
    # Change deletion-o-invocations setting
    #------------------------------
    async def delinvos(self, ctx, choice):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        if choice in ["true", "yes", "y", "allow", "enable", "1"]:
            choice = 1
        if choice in ["false", "no", "n", "deny", "disable", "0"]:
            choice = 0
        if choice not in [0, 1]:
            embed = self.constructResponseEmbedBase("This is not a valid input")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        config['General']['DeleteInvocations'] = choice
        if choice == 1:
            embed = self.constructResponseEmbedBase("You've successfully enabled Invocation Deletion")
            await ctx.send(embed = embed)
            await self.serverLog(ctx.guild.id, "delinvos", f"Invocation Deletion has been enabled")
        if choice == 0:
            embed = self.constructResponseEmbedBase("You've successfully disabled Invocation Deletion")
            await ctx.send(embed = embed)
            await self.serverLog(ctx.guild.id, "delinvos", f"Invocation Deletion has been disabled")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

    @delinvos.error
    async def make_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "choice":
                await ctx.send("Please provide an option for the setting (yes/no)")

    @commands.command()
    async def analytics(self, ctx, choice):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        if choice in ["true", "yes", "y", "allow", "enable", "1"]:
            choice = True
        if choice in ["false", "no", "n", "deny", "disable", "0"]:
            choice = False
        if choice not in [True, False]:
            embed = self.constructResponseEmbedBase("This is not a valid input")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        config['General']['Analytics'] = choice

        if choice == True:
            embed = self.constructResponseEmbedBase("You've successfully enabled Invite Analytics")
            await ctx.send(embed = embed)
            await self.serverLog(ctx.guild.id, "delinvos", f"Invite Analytics has been enabled")
        if choice == False:
            embed = self.constructResponseEmbedBase("You've successfully disabled Invite Analytics")
            await ctx.send(embed = embed)
            await self.serverLog(ctx.guild.id, "delinvos", f"Invite Analytics has been disabled")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

    @analytics.error
    async def analytics_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "choice":
                await ctx.send("Please provide an option for the setting (yes/no)")

    @commands.command()
    async def analyticslog(self, ctx, channel: discord.TextChannel = "None"):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        if channel == "None":
            config['General']['AnalyticsLog'] = 0
            await ctx.send(f"Disabled Invite Analytics log on channel {channel}")
        else:
            config['General']['AnalyticsLog'] = channel.id
            await ctx.send(f"Enabled Invite Analytics log on channel {channel}")
        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

    @analyticslog.error
    async def analyticslog_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "channel":
                await ctx.send("Your command is missing a required argument: a valid channel (Channel mention or Channel ID)")
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send("Channel you are trying to mention or provide ID of doesn't exist")

    @commands.command()
    async def analyticsuser(self, ctx, inviter: discord.Member):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        with open(f"users/{ctx.guild.id}.json", 'r') as f:
            users = json.load(f)

        if f"{inviter.id}" in list(users.keys()):
            numofinvitedby = users[f"{inviter.id}"]

            flex = "people"
            if numofinvitedby == 1:
                flex = "person"
            embed = self.constructResponseEmbedBase(f"{inviter.mention} has invited {numofinvitedby} {flex} 🎉")
        else:
            embed = self.constructResponseEmbedBase(f"{inviter.mention} hans't invited anyone yet")

        await ctx.send(embed = embed)

    @analyticsuser.error
    async def analyticsuser_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "inviter":
                await ctx.send("Your command is missing a required argument: a valid user (User mention or User ID)")
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("User you are trying to mention or provide ID of doesn't exist")
        if isinstance(error, commands.UserNotFound):
            await ctx.send("User you are trying to mention or provide ID of doesn't exist")

    @commands.command()
    #------------------------------
    # Change bot's server-prefix
    #------------------------------
    async def prefix(self, ctx, new_prefix: str = "None"):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        if new_prefix == "None":
            embed = self.constructResponseEmbedBase(f"Your current prefix is `{config['General']['Prefix']}`")
            await ctx.send(embed = embed)
            return


        config['General']['Prefix'] = new_prefix

        embed = self.constructResponseEmbedBase(f"You've successfully changed the prefix to `{new_prefix}`")
        await ctx.send(embed = embed)
        await self.serverLog(ctx.guild.id, "prefix_change", f"Prefix was changed to {new_prefix}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

    #@commands.Cog.listener()
    #------------------------------
    # Reset the server's prefix to original if you don't remember it
    #------------------------------
    #async def on_message(self, message):
    #    if str(message.mentions[0]) == "Invitebot#9675":
    #        if message.author.id != message.guild.owner_id:
    #            embed = self.constructResponseEmbedBase("You are not the server owner")
    #            await message.channel.send(embed = embed)
    #            return
    #
    #        with open(f'configs/{message.guild.id}.json', 'r') as f:
    #            config = json.load(f)
    #
    #        config['General']['Prefix'] = "i!"
    #
    #        embed = self.constructResponseEmbedBase(f"You've successfully changed the prefix back to `i!`")
    #        await message.channel.send(embed = embed)
    #
    #        with open(f'configs/{message.guild.id}.json', 'w') as f:
    #            json.dump(config, f, indent = 4)
    #    else:
    #        return

    @commands.command(aliases = ['h'])
    #------------------------------
    # Request help
    #------------------------------
    async def help(self, ctx):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        failsafe = 0

        embed = discord.Embed(title = f"**Invitebot Help**", color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
        now = datetime.datetime.now()
        embed.set_footer(text = f"Support Server - https://invitebot.xyz/support | Invitebot made with \u2764\ufe0f by Nevalicjus")

        if self.checkPerms(ctx.author.id, ctx.guild.id) == False:
            embed.add_field(name = "i!**invite**", value = "Sends you the bot invite", inline = False)
            embed.add_field(name = "i!**info**", value = "Sends you the bot's information", inline = False)
            await ctx.send(embed = embed)
            return

        elif ctx.message.author.id == ctx.guild.owner_id:
            embed.add_field(name = "i!**add <invite> @role**", value = "Aliases - inva\nAdds a link between <invite> and @role", inline = False)
            embed.add_field(name = "i!**remove <invite> (@role)**", value = "Aliases - invrem, invr\nRemoves a link between <invite> and @role or removes all invite-roles links on the invite if no role is specified", inline = False)
            embed.add_field(name = "i!**list**", value = "Aliases - invlist, invls\nLists all invite-role links for the current server", inline = False)
            embed.add_field(name = "i!**make #channel (name) (@role) (<max_uses>) (<max_age>)**", value = "Aliases - invm\nCreates an invite for #channel and instantly adds a link to @role for it. If <max_uses> and <max_age> are specified, the invite will be created with them in mind", inline = False)
            embed.add_field(name = "i!**delete <delete>**", value = "Aliases - invdel, invd\nDeletes <invite>", inline = False)
            embed.add_field(name = "**----------**", value = "**----------**", inline = False)
            embed.add_field(name = "i!**addmod @role**", value = "**Only for Server Owner**\nAdds @role to Admin Roles", inline = False)
            embed.add_field(name = "i!**delmod @role**", value = "**Only for Server Owner**\nRemoves @role from Admin Roles", inline = False)
            embed.add_field(name = "i!**delinvos y/n**", value = "Enables or disables Invocation Deletion.\nAcceptable input:\nyes/no, y/n, true/false, allow/deny, enable/disable, 1/0", inline = False)
            embed.add_field(name = "i!**enablelog #channel**", value = "**Only for Server Owner**\nAliases - elog\nEnables log on #channel", inline = False)
            embed.add_field(name = "i!**disablelog**", value = "**Only for Server Owner**\nAliases - dlog\nDisables log", inline = False)
            embed.add_field(name = "**----------**", value = "**----------**", inline = False)
            embed.add_field(name = "i!**saveconfig**", value = "**Only for Server Owner**\nAliases - savecnfg, sconf\nSaves current full-server config to saved configs", inline = False)
            embed.add_field(name = "i!**listconfigs**", value = "**Only for Server Owner**\nAliases - lscnfgs, lsconf\nLists your saved configs", inline = False)
            embed.add_field(name = "i!**deleteconfig**", value = "**Only for Server Owner**\nAliases - removeconfig, delcnfg, delconf, remconf\nDeletes a saved config", inline = False)
            embed.add_field(name = "i!**switchconfig**", value = "**Only for Server Owner**\nAliases - switchcnfg, switchconf\nLoads a saved config in place of the current one, after saving the currently used config", inline = False)
            embed.add_field(name = "**----------**", value = "**----------**", inline = False)
            embed.add_field(name = "i!**invite**", value = "Sends you the bot invite", inline = False)
            embed.add_field(name = "i!**info**", value = "Sends you the bot's information", inline = False)
            await ctx.send(embed = embed)
            return

        else:
            embed.add_field(name = "i!**add <invite> @role**", value = "Aliases - inva\nAdds a link between <invite> and @role", inline = False)
            embed.add_field(name = "i!**remove <invite> (@role)**", value = "Aliases - invrem, invr\nRemoves a link between <invite> and @role or removes all invite-roles links on the invite if no role is specified", inline = False)
            embed.add_field(name = "i!**list**", value = "Aliases - invlist, invls\nLists all invite-role links for the current server", inline = False)
            embed.add_field(name = "i!**make #channel (name) (@role) (<max_uses>) (<max_age>)**", value = "Aliases - invm\nCreates an invite for #channel and instantly adds a link to @role for it. If <max_uses> and <max_age> are specified, the invite will be created with them in mind", inline = False)
            embed.add_field(name = "i!**delete <delete>**", value = "Aliases - invdel, invd\nDeletes <invite>", inline = False)
            embed.add_field(name = "**----------**", value = "**----------**", inline = False)
            embed.add_field(name = "i!**delinvos y/n**", value = "Enables or disables Invocation Deletion.\nAcceptable input:\nyes/no, y/n, true/false, allow/deny, enable/disable, 1/0", inline = False)
            embed.add_field(name = "**----------**", value = "**----------**", inline = False)
            embed.add_field(name = "i!**invite**", value = "Sends you the bot invite", inline = False)
            embed.add_field(name = "i!**info**", value = "Sends you the bot's information", inline = False)
            await ctx.send(embed = embed)

    @commands.command()
    #------------------------------
    # Get info
    #------------------------------
    async def info(self, ctx):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        embed = discord.Embed(title = f"**Invitebot Help**", color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
        now = datetime.datetime.now()
        embed.set_footer(text = f"Support Server - https://invitebot.xyz/support | Invitebot made with \u2764\ufe0f by Nevalicjus")

        embed.add_field(name = "i!**invite**", value = "Sends you the bot invite", inline = False)
        embed.add_field(name = "i!**help**", value = "Sends you the bot's help page", inline = False)
        embed.add_field(name = "i!**info**", value = "Sends you this message", inline = False)
        embed.add_field(name = "[https://invitebot.xyz/]", value = "Bot's Main Page", inline = False)
        embed.add_field(name = "[https://docs.invitebot.xyz/]", value = "Bot's Documentation Page", inline = False)
        embed.add_field(name = "[https://invitebot.xyz/github]", value = "Bot's GitHub page", inline = False)
        embed.add_field(name = "[https://invitebot.xyz/topgg]", value = "Bot's Top.gg page", inline = False)
        await ctx.send(embed = embed)

    @commands.command()
    #------------------------------
    # Sends you the bot invite
    #------------------------------
    async def invite(self, ctx):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        self.log(ctx.guild.id, f"Invite to the bot requested by {ctx.message.author}[{ctx.message.author.id}] on {ctx.message.channel}")
        embed = self.constructResponseEmbedBase("**Invite the bot here:**\nhttps://invitebot.xyz/invite")
        await ctx.send(embed = embed)

    def log(self, guild_id, log_msg: str):
        with open('main-config.json', 'r') as f:
            config = json.load(f)
            logfile = config['LogFile']
        if guild_id == 0:
            print(f"[{datetime.datetime.now()}] [\033[34mOTHER\033[0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [OTHER]: " + log_msg + "\n")
        else:
            print(f"[{datetime.datetime.now()}] [{guild_id}] [\033[34mOTHER\033[0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [{guild_id}] [OTHER]: " + log_msg + "\n")

    def checkPerms(self, user_id, guild_id, addscopes = []):
        try:
            with open(f'configs/{guild_id}.json', 'r') as f:
                config = json.load(f)
                admin_roles = config['General']['AdminRoles']
        except FileNotFoundError:
            return False


        with open(f'main-config.json', 'r') as f:
            main_config = json.load(f)
            owners = main_config['OwnerUsers']

        isAble = 0

        guild = self.client.get_guild(guild_id)
        member = guild.get_member(user_id)

        if "owner_only" in addscopes:
            if user_id == guild.owner_id:
                return True

        if "owner_users_only" in addscopes:
            if user_id in owners:
                return True

        if user_id in owners:
            isAble += 1
        if user_id == guild.owner_id:
            isAble += 1
        for role in member.roles:
            if role.id in admin_roles:
                isAble += 1

        if "admin" in addscopes:
            if member.guild_permissions.administrator == True:
                isAble += 1
        if "manage_guild" in addscopes:
            if member.guild_permissions.manage_guild == True:
                isAble += 1

        if isAble >= 1:
            return True
        else:
            return False

    def checkInvos(self, guild_id):
        try:
            try:
                with open(f'configs/{guild_id}.json', 'r') as f:
                    config = json.load(f)
                    delinvos = config['General']['DeleteInvocations']
            except FileNotFoundError:
                return False

            if delinvos == 1:
                return True
            else:
                return False

        except KeyError:
            self.failSaveConfig

    def constructResponseEmbedBase(self, desc):
        embed = discord.Embed(title = f"**Invitebot**", description = desc, color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | Invitebot made with \u2764\ufe0f by Nevalicjus")

        return embed

    async def serverLog(self, guild_id, type: str, log_msg):
        with open(f'configs/{guild_id}.json', 'r') as f:
            config = json.load(f)
            log_channel_id = config['General']['ServerLog']
        if log_channel_id == 0:
            return

        if type in ["mod_added", "cnfg_save"]:
            em_color = discord.Colour.from_rgb(67, 181, 129)
        if type in ["delinvos", "prefix_change", "cnfg_switch"]:
            em_color = discord.Colour.from_rgb(250, 166, 26)
        if type in ["mod_deleted", "cnfg_del"]:
            em_color = discord.Colour.from_rgb(240, 71, 71)

        embed = discord.Embed(title = f"**Invitebot Logging**", color = em_color)
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | Invitebot made with \u2764\ufe0f by Nevalicjus")

        if type == "mod_added":
            embed.add_field(name = "Admin Role Added", value = log_msg, inline = False)
        if type == "delinvos":
            embed.add_field(name = "Invocation Deletion", value = log_msg, inline = False)
        if type == "mod_deleted":
            embed.add_field(name = "Admin Role Removed", value = log_msg, inline = False)
        if type == "prefix_change":
            embed.add_field(name = "Prefix Changed", value = log_msg, inline = False)
        if type == "cnfg_save":
            embed.add_field(name = "Saved Config Created", value = log_msg, inline = False)
        if type == "cnfg_switch":
            embed.add_field(name = "Current Config Switch", value = log_msg, inline = False)
        if type == "cnfg_del":
            embed.add_field(name = "Saved Config Deleted", value = log_msg, inline = False)

        log_channel = self.client.get_channel(log_channel_id)
        await log_channel.send(embed = embed)

    async def failSafeConfig(self, guild_id):
        try:
            if str(guild_id) not in guilds_with_saved_cnfgs:
                os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {guild_id}')

            savefp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            os.system(f'cp {os.getenv("PWD")}/configs/{guild_id}.json {os.getenv("PWD")}/saved-configs/{guild_id}/{savefp}.json')

        except:
            self.log(guild_id, f"failSaveConfig failed to create a saved config.")

        braces = "{}"

        os.system(f"touch configs/{guild_id}.json && echo {braces} > configs/{guild_id}.json")
        await asyncio.sleep(3)
        try:
            with open(f'configs/{guild_id}.json', 'r') as f:
                config = json.load(f)
        except:
            self.log(guild_id, f"failSafeConvig couldn't be created.")

        #creates config data
        config['General'] = {}
        config['Invites'] = {}

        config['General']['DeleteInvocations'] = 0
        config['General']['AdminRoles'] = []
        config['General']['ServerLog'] = 0
        config['General']['Prefix'] = "i!"
        config['General']['WelcomeMessage'] = "None"

        for invite in await guild.invites():
            config['Invites'][f'{invite.code}'] = {}
            config['Invites'][f'{invite.code}']['name'] = "None"
            config['Invites'][f'{invite.code}']['roles'] = []
            config['Invites'][f'{invite.code}']['uses'] = invite.uses
            config['Invites'][f'{invite.code}']['welcome'] = "None"

        with open(f'configs/{guild_id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

def setup(client):
    client.add_cog(Other(client))
