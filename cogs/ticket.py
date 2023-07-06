import discord
from discord.ext import commands
import configuration.discordConfig as config
import asyncio
import logging
import time

class Tickets(commands.Cog):
    """
    This Is The Main Class For Ticket Related Commands
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log_file = f"logs/log_{time.strftime('%Y%m%d-%H%M%S')}.log"

    async def cog_load(self):
        self.bot.add_view(TicketView())
        self.bot.add_view(Close())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def open_ticket(self, ctx: commands.Context):
        try:
            await ctx.send(content="Please select a ticket type", view=TicketView())
        except Exception as e:
            logging.error(f"Failed to open ticket: {e}")

class Tickett(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Order", description="Contact the staff for issues related to ordering", value="Order"),
            discord.SelectOption(label="Issue", description="Contact the admin for severe issues for higher priority", value="Issue"),
            discord.SelectOption(label="Partnership", description="Contact the partnership manager for partnerships", value="Partnership"),
            discord.SelectOption(label="Bot Issue", description="Contact the developer for bot related issues", value="Bot Issue")
        ]

        super().__init__(placeholder='Choose a type of ticket...', min_values=1, max_values=1, custom_id="Tick:panel",
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        try:
            if self.values[0] == "Order":
                mod = interaction.guild.get_role(config.TicketSupportRole)  # Mod1
                categ = discord.utils.get(interaction.guild.categories, id=config.ticket_categ_id)
                await interaction.response.send_message("Creating a ticket for you, this may take a while!", ephemeral=True)
                ticket_channel = await categ.create_text_channel(name=f"order-{interaction.user.name}")

                await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
                await ticket_channel.set_permissions(mod, read_messages=True, send_messages=True)
                view = Close()
                await ticket_channel.send(
                        f"{interaction.user.mention} | <@&{config.TicketSupportRole}> ")
                embed = discord.Embed(title=f"{interaction.guild.name} Support!",
                                      description="Thank you for reaching out. Our staff will assist you with your order-related issue.")
                await ticket_channel.send(embed=embed, view=view)

            if self.values[0] == "Issue":
                mod = interaction.guild.get_role(config.AdminSupportRole)  # Mod2
                categ = discord.utils.get(interaction.guild.categories, id=config.ticket_categ_id)
                await interaction.response.send_message("Creating a ticket for you, this may take a while!", ephemeral=True)
                ticket_channel = await categ.create_text_channel(name=f"issue-{interaction.user.name}")

                await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
                await ticket_channel.set_permissions(mod, read_messages=True, send_messages=True)
                view = Close()
                await ticket_channel.send(
                        f"{interaction.user.mention} | <@&{config.AdminSupportRole}> ")
                embed = discord.Embed(title=f"{interaction.guild.name} Support!",
                                      description="Thank you for reaching out. Our admin will assist you with your issue.")
                await ticket_channel.send(embed=embed, view=view)
            
            if self.values[0] == "Partnership":
                mod = interaction.guild.get_role(config.PartnerShipSupportRole)  # Mod3
                categ = discord.utils.get(interaction.guild.categories, id=config.ticket_categ_id)
                await interaction.response.send_message("Creating a ticket for you, this may take a while!", ephemeral=True)
                ticket_channel = await categ.create_text_channel(name=f"partnership-{interaction.user.name}")

                await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
                await ticket_channel.set_permissions(mod, read_messages=True, send_messages=True)
                view = Close()
                await ticket_channel.send(
                        f"{interaction.user.mention} | <@&{config.PartnerShipSupportRole}> ")
                embed = discord.Embed(title=f"{interaction.guild.name} Support!",
                                      description="Thank you for reaching out. Our partnership manager will assist you with your partnership inquiry.")
                await ticket_channel.send(embed=embed, view=view)

            if self.values[0] == "Bot Issue":
                mod = interaction.guild.get_role(config.BotDevRole)  # Mod4
                categ = discord.utils.get(interaction.guild.categories, id=config.ticket_categ_id)
                await interaction.response.send_message("Creating a ticket for you, this may take a while!", ephemeral=True)
                ticket_channel = await categ.create_text_channel(name=f"bot-issue-{interaction.user.name}")

                await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
                await ticket_channel.set_permissions(mod, read_messages=True, send_messages=True)
                view = Close()
                await ticket_channel.send(
                        f"{interaction.user.mention} | <@&{config.BotDevRole}> ")
                embed = discord.Embed(title=f"{interaction.guild.name} Support!",
                                      description="Thank you for reaching out. Our developer will assist you with your bot-related issue.")
                await ticket_channel.send(embed=embed, view=view)
        except Exception as e:
            logging.error(f"Failed to create ticket: {e}")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Tickett())

class Close(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, custom_id='del')
    async def tick_close(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message('You are missing permissions to delete the channel!', ephemeral=True)
            else:
                await interaction.response.send_message('Deleting the channel in 10 seconds!')
                await asyncio.sleep(10)
                await interaction.channel.delete()
                self.value = True
        except Exception as e:
            logging.error(f"Failed to close ticket: {e}")

async def setup(bot: commands.Bot):
    try:
        await bot.add_cog(Tickets(bot))
        logging.info("Tickets cog loaded successfully")
    except Exception as e:
        logging.error(f"Failed to load Tickets cog: {e}")

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename=f"./logs/log_{time.strftime('%Y%m%d-%H%M%S')}.log")

# Add console handler to log messages to the console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)
