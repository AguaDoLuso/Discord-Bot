#---------------------------------------------------------------------------------------
# Imports
import discord
from discord.ext import commands
import random
import numpy as np
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

ERROR = -1  # used to indicate an error in the code

role_tupid = "tupid"
    
# !hello    
@commands.command(name='hello', aliases=['hi'])   
async def hello(ctx):   # 'ctx' is the information about the message like author, channel, etc...  
    await ctx.send(f"Hello {ctx.author.mention}!") 
    
# !cursed
@commands.command()
async def cursed(ctx):
    counter = database.child("Servers").child(f"{ctx.guild.id}").child("Users").child(f"{ctx.author.id}").get().val()
    if counter == None:
        await ctx.send(f"{ctx.author.mention} - You haven't cursed on this server yet!\nEveryone, here lies an **uncorrupted soul** a living **Saint** among Men!")
        return
    await ctx.send(f"{ctx.author.mention} - Your **Cursed Level** is currently **{counter["Cursed_Counter"]}** slurs on this server, you degenerate!")

# !topcursed
@commands.command()
async def topcursed(ctx):
    users = database.child("Servers").child(f"{ctx.guild.id}").child("Users").order_by_child("Cursed_Counter").limit_to_last(5).get()   #gets the last 5 by increassing order
    top_counters = []
    top_users = []
    msg = ""
    if users.val() == None:
        await ctx.send(" ### **Uau**! There isn't a single corrupted soul here. Is this heaven??")
        return
    for user in users:
        user_id = user.key()
        counter = user.val()["Cursed_Counter"]
        top_users.append(user_id)
        top_counters.append(counter)
    
    # pair them:
    pairs = list(zip(top_users, top_counters))
    # sort by counter descending
    pairs.sort(key=lambda x: x[1], reverse=True)
    
    place = 0
    previous_counter = None
    for user_id, counter in pairs:
        if counter != previous_counter:
            place += 1
        previous_counter = counter
        msg += f" - **{place}º -** __<@{int(user_id)}>__ with (**{counter} curses**)\n"
    await ctx.send(msg)
    

def is_op(char):
    op = 0
    if char == '+':
        op = 1
    elif char == '-':
        op = 2
    elif char == '*':
        op = 3
    elif char == '/':
        op = 4
    return op
    
async def roll_info_scan(ctx, input_str, roll_info):  # 0: Error, 1: end, 2: sum, 3: sub, 4: mul
    number = ""
    op = 0
    for i, char in enumerate(input_str):    #takes the numbers from the string
        if (char.isdigit()) and (len(roll_info) < 2):
            number += char
            continue
        if(char == ' '):
            continue
        op = is_op(char)
        if op > 0:
            break
        if (char == 'd') and ((i+1 < len(input_str)) and (input_str[i+1].isdigit())) and (len(roll_info) < 2): 
            if number == "":   # if roll_info == []
                roll_info.append(1) 
            elif number != "":
                roll_info.append(int(number)) 
            number = ""
        else:
            await ctx.send(f"{ctx.author.mention} - Didn't understood what you meant, say something more like this `2d20`!")
            return ERROR, i
    if number != "":    
        roll_info.append(int(number))  
    return op, i
    
def normal_dist_roll(ndice, sides): # calculates the normal distribution roll of more then 10.000 dice rolls
    mean = ndice * (1 + sides) / 2
    stddev = (sides**2 - 1) / 12
    total_stddev = (ndice * stddev)**0.5
    return int(random.gauss(mean, total_stddev))
    
async def roll_random(ctx, ndice, sides, final_msg):
    if not ndice:   # if no dice are rolled, it will return -1
        await ctx.send(f"{ctx.author.mention} - I can't roll 0 dice dumbass!")
        return ERROR
    if sides < 2:
        await ctx.send(f"{ctx.author.mention} - I only have stuff with 2 or more sides!")
        return ERROR
    
    import random
    final_result = 0
    if ndice > 10000:   # more then 10.000 dice, it will use the normal distribution to calculate faster
        return normal_dist_roll(ndice, sides)
    for index in range(ndice):      
        result = random.randint(1, sides)
        if not (ndice > 10):  # if more than 10 dice are rolled, it will not show the result of each dice
            if result > sides / 2:
                if result == sides:
                    final_msg.append(f"{ctx.author.mention} - Its a 🎉 nat **{result}** 🎉!HOLY SHIT! Give me that dice!")
                else:
                    final_msg.append(f"{ctx.author.mention} - Its a **{result}**! Lucky 😒")
            else:
                if result == 1:
                    final_msg.append(f"{ctx.author.mention} - Its a 🎉 nat **{result}** 🎉! Buwaahhahahaha! *rolls on the floor*")
                else:
                    final_msg.append(f"{ctx.author.mention} - Its a **{result}**! Don't you dare to blame my dice!") 
        final_result += result
    return final_result

