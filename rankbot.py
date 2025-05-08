import os
import discord

intents = discord.Intents.default()
intents.message_content = True  # Ensure the bot can read messages

# Create the bot instance with the necessary intents
bot = discord.Client(intents=intents)

# Access the Discord bot token from the environment variable
TOKEN = os.getenv('DISCORD_TOKEN')

# Ensure that the token was retrieved
if not TOKEN:
    raise ValueError("No token found! Please set the DISCORD_TOKEN environment variable.")

# Define some ranks (example)
ranks = {
    "account1": "gm3",
    "account2": "gm5",
    "account3": "master"
}

# Command to update rank
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Command to set the rank
    if message.content.startswith("!setrank"):
        parts = message.content.split(" ")
        if len(parts) == 3:
            account = parts[1]
            rank = parts[2]
            if account in ranks:
                ranks[account] = rank
                await message.channel.send(f"{account} rank updated to {rank}.")
                await update_rank_message(message)
            else:
                await message.channel.send(f"Account {account} not found.")
        else:
            await message.channel.send("Invalid command format. Use: !setrank <account> <rank>")

    # Command to delete the rank
    if message.content.startswith("!deleterank"):
        parts = message.content.split(" ")
        if len(parts) == 2:
            account = parts[1]
            if account in ranks:
                del ranks[account]  # Delete the account's rank
                await message.channel.send(f"{account}'s rank has been deleted.")
                await update_rank_message(message)
            else:
                await message.channel.send(f"Account {account} not found.")
        else:
            await message.channel.send("Invalid command format. Use: !deleterank <account>")

    # Command to view ranks
    if message.content == "!viewranks":
        await view_ranks(message)

# Function to view ranks
async def view_ranks(message):
    rank_list = "\n".join([f"{account}: {rank}" for account, rank in ranks.items()])
    await message.channel.send(f"Current ranks:\n{rank_list}")

# Function to update the rank message
async def update_rank_message(message):
    channel = message.channel
    rank_message = "\n".join([f"{account}: {rank}" for account, rank in ranks.items()])
    
    # Search for the existing "Current ranks" message in the channel
    async for msg in channel.history(limit=100):
        if msg.author == bot.user and msg.content.startswith("Current ranks:"):
            # If found, edit the existing message
            await msg.edit(content=f"Current ranks:\n{rank_message}")
            return  # Exit after editing the message

    # If no "Current ranks" message was found, send a new one
    await channel.send(f"Current ranks:\n{rank_message}")

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Bot is ready to receive commands.')

# Run the bot with the token from the environment variable
bot.run(TOKEN)
