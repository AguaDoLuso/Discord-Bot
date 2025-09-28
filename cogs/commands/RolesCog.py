# Imports
import discord
from discord.ext import commands

class RolesCog(commands.Cog):
    role_tupid = 'tupid'
    
    def __init__(self, bot):    # Initialization of static variables
        self.bot = bot
        
    # ------------------------ Commands ----------------------------------
    
    # !assign
    @commands.command()
    async def assign(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name=self.role_tupid)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention} - You have been assigned the {self.role_tupid} role!")
        else:
            await ctx.send(f"{ctx.author.mention} - Role {self.role_tupid} doesn't exist!")

    # !remove
    @commands.command()
    async def remove(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name=self.role_tupid)
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention} - You have been removed from the {self.role_tupid} role!")
        else:
            await ctx.send(f"{ctx.author.mention} - You don't have the {self.role_tupid} role!")
            
    # !secret
    @commands.command()
    @commands.has_role(role_tupid)
    async def secret(self, ctx):
        await ctx.send(f"{ctx.author.mention} - Welcome to the club!")

    @secret.error
    async def secret_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("You do not have permission to do that!")
    
    
# -------------------------- Setup -----------------------------------------
           
async def setup(bot):
    await bot.add_cog(RolesCog(bot))