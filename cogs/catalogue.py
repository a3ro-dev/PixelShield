import discord
from discord.ext import commands
import configuration.discordConfig as dcfg
from discord.ui import button
import os
import logging
from datetime import datetime

# Configure logging
log_file = f"./logs/{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.log"
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=log_file
)

# Create a logger instance
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)

admin_id = dcfg.admin_uid
base_dir = dcfg.base_dir
cover_dir = os.path.join(base_dir, "covers")
skin_dir = os.path.join(base_dir, "skins")


class Catalogue(commands.Cog):
    """
    Shows The Available Designs' Catalogue
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=['designs', 'catalog', 'covers', 'skins'])
    async def catalogue(self, ctx):
        """
        Display the available designs catalogue.
        """
        if isinstance(ctx.channel, discord.DMChannel) or isinstance(ctx.channel, discord.GroupChannel):
            await self.send_catalogue(ctx)
        else:
            if ctx.author.guild_permissions.administrator:
                await self.send_catalogue(ctx)
            else:
                await ctx.send("This command is restricted to admins.")

    async def send_catalogue(self, ctx):
        view = coversSkinsButtons()
        view.response = await ctx.send("Which catalog do you want to browse?", view=view, ephemeral=True)
        view.response.author_id = ctx.author.id

    @commands.Cog.listener()
    async def on_component(self, ctx):
        if ctx.author.id == self.bot.user.id:
            return

        if ctx.origin_message.author.id == self.bot.user.id:
            if ctx.author.id == ctx.origin_message.author_id:
                view = ctx.view
                view.value = ctx.custom_id

                if view.value == 'covers':
                    await self.send_cover_catalogue(ctx)
                elif view.value == 'skins':
                    await self.send_skin_catalogue(ctx)

    async def send_cover_catalogue(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and not isinstance(ctx.channel, discord.GroupChannel):
            view = coversSkinsButtons()
            files = os.listdir(cover_dir)
            files = [f for f in files if os.path.isfile(os.path.join(cover_dir, f))]
            files.sort()
            for file in files:
                name = os.path.splitext(file)[0]
                embed = discord.Embed(title=f"Covers Catalogue - {name}")
                embed.set_image(url=f"attachment://{file}")
                await ctx.send(file=discord.File(os.path.join(cover_dir, file), filename=file), embed=embed, view=view)

            view.response = await ctx.send("All covers have been displayed.", ephemeral=True)

    async def send_skin_catalogue(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and not isinstance(ctx.channel, discord.GroupChannel):
            view = coversSkinsButtons()
            files = os.listdir(skin_dir)
            files = [f for f in files if os.path.isfile(os.path.join(skin_dir, f))]
            files.sort()
            for file in files:
                name = os.path.splitext(file)[0]
                embed = discord.Embed(title=f"Skins Catalogue - {name}")
                embed.set_image(url=f"attachment://{file}")
                await ctx.send(file=discord.File(os.path.join(skin_dir, file), filename=file), embed=embed, view=view)

            view.response = await ctx.send("All skins have been shared.", ephemeral=True)


class coversSkinsButtons(discord.ui.View):
    def __init__(self):
        self.value = None
        super().__init__(timeout=None)

    @button(label='Covers', style=discord.ButtonStyle.green, custom_id='covers')
    async def coversbtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        files = os.listdir(cover_dir)
        files = [f for f in files if os.path.isfile(os.path.join(cover_dir, f))]
        files.sort()
        for file in files:
            name = os.path.splitext(file)[0]
            embed = discord.Embed(title=f"Covers Catalogue - {name}")
            embed.set_image(url=f"attachment://{file}")
            await interaction.channel.send(file=discord.File(os.path.join(cover_dir, file), filename=file), embed=embed)

        try:
            await interaction.response.send_message("All covers have been displayed.", ephemeral=True)
        except discord.errors.NotFound as e:
            logger.error(f"Error sending message: {e}")

    @button(label='Skins', style=discord.ButtonStyle.blurple, custom_id='skins')
    async def skinsbtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        files = os.listdir(skin_dir)
        files = [f for f in files if os.path.isfile(os.path.join(skin_dir, f))]
        files.sort()
        for file in files:
            name = os.path.splitext(file)[0]
            embed = discord.Embed(title=f"Skins Catalogue - {name}")
            embed.set_image(url=f"attachment://{file}")
            await interaction.channel.send(file=discord.File(os.path.join(skin_dir, file), filename=file), embed=embed)

        try:
            await interaction.response.send_message("All skins have been shared.", ephemeral=True)
        except discord.errors.NotFound as e:
            logger.error(f"Error sending message: {e}")


async def setup(bot):
    await bot.add_cog(Catalogue(bot))
