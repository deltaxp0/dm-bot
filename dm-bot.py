import os, discord, random, json
from dotenv import load_dotenv, dotenv_values

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

if os.path.exists("db.json"):
    with open("db.json", "r") as f:
        db = json.load(f)
        players = db["players"]
        stats = db["stats"]
        ids = db["ids"]
        sectors = db["sectors"]
        registered_messages = db["registered_messages"]
else:
    with open("db.json", 'w') as file:
        file.write("{players={},stats={},ids={},sectors={},registered_messages=[]}")

def update_db():
    with open("db.json", 'w') as file:
        json.dump({'players'=players,'stats'=stats,'ids'=ids,'sectors'=sectors,'registered_messages'=registered_messages}, file, indent=4)

'''players = {}
stats = {}
ids = {}

sectors = {}
server = client.get_guild(1272746089224867921)
registered_messages = []
'''

# Delta: Added player class. Should be extensible enough.

class Player:
    def __init__(self, name, class_name, str, dex, con, int, wis, cha):
        self.name = name
        self.class_name = class_name
        self.str = str
        self.dex = dex
        self.con = con
        self.int = int
        self.wis = wis
        self.cha = cha

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    server = client.get_guild(1272746089224867921)
    sectors['sector-1'] = server.get_role(1274803528690438145)
    sectors['sector-2'] = server.get_role(1274803583111663618)
    sectors['sector-3'] = server.get_role(1274803643308052490)

