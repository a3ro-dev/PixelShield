import discord
from discord.ext import commands
import os
import sqlite3
import configuration.discordConfig as dcfg

admin_id = dcfg.admin_uid  # Replace with the actual admin user ID
cover_dir = os.path.join(dcfg.base_dir, "covers")
skin_dir = os.path.join(dcfg.base_dir, "skins")

database_file = "./database/users.db"
table_name = "users"


class Ordering(commands.Cog):
    """
    Orders Handler
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """
         Load cog. This is called when the user clicks on the button to load
        """
        self.bot.add_view(OrderingModalViewBut())

    @commands.command(aliases=['buy', 'form', 'place_order'])
    async def order(self, ctx):
        """
         Displays the order modal. Note that you need to be logged in to make this a bot command
        """
        
        embed = discord.Embed(title="Place an Order",
                              description="**Fill This Form To Proceed**")
        embed.set_footer(
            icon_url="https://media.discordapp.net/attachments/1120014819278463107/1126180390466490468/pixelshield.png?width=404&height=404")
        view = OrderingModalViewBut()
        await ctx.send(embed=embed, view=view)

class OrderingCallModalView(discord.ui.Modal, title='Order Details'):
    q1 = discord.ui.TextInput(
        label='Device Information',
        style=discord.TextStyle.short,
        placeholder='Enter your device/model name',
        required=True,
        max_length=80
    )

    q2 = discord.ui.TextInput(
        label='Address',
        style=discord.TextStyle.short,
        placeholder='Enter your delivery address',
        required=True,
        max_length=200
    )

    q3 = discord.ui.TextInput(
        label='Design Name',
        style=discord.TextStyle.short,
        placeholder='Enter design name',
        required=True,
        max_length=50
    )

    q4 = discord.ui.TextInput(
        label='Phone Number',
        style=discord.TextStyle.short,
        placeholder='Enter your phone number',
        required=True,
        max_length=15
    )
    q5 = discord.ui.TextInput(
        label='Delivery Instructions',
        style=discord.TextStyle.short,
        placeholder='Enter delivery instructions',
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        """
         Called when user submits order request. This is a callback for discord to create a file and send it to the user
         
         @param interaction - Object containing information about the
        """
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed()
        embed.title = f'Order Request From - __@{interaction.user.name}__'
        user_id = interaction.user.id
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        order_data = f"{self.q3.value},"
        cursor.execute("UPDATE users SET orders = ? WHERE id = ?", (order_data, user_id))
        conn.commit()
        conn.close()
        accname = get_user_name(user_id=user_id)
        embed.add_field(name="User's Name", value=f'`{accname}`', inline=True)
        embed.add_field(name='Device Information', value=f'`{self.q1.value}`', inline=True)
        embed.add_field(name='Address', value=f'`{self.q2.value}`', inline=True)
        embed.add_field(name='Design Name', value=f'`{self.q3.value}`', inline=True)
        embed.add_field(name='Phone Number', value=f'`{self.q4.value}`', inline=True)
        embed.add_field(name='Delivery Instructions', value=f'`{self.q5.value}`', inline=False)
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        embed.set_footer(text=interaction.guild.name, #type: ignore
                         icon_url="https://media.discordapp.net/attachments/1120014819278463107/1126180390466490468/pixelshield.png?width=404&height=404")
        guild = interaction.guild
        category_id = dcfg.ticket_categ_id
        user_name = interaction.user.name

        # Create a new category if it doesn't exist
        category = discord.utils.get(guild.categories, id=category_id) #type: ignore
        if category is None:
            category = await guild.create_category('Tickets') #type: ignore

        # Create the ticket channel
        ticket_channel = await category.create_text_channel(name=f'{user_name}-ticket')

        # Send the embed and mention the staff role
        await ticket_channel.send(embed=embed) #type: ignore
        staff_role_id = 1117696325010587723
        staff_role = discord.utils.get(guild.roles, id=staff_role_id) #type: ignore
        if staff_role:
            await ticket_channel.send(f'{staff_role.mention}')
        user = interaction.user.id
        await ticket_channel.send(f'<@{user}>')

        # Return the ticket channel
        return ticket_channel

class OrderingModalViewBut(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(emoji='<:pixelshield:1126182274422026300>', style=discord.ButtonStyle.gray, custom_id='applybut')
    async def callmodalcallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(OrderingCallModalView())

def get_user_name(user_id):
    """
     Get the name of a user.
     
     @param user_id - The user's id
     
     @return The user's name or " Unknown " if not
    """
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM {table_name} WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "User not yet signed up"

async def setup(bot):
    await bot.add_cog(Ordering(bot))
