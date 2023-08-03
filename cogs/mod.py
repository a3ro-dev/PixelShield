import discord
from discord.ext import commands
import sqlite3

# Connect to the mod.db database
mod_db = sqlite3.connect('./database/mod.db')
mod_cursor = mod_db.cursor()
mod_cursor.execute('CREATE TABLE IF NOT EXISTS warnings (user_id INTEGER, moderator_id INTEGER, reason TEXT)')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log deleted messages"""
        logs_channel = discord.utils.get(message.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Message Deleted', color=discord.Color.red())
            embed.add_field(name='Author', value=message.author.mention)
            embed.add_field(name='Channel', value=message.channel.mention)
            embed.add_field(name='Content', value=message.content)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log edited messages"""
        logs_channel = discord.utils.get(before.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Message Edited', color=discord.Color.orange())
            embed.add_field(name='Author', value=before.author.mention)
            embed.add_field(name='Channel', value=before.channel.mention)
            embed.add_field(name='Before', value=before.content)
            embed.add_field(name='After', value=after.content)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Log category creation"""
        logs_channel = discord.utils.get(channel.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Channel Created', color=discord.Color.green())
            embed.add_field(name='Channel', value=channel.name)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_category_create(self, category):
        """Log category creation"""
        logs_channel = discord.utils.get(category.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Category Created', color=discord.Color.green())
            embed.add_field(name='Category', value=category.name)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Log category deletion"""
        logs_channel = discord.utils.get(channel.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Channel', color=discord.Color.red())
            embed.add_field(name='Category', value=channel.name)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_category_delete(self, category):
        """Log category deletion"""
        logs_channel = discord.utils.get(category.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Channel', color=discord.Color.red())
            embed.add_field(name='Category', value=category.name)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Log role creation"""
        logs_channel = discord.utils.get(role.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Role Created', color=discord.Color.green())
            embed.add_field(name='Role', value=role.name)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Log role deletion"""
        logs_channel = discord.utils.get(role.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Role Deleted', color=discord.Color.red())
            embed.add_field(name='Role', value=role.name)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log member join"""
        logs_channel = discord.utils.get(member.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Member Joined', color=discord.Color.green())
            embed.add_field(name='Member', value=member.mention)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log member leave"""
        logs_channel = discord.utils.get(member.guild.channels, name='server-logs')
        if logs_channel:
            embed = discord.Embed(title='Member Left', color=discord.Color.red())
            embed.add_field(name='Member', value=member.mention)
            await logs_channel.send(embed=embed)

    @commands.hybrid_command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server"""
        if member == None:
            await ctx.send("Provide member mention to kick")
        await member.kick(reason=reason)
        # Log the kick
        self.log_action(ctx.author, member, 'Kick', reason)
        # DM the user
        await member.send(f"You have been kicked from {ctx.guild.name}. Reason: {reason}")

    @commands.hybrid_command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member from the server"""
        if member == None:
            await ctx.send('Provide member mention to ban')
        await member.ban(reason=reason)
        # Log the ban
        self.log_action(ctx.author, member, 'Ban', reason)
        # DM the user
        await member.send(f"You have been banned from {ctx.guild.name}. Reason: {reason}")

    @commands.hybrid_command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        """Warn a member"""
        if member == None:
            await ctx.send('Provide member mention to warn')
        mod_cursor.execute('INSERT INTO warnings VALUES (?, ?, ?)', (member.id, ctx.author.id, reason))
        mod_db.commit()
        # Log the warning
        self.log_action(ctx.author, member, 'Warn', reason)
        # DM the user
        await member.send(f"You have been warned in {ctx.guild.name}. Reason: {reason}")

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, channel: discord.TextChannel):
        """Lockdown a channel, preventing everyone from sending messages"""
        if channel == None:
            await ctx.send('Provide channel mention to lockdown')
            
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"{channel.mention} is now in lockdown.")

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def log(self, ctx):
        """Log various events and actions in the server"""
        logs_category = discord.utils.get(ctx.guild.categories, name='Logs')
        if not logs_category:
            logs_category = await ctx.guild.create_category('Logs')

        logs_channel = await logs_category.create_text_channel('server-logs')

        await logs_channel.send('Logging has been enabled. Events and actions will be logged here.')

    def log_action(self, moderator, member, action, reason):
        """Log a moderation action to the mod.db database"""
        mod_cursor.execute('CREATE TABLE IF NOT EXISTS mod_log (moderator_id TEXT, moderator_name TEXT, member_id TEXT, member_name TEXT, action TEXT, reason TEXT)')
        mod_cursor.execute('INSERT INTO mod_log VALUES (?, ?, ?, ?, ?, ?)',
                        (moderator.id, moderator.name, member.id, member.name, action, reason))
        mod_db.commit()

    def cog_unload(self):
        mod_db.close()

async def setup(bot):
    await bot.add_cog(Moderation(bot))
