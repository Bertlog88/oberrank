import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = 'user_accounts.json'
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        user_data = json.load(f)
else:
    user_data = {}

VALID_RANKS = ['bronze', 'silver', 'gold', 'plat', 'diamond', 'master', 'gm', 'top500']

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(user_data, f, indent=2)

def generate_message(accounts: dict) -> str:
    if not accounts:
        return "No ranks set yet."
    lines = [f"**{name}:** {rank.upper()}" for name, rank in accounts.items()]
    return "\n".join(lines)

@bot.command()
async def setrank(ctx, account: str, rank: str):
    rank = rank.lower()
    account = account.strip()
    if rank not in VALID_RANKS:
        await ctx.send(f"Invalid rank. Valid ranks: {', '.join(VALID_RANKS)}")
        return

    user_id = str(ctx.author.id)
    if user_id not in user_data:
        user_data[user_id] = {"accounts": {}, "message_id": None, "channel_id": None}
    
    user_data[user_id]["accounts"][account] = rank
    save_data()

    try:
        channel_id = user_data[user_id]["channel_id"]
        message_id = user_data[user_id]["message_id"]
        channel = bot.get_channel(channel_id) or await ctx.guild.fetch_channel(channel_id)
        msg = await channel.fetch_message(message_id)
        await msg.edit(content=generate_message(user_data[user_id]["accounts"]))
        await ctx.send("Rank updated.")
        return
    except Exception as e:
        pass  # Message might not exist

    # Send a new message if previous one isn't found
    content = generate_message(user_data[user_id]["accounts"])
    new_msg = await ctx.send(content)
    user_data[user_id]["message_id"] = new_msg.id
    user_data[user_id]["channel_id"] = new_msg.channel.id
    save_data()
    await ctx.send("Rank message created.")

@bot.command()
async def viewranks(ctx):
    user_id = str(ctx.author.id)
    if user_id not in user_data or not user_data[user_id]["accounts"]:
        await ctx.send("You haven’t set any ranks yet.")
        return
    content = generate_message(user_data[user_id]["accounts"])
    await ctx.send(content)

# ✅ Start the bot (replace the token below with your actual bot token)
bot.run("MTM3MDA0NjMwNzM2ODA0MjUxMA.GD8LbP.zyr35qYeYuWU60EOCoJwE8Z0XDU5jq0_krtbpE")
