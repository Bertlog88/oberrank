import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

RANKS_FILE = "ranks.json"
MESSAGE_ID_FILE = "rank_message_id.txt"

VALID_RANKS = [
    f"{tier} {i}" for tier in [
        "bronze", "silver", "gold", "platinum", "diamond", "master", "grandmaster"
    ] for i in range(1, 6)
]

ranks = {}

if os.path.exists(RANKS_FILE):
    with open(RANKS_FILE, "r") as f:
        ranks = json.load(f)

def save_ranks():
    with open(RANKS_FILE, "w") as f:
        json.dump(ranks, f)

def get_rank_message():
    if not ranks:
        return "Current ranks: (none set)"
    return "Current ranks:\n" + "\n".join(f"{account}: {rank}" for account, rank in ranks.items())

async def update_rank_message(channel):
    message_id = None
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            try:
                message_id = int(f.read().strip())
            except ValueError:
                pass

    content = get_rank_message()

    if message_id:
        try:
            message = await channel.fetch_message(message_id)
            await message.edit(content=content)
            return
        except discord.NotFound:
            pass

    msg = await channel.send(content)
    with open(MESSAGE_ID_FILE, "w") as f:
        f.write(str(msg.id))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                await update_rank_message(channel)
                break
            except discord.Forbidden:
                continue

@bot.command()
async def setrank(ctx, account: str, *, rank: str):
    rank = rank.lower()
    if rank not in VALID_RANKS:
        await ctx.send(f"Invalid rank. Valid ranks are: {', '.join(VALID_RANKS)}")
        return

    if account not in ranks:
        await ctx.send(f"Account '{account}' not found. Use `!add {account} {rank}` to add it.")
        return

    ranks[account] = rank
    save_ranks()
    await update_rank_message(ctx.channel)
    await ctx.send(f"Updated rank for {account} to {rank}.")

@bot.command()
async def add(ctx, account: str, *, rank: str):
    rank = rank.lower()
    if rank not in VALID_RANKS:
        await ctx.send(f"Invalid rank. Valid ranks are: {', '.join(VALID_RANKS)}")
        return

    ranks[account] = rank
    save_ranks()
    await update_rank_message(ctx.channel)
    await ctx.send(f"Added {account} with rank {rank}.")

@bot.command()
async def deleterank(ctx, account: str):
    if account in ranks:
        del ranks[account]
        save_ranks()
        await update_rank_message(ctx.channel)
        await ctx.send(f"Deleted rank for {account}.")
    else:
        await ctx.send(f"Account '{account}' not found.")

@bot.command()
async def rank(ctx):
    await ctx.send(get_rank_message())

bot.run(TOKEN)
