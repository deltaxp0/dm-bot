import os, discord, random, json
from discord.ext import commands
from dotenv import load_dotenv
from modal import RegisterModal
from database import *

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=intents)

async def setup_hook() -> None:  # This function is automatically called before the bot starts
    await bot.tree.sync()   # This function is used to sync the slash commands with Discord it is mandatory if you want to use slash commands

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()
    
@bot.hybrid_command()
async def ping(ctx):
    await ctx.send(f"> Pong! {round(bot.latency * 1000)}ms")

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

@bot.tree.command()
async def register(interaction: discord.Interaction):
    if interaction.user.id not in db['registry']:
        await interaction.response.send_modal(RegisterModal())
    else:
        await interaction.response.send_message("You have already registered!", ephemeral=True)

@bot.command()
@commands.has_role("Coding Department")
async def data(ctx):
    await ctx.send(db)

@bot.command()
@commands.has_role("Coding Department")
async def stop(ctx):
    await ctx.send("Stopping...")
    bot.close()
    exit(0)


@bot.command()
@commands.has_role("Coding Department")
async def reset(ctx):
    await ctx.send("Reseting db...")
    global db
    db = reset_db()

bot.run(os.getenv('TOKEN'))
