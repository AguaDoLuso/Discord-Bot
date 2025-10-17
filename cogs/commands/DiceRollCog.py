# Imports
import discord
from discord.ext import commands
import random
import numpy as np
import re

class Equation:     # Aux Struct
    def __init__(self, str, priority):
        self.str = str
        self.priority = priority

# ------------------------------ AUX Functions ---------------------------------------------

def normal_dist_roll(ndice, sides): # calculates the normal distribution roll of more then 10.000 dice rolls
        mean = ndice * (1 + sides) / 2
        stddev = (sides**2 - 1) / 12
        total_stddev = (ndice * stddev)**0.5
        return int(random.gauss(mean, total_stddev))

async def roll_random(ctx, ndice, sides, final_msg):
        if not ndice:   # if no dice are rolled, it will return -1
            await ctx.send(f"{ctx.author.mention} - I can't roll 0 dice dumbass!")
            return None
        if sides < 2:
            await ctx.send(f"{ctx.author.mention} - I only have stuff with 2 or more sides!")
            return None

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

####################################################################### WORK ABOVE ############################################################################################

async def calculator_withRoll(ctx, Numbers, Operators, final_msg):
    
    priority_ops = ['*', '/', 'd']
    for idx, op in enumerate(Operators):
        if op in priority_ops:
            match op:
                case '*':
                    Numbers[idx] = Numbers[idx] * Numbers[idx+1]
                    Operators.pop(idx)
                    Numbers.pop(idx+1)
                case '/':
                    if(Numbers[idx+1] == 0):    # Verification, indetermination (x/0)
                        await ctx.send(f"{ctx.author.mention} - How the Hell am I supposed to do that???")
                        return None
                    Numbers[idx] = Numbers[idx] / Numbers[idx+1]
                    Operators.pop(idx)
                    Numbers.pop(idx+1)
                case 'd':
                    Numbers[idx] = await roll_random(ctx, Numbers[idx], Numbers[idx+1], final_msg)
                    Operators.pop(idx)
                    Numbers.pop(idx+1)
                   
                    
    total = 0           
    for num in Numbers:
        total += num
    return total   

# -------------------------------------------------------------------------------------------------------------------------------------------

def compartmentalization(str):
    if (str.count('(') != str.count(')')):  # Verification, quick check
        return None
    equations = []
    priorities = [0]
    prio_level = 0

    open_idx = -1
    close_idx = -1
    for count in range(str.count('(')):     # Verification, long check 
        oldOpen_idx = open_idx
        open_idx = str.find('(', open_idx+1)
        oldClose_idx = close_idx
        close_idx = str.find(')', close_idx+1)  
        
        if (open_idx > close_idx):  # Verification
            return None
          
        str = list(str)
        prio_level += 1
        if (count != 0):
            if (open_idx - oldOpen_idx == 1):
                str.insert(open_idx, '0+')
            if(close_idx - oldClose_idx != 1):
                    priorities.append(prio_level)
                    prio_level -= 1

            elif (open_idx > oldClose_idx):
                str.insert(open_idx, '*')
                priorities.insert(len(priorities)-1, prio_level-1)
        str = ''.join(str)
        priorities.append(prio_level)
        
    str_splited = re.split(r"[(]", str)
    
    if (len(str_splited) == 1):     # If it has no '()'
        equations.append(Equation(str, 0))
        return equations
    
    for split in str_splited:   # Verification, '()'
        if (split == ''):
            continue
        if (split[0] == ')'):
            return None
     
    str_splited = re.split(r"[()]", str)
    
    if (str_splited[0] == ''):
        str_splited.pop(0)  # Removes the first element of the list
        str_splited.insert(0, "0+")
        
    if (str_splited[len(str_splited)-1] != ''):
        priorities.append(0)
    
    for i in range(str_splited.count('')):  # Removes all ''
        str_splited.remove('')
            
    #print(str_splited)
    #print(priorities)  
        
    if(len(str_splited) != len(priorities)):
        return None
        
    for split, priority in zip(str_splited, priorities):    # Creating the struct
        eq = Equation(split, priority)
        equations.append(eq)    
    
    return equations

# --------------------------------------------------------------------------------------------------------------------------------------

