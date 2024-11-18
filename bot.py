import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

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

# Function to create the poll
async def create_poll(channel):
    try:
        # Create the poll message
        poll_message = await channel.send(f"{poll_question}\n" + "\n".join([f"{i + 1}. {option}" for i, option in enumerate(poll_options)]))
        # Add reactions for each option
        for i in range(len(poll_options)):
            await poll_message.add_reaction(chr(127462 + i))  # Adding emojis as reactions
        logger.info("Poll sent to channel.")
    except Exception as e:
        logger.error(f"An error occurred while sending the poll: {e}")

# Function to send a notification on Wednesday
async def send_wednesday_notification(channel):
    try:
        await channel.send("Reminder: Don't forget to check out the poll and participate!")
        logger.info("Wednesday notification sent to channel.")
    except Exception as e:
        logger.error(f"An error occurred while sending the Wednesday notification: {e}")

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    channel_id = os.getenv('CHANNEL_ID')
    if channel_id is None:
        logger.error("CHANNEL_ID is not set!")
        return

    channel = bot.get_channel(int(channel_id))
    if channel is None:
        logger.error("Channel not found. Please check the CHANNEL_ID.")
        return

    # Call the create_poll function to create the poll when the bot is ready
    await create_poll(channel)  # Create the poll immediately when the bot starts
    await send_wednesday_notification(channel)  # Send the Wednesday notification when the bot starts

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))

