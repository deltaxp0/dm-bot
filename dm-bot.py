import os, discord, random, json

from discord.ext import commands
from dotenv import load_dotenv, dotenv_values
from typing import Literal

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)  # commands.when_mentioned_or("!") is used to make the bot respond to !ping and @bot ping

load_dotenv()

# some constants
REACTION = '✅'
staff = "D&D Staff"
dice = [4,6,8,10,12,20]

async def setup_hook() -> None:  # This function is automatically called before the bot starts
    await bot.tree.sync()   # This function is used to sync the slash commands with Discord it is mandatory if you want to use slash commands

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

registered_messages = []'''

#Delta: Added player class. Should be extensible enough.
class Player:
    def __init__(self, user, strength, speed, defence):
        self.user = user
        self.strength = strength
        self.speed = speed
        self.defence = defence

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.hybrid_command()
async def ping(ctx):
    await ctx.send(f"> Pong! {round(bot.latency * 1000)}ms")

@bot.hybrid_command()
async def sync(ctx):
    bot.setup_hook = setup_hook
    await ctx.send("synced")

async def parseUser(guild, user):
    user = user.strip("<@")
    if user.isdigit():
        try:
            return await guild.fetch_user(user)
        except NotFound:
            return None
    else:
        return discord.utils.get(guild.members, name=user)

@bot.hybrid_command()
@commands.has_role(staff)
async def start(ctx):
    sectors['test'] = bot.get_channel(1274370660226957342)
    sectors['test-2'] = bot.get_channel(1274388708073668720)
    sectors['test-3'] = bot.get_channel(1274388788092731434)

    register_message = await channel.send("Please react to this message to be registed as a player!")
    await register_message.add_reaction(REACTION)
    registered_messages.append(register_message)

@bot.hybrid_command()
@commands.has_role(staff)
async def sectors(ctx):
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
    
@bot.hybrid_command()
@commands.has_role(staff)
async def move(ctx):
    msg = message.content.split()
    if len(msg) < 3 or len(msg) > 3:
       await message.channel.send("Incorrect usage! Should be: !move [player] [sector]")
       return
    elif len(msg) == 3: #msg[1] = user, msg[2] = sector | Delta: Useless elif statement, lol. 
        if msg[1] in players:
            players[msg[1]] = msg[2]
            await sectors[msg[2]].send(f"<@{ids[msg[1]]}> welcome to {msg[2]}!")
            user = await bot.fetch_user(ids[msg[1]])
            for sector in sectors:
                if sector != msg[2]:
                    await sectors[sector].remove_user(user)
        else:
            await message.channel.send("No such registered player found!")
            print(msg[1])
            return

@bot.hybrid_command()
@commands.has_role(staff)
async def register(ctx):
    msg = message.content.split()
    if len(msg) < 5 or len(msg) > 5:
        await message.channel.send("Incorrect usage! Should be: !register_stats [name] [strength] [speed] [defence]")
        return
    if msg[1] not in players:
        await message.channel.send("This user is not playing!")
        return

    new_player = Player(msg[1], msg[2], msg[3], msg[4])
    stats[msg[1]] = new_player

@bot.hybrid_command()
@commands.has_role(staff)
async def stats(ctx):
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
    
@bot.hybrid_command()
async def roll(ctx, sides: Literal[tuple(dice)]):
    '''if dice not in [4,6,8,10,12,20]:
        await message.channel.send(f"Incorrect usage! Should be: !roll {dice}")
        return'''
    embed = discord.Embed(
    title=msg[1] + "Dices:",
    color=discord.Color.blurple()
    )
    #roll 6 times
    values = sort([random.randint(1, sides) for _ in range(6)])
    for i in range(6):
        embed.add_field(name="Dice " + str(i+1), value=str(values[i]))
    await message.channel.send(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message == registered_messages[0] and user.name not in players:
        players[user.name] = 'test'
        ids[user.name] = user.id
        await sectors["test"].send(f"<@{user.id}> welcome to test!")

bot.run(os.getenv('TOKEN')) 
