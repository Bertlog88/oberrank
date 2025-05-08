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
    "account3": "master"
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
                pass

    # Try to edit the existing message
    if message_id:
        try:
            msg = await channel.fetch_message(message_id)
            await msg.edit(content=content)
            return
        except discord.NotFound:
            pass  # message no longer exists
        except discord.HTTPException:
            pass  # failed to edit message for another reason

    # If no message found, send a new one and store its ID
    new_msg = await channel.send(content)
    with open(RANK_MSG_FILE, "w") as f:
        f.write(str(new_msg.id))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!setrank"):
        parts = message.content.split(" ")
        if len(parts) == 3:
            account = parts[1]
            rank = parts[2]
            if account in ranks:
                ranks[account] = rank
                await message.channel.send(f"{account} rank updated to {rank}.")
                await update_rank_message(message.channel)
            else:
                await message.channel.send(f"Account {account} not found.")
        else:
            await message.channel.send("Usage: !setrank <account> <rank>")

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

    if message.content == "!viewranks":
        await update_rank_message(message.channel)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
