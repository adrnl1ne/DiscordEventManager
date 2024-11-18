import discord
from discord.ext import commands
import os  # Add this import at the top of the file

# Create bot instance with privileged intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    channel_id = os.getenv('CHANNEL_ID')
    print("CHANNEL_ID:", channel_id)  # Debugging line
    channel = bot.get_channel(int(channel_id)) if channel_id else None
    if channel:
        await channel.send('Hello, I am your bot!')  # Send a message to the channel
        print("Message sent to channel.")
    else:
        print("Channel not found or CHANNEL_ID is not set!")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))

# Scheduler to run tasks at specific times
# scheduler = AsyncIOScheduler()

# Channel ID where the bot will post
# CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Replace with your actual channel ID from environment variable

# Poll content for Monday
# poll_question = "Can You Attend?"
# poll_options = ["Yes", "No"]

# Function to create the poll
# async def create_poll():
#     channel = bot.get_channel(CHANNEL_ID)
#     poll_message = await channel.send(f"{poll_question}\n" + "\n".join([f"{i + 1}. {option}" for i, option in enumerate(poll_options)]))
#     for i in range(len(poll_options)):
#         await poll_message.add_reaction(chr(127462 + i))  # Adding emojis as reactions

# Function to send a notification on Wednesday
# async def send_wednesday_notification():
#     channel = bot.get_channel(CHANNEL_ID)
#     await channel.send("Reminder: Don't forget to check out the poll and participate!")

# Function to schedule tasks
# def schedule_tasks():
#     # Create a poll every Monday at 10:00 AM
#     scheduler.add_job(create_poll, 'cron', day_of_week='mon', hour=10, minute=0)
#     # Send a notification every Wednesday at 10:00 AM
#     scheduler.add_job(send_wednesday_notification, 'cron', day_of_week='wed', hour=10, minute=0)