@client.event
async def on_message(message):
    if message.content.startswith('!newgame'):
        register_message = await message.channel.send("Please react to this message to be registed as a player!")
        await register_message.add_reaction('⚔️')
        await register_message.add_reaction('🗡️')
        await register_message.add_reaction('🍾')
        await register_message.add_reaction('🧙‍♂️')
        registered_messages.append(register_message)

    if message.content.startswith('!sectors'):
        dm_role = discord.utils.get(message.author.roles, name="D&D Staff")
        if dm_role is None:
            return
        grouped_data = {}
        for key, value in players.items():
            if value not in grouped_data:
                grouped_data[value] = []
            grouped_data[value].append(key)
        # await message.channel.send(str(players))

        embed = discord.Embed(title="List")
        print(grouped_data)
        for value, keys in grouped_data.items():
            # Join the keys into a single string, separated by a new line
            keys_str = "\n".join(keys)
        # Add a field to the embed
            embed.add_field(name=value, value=keys_str, inline=False)
        await message.channel.send(embed=embed)

    if message.content.startswith('!move'):
        dm_role = discord.utils.get(message.author.roles, name="D&D Staff")
        if dm_role is None:
            return
        msg = message.content.split()
        if len(msg) < 3 or len(msg) > 3:
            await message.channel.send("Incorrect usage! Should be: !move [player] [sector]")
            return
        # msg[1] = user, msg[2] = sector | Delta: Useless elif statement, lol.
        elif len(msg) == 3:
            if msg[1] in players:
                if "<" not in msg[2]:
                    user = await message.guild.fetch_member(ids[msg[1]])
                    for sector in sectors:
                        await user.remove_roles(sectors[sector])
                    
                    try:
                        await user.add_roles(sectors[msg[2]])
                        players[msg[1]] = msg[2]
                        await message.channel.send(f"{msg[1]} moved to {msg[2]}")
                    except:
                        await message.channel.send("Error! No such sector!")
                        return
                else:
                    msg[2] = msg[2].replace('<', ''); msg[2] = msg[2].replace('>', ''); msg[2] = msg[2].replace('#', '')
                    grouped_data = {}
                    sector_key = int(msg[2])
                    channel_to_ping = client.get_channel(sector_key)

                    user = await message.guild.fetch_member(ids[msg[1]])
                    for sector in sectors:
                        await user.remove_roles(sectors[sector])
                    try:
                        await user.add_roles(sectors[channel_to_ping])
                        players[msg[1]] = str(channel_to_ping)
                        await message.channel.send(f"{msg[1]} moved to {channel_to_ping}")
                    except:
                        await message.channel.send("Error! No such sector!")
                        return
            elif "<" in msg[1]:
                msg[1].replace('<', '')
                msg[1].replace('>', '')
                msg[1].replace('@', '')
                grouped_data = {}
                for key, value in ids.items():
                    if value not in grouped_data:
                        grouped_data[value] = []
                        grouped_data[value].append(key)
                player_key = grouped_data[value][0]
                for value, keys in grouped_data.items():
                    keys_str = "\n".join(keys)
                if "<" not in msg[2]:
                    user = await message.guild.fetch_member(ids[player_key])
                    for sector in sectors:
                        await user.remove_roles(sectors[sector])
                    try:
                        await user.add_roles(sectors[msg[2]])
                        await message.channel.send(f"{msg[1]} moved to {msg[2]}")
                        players[player_key] = msg[2]
                    except:
                        await message.channel.send("Error! No such role!")
                else:
                    msg[2] = msg[2].replace('<', ''); msg[2] = msg[2].replace('>', ''); msg[2] = msg[2].replace('#', '')
                    grouped_data = {}
                    sector_key = int(msg[2])
                    channel_to_ping = client.get_channel(sector_key)

                    user = await message.guild.fetch_member(ids[player_key])
                    for sector in sectors:
                        await user.remove_roles(sectors[sector])

                    try:
                        await user.add_roles(sectors[str(channel_to_ping)])
                        players[player_key] = str(channel_to_ping)
                        await message.channel.send(f"{msg[1]} moved to {str(channel_to_ping)}")
                    except:
                        await message.channel.send("Error! No sector like that exists!")
                        return
                    
                    
    if message.content.startswith('!register'):
        dm_role = discord.utils.get(message.author.roles, name="D&D Staff")
        if dm_role is None:
            return
        msg = message.content.split()
        if len(msg) < 5 or len(msg) > 5:
            await message.channel.send("Incorrect usage! Should be: !register_stats [name] [strength] [speed] [defence]")
            return
        if msg[1] not in players:
            await message.channel.send("This user is not playing!")
            return

        new_player = Player(msg[1], msg[2], msg[3], msg[4])
        stats[msg[1]] = new_player

    if message.content.startswith('!stats'):
        dm_role = discord.utils.get(message.author.roles, name="D&D Staff")
        if dm_role is None:
            return
        msg = message.content.split()
        if len(msg) < 2 or len(msg) > 2:
            await message.channel.send("Incorrect usage! Should be: !show_stats [name]")
            return
        if msg[1] in stats:
            embed = discord.Embed(
                title=msg[1] + "Stats:",
                color=discord.Color.blue()
            )
            embed.add_field(name="Name", value=stats[player_key].name)
            embed.add_field(name="Class", value=stats[player_key].class_name)
            embed.add_field(name="Str", value=stats[player_key].str)
            embed.add_field(name="Dex", value=stats[player_key].dex)
            embed.add_field(name="Con", value=stats[player_key].con)
            embed.add_field(name="Int", value=stats[player_key].int)
            embed.add_field(name="Wis", value=stats[player_key].wis)
            embed.add_field(name="Cha", value=stats[player_key].cha)

            await message.channel.send(embed=embed)
        elif "<" in msg[1]:
            msg[1].replace('<', '')
            msg[1].replace('>', '')
            msg[1].replace('@', '')
            grouped_data = {}
            for key, value in ids.items():
                if value not in grouped_data:
                    grouped_data[value] = []
                    grouped_data[value].append(key)
            player_key = grouped_data[value][0]
            for value, keys in grouped_data.items():
                keys_str = "\n".join(keys)

            embed = discord.Embed(
                title="Stats:",
                color=discord.Color.blue()
            )

            # name, class_name, str, dex, con, int, wis, cha
            embed.add_field(name="Name", value=stats[player_key].name)
            embed.add_field(name="Class", value=stats[player_key].class_name)
            embed.add_field(name="Str", value=stats[player_key].str)
            embed.add_field(name="Dex", value=stats[player_key].dex)
            embed.add_field(name="Con", value=stats[player_key].con)
            embed.add_field(name="Int", value=stats[player_key].int)
            embed.add_field(name="Wis", value=stats[player_key].wis)
            embed.add_field(name="Cha", value=stats[player_key].cha)

            await message.channel.send(embed=embed)

    if message.content.startswith('!roll'):
        msg = message.content.split()
        if len(msg) < 2 or len(msg) > 2 or int(msg[1]) not in [4, 6, 8, 10, 12, 20]:
            await message.channel.send("Incorrect usage! Should be: !roll [4,6,8,10,12,20]")
            return
        else:
            sides = int(msg[1])
            embed = discord.Embed(
                title=msg[1] + "Dices:",
                color=discord.Color.blurple()
            )
            # roll 6 times
            for i in range(6):
                embed.add_field(name="Dice " + str(i+1),
                                value=str(random.randint(1, sides) + 12))
            await message.channel.send(embed=embed)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message == registered_messages[0] and user.name not in players:
        for sector in sectors:
            await user.remove_roles(sectors[sector])
        print(user)
        ids[user.name] = user.id
        my_sector = random.choice(list(sectors.keys()))
        players[user.name] = sectors[my_sector]
        await user.add_roles(sectors[my_sector])
        # Stats section
        sides = 4
        statistics = []
        for _ in range(6):
            statistics.append(random.randint(1, sides) + 12)

        # name, class_name, Str = 0, Dex = 1, Con = 2, Int = 3, Wis = 4, Cha = 5

        # fighter:  Str, Dex, Con, Cha, Wis, Int [0, 1, 2, 5, 4, 3]
        # rogue:    Dex, Str, Con, Wis, Int, Cha [1, 0, 2, 4, 3, 5]
        # cleric:   Wis, Con, Str, Dex, Cha, Int [4, 2, 0, 1, 5, 3]
        # wizard:   Int, Dex, Con, Cha, Wis, Str [3, 1, 2, 5, 4, 0]

        statistics.sort(reverse=True)
        match reaction.emoji:
            case '⚔️':
                stats[user.name] = Player(user.name, "Fighter", statistics[0], statistics[1],
                                          statistics[2], statistics[5], statistics[4], statistics[3])
            case '🗡️':
                stats[user.name] = Player(user.name, "Rogue", statistics[1], statistics[0],
                                          statistics[2], statistics[4], statistics[3], statistics[5])
            case '🍾':
                stats[user.name] = Player(user.name, "Cleric", statistics[4], statistics[2],
                                          statistics[0], statistics[1], statistics[5], statistics[3])
            case '🧙‍♂️':
                stats[user.name] = Player(user.name, "Wizard", statistics[3], statistics[1],
                                          statistics[2], statistics[5], statistics[4], statistics[0])

client.run(os.getenv('TOKEN'))
