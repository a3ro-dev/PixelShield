import discord
from discord.ext import commands
from typing import Union
import configuration.discordConfig as dcfg
import platform
import socket

class Utilities(commands.Cog):
    """A collection of utility commands for managing and manipulating server-related tasks."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def ping(self, ctx):
        """Check the bot's latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! Latency: {latency}ms")

    @commands.hybrid_command()
    async def say(self, ctx, *, message):
        """Make the bot say a message"""
        if message == None:
            await ctx.send('Provide the message to say')
        await ctx.send(message)

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def rename_channel(self, ctx, channel: discord.TextChannel, new_name: str):
        """Rename a channel"""
        if channel == None:
            await ctx.send('Provide channel mention')
        if new_name == None:
            await ctx.send(f'Provide the new name for {channel}')
        await channel.edit(name=new_name)
        await ctx.send(f"The channel has been renamed to {channel.mention}.")

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def move_channel(self, ctx, channel: discord.TextChannel, category: discord.CategoryChannel):
        """Move a channel to a different category"""
        await channel.edit(category=category)
        await ctx.send(f"The channel {channel.mention} has been moved to the category {category.name}.")

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, channel: discord.TextChannel, duration: int):
        """Set the slowmode duration for a channel"""
        await channel.edit(slowmode_delay=duration)
        await ctx.send(f"The slowmode duration for {channel.mention} has been set to {duration} seconds.")

    @commands.hybrid_command(aliases=['delete'])
    @commands.has_permissions(manage_channels=True)
    async def delete_channel(self, ctx, channel: discord.TextChannel):
        """Delete a channel"""
        await channel.delete()
        await ctx.send(f"The channel {channel.mention} has been deleted.")

    @commands.hybrid_command()
    @commands.has_permissions(manage_roles=True, manage_channels=True)
    async def add_role_to_channel(self, ctx, channel: discord.TextChannel, role: discord.Role):
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

    @commands.hybrid_command()
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

    @commands.hybrid_command()
    async def avatar(self, ctx, member: discord.Member = None): #type: ignore
        """Show the avatar of a user"""
        if member is None:
            member = ctx.author

        avatar_url = member.avatar.url #type: ignore

        embed = discord.Embed(title="User Avatar")
        embed.set_image(url=avatar_url)

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def userinfo(self, ctx, member: discord.Member = None): #type: ignore
        """Get information about a user"""
        if member is None:
            member = ctx.author

        embed = discord.Embed(title="User Info")
        embed.set_thumbnail(url=member.avatar.url) #type: ignore

        if member.banner is not None:
            embed.set_image(url=member.banner.url)

        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="Discriminator", value=member.discriminator, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Bot", value=member.bot, inline=True)
        embed.add_field(name="Created At", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True) #type: ignore
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=['dmrole'])
    @commands.has_permissions(administrator=True)
    async def dm_role(self, ctx, role: discord.Role, *, args):
        memberlist = []
        mlist = []
        for member in role.members:
            try:
                await member.send(args)
                memberlist.append(member.name)
                mlist = ", \n".join(memberlist)
            except Exception as e:
                print(e)
        embed = discord.Embed(title="Direct Message sent to Members")
        embed.description = f"""
**__Role:__**
```{role}```

**__Members:__** 
```{mlist}```

**__Message:__**
```{args}```
"""
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar)
        embed.timestamp = discord.utils.utcnow()
        channel = self.bot.get_channel(dcfg.modchannel)
        await channel.send(embed=embed)

    @commands.hybrid_command(aliases=['message'])
    @commands.has_permissions(administrator=True)
    async def dm(self, ctx, member: discord.Member, *, message):
        "Direct message a user"
        try:
            await member.send(message)
            await ctx.send(f"```{message}``` sent to {member.name}#{member.discriminator}")
            logembed = discord.Embed()
            logembed.title = f'Direct Message send to: __`{member.name}{member.discriminator}`__'
            logembed.description = f'''
            **__Message:__** 
            ```{message}``` '''
            logembed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar)
            dmchannel = discord.utils.get(ctx.guild.channels, id=dcfg.modchannel)
            await dmchannel.send(embed=logembed)
        except:
            return await ctx.send('❌ Logging has failed!')

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

    @commands.hybrid_command()
    async def devinfo(self, ctx):
        """
        Get information about the bot developer and other details
        """
        # Developer Information
        dev_socials = "https://solo.to/a3ro.xyz"
        dev_web = "https://a3ro.xyz"
        dev_github = "a3ro-dev"

        # Bot Information
        bot_name = self.bot.user.name
        bot_version = discord.__version__
        python_version = platform.python_version()
        discord_py_version = discord.__version__
        os_info = f"{platform.system()} {platform.release()}"
        isp_info = socket.gethostname()
        # print(isp_info) 

        embed = discord.Embed(title=f"{bot_name} Developer Info", description=f"💻 {dev_socials}\n🌐 {dev_web}\n📚 {dev_github}")
        embed.add_field(name="Bot Version", value=bot_version, inline=True)
        embed.add_field(name="Python Version", value=python_version, inline=True)
        embed.add_field(name="discord.py Version", value=discord_py_version, inline=True)
        embed.add_field(name="OS Info", value=os_info, inline=True)
        embed.add_field(name="ISP Info", value=isp_info, inline=True)

        # Add a link to the bot's GitHub repository
        github_repo = "https://github.com/a3ro-dev/pixelshield"
        embed.add_field(name="GitHub Repository", value=f"[GitHub Repo]({github_repo})", inline=False)

        # Customize the footer with a nerdy message
        embed.set_footer(text="Aero by day, Aeroplane by night!")

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        targeted_category_id = dcfg.ticket_categ_id 
        targeted_user_id = 929438824227020832

        if message.author.bot:
            return

        if message.channel.category_id != targeted_category_id:
            return
        
        if message.channel == discord.DMChannel:
            return

        if message.mentions and not message.author.guild_permissions.administrator:
            targeted_user = message.guild.get_member(targeted_user_id)  
            if targeted_user and targeted_user in message.mentions:
                reply = f"Hello {message.author.mention}, please note that the minimum response time for {targeted_user.mention} is three hours. We kindly request your patience as they may be busy attending to other matters. We appreciate your understanding!"
                await message.channel.send(reply)

    @commands.hybrid_command(aliases=['social'], description="Sends socials of PixelShield")
    async def socials(self, ctx):
        button1 = discord.ui.Button(label='Facebook', url="https://discord.com/channels/1117696325010587720/1117696326839312418",
                             emoji='<:facebook:1132595134769397830>')

        button2 = discord.ui.Button(label='Telegram',
                             url="https://discord.com/channels/1117696325010587720/1117696326839312423",
                             emoji='<:Telegram:1136858886096298158>')

        button3 = discord.ui.Button(label='Instagram',
                             url="https://discord.com/channels/1117696325010587720/1117696326839312417",
                             emoji='<:Instagram:1132594548074360933>')

        button4 = discord.ui.Button(label='Website',
                             url="https://discord.com/channels/1117696325010587720/1117696327095156746",
                             emoji='<:website:1132594836202061905>')

        view = discord.ui.View()
        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
        view.add_item(button4)
        await ctx.send("Choose the social media that you would like to follow!", view=view)



async def setup(bot):
    await bot.add_cog(Utilities(bot))
