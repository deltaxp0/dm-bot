import os, discord, random, json

from discord.ext import commands
from dotenv import load_dotenv, dotenv_values
from typing import Literal

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)  # commands.when_mentioned_or("!") is used to make the bot respond to !ping and @bot ping

load_dotenv()

# some constants
reactions = ["1️⃣","2️⃣","3️⃣"]
staff = "D&D Staff"
dice = [4,6,8,10,12,20]

async def setup_hook() -> None:  # This function is automatically called before the bot starts
    await bot.tree.sync()   # This function is used to sync the slash commands with Discord it is mandatory if you want to use slash commands

db = {}

def update_db():
    with open("db.json", 'w') as file:
        json.dump(db, file, indent=4)

if os.path.exists("db.json"):
    with open("db.json", "r") as file:
        db = json.load(file)
else:
    db={"players":{},"stats":{},"sectors":{},"registry":0}
    update_db()

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
    db["sectors"]['1'] = 1274803528690438145
    db["sectors"]['2'] = 1274803583111663618
    db["sectors"]['3'] = 1274803643308052490

    register_message = await ctx.send("Please react to this message to be registered as a player!")
    for reaction in reactions:
        await register_message.add_reaction(reaction)
    db["registry"]=register_message.id
    update_db()

@bot.hybrid_command()
@commands.has_role(staff)
async def sectors(ctx):
    grouped_data = {}
    for key, value in db["players"].items():
        if value not in grouped_data:
            grouped_data[value] = []
        grouped_data[value].append(key)
    #await message.channel.send(str(db["players"]))

    embed=discord.Embed(title="List")
    for value, key in grouped_data.items():
    # Join the keys into a single string, separated by a new line
        keys_str = "\n".join("Sector" + key)
    # Add a field to the embed
        embed.add_field(name=value, value=keys_str, inline=False)
    await ctx.channel.send(embed=embed)
    
@bot.hybrid_command()
@commands.has_role(staff)
async def move(ctx, user: discord.User, sector: str):
    #user = await parseUser(ctx, user)
    if str(user.id) in db["players"].keys() and sector in db["sectors"].keys():
        db["players"][user.id] = sector
        await bot.get_channel(db["sectors"][sector]).send(f"{user.mention} welcome to {sector}!")
        for sect in db["sectors"]:
            if sect != sectors:
                await bot.get_channel(db["sectors"][sector]).remove_user(user)
        update_db()
    else:
        await ctx.channel.send("No such registered player found!")
        print(user.id)
        return

@bot.hybrid_command()
@commands.has_role(staff)
async def register(ctx, user: discord.User, strength: int, speed: int, defence: int):
    if str(user.id) not in db["players"].keys:
        await ctx.channel.send("This user is not playing!")
        return

    new_player = Player(user, strength, speed, defence)
    db["stats"][user.id] = new_player
    update_db()

@bot.hybrid_command()
@commands.has_role(staff)
async def stats(ctx, user: discord.User):
   try:
        embed = discord.Embed(
        title=user.name + "Stats:",
        color=discord.Color.blue()
        )
        #embed.add_field(name=value, value=keys_str, inline=False)
        embed.add_field(name="Strength", value=db["stats"][user.id].strength)
        embed.add_field(name="Speed", value=db["stats"][user.id].speed)
        embed.add_field(name="Defence", value=db["stats"][user.id].defence)
        
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
    title=str(sides) + "Dice:",
    color=discord.Color.blurple()
    )
    #roll 6 times
    values = [random.randint(1, sides) for _ in range(6)]
    values.sort()
    for i in range(6):
        embed.add_field(name="Dice " + str(i+1), value=values[i])
    await ctx.send(embed=embed)
    
@bot.hybrid_command()
@commands.has_role("Coding Department")
async def stop(ctx):
    ctx.send("stopping...")
    update_db()
    exit(0)

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.id == db["registry"] and not user.bot and str(user.id) not in db["players"].keys() and reaction.emoji[0].isdigit:
        db["players"][str(user.id)] = reaction.emoji[0]
        #await bot.get_channel(db["sectors"][reaction.emoji[0]]).send(f"{user.mention} welcome to sector {reaction.emoji[0]}!")
        role = ctx.guild.get_role(db["sectors"][reaction.emoji[0]])
        await bot.add_roles(user, role)
        update_db()

bot.run(os.getenv('TOKEN')) 
