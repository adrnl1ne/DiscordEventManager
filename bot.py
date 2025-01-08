import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
import asyncio  # Import asyncio for delay functionality
import json  # Import JSON for data persistence

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO
logger = logging.getLogger(__name__)

# Create bot instance with privileged intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix="!", intents=intents)
if not intents.message_content:
    logger.warning("message_content intent is disabled; bot may not function fully.")

# Poll content for Monday
poll_question = "Can You Attend?"
poll_options = ["Yes", "No"]

# Global variables to track last execution dates
last_poll_date = None
last_notification_date = None

# Function to load last execution dates from a JSON file
def load_last_execution_dates():
    try:
        with open('last_execution_dates.json', 'r') as f:
            data = json.load(f)
            # Convert string dates to datetime.date objects
            last_poll_date = datetime.strptime(data['last_poll_date'], '%Y-%m-%d').date() if data['last_poll_date'] else None
            last_notification_date = datetime.strptime(data['last_notification_date'], '%Y-%m-%d').date() if data['last_notification_date'] else None
            return {'last_poll_date': last_poll_date, 'last_notification_date': last_notification_date}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading execution dates: {e}")
        return {'last_poll_date': None, 'last_notification_date': None}

# Function to save last execution dates to a JSON file
def save_last_execution_dates(last_poll_date, last_notification_date):
    logger.info("Saving last execution dates to JSON")  # Debugging output
    with open('last_execution_dates.json', 'w') as f:
        json.dump({
            'last_poll_date': last_poll_date.strftime('%Y-%m-%d') if last_poll_date else None,
            'last_notification_date': last_notification_date.strftime('%Y-%m-%d') if last_notification_date else None
        }, f)

# Function to initialize the JSON file with default values
def initialize_execution_dates():
    default_data = {
        'last_poll_date': None,
        'last_notification_date': None
    }
    with open('last_execution_dates.json', 'w') as f:
        json.dump(default_data, f)

# Function to calculate the next Thursday
def get_next_thursday():
    today = datetime.now()
    days_ahead = (3 - today.weekday()) % 7  # 3 represents Thursday (Monday is 0)
    if days_ahead == 0:  # If today is already Thursday, get the next one
        days_ahead = 7
    next_thursday = today + timedelta(days=days_ahead)
    return next_thursday.strftime("%A, %B %d, %Y")  # Format as 'Thursday, Month Day, Year'

# Function to create the poll
async def create_poll(channel):
    global last_poll_date  # Declare as global to modify the variable
    try:
        # Define the emojis
        emojis = ["👍", "👎"]
        
         # Check that the number of emojis matches the number of poll options
        assert len(emojis) == len(poll_options), "Mismatch between emojis and poll options."

        # Calculate next Thursday's date
        next_thursday = get_next_thursday()
        
        # Create the poll message with the date, time, and number of games
        poll_message = await channel.send(
            f"**{poll_question}**\n\n"  # Bold the question
            f"📅 **Next Practice Date:** {next_thursday}\n"
            f"⏰ **Time:** 19:30\n"
            f"🎮 **Number of Games:** 3\n\n"
            + "\n\n".join([f"{emojis[i]} **{poll_options[i]}**" for i in range(len(poll_options))])  # Add new line between options
        )
        
        # Add reactions for each option
        for emoji in emojis:
            await poll_message.add_reaction(emoji)
        
        logger.info("Poll sent to channel.")
        
        # Update the last poll date
        last_poll_date = datetime.now().date()
        logger.info(f"Updating last_poll_date to {last_poll_date}")  # Debugging output
        
        # Save to JSON
        save_last_execution_dates(last_poll_date, last_notification_date)
    except Exception as e:
        logger.error(f"An error occurred while sending the poll: {e}. Channel: {channel.id}")

# Function to send a notification on Thursday
async def send_thursday_notification(channel):
    global last_notification_date  # Declare as global to modify the variable
    try:
        await channel.send("Reminder: Don't forget to check out the poll and participate!")
        logger.info("Thursday notification sent to channel.")
        last_notification_date = datetime.now().date()  # Update the last notification date
        logger.info(f"Updating last_notification_date to {last_notification_date}")  # Debugging output
        save_last_execution_dates(last_poll_date, last_notification_date)  # Save to JSON
    except Exception as e:
        logger.error(f"An error occurred while sending the Thursday notification: {e}")

@bot.event
async def on_ready():
    if not os.getenv('DISCORD_TOKEN') or not os.getenv('CHANNEL_ID'):
        logger.error("Missing DISCORD_TOKEN or CHANNEL_ID in environment variables.")
        return

    global last_poll_date, last_notification_date  # Declare as global to modify the variables
    logger.info(f'Logged in as {bot.user}')
    channel_id = os.getenv('CHANNEL_ID')
    if channel_id is None:
        logger.error("CHANNEL_ID is not set!")
        return

    channel = bot.get_channel(int(channel_id))
    if channel is None:
        logger.error(f"Channel with ID {channel_id} not found or bot lacks permission.")
        return

    # Initialize the JSON file if it doesn't exist
    if not os.path.exists('last_execution_dates.json'):
        initialize_execution_dates()  # Create the file with default values

    # Load last execution dates
    execution_dates = load_last_execution_dates()
    last_poll_date = execution_dates['last_poll_date']
    last_notification_date = execution_dates['last_notification_date']

    # Get the current date
    current_date = datetime.now().date()

    # Create the poll only on Mondays and if it hasn't been created today
    if datetime.now().strftime('%A') == 'Monday' and (last_poll_date is None or last_poll_date < current_date):
        await create_poll(channel)  # Create the poll immediately when the bot starts

    # Send the notification only on Thursdays and if it hasn't been sent today
    if datetime.now().strftime('%A') == 'Thursday' and (last_notification_date is None or last_notification_date < current_date):
        await send_thursday_notification(channel)  # Send the Thursday notification when the bot starts

    # Add a delay of 5 minutes before shutting down the bot
    asyncio.create_task(shutdown_after_delay(300))

async def shutdown_after_delay(delay):
    await asyncio.sleep(delay)
    logger.info("Shutting down the bot after delay.")
    await bot.close()

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
