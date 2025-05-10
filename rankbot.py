import os
import json
import discord

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set.")

RANKS_FILE = "ranks.json"
RANK_MSG_FILE = "rank_message_id.txt"

# Load ranks from file
def load_ranks():
    if os.path.exists(RANKS_FILE):
        with open(RANKS_FILE, "r") as f:
            return json.load(f)
    return {}

# Save ranks to file
def save_ranks():
    with open(RANKS_FILE, "w") as f:
        json.dump(ranks, f, indent=2)

ranks = load_ranks()

async def update_rank_message(channel):
    rank_text = "\n".join([f"{account}: {rank}" for account, rank in ranks.items()])
    content = f"Current ranks:\n{rank_text}" if rank_text else "Current ranks:\n(No accounts yet)"

    message_id = None
    if os.path.exists(RANK_MSG_FILE):
        with open(RANK_MSG_FILE, "r") as f:
            try:
                message_id = int(f.read().strip())
            except ValueError:
                message_id = None

    if message_id:
        try:
            msg = await channel.fetch_message(message_id)
            await msg.edit(content=content)
            return
        except discord.NotFound:
            pass

    new_msg = await channel.send(content)
    with open(RANK_MSG_FILE, "w") as f:
        f.write(str(new_msg.id))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # !setrank <account> <rank>
    if message.content.startswith("!setrank"):
        parts = message.content.split(" ")
        if len(parts) == 3:
            account = parts[1].lower()
            rank = parts[2]
            if account in ranks:
                ranks[account] = rank
                save_ranks()
                await message.channel.send(f"{account} rank updated to {rank}.")
                await update_rank_message(message.channel)
            else:
                await message.channel.send(f"Account {account} not found.")
        else:
            await message.channel.send("Usage: !setrank <account> <rank>")

    # !deleterank <account>
    if message.content.startswith("!deleterank"):
        parts = message.content.split(" ")
        if len(parts) == 2:
            account = parts[1].lower()
            if account in ranks:
                del ranks[account]
                save_ranks()
                await message.channel.send(f"{account}'s rank deleted.")
                await update_rank_message(message.channel)
            else:
                await message.channel.send(f"Account {account} not found.")
        else:
            await message.channel.send("Usage: !deleterank <account>")

    # !viewranks
    if message.content == "!viewranks":
        await update_rank_message(message.channel)

    # !add <account> <rank>
    if message.content.startswith("!add"):
        parts = message.content.split(" ")
        if len(parts) == 3:
            account = parts[1].lower()
            rank = parts[2]
            if account in ranks:
                await message.channel.send(f"Account {account} already exists with rank {ranks[account]}.")
            else:
                ranks[account] = rank
                save_ranks()
                await message.channel.send(f"Account {account} added with rank {rank}.")
                await update_rank_message(message.channel)
        else:
            await message.channel.send("Usage: !add <account> <rank>")

@bot.event
async def on_ready():
    if not hasattr(bot, 'started'):
        bot.started = True
        print(f"Logged in as {bot.user}")

bot.run(TOKEN)
