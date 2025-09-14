#---------------------------------------------------------------------------------------
# Imports
import discord
from discord.ext import commands
from discord.utils import utcnow
import pyrebase
from datetime import datetime, timedelta
import os

#initialize the DataBase 
APIKEY = os.getenv('APIKEY')  # gets the token from the .env file
config = {
    "apiKey": f"{APIKEY}",
    "authDomain": "discordbotdb-6b3e8.firebaseapp.com",
    "projectId": "discordbotdb-6b3e8",
    "databaseURL": "https://discordbotdb-6b3e8-default-rtdb.europe-west1.firebasedatabase.app/",
    "storageBucket": "discordbotdb-6b3e8.firebasestorage.app",
    "messagingSenderId": "413925010268",
    "appId": "1:413925010268:web:d1f1bb14b138cf8245af99",
    "measurementId": "G-CKSYGDE1V1"
}
firebase = pyrebase.initialize_app(config)
database = firebase.database()

#---------------------------------------------------------------------------------------
# Auxliary Functions
def create_user_db(author, guild):
    database.child("Servers").child(f"{guild.id}").update({"Server_Name": guild.name})  #updates da name of the server
    nUsers = database.child("Servers").child(f"{guild.id}").get().val()["UsersDB_counter"]
    user_data = {"UserDB_ID": nUsers, "User_Name": f"{author.name}", "Cursed_Counter": 0}
    server_db = database.child("Servers").child(f"{guild.id}")
    server_db.child("Users").child(f"{author.id}").set(user_data)    # Creates a new user db
    nUsers += 1
    database.child("Servers").child(f"{guild.id}").update({"UsersDB_counter": nUsers})      # Update server users counter

def create_server_db(guild):
    server_data = {"Server_Name": f"{guild.name}", "UsersDB_counter": 0}
    database.child("Servers").child(f"{guild.id}").set(server_data)  # Creates a new server db

def check_user_db(message):
    server_db = database.child("Servers").child(f"{message.guild.id}").get().val()   # Verifies if the server is already in the db
    if server_db == None:
        create_server_db(message.guild)
       
    user_db = database.child("Servers").child(f"{message.guild.id}").child("Users").child(f"{message.author.id}").get().val()
    if user_db == None:
        create_user_db(message.author, message.guild)
       

async def timeout_member(member , punish_time_sec):
    until_time = utcnow() + timedelta(seconds=punish_time_sec)
    await member.edit(timed_out_until=until_time, reason="spamming... dumbass")


#---------------------------------------------------------------------------------------
# Events Class
class BotEvents(commands.Cog):     # contains an optimized HashTable that initiallizes if not before 
    word_set = set()    # HashTable, optimized by set()

    def __init__(self, bot):    # initiallizes 
        self.bot = bot
        if not BotEvents.word_set:
            with open("text_files/cursed_words.txt", "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        BotEvents.word_set.add(word)
           
        
 # static variables
    SPAM_SERVER_ID = []
    SPAM_USER_ID = []
    SPAM_COUNTER = []
    SPAM_TIME = []
    
    # <word>
    @commands.Cog.listener()    # listener == event
    async def on_message(self, message):
        import re   # for re.splits
        DumbKoboldBot_id = 1104277799616905237
        BoblinTheTestGoblinBot_id = 1393902920906309673
        if (message.author.id == DumbKoboldBot_id) or (message.author.id == BoblinTheTestGoblinBot_id): #prevents my bots to respond to themselves and each other
            return  
        if message.author.bot:  # calls slurs to other bots
            await message.channel.send("Get out of my house **__Clanker__!**")
            return
        #--------------------------------------------------------------
        # idx finder
        if not (message.guild.id in BotEvents.SPAM_SERVER_ID):  # if server_id doesnt exist on the list yet
            idx = len(BotEvents.SPAM_SERVER_ID)
            BotEvents.SPAM_SERVER_ID.append(message.guild.id) 
            BotEvents.SPAM_USER_ID.append(0)
            BotEvents.SPAM_COUNTER.append(0)
            BotEvents.SPAM_TIME.append(0)
        else:                                                   # gets the idx of the server on the list
            for idx in range(len(BotEvents.SPAM_SERVER_ID)):
                if BotEvents.SPAM_SERVER_ID[idx] == message.guild.id:
                    break
        #--------------------------------------------------------------
        # SPAM control
        if message.author.id != BotEvents.SPAM_USER_ID[idx]:    # if its a new user sending msgs
            BotEvents.SPAM_TIME[idx] = datetime.now()
            BotEvents.SPAM_USER_ID[idx] = message.author.id
            BotEvents.SPAM_COUNTER[idx] = 1
        elif BotEvents.SPAM_COUNTER[idx] >= 3:                  # if it hit the SPAM check (5 consecutive msgs)
                current_time = datetime.now()
                delta = current_time - BotEvents.SPAM_TIME[idx]
                if delta.total_seconds() <= 4:               # if the delta time of the 1st and the 5th msgs are less or equal then 3 sec
                    await timeout_member(message.guild.get_member(message.author.id), 69)    # punish user by 69 sec (nice)
                    await message.channel.send("STOP SPAMMING SHUCKA!")
                BotEvents.SPAM_TIME[idx] = current_time
                BotEvents.SPAM_COUNTER[idx] = 1
        else:
            BotEvents.SPAM_COUNTER[idx] += 1
        #------------------------------------------------------------
        # word a word msg analysis
        nSlurs=0
        for token in re.split(r'[ ,;]+', message.content.lower()):   # splits the ,already lowercased, message into an array of words and check if the message contains the word 
        #words that do specific things
            if "word" in token:
                await message.channel.send(f"{message.author.mention} - You said the word!")    # await command is used to wait for the message to be sent before continuing (its important for async functions)    
                break
        #search on the list
            elif any(word in token for word in BotEvents.word_set): # seachs for a member of the list that is in the word                 
                check_user_db(message)   # Checks if the user exists on the database
                counter = database.child("Servers").child(f"{message.guild.id}").child("Users").child(f"{message.author.id}").get().val()["Cursed_Counter"]  # Gets the value of counter (has to be the entire code bc figures)
                counter += 1    
                database.child("Servers").child(f"{message.guild.id}").child("Users").child(f"{message.author.id}").update({"Cursed_Counter": counter})    # Updates the database
                nSlurs += 1
                if nSlurs >= 10:
                    await timeout_member(message.guild.get_member(message.author.id), 69)    # punish user by 69 sec (nice)
                    await message.channel.send("BEHAVE KITTEN!")
        await message.bot.process_commands(message)  # this allows the bot to process commands after handling the message


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        role_name = "tupid"
        msg_id = 1397677935707820103

        if payload.user_id == self.bot.user.id:
            return
        if payload.message_id != msg_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = await guild.fetch_member(payload.user_id)
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            await member.send(f"{member.mention} - Role **{role_name}** doesn't exist on **{guild.name}**!")
            return

        await member.add_roles(role)
        await member.send(f"{member.mention} - You have been assigned the **{role_name}** role on the **{guild.name}**!")



# Required setup function
async def setup(bot):
    await bot.add_cog(BotEvents(bot))

