import os, discord, random, json
from dotenv import load_dotenv, dotenv_values

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=intents)

client = discord.Client(intents=intents)

players = {}
stats = {}
ids = {}

sectors = {}
registered_messages = []

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

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    server = bot.get_guild(1272746089224867921)
    sectors['sector-1'] = server.get_role(1274803528690438145)
    sectors['sector-2'] = server.get_role(1274803583111663618)
    sectors['sector-3'] = server.get_role(1274803643308052490)

@bot.command()
async def newgame(ctx):
    register_message = await ctx.send("Please react to this message to be registered as a player!")
    await register_message.add_reaction('⚔️')
    await register_message.add_reaction('🗡️')
    await register_message.add_reaction('🍾')
    await register_message.add_reaction('🧙‍♂️')
    registered_messages.append(register_message)

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def list_sectors(ctx):
    grouped_data = {}
    for key, value in players.items():
        if value not in grouped_data:
            grouped_data[value] = []
        grouped_data[value].append(key)

    embed = discord.Embed(title="List")
    for value, keys in grouped_data.items():
        keys_str = "\n".join(keys)
        embed.add_field(name=value, value=keys_str, inline=False)
    await ctx.send(embed=embed)

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def move(ctx, user: discord.User, sector: discord.TextChannel):
    if user.name in players:
        member = await ctx.guild.fetch_member(user.id)
        for role in sectors.values():
            await member.remove_roles(role)
        try:
            await member.add_roles(sectors[sector.name])
            players[user.name] = sector.name
            await ctx.send(f"{user.name} moved to {sector.name}")
        except KeyError:
            await ctx.send("Error! No such sector!")
    else:
        await ctx.send("This user is not registered!")

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def register(ctx, name: str, class_name: str, str_stat: int, dex_stat: int, con_stat: int, int_stat: int, wis_stat: int, cha_stat: int):
    if name not in players:
        await ctx.send("This user is not playing!")
        return

    new_player = Player(name, class_name, str_stat, dex_stat, con_stat, int_stat, wis_stat, cha_stat)
    stats[name] = new_player
    await ctx.send(f"Player {name} has been registered with the stats provided.")

@bot.hybrid_command()
@commands.has_role("D&D Staff")
async def show_stats(ctx, user: discord.User):
    if user.name in stats:
        player = stats[user.name]
        embed = discord.Embed(title=f"{user.name}'s Stats:", color=discord.Color.blue())
        embed.add_field(name="Name", value=player.name)
        embed.add_field(name="Class", value=player.class_name)
        embed.add_field(name="Strength", value=player.str)
        embed.add_field(name="Dexterity", value=player.dex)
        embed.add_field(name="Constitution ", value=player.con)
        embed.add_field(name="Intelligence", value=player.int)
        embed.add_field(name="Wisdom", value=player.wis)
        embed.add_field(name="Charisma", value=player.cha)

        await ctx.send(embed=embed)
    else:
        await ctx.send("No stats found for this user!")

@bot.hybrid_command()
async def roll(ctx, sides: int):
    if sides not in [4, 6, 8, 10, 12, 20]:
        await ctx.send("Incorrect usage! Should be: !roll [4,6,8,10,12,20]")
        return
    else:
        embed = discord.Embed(title=f"{sides}-Sided Dice Rolls:", color=discord.Color.blurple())
        for i in range(6):
            embed.add_field(name=f"Dice {i+1}", value=str(random.randint(1, sides) + 12))
        await ctx.send(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message == registered_messages[0] and user.name not in players:
        member = await reaction.message.guild.fetch_member(user.id)
        for role in sectors.values():
            await member.remove_roles(role)

        ids[user.name] = user.id
        my_sector = random.choice(list(sectors.keys()))
        players[user.name] = my_sector
        await member.add_roles(sectors[my_sector])

        sides = 4
        statistics = []
        for _ in range(6):
            statistics.append(random.randint(1, sides) + 12)

        statistics.sort(reverse=True)
        match reaction.emoji:
            case '⚔️':
                stats[user.name] = Player(user.name, "Fighter", statistics[0], statistics[1], statistics[2], statistics[5], statistics[4], statistics[3])
            case '🗡️':
                stats[user.name] = Player(user.name, "Rogue", statistics[1], statistics[0], statistics[2], statistics[4], statistics[3], statistics[5])
            case '🍾':
                stats[user.name] = Player(user.name, "Cleric", statistics[4], statistics[2], statistics[0], statistics[1], statistics[5], statistics[3])
            case '🧙‍♂️':
                stats[user.name] = Player(user.name, "Wizard", statistics[3], statistics[1], statistics[2], statistics[5], statistics[4], statistics[0])

bot.run(os.getenv('TOKEN'))
