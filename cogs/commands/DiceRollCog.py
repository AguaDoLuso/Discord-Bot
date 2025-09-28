# Imports
import discord
from discord.ext import commands
import random
import numpy as np

ERROR = -1  # used to indicate an error in the code

# ------------------------------ AUX Functions ---------------------------------------------

def calculate(op, a, b):    
        if op == 1:
            return (a + b)
        if op == 2:
            return (a - b)
        if op == 3:
            return (a * b)
        if op == 4:
            return (a / b)

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
    
def normal_dist_roll(ndice, sides): # calculates the normal distribution roll of more then 10.000 dice rolls
        mean = ndice * (1 + sides) / 2
        stddev = (sides**2 - 1) / 12
        total_stddev = (ndice * stddev)**0.5
        return int(random.gauss(mean, total_stddev))

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
    
# ------------------------------------- Class ----------------------------------------

class DiceRollCog(commands.Cog):
    def __init__(self, bot):    # Initialization of static variables
        self.bot = bot
    
    # ------------------------ Commands ----------------------------------
    
    # !roll <number>
    @commands.command(name='roll', aliases=['r'])
    async def roll(self, ctx, *, input_str: str = None): 
        if not input_str:
            await ctx.send(f"{ctx.author.mention} - I need a number to roll!")
            return 

        roll_info = []
        final_msg = []
        operation = False

        op, index = await roll_info_scan(ctx, input_str, roll_info)
        if op == ERROR:
            return

        if len(roll_info) < 2:
            final_result = roll_info[0] if roll_info else 0
        else:
            final_result = await roll_random(ctx, roll_info[0], roll_info[1], final_msg)
            if final_result == ERROR:
                return

        i = 1
        while op > 1:
            operation = True
            i += 1
            if i >= 10:
                await ctx.send(f"{ctx.author.mention} - I only have 10 fingers! Please give me fewer than 10 things to do at once.")
                return

            roll_info.clear()
            new_op, new_index = await roll_info_scan(ctx, input_str[index+1:], roll_info)
            if new_op == ERROR:
                return
            index += new_index + 1

            if len(roll_info) < 2:
                result = roll_info[0]
            else:
                result = await roll_random(ctx, roll_info[0], roll_info[1], final_msg)
                if result == ERROR:
                    return

            if (op != 4) or (result != 0):
                final_result = calculate(op, final_result, result)
            else:
                await ctx.send(f"{ctx.author.mention} - How the Hell am I supposed to do that???")
                return
            op = new_op

        if operation or roll_info[0] > 1:
            final_msg.append(f"{ctx.author.mention} - To a total of:  **{final_result}**")
        await ctx.send("\n".join(final_msg))
        
# ----------------------------------- Setup -----------------------------------------
           
async def setup(bot):
    await bot.add_cog(DiceRollCog(bot))
