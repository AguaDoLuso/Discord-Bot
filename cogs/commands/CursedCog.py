# Imports
import discord
from discord.ext import commands
import pyrebase
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


# -------------------------------- Class -----------------------------------------

class CursedCog(commands.Cog):
    def __init__(self, bot):    # Initialization of static variables
        self.bot = bot
    
    # ------------------------ Commands ----------------------------------

    # !cursed
    @commands.command()
    async def cursed(self, ctx):
        counter = database.child("Servers").child(f"{ctx.guild.id}").child("Users").child(f"{ctx.author.id}").get().val()
        if counter is None:
            await ctx.send(f"{ctx.author.mention} - You haven't cursed on this server yet!\nEveryone, here lies an **uncorrupted soul** a living **Saint** among Men!")
            return
        await ctx.send(
            f"{ctx.author.mention} - Your **Cursed Level** is currently **{counter['Cursed_Counter']}** slurs on this server, you degenerate!"
        )
    
    # ------------------------------------------------------------------

    # !topcursed
    @commands.command()
    async def topcursed(self, ctx):
        users = database.child("Servers").child(f"{ctx.guild.id}").child("Users").order_by_child("Cursed_Counter").limit_to_last(5).get()
        top_counters = []
        top_users = []
        msg = ""
        if users.val() is None:
            await ctx.send("### **Uau**! There isn't a single corrupted soul here. Is this heaven??")
            return

        for user in users:
            user_id = user.key()
            counter = user.val()["Cursed_Counter"]
            top_users.append(user_id)
            top_counters.append(counter)

        pairs = list(zip(top_users, top_counters))
        pairs.sort(key=lambda x: x[1], reverse=True)

        place = 0
        previous_counter = None
        for user_id, counter in pairs:
            if counter != previous_counter:
                place += 1
            previous_counter = counter
            msg += f" - **{place}º -** __<@{int(user_id)}>__ with (**{counter} curses**)\n"
        await ctx.send(msg)
        
        
        
# -------------------------- Setup -----------------------------------------
           
async def setup(bot):
    await bot.add_cog(CursedCog(bot))