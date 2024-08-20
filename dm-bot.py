import os, discord, random, json
from discord.ext import commands
from dotenv import load_dotenv, dotenv_values

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

load_dotenv()

bot = commands.Bot(command_prefix=".", intents=intents)

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
        db["stats"] = {int(k): v for k, v in db["stats"].items()}
else:
    reset_db()

def Player(name, class_name, sect, str, dex, con, int, wis, cha):
    return {
        "Name": name,
        "Class": class_name,
        "Sector": sect,
        "Strength": str,
        "Dexterity": dex,
        "Constitution": con,
        "Intelligence": int,
        "Wisdom": wis,
        "Charisma": cha
    }

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
        grouped_data[value].append(db["stats"][key]["Name"])
    
    grouped_data = dict(sorted(grouped_data.items()))
    
    embed = discord.Embed(title="List")
    for value, keys in grouped_data.items():
        keys_str = "\n".join(keys)
        embed.add_field(name=value, value=keys_str, inline=False)
    await ctx.send(embed=embed)

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def move(ctx, user: discord.User, sector: discord.TextChannel):
    if user.id in db["stats"]:
        member = await ctx.guild.fetch_member(user.id)
        for role in sector_list.values():
            await member.remove_roles(ctx.guild.get_role(role))
        try:
            await member.add_roles(ctx.guild.get_role(sector_list[sector.name]))
            db["stats"][user.id]["Sector"] = sector.name
            await ctx.send(f"{user.name} moved to {sector.name}")
        except KeyError:
            await ctx.send("Error! No such sector!")
    else:
        await ctx.send("This user is not registered!")
    update_db()

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def register(ctx, user: discord.User, class_name: str, sector: discord.TextChannel, str_stat: int, dex_stat: int, con_stat: int, int_stat: int, wis_stat: int, cha_stat: int):
    if user.id in db["stats"]:
        await ctx.send("This user is already registered!")
        return

    new_player = Player(user.id, user.name, class_name, sector.name, str_stat, dex_stat, con_stat, int_stat, wis_stat, cha_stat)
    db["stats"][user.id] = new_player
    await ctx.send(f"Player {user.name} has been registered with the stats provided.")
    update_db()

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def stats(ctx, user: discord.User=None):
    if not user:
        user = ctx.author
    if user.id in db["stats"]:
        embed = discord.Embed(title=f"{user.name}'s Stats:", color=discord.Color.blue())
        for key, value in db["stats"][user.id].items():
            if key != "User ID":
                if key == "Sector":
                    channel = discord.utils.get(ctx.guild.channels, name=db["stats"][user.id]["Sector"])
                    embed.add_field(name="Sector", value=f"<#{channel.id}>")
                else:
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
    if reaction.message.id in db["registry"] and user.id not in db["stats"]:
        member = await reaction.message.guild.fetch_member(user.id)
        for role in sector_list.values():
            if role in member.roles:
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
                db["stats"][user.id] = Player(user.name, "Fighter", my_sector, statistics[0], statistics[1], statistics[2], statistics[5], statistics[4], statistics[3])
            case "rogue":
                db["stats"][user.id] = Player(user.name, "Rogue", my_sector, statistics[1], statistics[0], statistics[2], statistics[4], statistics[3], statistics[5])
            case "cleric":
                db["stats"][user.id] = Player(user.name, "Cleric", my_sector, statistics[4], statistics[2], statistics[0], statistics[1], statistics[5], statistics[3])
            case "wizard":
                db["stats"][user.id] = Player(user.name, "Wizard", my_sector, statistics[3], statistics[1], statistics[2], statistics[5], statistics[4], statistics[0])
    '''elif user.id in db["stats"]:
        member = await reaction.message.guild.fetch_member(user.id)
        if reaction.message.guild.get_role(db["stats"][user.id]['Sector']) not in member.roles:
            await member.add_roles(reaction.message.guild.get_role(sector_list[db["stats"][user.id]['Sector']]))'''
    update_db()
# Rasty: added assign command to sync roles with the db
@bot.hybrid_command()
@commands.has_role("Coding Department")
async def assign(ctx):
    db["stats"] = {int(k): v for k, v in db["stats"].items()}    
    for k, v in db["stats"].items():
        member = await ctx.guild.fetch_member(k)
        for role in sector_list.values():
            if role in [r.id for r in member.roles]:
                await member.remove_roles(ctx.guild.get_role(role))
        await member.add_roles(ctx.guild.get_role(sector_list[v["Sector"]]))

class CharacterButton(discord.ui.Button):
    def __init__(self, character_name, stats, color):
        super().__init__(label=character_name, style=color)
        self.stats = stats
        self.character_name = character_name
    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        if user.id not in db["stats"]:
            member = await interaction.guild.fetch_member(user.id)
            for role in sector_list.values():
                if role in member.roles:
                    await member.remove_roles(interaction.guild.get_role(role))

            my_sector = random.choice(list(sector_list.keys()))
            await member.add_roles(interaction.guild.get_role(sector_list[my_sector]))
            db["stats"][user.id] = Player(user.name, self.character_name, my_sector, *self.stats)
            await interaction.response.send_message(f"You have chosen {self.character_name}!", ephemeral=True)
            update_db()
        else:
            await interaction.response.send_message("You are already registered.", ephemeral=True)

class CharacterSelectionView(discord.ui.View):
    def __init__(self, character_arrangement):
        super().__init__()
        colors = [
            discord.ButtonStyle.gray,
            discord.ButtonStyle.blurple,
            discord.ButtonStyle.red,
            discord.ButtonStyle.success
        ]
        for key, value in character_arrangement.items():
            self.add_item(CharacterButton(value["class"],stats=value["stats"], color=colors[value["index"]]))
      
@bot.hybrid_command()
@commands.has_role("Coding Department")
async def btn(ctx):
    sides = 4
    statistics = [random.randint(1, sides) + 12 for _ in range(6)]
    statistics.sort(reverse=True)

    character_arrangement = {
        "fighter": {
            "index": 0,
            "class": "Fighter",
            "stats": [statistics[0], statistics[1], statistics[2], statistics[5], statistics[4], statistics[3]]
        },
        "rogue": {
            "index": 1,
            "class": "Rogue",
            "stats": [statistics[1], statistics[0], statistics[2], statistics[4], statistics[3], statistics[5]]
        },
        "cleric": {
            "index": 2,
            "class": "Cleric",
            "stats": [statistics[4], statistics[2], statistics[0], statistics[1], statistics[5], statistics[3]]
        },
        "wizard": {
            "index": 3,
            "class": "Wizard",
            "stats": [statistics[3], statistics[1], statistics[2], statistics[5], statistics[4], statistics[0]]
        }
    }

    embed = discord.Embed(title="Character Selection", color=discord.Color.blue())
    embed.add_field(name="\u200b", value="Choose your character:", inline=False)
    for key, value in character_arrangement.items():
        embed.add_field(name="\u200b", value=value['class'], inline=False)

    view = CharacterSelectionView(character_arrangement)
    
    register_message = await ctx.send(embed=embed, view=view)
    db["registry"].append(register_message.id)
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
    await ctx.send(f"```json\n{json.dumps(db, indent=2)}```")

bot.run(os.getenv('TOKEN'))