import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import logging
import sys
import os

os.system('clear')  # clears the terminal (writes the 'clear' command on the terminal to be exact)

# ----------------------------- Logging setup --------------------------------------
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)  # Capture everything, handlers will filter

# Formatter (same for all handlers)
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    "%Y-%m-%d %H:%M:%S"
)

# 1) File handler: INFO and above
info_handler = logging.FileHandler(filename="bot_info.log", encoding="utf-8", mode="w")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

# 2) File handler: EVERYTHING
debug_handler = logging.FileHandler(filename="bot_debug.log", encoding="utf-8", mode="w")
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)

# 3) Terminal handler: only INFO and above
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add all handlers
logger.addHandler(info_handler)
logger.addHandler(debug_handler)
logger.addHandler(console_handler)


# ---------------------------------- Bot Setup ------------------------------------------
load_dotenv()   #loads file .env content
token = os.getenv('DISCORD_TOKEN')  # gets the token from the .env file

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True        # needed for on_reaction_add
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)  #create the bot with the prefix '!'

@bot.event
async def on_ready():   # async is important for discord bots, so it doesnt get stuck on a function and miss other events
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for !help"), status=discord.Status.online)
    logger.info(f"Logged in as {bot.user.name} - {bot.user.id} [is online!]")   # writes on the bot.log
   
async def load_cogs():
    for root, _, files in os.walk("cogs"):
        for filename in files:
            if filename.endswith(".py"):
                # build module path relative to cogs/
                rel_path = os.path.relpath(os.path.join(root, filename), ".")
                module = rel_path.replace(os.path.sep, ".")[:-3]  # "cogs.commands.hello"
                try:
                    await bot.load_extension(module)
                    logger.info(f"✅ Loaded {module}")  # INFO log
                except Exception as e:
                    logger.exception(f"❌ Failed to load {module}: {e}")    # ERROR log
    
async def main():
    async with bot:
        await load_cogs()
        await bot.start(token)
    
    
asyncio.run(main())