import discord
import mysql.connector

token_first = "NzkyMTQ0NDUwNjQxMzMwMjU2.X-ZcAg."
token_second = "FbS-SGkycAxTXCxBap2_gn55Gp0"
token = token_first + token_second
client = discord.Client()
guilds = list()
commands = dict()
disChannels = dict()
proGuilds = dict()


@client.event
async def on_ready():
    print("Discord bot is ready")


async def add_command(message, guild_id):
    # Getting the values of the command
    try:
        content = message.content.strip()
        _, first_first = content.split("-")
        first, second = first_first.split("=")
        first = first.lower().strip()
        second = second.strip()
        comms = commands[guild_id]
        comms[first] = second
        await message.channel.send(f"Commands <{first}> with value of <{second}> was added")
    except:
        await message.channel.send("There was an error, when adding the command.")


async def max_commands(message):
    await message.channel.send("You have used the maximum number of commands, you can create. If you want to use more "
                               "commands, contact us here: stranavadavid@protonmail.com")


async def delete_command(message, guild_id):
    try:
        _, first = message.content.lower().strip().split("-")
        comms = commands[guild_id]
        if first in comms:
            comms.pop(first)
            # TODO create function for deleting items to speed up the actual code flow, without await
            await message.channel.send(f"Command with value <{first}> vas successfully deleted")
    except:
        await message.channel.send("There was an error, when deleting the command")


@client.event
async def on_message(message):
    guild_id = message.guild.id
    if guild_id not in guilds:
        guilds.append(guild_id)
    if guild_id not in commands:
        commands[guild_id] = dict()
    if guild_id not in disChannels:
        disChannels[guild_id] = list()

    author_roles = []
    for role in message.author.roles:
        author_roles.append(role.name)
    if message.channel.id not in disChannels[guild_id] and message.content.lower().strip() != ".disable":
        if "Radana" not in author_roles:
            if ".cc" in message.content.lower().strip():
                # Check the guild's number of commands and maximum commands allowed
                if guild_id in proGuilds:
                    if len(commands[guild_id]) < proGuilds[guild_id]:
                        #print("This is a pro guild available commands")
                        await add_command(message, guild_id)
                    elif len(commands[guild_id]) >= proGuilds[guild_id]:
                        await max_commands(message)
                    else:
                        print("There was some problem with commands number")
                else:
                    #print(commands[guild_id])
                    if len(commands[guild_id]) < 3:
                        #print("This is a normal guild with available commands")
                        await add_command(message, guild_id)
                    elif len(commands[guild_id]) >= 3:
                        await max_commands(message)
                    else:
                        print("There was some problem with available commands")

            elif ".dc" in message.content.lower().strip():
                await delete_command(message, guild_id)

            elif message.content.lower().strip() == ".help":
                await message.channel.send("You can create commands by typing .cc-<command-name>-<command-value> "
                                           "(Replace the brackets with your values). Also you can delete commands by "
                                           "typing .dc-<command-name> (Replace the brackets with your value)")
            elif message.content.lower().strip() == ".id":
                await message.channel.send(f"{guild_id} is your server id")
            else:
                comms = commands[guild_id]
                if comms:
                    for command in comms:
                        if str(" " + command.strip() + " ") in str(" " + message.content.strip().lower() + " "):
                            if comms[command].strip() != "":
                                await message.channel.send(comms[command])
    elif message.content.lower().strip() == ".disable":
        dch = disChannels[guild_id]
        if message.channel.id in dch:
            dch.remove(int(message.channel.id))
            await message.channel.send("I have been enabled in this channel")
        else:
            dch.append(int(message.channel.id))
            await message.channel.send("I have been disabled in this channel")

    if guild_id == 792144909125025822:
        if ".addproguild" in message.content.lower().strip():
            _, first = message.content.lower().split("-")
            first, second = first.split("=")
            first = first.strip()
            second = second.strip()
            try:
                print(first)
                print(second)
                id = int(first)
                num = int(second)
                if id in proGuilds:
                    proGuilds.pop(id)
                proGuilds[id] = num
                await message.channel.send(f"Guild id {id} is now a pro guild with {num} total commands")
            except:
                await message.channel.send("Problem with converting id to integer")
        elif ".deleteproguild" in message.content.lower().strip():
            _, first = message.content.lower().split("-")
            try:
                # TODO check if guild exists first
                # There is an error, somewhere here, or actually there isn't any, but double check
                id = int(first.strip())
                if id in proGuilds:
                    proGuilds.pop(id)
                    commands.pop(id)
                    await message.channel.send("Pro guild and commands were deleted")
                await message.channel.send("There is no pro guild with that id")
            except:
                await message.channel.send("There was some problem deleting the pro guild")


# TODO when creating new list with list[list id] check if it is being stored back
client.run(token)
