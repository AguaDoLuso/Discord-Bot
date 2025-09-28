# Imports
import discord
from discord.ext import commands

class HelloCog(commands.Cog):
    def __init__(self, bot):    # Initialization of static variables
        self.bot = bot
        
    # ------------------------ Commands ----------------------------------
    
    # !hello
    @commands.command(name="hello", aliases=["hi"])
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")
          
# -------------------------- Setup -----------------------------------------
           
async def setup(bot):
    await bot.add_cog(HelloCog(bot))