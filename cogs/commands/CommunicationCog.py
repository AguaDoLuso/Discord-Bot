# Imports
import discord
from discord.ext import commands

class CommunicationCog(commands.Cog):
    def __init__(self, bot):    # Initialization of static variables
        self.bot = bot
        
    # ------------------------ Commands ----------------------------------
    
    # !dm <msg>
    @commands.command()
    async def dm(self, ctx, *, msg):
        await ctx.author.send(f"You said: {msg}")

    # !reply
    @commands.command()
    async def reply(self, ctx):
        await ctx.reply("This is a reply to your message!")

    # !poll <question>
    @commands.command()
    async def poll(self, ctx, *, question):
        embed = discord.Embed(title="New Poll", description=question)
        poll_message = await ctx.send(embed=embed)
        await poll_message.add_reaction("👍") 
        await poll_message.add_reaction("👎") 
        
# -------------------------- Setup -----------------------------------------
           
async def setup(bot):
    await bot.add_cog(CommunicationCog(bot))