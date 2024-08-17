import discord
import random

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

players = {}
stats = {}
ids = {}

sectors = {}

registered_messages = []

#Delta: Added player class. Should be extensible enough.
class Player:
    def __init__(self, name, class_name, str, con, dex, cha, wis, int):
        self.name = name
        self.class_name = class_name
        self.str = str
        self.con = con
        self.dex = dex
        self.cha = cha
        self.wis = wis
        self.int = int

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    channel = client.get_channel(1272746089555955758)
    sectors['test'] = client.get_channel(1274370660226957342)
    sectors['test-2'] = client.get_channel(1274388708073668720)
    sectors['test-3'] = client.get_channel(1274388788092731434)

    register_message = await channel.send("Please react to this message to be registed as a player!")
    await register_message.add_reaction('💀')
    await register_message.add_reaction('🧢')
    await register_message.add_reaction('🔥')
    registered_messages.append(register_message)

@client.event
async def on_message(message):
    if message.content.startswith('!list_sectors'):
        dm_role = discord.utils.get(message.author.roles, name="D&D Staff")
        if dm_role is None:
            return
        grouped_data = {}
        for key, value in players.items():
            if value not in grouped_data:
                grouped_data[value] = []
            grouped_data[value].append(key)
        #await message.channel.send(str(players))

        embed=discord.Embed(title="List")
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
        elif len(msg) == 3: #msg[1] = user, msg[2] = sector | Delta: Useless elif statement, lol. 
            if msg[1] in players:
                players[msg[1]] = msg[2]
                await sectors[msg[2]].send(f"<@{ids[msg[1]]}> welcome to {msg[2]}!")
                user = await client.fetch_user(ids[msg[1]])
                for sector in sectors:
                    if sector != msg[2]:
                        await sectors[sector].remove_user(user)
            else:
                await message.channel.send("No such registered player found!")
                print(msg[1])
                return
    if message.content.startswith('!register_stats'):
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
    
    if message.content.startswith('!show_stats'):
       dm_role = discord.utils.get(message.author.roles, name="D&D Staff")
       if dm_role is None:
            return
       msg = message.content.split()
       if len(msg) < 2 or len(msg) > 2:
           await message.channel.send("Incorrect usage! Should be: !show_stats [name]")
           return
       try:
            embed = discord.Embed(
            title=msg[1] + "Stats:",
            color=discord.Color.blue()
            )
            #embed.add_field(name=value, value=keys_str, inline=False)
            embed.add_field(name="Strength", value=stats[msg[1]].strength)
            embed.add_field(name="Speed", value=stats[msg[1]].speed)
            embed.add_field(name="Defence", value=stats[msg[1]].defence)
            
            await message.channel.send(embed=embed)
       except KeyError:
           await message.channel.send("No such player found!")
           return
    
    if message.content.startswith('!roll'):
        msg = message.content.split()
        if len(msg) < 2 or len(msg) > 2 or int(msg[1]) not in [4,6,8,10,12,20]:
            await message.channel.send("Incorrect usage! Should be: !roll [4,6,8,10,12,20]")
            return
        else:
            sides = int(msg[1])
            embed = discord.Embed(
            title=msg[1] + "Dices:",
            color=discord.Color.blurple()
            )
            #roll 6 times
            for i in range(6):
                embed.add_field(name="Dice " + str(i+1), value=str(random.randint(1, sides) + 12))
            await message.channel.send(embed=embed)
           
@client.event
async def on_reaction_add(reaction, user):
    if reaction.message == registered_messages[0] and user.name not in players:
        players[user.name] = 'test'
        ids[user.name] = user.id
        await sectors["test"].send(f"<@{user.id}> welcome to test!")
        for sector in sectors:
            if sector != "test":
                await sectors[sector].remove_user(user)
        
        #Stats section
        sides = 4
        stats = []
        for _ in range(6):
            stats.append(random.randint(1, sides) + 12)
        
        #name, class_name, str = 0, con = 1, dex = 2, cha = 3, wis = 4, int = 5
        if reaction.emoji == '💀':
            stats.sort(reverse=True)
            players[user.name] = Player(user.name, "Fighter", stats[0], stats[1], stats[2], stats[3], stats[4], stats[5])
        if reaction.emoji == '🧢':
            players[user.name] = Player(user.name, "Rogue", stats[1], stats[0], stats[2], stats[5], stats[4], stats[0])
        
        print(players[user.name].name)
        print(players[user.name].class_name)
        print(players[user.name].str)
        print(players[user.name].con)
        print(players[user.name].dex)
        print(players[user.name].cha)
        print(players[user.name].wis)
        print(players[user.name].int)

client.run(os.getenv('TOKEN')) 
