import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import asyncio  # Import asyncio for delay functionality
import json  # Import JSON for data persistence
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO
logger = logging.getLogger(__name__)

# Create bot instance with privileged intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

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
    except (FileNotFoundError, json.JSONDecodeError):
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


# Function to calculate the next Wednesday
def get_next_wednesday():
    today = datetime.now()
    days_ahead = (2 - today.weekday()) % 7  # 2 represents Wednesday (Monday is 0)
    if days_ahead == 0:  # If today is already Wednesday, get the next one
        days_ahead = 7
    next_wednesday = today + timedelta(days=days_ahead)
    return next_wednesday.strftime("%A, %B %d, %Y")  # Format as 'Wednesday, Month Day, Year'

# Function to create the poll
async def create_poll(channel):
    global last_poll_date  # Declare as global to modify the variable
    try:
        # Define the emojis
        emojis = ["👍", "👎"]
        
        # Calculate next Wednesday's date
        next_wednesday = get_next_wednesday()
        
        # Create the poll message with the date, time, and number of games
        poll_message = await channel.send(
            f"**{poll_question}**\n\n"  # Bold the question
            f"📅 **Next Practice Date:** {next_wednesday}\n"
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
        logger.error(f"An error occurred while sending the poll: {e}")


# Function to send a notification on Wednesday
async def send_wednesday_notification(channel):
    global last_notification_date  # Declare as global to modify the variable
    try:
        await channel.send("Reminder: Don't forget to check out the poll and participate!")
        logger.info("Wednesday notification sent to channel.")
        last_notification_date = datetime.now().date()  # Update the last notification date
        logger.info(f"Updating last_notification_date to {last_notification_date}")  # Debugging output
        save_last_execution_dates(last_poll_date, last_notification_date)  # Save to JSON
    except Exception as e:
        logger.error(f"An error occurred while sending the Wednesday notification: {e}")

@bot.event
async def on_ready():
    global last_poll_date, last_notification_date  # Declare as global to modify the variables
    logger.info(f'Logged in as {bot.user}')
    channel_id = os.getenv('CHANNEL_ID')
    if channel_id is None:
        logger.error("CHANNEL_ID is not set!")
        return

    channel = bot.get_channel(int(channel_id))
    if channel is None:
        logger.error("Channel not found. Please check the CHANNEL_ID.")
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

    # Send the notification only on Wednesdays and if it hasn't been sent today
    if datetime.now().strftime('%A') == 'Wednesday' and (last_notification_date is None or last_notification_date < current_date):
        await send_wednesday_notification(channel)  # Send the Wednesday notification when the bot starts

        
    # Add a delay of 5 minutes before shutting down the bot
    await asyncio.sleep(300)
    await bot.close()

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))

