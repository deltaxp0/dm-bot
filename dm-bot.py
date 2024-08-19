import os, discord, random, json
from discord.ext import commands
from dotenv import load_dotenv, dotenv_values

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=intents)

client = discord.Client(intents=intents)

emojis = {"Fighter": "<:fighter:1274924299102457887>", "Rogue": "<:rogue:1274924376562597929>", "Cleric": "<:cleric:1274924223508516947>", "Wizard": "<:wizard:1274924429167824949>"}
sector_list = {"sector-1": 1274803528690438145, "sector-2": 1274803583111663618, "sector-3": 1274803643308052490}

async def setup_hook() -> None:  # This function is automatically called before the bot starts
    await bot.tree.sync()   # This function is used to sync the slash commands with Discord it is mandatory if you want to use slash commands

db = {}

def update_db():
    with open("db.json", 'w') as file:
        json.dump(db, file, indent=4)

def reset_db():
    global db
    db={"stats":{}, "registry":[]}
    update_db()

if os.path.exists("db.json"):
    with open("db.json", "r") as file:
        db = json.load(file)
else:
    reset_db()

def Player(name, class_name, sect, str, dex, con, int, wis, cha):
    return {"Name": name, "Class": class_name, "Sector": sect, "Strength": str, "Dexterity": dex, "Constitution": con, "Intelligence": int, "Wisdom": wis, "Charisma": cha}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
@bot.hybrid_command()
async def ping(ctx):
    await ctx.send(f"> Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def newgame(ctx):
    register_message = await ctx.send("Please react to this message to be registered as a player!")
    for emoji in emojis.values():
        await register_message.add_reaction(emoji)
    db["registry"].append(register_message.id)
    update_db()

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def sectors(ctx):
    grouped_data = {}
    for key in db["stats"].keys():
        value = db["stats"][key]["Sector"]
        if value not in grouped_data:
            grouped_data[value] = []
        grouped_data[value].append(key)
    
    grouped_data = dict(sorted(grouped_data.items()))
    
    embed = discord.Embed(title="List")
    for value, keys in grouped_data.items():
        keys_str = "\n".join(keys)
        embed.add_field(name=value, value=keys_str, inline=False)
    await ctx.send(embed=embed)

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def move(ctx, user: discord.User, sector: discord.TextChannel):
    if user.name in db["stats"].keys():
        member = await ctx.guild.fetch_member(user.id)
        for role in sector_list.values():
            await member.remove_roles(ctx.guild.get_role(role))
        try:
            await member.add_roles(ctx.guild.get_role(sector_list[sector.name]))
            db["stats"][user.name]["Sector"] = sector.name
            await ctx.send(f"{user.name} moved to {sector.name}")
        except KeyError:
            await ctx.send("Error! No such sector!")
    else:
        await ctx.send("This user is not registered!")
    update_db()

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def register(ctx, user: discord.User, class_name: str, sector: discord.TextChannel, str_stat: int, dex_stat: int, con_stat: int, int_stat: int, wis_stat: int, cha_stat: int):
    if user.name not in db["stats"].keys():
        await ctx.send("This user is not playing!")
        return

    new_player = Player(user.name, class_name, sector.name, str_stat, dex_stat, con_stat, int_stat, wis_stat, cha_stat)
    db["stats"][user.name] = new_player
    await ctx.send(f"Player {user.name} has been registered with the stats provided.")
    update_db()

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def stats(ctx, user: discord.User=None):
    if not user:
        user = ctx.author
    if user.name in db["stats"].keys():
        embed = discord.Embed(title=f"{user.name}'s Stats:", color=discord.Color.blue())
        for key, value in db["stats"][str(user.name)].items():
            embed.add_field(name=key, value=value)

        await ctx.send(embed=embed)
    else:
        await ctx.send("No stats found for this user!")

@bot.hybrid_command()
async def roll(ctx, sides: int=None):
    if not sides or sides not in [4, 6, 8, 10, 12, 20]:
        await ctx.send("Incorrect usage! Should be: !roll [4,6,8,10,12,20]")
        return
    else:
        embed = discord.Embed(title=f"{sides}-Sided Dice Rolls:", color=discord.Color.blurple())
        for i in range(6):
            embed.add_field(name=f"Dice {i+1}", value=str(random.randint(1, sides) + 12))
        await ctx.send(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.id in db["registry"] and user.name not in db["stats"].keys():
        member = await reaction.message.guild.fetch_member(user.id)
        for role in sector_list.values():
            await member.remove_roles(reaction.message.guild.get_role(role))

        my_sector = random.choice(list(sector_list.keys()))
        await member.add_roles(reaction.message.guild.get_role(sector_list[my_sector]))

        sides = 4
        statistics = []
        for _ in range(6):
            statistics.append(random.randint(1, sides) + 12)

        statistics.sort(reverse=True)
        match reaction.emoji.name:
            case "fighter":
                db["stats"][user.name] = Player(user.name, "Fighter", my_sector, statistics[0], statistics[1], statistics[2], statistics[5], statistics[4], statistics[3])
            case "rogue":
                db["stats"][user.name] = Player(user.name, "Rogue", my_sector, statistics[1], statistics[0], statistics[2], statistics[4], statistics[3], statistics[5])
            case "cleric":
                db["stats"][user.name] = Player(user.name, "Cleric", my_sector, statistics[4], statistics[2], statistics[0], statistics[1], statistics[5], statistics[3])
            case "wizard":
                db["stats"][user.name] = Player(user.name, "Wizard", my_sector, statistics[3], statistics[1], statistics[2], statistics[5], statistics[4], statistics[0])
    update_db()

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

bot.run(os.getenv('TOKEN'))
