import discord
from discord.ext import commands
from typing import Union
import configuration.discordConfig as dcfg

class Utilities(commands.Cog):
    """A collection of utility commands for managing and manipulating server-related tasks."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Check the bot's latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! Latency: {latency}ms")

    @commands.command()
    async def say(self, ctx, *, message):
        """Make the bot say a message"""
        await ctx.send(message)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def rename_channel(self, ctx, channel: discord.TextChannel, new_name: str):
        """Rename a channel"""
        await channel.edit(name=new_name)
        await ctx.send(f"The channel has been renamed to {channel.mention}.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def move_channel(self, ctx, channel: discord.TextChannel, category: discord.CategoryChannel):
        """Move a channel to a different category"""
        await channel.edit(category=category)
        await ctx.send(f"The channel {channel.mention} has been moved to the category {category.name}.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, channel: discord.TextChannel, duration: int):
        """Set the slowmode duration for a channel"""
        await channel.edit(slowmode_delay=duration)
        await ctx.send(f"The slowmode duration for {channel.mention} has been set to {duration} seconds.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def delete_channel(self, ctx, channel: discord.TextChannel):
        """Delete a channel"""
        await channel.delete()
        await ctx.send(f"The channel {channel.mention} has been deleted.")

    @commands.command()
    @commands.has_permissions(manage_roles=True, manage_channels=True)
    async def add_role_to_channel(self, ctx, channel: discord.TextChannel, role: Union[discord.Role, int]):
        """Add a role to a channel"""
        if isinstance(role, int):
            role_id = role
            role = ctx.guild.get_role(role)
            if role is None:
                return await ctx.send(f"The role with ID {role_id} does not exist.")

        if isinstance(role, discord.Role):
            await channel.set_permissions(role, read_messages=True, send_messages=True)
            await ctx.send(f"The role {role.mention} has been added to the channel {channel.mention}.")
        else:
            await ctx.send("Invalid role provided.")

    @commands.command()
    async def server_info(self, ctx):
        """Get information about the server"""
        server = ctx.guild
        total_members = len(server.members)
        total_channels = len(server.channels)
        total_roles = len(server.roles)

        embed = discord.Embed(title="Server Information")
        embed.add_field(name="Server Name", value=server.name, inline=False)
        embed.add_field(name="Total Members", value=total_members, inline=False)
        embed.add_field(name="Total Channels", value=total_channels, inline=False)
        embed.add_field(name="Total Roles", value=total_roles, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        """Show the avatar of a user"""
        if member is None:
            member = ctx.author

        avatar_url = member.avatar.url

        embed = discord.Embed(title="User Avatar")
        embed.set_image(url=avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Get information about a user"""
        if member is None:
            member = ctx.author

        embed = discord.Embed(title="User Info")
        embed.set_thumbnail(url=member.avatar.url)

        if member.banner is not None:
            embed.set_image(url=member.banner.url)

        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="Discriminator", value=member.discriminator, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Bot", value=member.bot, inline=True)
        embed.add_field(name="Created At", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def server_icon(self, ctx):
        """Show the server's icon"""
        server = ctx.guild
        if server.icon_url:
            embed = discord.Embed(title="Server Icon")
            embed.set_image(url=server.icon_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("The server does not have an icon.")

    @commands.Cog.listener()
    async def on_message(self, message):
        targeted_category_id = dcfg.ticket_categ_id 
        targeted_user_id = 929438824227020832

        if message.author.bot:
            return

        if message.channel.category_id != targeted_category_id:
            return

        if message.mentions and not message.author.guild_permissions.administrator:
            targeted_user = message.guild.get_member(targeted_user_id)  
            if targeted_user and targeted_user in message.mentions:
                reply = f"Hello {message.author.mention}, please note that the minimum response time for {targeted_user.mention} is three hours. We kindly request your patience as they may be busy attending to other matters. We appreciate your understanding!"
                await message.channel.send(reply)


async def setup(bot):
    await bot.add_cog(Utilities(bot))
