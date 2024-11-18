import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO
logger = logging.getLogger(__name__)

# Create bot instance with privileged intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

# Scheduler instance
scheduler = AsyncIOScheduler()

# Poll content for Monday
poll_question = "Can You Attend?"
poll_options = ["Yes", "No"]

# Set your desired timezone
tz = timezone('Europe/Copenhagen')  # Correct timezone for Denmark

# Function to create the poll
async def create_poll():
    channel_id = os.getenv('CHANNEL_ID')
    if channel_id is None:
        logger.error("CHANNEL_ID is not set!")
        return

    try:
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            logger.error("Channel not found. Please check the CHANNEL_ID.")
            return

        poll_message = await channel.send(f"{poll_question}\n" + "\n".join([f"{i + 1}. {option}" for i, option in enumerate(poll_options)]))
        for i in range(len(poll_options)):
            await poll_message.add_reaction(chr(127462 + i))  # Adding emojis as reactions
        logger.info("Poll sent to channel.")
    except Exception as e:
        logger.error(f"An error occurred while sending the poll: {e}")

# Function to send a notification on Wednesday
async def send_wednesday_notification():
    channel_id = os.getenv('CHANNEL_ID')
    if channel_id is None:
        logger.error("CHANNEL_ID is not set!")
        return

    try:
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            logger.error("Channel not found. Please check the CHANNEL_ID.")
            return

        await channel.send("Reminder: Don't forget to check out the poll and participate!")
        logger.info("Wednesday notification sent to channel.")
    except Exception as e:
        logger.error(f"An error occurred while sending the Wednesday notification: {e}")

# Function to schedule tasks
def schedule_tasks():
    # Create a poll every Monday at 10:00 AM in the specified timezone
    scheduler.add_job(create_poll, 'cron', day_of_week='mon', hour=10, minute=0, timezone=tz)
    # Send a notification every Wednesday at 10:00 AM in the specified timezone
    scheduler.add_job(send_wednesday_notification, 'cron', day_of_week='wed', hour=18, minute=0, timezone=tz)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    schedule_tasks()  # Start scheduling tasks
    scheduler.start()  # Start the scheduler

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))

