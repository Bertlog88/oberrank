import os
import discord
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set.")

ranks = {
    "account1": "gm3",
    "account2": "gm5",
    "account3": "master",
    "succubus": "unranked"  # Add succubus account here with a default rank
}

RANK_MSG_FILE = "rank_message_id.txt"

async def update_rank_message(channel):
    rank_text = "\n".join([f"{account}: {rank}" for account, rank in ranks.items()])
    content = f"Current ranks:\n{rank_text}"

    message_id = None
    if os.path.exists(RANK_MSG_FILE):
        with open(RANK_MSG_FILE, "r") as f:
            try:
                message_id = int(f.read().strip())
            except ValueError:
                print("Could not read message ID from file.")
                message_id = None

    if message_id:
        try:
            msg = await channel.fetch_message(message_id)
            await msg.edit(content=content)
            print(f"Edited message ID {message_id}")
            return
        except discord.NotFound:
            print("Stored message ID not found. Will send new message.")
        except discord.HTTPException as e:
            print(f"HTTP error while editing message: {e}")

    new_msg = await channel.send(content)
    with open(RANK_MSG_FILE, "w") as f:
        f.write(str(new_msg.id))
    print(f"Sent new message with ID {new_msg.id}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # !setrank command
    if message.content.startswith("!setrank"):
        parts = message.content.split(" ")
        if len(parts) == 3:
            account = parts[1].lower()  # Ensure case-insensitive matching
            rank = parts[2]
            print(f"Received account: '{account}', rank: '{rank}'")  # Debug output
            if account in ranks:
                ranks[account] = rank
                await message.channel.send(f"{account} rank updated to {rank}.")
                await update_rank_message(message.channel)
            else:
                await message.channel.send(f"Account {account} not found. Current accounts: {list(ranks.keys())}")  # Debug output
        else:
            await message.channel.send("Usage: !setrank <account> <rank>")

    # !deleterank command
    if message.content.startswith("!deleterank"):
        parts = message.content.split(" ")
        if len(parts) == 2:
            account = parts[1]
            if account in ranks:
                del ranks[account]
                await message.channel.send(f"{account}'s rank deleted.")
                await update_rank_message(message.channel)
            else:
                await message.channel.send(f"Account {account} not found.")
        else:
            await message.channel.send("Usage: !deleterank <account>")

    # !viewranks command
    if message.content == "!viewranks":
        await update_rank_message(message.channel)

    # !add command (adds a new account)
    if message.content.startswith("!add"):
        parts = message.content.split(" ")
        if len(parts) == 3:
            account = parts[1].lower()  # Ensure case-insensitive matching
            rank = parts[2]
            if account in ranks:
                await message.channel.send(f"Account {account} already exists with rank {ranks[account]}.")
            else:
                ranks[account] = rank
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
