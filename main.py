import discord
import mysql.connector
from config import config

mydb = mysql.connector.connect(
  host="192.46.233.86",
  user="root",
  password="<Code><Tech> 127521",
  database="discord_bot"
)

mycursor = mydb.cursor()

token = config["token"]
client = discord.Client()
guilds = list()
commands = dict()
disChannels = dict()
proGuilds = dict()

sql_commands = {
    "add_commands": "INSERT INTO %s (name, value) VALUES (%s, %s)",
    "delete_command": "DELETE FROM %s WHERE name = %s",
    "disable_channel": "INSERT INTO %s (id,) VALUES (%s)",
    "enable_channel": "DELETE FROM %s WHERE id = %s",
    "add_proguild": "INSERT INTO guilds (id, commands) VALUES (%s, %s)",
    "delete_proguild": "DELETE FROM guilds WHERE id = %s",
    "show_tables": "SHOW TABLES",
    "create_commands_table": "CREATE TABLE %s (id BIGINT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), value VARCHAR(255))",
    "create_disabled_channels_table": "CREATE TABLE %s (id BIGINT PRIMARY KEY)",
}


# MySQL functions
def add_guild(guild_id):
    commands_table = "commandsx" + str(guild_id)
    disabled_channels_table = "disabled_channelsx" + str(guild_id)
    create_commands_table = f"CREATE TABLE {commands_table} (id BIGINT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), value VARCHAR(255))"
    create_disabled_channels_table = f"CREATE TABLE {disabled_channels_table} (id BIGINT PRIMARY KEY)"

    # Changed from commit after every change to commit just once
    mycursor.execute(create_commands_table)
    mycursor.execute(create_disabled_channels_table)
    mycursor.execute(sql_commands["add_proguild"], (guild_id, 10))
    mydb.commit()
    return


# Adding command with .cc
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
        db_guild_id = "commandsx" + str(guild_id)
        mycursor.execute(f"INSERT INTO {db_guild_id} (name, value) VALUES (%s, %s)", (first, second))
        mydb.commit()
        await message.channel.send(f"Commands <{first}> with value of <{second}> was added")
    except:
        await message.channel.send("There was an error, when adding the command.")


# Maximum commands
async def max_commands(message):
    await message.channel.send("You have used the maximum number of commands, you can create. If you want to use more "
                               "commands, contact us here: stranavadavid@protonmail.com")


# Deleting commands with .dc command
async def delete_command(message, guild_id):
    try:
        _, first = message.content.lower().strip().split("-")
        comms = commands[guild_id]
        if first in comms:
            comms.pop(first)
            db_guild_id = "commandsx" + str(guild_id)
            mycursor.execute(f"DELETE FROM {db_guild_id} WHERE name = '{first}'")
            mydb.commit()
            # TODO create function for deleting items to speed up the actual code flow, without await
            await message.channel.send(f"Command with value <{first}> vas successfully deleted")
    except:
        await message.channel.send("There was an error, when deleting the command")


# Update all of the lists and dictionaries from mysql db
def update_db():
    mycursor.execute(sql_commands["show_tables"])
    result = mycursor.fetchall()
    for res in result:
        table_name = res[0]
        if "commands" in table_name:
            _, guild_id = table_name.split("x")
            guild_id = int(guild_id)
            mycursor.execute(f"SELECT * FROM {table_name}")
            commands_query = mycursor.fetchall()
            if commands_query:
                commands_place = dict()
                for command in commands_query:
                    commands_place[command[1]] = command[2]
                commands[guild_id] = commands_place
        elif "disabled_channels" in table_name:
            _, guild_id = table_name.split("x")
            guild_id = int(guild_id)
            mycursor.execute(f"SELECT * FROM {table_name}")
            channels_query = mycursor.fetchall()
            if channels_query:
                disabled_channels = list()
                for channel in channels_query:
                    disabled_channels.append(channel[0])
                disChannels[guild_id] = disabled_channels
        elif table_name == "guilds":
            mycursor.execute("SELECT * FROM guilds")
            guilds_results = mycursor.fetchall()
            if guilds_results:
                for guilds_result in guilds_results:
                    guilds.append(guilds_result[0])
        else:
            print("Table name " + table_name + " is not recognized")

    print("DB was updated")


# TODO adding commands, not working. move creating disChannels and commands to add guild function
@client.event
async def on_ready():
    update_db()
    print("Discord bot is ready")


@client.event
async def on_message(message):
    guild_id = message.guild.id
    # TODO double check statement below, get things to dicts and lists when app is ready
    if guild_id not in guilds:
        add_guild(guild_id)
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
                        await add_command(message, guild_id)
                    elif len(commands[guild_id]) >= proGuilds[guild_id]:
                        await max_commands(message)
                    else:
                        print("There is a problem with number of commands")
                else:
                    if len(commands[guild_id]) < 3:
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
        db_guild_id = "disabled_channelsx" + str(guild_id)
        if message.channel.id in dch:
            db_guild_id = "disabled_channelsx" + str(guild_id)
            mycursor.execute(f"DELETE FROM {db_guild_id} WHERE id = {message.channel.id}")
            mydb.commit()
            dch.remove(int(message.channel.id))
            await message.channel.send("I have been enabled in this channel")
        else:
            dch.append(int(message.channel.id))
            mycursor.execute(f"INSERT INTO {db_guild_id} (id) VALUES ({message.channel.id})")
            mydb.commit()
            await message.channel.send("I have been disabled in this channel")

    if guild_id == 792144909125025822:
        if ".addproguild" in message.content.lower().strip():
            _, first = message.content.lower().split("-")
            first, second = first.split("=")
            first = first.strip()
            second = second.strip()
            try:
                id = int(first)
                num = int(second)
                if id in proGuilds:
                    proGuilds.pop(id)
                proGuilds[id] = num
                mycursor.execute("UPDATE guilds SET commands = %s WHERE id = %s", (num, id))
                mydb.commit()
                await message.channel.send(f"Guild id {id} is now a pro guild with {num} total commands")
            except:
                await message.channel.send("Problem with converting id to integer")
        elif ".deleteproguild" in message.content.lower().strip():
            _, first = message.content.lower().split("-")
            try:
                id = int(first.strip())
                if id in proGuilds:
                    proGuilds.pop(id)
                    commands.pop(id)
                    db_guild_id = "commandsx" + str(id)
                    mycursor.execute("UPDATE guilds SET commands = 10 WHERE id = %s", (id,))
                    mycursor.execute(f"DELETE FROM {db_guild_id}")
                    mydb.commit()
                    await message.channel.send("Pro guild and commands were deleted")
                else:
                    await message.channel.send("There is no pro guild with that id")
            except:
                await message.channel.send("There was some problem deleting the pro guild")

client.run(token)