def calculate(op, a, b):
    if op == 1:
        return (a + b)
    if op == 2:
        return (a - b)
    if op == 3:
        return (a * b)
    if op == 4:
        return (a / b)
        
# !roll <number>
@commands.command(name='roll', aliases=['r'])   # the command name is 'roll', but it can also be called with 'r'
async def roll(ctx, *, input_str: str = None): 
    if not input_str or input_str == "":    # if no string is provided, it will return an error message
        await ctx.send(f"{ctx.author.mention} - I need a number to roll!")
        return 
    
    roll_info = []   # list,  0: ndice, 1: nsides,   
    final_msg = []   # message to be sent at the end
    operation = False
    op, index = await roll_info_scan(ctx, input_str, roll_info)  # scan the input string for numbers and operators
    if op == ERROR:  #error
        return
    #first operator or roll
    if len(roll_info) < 2:  #normal numbers for operations
        if not roll_info:
            final_result = 0
        else:
            final_result = roll_info[0]
    else:   #doll a dice
        final_result = await roll_random(ctx, roll_info[0], roll_info[1], final_msg)
        if final_result == ERROR:  # if the roll failed, end the command
            return
    
    i = 1
    while op > 1:   # works the lenght of the command (wordwise)
        operation = True
        i += 1
        if i >= 10:     # prevents one line spam of commands
            await ctx.send(f"{ctx.author.mention} - I only have 10 hand fingers and a pencil, Could you please give me 10 diferent things to do at a time?")
            return
        
        roll_info.clear()  # clear the roll_info array
        new_op, new_index = await roll_info_scan(ctx, input_str[index+1:], roll_info) #sends the string foward starting on the index+1
        if new_op == ERROR:
            return
        index += new_index + 1
        if len(roll_info) < 2:  #normal numbers for operations
            result = roll_info[0]
        else:   #doll a dice
            result = await roll_random(ctx, roll_info[0], roll_info[1], final_msg)
            if result == ERROR:  # if the roll failed, end the command
               return
        if (op != 4) or (result != 0):  # avoids division by zero
            final_result = calculate(op, final_result, result)
        else:
            await ctx.send(f"{ctx.author.mention} - How the Hell am I supposed to do that???")
            return
        op = new_op
        
    if operation or roll_info[0] > 1:   # if there was an operation or more than one dice rolled
        final_msg.append(f"{ctx.author.mention} - To a total of:  **{final_result}**")
    await ctx.send("\n".join(final_msg))    # prints every member of the list with '/n' at the end
    
# !assign    
@commands.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name = role_tupid)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} - You have been assigned the {role_tupid} role!")
    else:
        await ctx.send(f"{ctx.author.mention} - Role {role_tupid} doesn't exist!")
    
# !remove
@commands.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name = role_tupid)
    if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} - You have been removed from the {role_tupid} role!")
    else:
        await ctx.send(f"{ctx.author.mention} - You don't have the {role_tupid} role!")

# !dm <msg>
@commands.command()  
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said: {msg}")

# !reply
@commands.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")

# !poll <question>
@commands.command()  # windows key + . to open emoji keyboard
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_messsage = await ctx.send(embed=embed)
    await poll_messsage.add_reaction("👍") 
    await poll_messsage.add_reaction("👎") 
    
# !secret
@commands.command()
@commands.has_role(role_tupid)  # this command can only be used by users with the test_role
async def secret(ctx):
    await ctx.send(f"{ctx.author.mention} - Welcome to the club!")
    
@secret.error   # if the user does not have the role, this function will be called
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")  

async def setup(bot):   # creates all the bot commands
    bot.add_command(hello)
    bot.add_command(cursed)
    bot.add_command(topcursed)
    bot.add_command(roll)
    bot.add_command(assign)
    bot.add_command(remove)
    bot.add_command(dm)
    bot.add_command(reply)
    bot.add_command(poll)
    bot.add_command(secret)