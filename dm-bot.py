import os, discord, random, json

from discord.ext import commands
from dotenv import load_dotenv, dotenv_values
from typing import Literal

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"), intents=intents)  # commands.when_mentioned_or("!") is used to make the bot respond to !ping and @bot ping

load_dotenv()

# some constants
emojis = {"Fighter": "<:fighter:1274924299102457887>", "Rogue": "<:rogue:1274924376562597929>", "Cleric": "<:cleric:1274924223508516947>", "Wizard": "<:wizard:1274924429167824949>"}
staff = "D&D Staff"
dice = [4,6,8,10,12,20]
sector_list = {"sector-1": 1274803528690438145, "sector-2": 1274803583111663618, "sector-3": 1274803643308052490}

async def setup_hook() -> None:  # This function is automatically called before the bot starts
    await bot.tree.sync()   # This function is used to sync the slash commands with Discord it is mandatory if you want to use slash commands

db = {}

def update_db():
    with open("db.json", 'w') as file:
        json.dump(db, file, indent=4)

def reset_db():
    global db
    db={"players":{},"stats":{}, "registry":[]}
    update_db()

if os.path.exists("db.json"):
    with open("db.json", "r") as file:
        db = json.load(file)
else:
    reset_db()


# Delta: Added player class. Should be extensible enough.

'''class Player:
    def __init__(self, name, class_name, str, dex, con, int, wis, cha):
        self.name = name
        self.class_name = class_name
        self.str = str
        self.dex = dex
        self.con = con
        self.int = int
        self.wis = wis
        self.cha = cha'''
        
def Player(name, class_name, str, dex, con, int, wis, cha):
    return {"Name": name, "Class": class_name, "Strength": str, "Dexterity": dex, "Constitution": con, "Intelligence": int, "Wisdom": wis, "Charisma": cha}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    update_db()

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
async def newgame(ctx):
    register_message = await ctx.send("Please react to this message to be registed as a player!")
    for emoji in emojis.values():
        await register_message.add_reaction(emoji) 
    db["registry"].append(register_message.id)
    update_db()

@bot.hybrid_command()
@commands.has_role(staff)
async def sectors(ctx):
    grouped_data = {}
    for key, value in db["players"].items():
        if value not in grouped_data:
            grouped_data[value] = []
        grouped_data[value].append(key)
    # await message.channel.send(str(players))

    embed = discord.Embed(title="List")
    print(grouped_data)
    for value, keys in grouped_data.items():
        # Join the keys into a single string, separated by a new line
        keys_str = "\n".join(ctx.guild.get_role(keys).name)
    # Add a field to the embed
        embed.add_field(name=bot.fetch_user(value).name, value=keys_str, inline=False)
    await ctx.channel.send(embed=embed)
    
@bot.hybrid_command()
@commands.has_role(staff)
async def move(ctx, user: discord.User, sector: discord.abc.GuildChannel):
    for sect in sector_list.values():
        await user.remove_roles(ctx.guild.get_role(sect))
    try:
        await user.add_roles(ctx.guild.get_role(sector_list[sector.id]))
        db["players"][user.id] = sector.id
        await ctx.send(f"{user.mention} moved to {sector.mention}")
    except:
        await ctx.send("Error! No such sector!")
    update_db()

@bot.hybrid_command()
@commands.has_role(staff)
async def register(ctx, user: discord.User, class_name: str, strength: int, dexterity: int, constitution: int, intelligence: int, wisdom: int, charisma: int):
    if str(user.id) not in db["players"].keys():
        await ctx.channel.send("This user is not playing!")
        return

    new_player = Player(user.id, class_name, strength, dexterity, constitution, intelligence, wisdom, charisma)
    db["stats"][user.id] = new_player
    update_db()

@bot.hybrid_command()
@commands.has_role(staff)
async def stats(ctx, user: discord.Member=None):
    if not user:
        user = ctx.author
    try:
        embed = discord.Embed(
            title=user.name + " Stats:",
            color=discord.Color.blue()
        )
        for key, value in db["stats"][str(user.id)].items():
            embed.add_field(name=key, value=value)

        await ctx.send(embed=embed)
    except KeyError:
        await ctx.send("No such player found!")
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
    await ctx.send("stopping...")
    update_db()
    exit(0)
    
@bot.hybrid_command()
@commands.has_role("Coding Department")
async def reset(ctx):
    await ctx.send("wiping db...")
    await on_ready()
    reset_db()
    
@bot.hybrid_command()
@commands.has_role("Coding Department")
async def data(ctx):
    await ctx.send(f"```{db}```")

@bot.event
async def on_reaction_add(reaction, user):
    '''if reaction.message.id in db["registry"] and not user.bot and str(user.id) not in db["players"].keys() and reaction.emoji[0].isdigit:
        db["players"][str(user.id)] = reaction.emoji[0]
        #await bot.get_channel(sector_list[reaction.emoji[0]]).send(f"{user.mention} welcome to sector {reaction.emoji[0]}!")
        role = reaction.message.guild.get_role(sector_list[reaction.emoji[0]])
        await bot.add_roles(user, role)
        update_db()'''
    
    if reaction.message.id in db["registry"] and not user.bot and str(user.id) not in db["players"].keys():
        for sector in sector_list:
            await user.remove_roles(reaction.message.guild.get_role(sector_list[sector]))
        print(user.name)
        my_sector = random.choice(list(sector_list.keys()))
        db["players"][user.id] = sector_list[my_sector]
        await user.add_roles(reaction.message.guild.get_role(sector_list[my_sector]))
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
        match reaction.emoji.name:
            case "fighter":
                db["stats"][user.id] = Player(user.name, "Fighter", statistics[0], statistics[1],
                                          statistics[2], statistics[5], statistics[4], statistics[3])
            case "rogue":
                db["stats"][user.id] = Player(user.name, "Rogue", statistics[1], statistics[0],
                                          statistics[2], statistics[4], statistics[3], statistics[5])
            case "cleric":
                db["stats"][user.id] = Player(user.name, "Cleric", statistics[4], statistics[2],
                                          statistics[0], statistics[1], statistics[5], statistics[3])
            case "wizard":
                db["stats"][user.id] = Player(user.name, "Wizard", statistics[3], statistics[1],
                                          statistics[2], statistics[5], statistics[4], statistics[0])
    update_db()

bot.run(os.getenv('TOKEN')) 