def str_decoder(str):
    str = list(str)
    separators = "[+*/d]"
    Operators = []
    Numbers = []
    inverse = False
    
    idx = 0
    while idx < len(str):   # Fills the Operators[] list, and fixes the string for the next step
        chr = str[idx]
        if (chr in separators): 
            Operators.append(chr)  
            if ((idx == 0) and (chr == 'd')):
                str.insert(idx, '1')  # "d20" -> "1d20"
                idx += 1
                
            if (idx != len(str)-1):
                if (str[idx+1] == '-'):  # Skips the '-' after any operation
                    idx += 1
                elif (str[idx+1] == 'd'):   # Fixes the string if the roll operation 'd' doesnt have a prefix
                    str.insert(idx+1, '1')  # "1 + d20" -> "1 + 1d20"
                    idx += 1
                          
        elif ((idx != 0) and (chr == '-')):
            str.insert(idx, '+')    # "1-2" -> "1+-2"
            continue    # retries on this index (chr = '+')
        idx += 1
    if (str[len(str)-1] == '-'):    # In case of "1 - (2 + 3)"
            str.pop(len(str)-1) # So it doesnt trigger anything on the next segment
            inverse = True
    
            
    # Fills the Numbers[] and Verifies if every is right
    str = ''.join(str)    # Converts a list into a string
    expr = re.split(separators, str)
    if(expr[0] == ''):
        expr.pop(0)
    if (expr[len(expr)-1] == ''):
        expr.pop(len(expr)-1) # Removes the last element of the list 
    if ('' in expr): # Verification
        return None, None, None    
    
    for num_str in expr:
        if not (num_str.isalnum()):
            if ((num_str.count('.') > 1) or ((len(num_str) == 1) and (num_str[0] == '-'))):     # Verifications
                return None, None, None    
            
            for chr in num_str:
                if ((chr.isnumeric()) or (chr == '.') or (chr == '-')):   # Verification
                    continue
                return None, None, None           
        num = float(num_str) if "." in num_str else int(num_str)    # float if its a decimal, int if not
        Numbers.append(num)
    
    return inverse, Numbers, Operators

# ----------------------------------------------------------------------------------------------------------------

async def expr_manager(ctx, str_splited, final_msg):
        
    expr = str_splited[0]
    str_splited.pop(0)  
    str = expr.str
                   
    # -------------------------------------- str Decoder -----------------------------------------  
    
    if(str.isnumeric()):  # Quick result, in case its all numbers
        return int(str)
    
    inverse, Numbers, Operators = str_decoder(str)
    if (inverse == None):
        return None
        
    # ------------------------------------------ Recursive Calls ---------------------------------------------------  
    
    idx = 0  
    while idx < len(str_splited):
        eq = str_splited[idx]
        
        #print("------------------------------")
        #print("MAIN STR: ", str)
        #print("str: ", eq.str)
        #print("Prio: ", eq.priority)
   
        if (expr.priority > eq.priority):
            print("--BREAK--")
            break
        
        if (expr.priority == eq.priority):
            otherinverse, otherNumbers, otherOperators = str_decoder(eq.str)
            if(otherinverse == None):   # Verification
                return None
            if(otherNumbers[0] < 0):
                Operators.append('+') 
            inverse = otherinverse
            for otherNum in otherNumbers:
                Numbers.append(otherNum)
            for otherOp in otherOperators:
                Operators.append(otherOp)
            str = eq.str
              
        elif(eq.priority - expr.priority == 1):
            newNum = await expr_manager(ctx, str_splited[idx:], final_msg)
            if (newNum == None):    # Verification
                return None
            if (inverse):
                newNum *= -1               
            Numbers.append(newNum)
            
            for i, x in enumerate(str_splited[idx+1:]):
                if (expr.priority == x.priority):
                    idx = i
        idx += 1

    #print(Numbers)
    #print(Operators)
        
    if ((len(Numbers) != len(Operators)+1) or inverse):  # Verification
        return None

    total = await calculator_withRoll(ctx, Numbers, Operators, final_msg)
    if (total == None): # Verification
        return None
    
    return total
    
# -------------------------------------------- Class ----------------------------------------------------------     

class DiceRollCog(commands.Cog):
    def __init__(self, bot):    # Initialization of static variables
        self.bot = bot
    
    # -------------------------------------- Commands --------------------------------------
    
    # !roll <number>
    @commands.command(name='roll', aliases=['r'])
    async def roll(self, ctx, *, input_str: str = None): 
        if not input_str:
            await ctx.send(f"{ctx.author.mention} - I need SOMETHING to work with!")
            return 
        
        input_str = input_str.replace(' ', '')  # Replaces all spaces
        input_str = input_str.casefold()        # Lowers all CapSized letters (usefull for 'D')
          
        equations = compartmentalization(input_str)
        if (equations != None):
            final_msg = []
            total = await expr_manager(ctx, equations, final_msg)
            #print(total)
            if(total != None):
                if (len(final_msg) != 1):
                    if (len(final_msg) > 10):
                        final_msg.clear()
                    final_msg.append(f"{ctx.author.mention} - To a total of:  **{total}**")
                await ctx.send("\n".join(final_msg))
                return
            
        await ctx.send(f"{ctx.author.mention} - Didn't understood what you meant, say something more like this \n`!r 2d20 + (4.5 * 7)`")
        
# ------------------------------------------- Setup ---------------------------------------------------
           
async def setup(bot):
    await bot.add_cog(DiceRollCog(bot))
