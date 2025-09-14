import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
import webserver

load_dotenv()   #loads file .env content
token = os.getenv('DISCORD_TOKEN')  # gets the token from the .env file
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')       #create the file bot log history

#Bot permisions
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True        # needed for on_reaction_add
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)  #create the bot with the prefix '!'

@bot.event
async def on_ready():   # async is important for discord bots, so it doesnt get stuck on a function and miss other events
    print(f"Logged in as {bot.user.name} - {bot.user.id} [is online!]")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for !help"), status=discord.Status.online)
    # Load modules
    await bot.load_extension("cogs.bot_commands")
    await bot.load_extension("cogs.bot_events")
    
webserver.keep_alive()  # starts the webserver to keep the bot alive
bot.run(token, log_handler=handler, log_level=logging.INFO) # starts the bot and inicializes the log file