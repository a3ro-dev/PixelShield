import sqlite3
from configuration import discordConfig as dcfg
from discord.ext import commands
import asyncio
import logging
import json
import pickle

logger = logging.getLogger(__name__)

class Auth(commands.Cog):
    """
    PixelShield Account Handler
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('./database/users.db')
        self.cursor = self.db.cursor()
        self.create_table()

    def create_table(self):
        """
        Create the users table if it doesn't exist.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT
                orders TEXT
            )
        """)
        self.db.commit()

    @commands.hybrid_command(aliases=['signup', 'create_account'])
    async def register(self, ctx):
        """
        Register a new user account with PixelShield.
        """
        user_id = ctx.author.id
        self.cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        result = self.cursor.fetchone()
        if result:  # User already exists in database
            await ctx.send(f"Welcome, {result[1]}! You are already a registered user of PixelShield.")
        else:
            await ctx.send("<:pixelshield:1126182274422026300>")

            async def loading_animation():
                frames = ["/", "-", "\\", "|"]
                i = 0
                message = await ctx.send("Creating PixelShield account...")
                while i < 5:
                    await asyncio.sleep(1)
                    i += 1
                    await message.edit(content=f"Creating PixelShield account... {frames[i % 4]}")

            try:
                await asyncio.gather(loading_animation(), asyncio.sleep(5))

                await ctx.send("Send your user ID to complete the account creation process.")
                user_id_input = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
                if user_id_input.content.strip() != str(user_id):  # Check if user ID matches the input
                    await ctx.send("Invalid user ID.")
                    return

                await ctx.send("Please enter your full name.")
                name_input = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
                name = name_input.content.strip()

                self.cursor.execute("INSERT INTO users (id, name) VALUES (?, ?)", (user_id, name))
                self.db.commit()

                await ctx.send(f"Welcome, {name}! Your account has been created.")
            except asyncio.TimeoutError:
                await ctx.send("Sorry, I didn't get a response from you. Please try again later.")
                return
            except Exception as e:
                await ctx.send("An error occurred during account creation. Please try again later.")
                error_message = f"Error: {str(e)}"
                logger.error(error_message)
                admin_id = dcfg.admin_uid #type: ignore
                admin = await self.bot.fetch_user(admin_id)
                await admin.send(error_message)

    @commands.hybrid_command(aliases=['logout', 'signout', 'del_acc'])
    async def delete_account(self, ctx):
        """
        Delete the user account and related data from PixelShield.
        """
        user_id = ctx.author.id
        self.cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        result = self.cursor.fetchone()
        if not result:  # User does not exist in the database
            await ctx.send("You don't have a PixelShield account to delete.")
            return

        await ctx.send("Are you sure you want to delete your account and all related data? (y/n)")
        try:
            confirm = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=10)
        except asyncio.TimeoutError:
            await ctx.send("Time's up. Account deletion canceled.")
            return

        if confirm.content.strip().lower() != 'y':
            await ctx.send("Account deletion canceled.")
            return

        async def loading_animation():
            frames = ["/", "-", "\\", "|"]
            i = 0
            message = await ctx.send("Deleting PixelShield account...")
            while i < 5:
                await asyncio.sleep(1)
                i += 1
                await message.edit(content=f"Deleting PixelShield account... {frames[i % 4]}")

        try:
            await asyncio.gather(loading_animation(), asyncio.sleep(5))

            self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            self.db.commit()

            await ctx.send("Your account and related data have been deleted successfully.")
        except Exception as e:
            await ctx.send("An error occurred during account deletion. Please try again later.")
            error_message = f"Error: {str(e)}"
            logger.error(error_message)
            admin_id = dcfg.admin_uid  # type: ignore
            admin = await self.bot.fetch_user(admin_id)
            await admin.send(error_message)


    @commands.has_any_role(*dcfg.bot_dev)  # Check if the user has any role in the bot_dev list
    @commands.hybrid_command(aliases=['addo', 'add_orderhist', 'addhist'])
    async def add_order(self, ctx, user: commands.UserConverter, *, order_details: str):
        """
        Add an order for a user in the database.
        """
        self.create_table()
        user_id = user.id # type: ignore
        self.cursor.execute("SELECT id, orders FROM users WHERE id=?", (user_id,))
        result = self.cursor.fetchone()

        if result is None:  # User does not exist in the database
            await ctx.send(f"{user.display_name} does not have a PixelShield account. They need to register first.") # type: ignore
            return

        user_id, orders_data = result
        if not orders_data:
            orders_data = []

        orders_data.append(order_details)
        self.cursor.execute("UPDATE users SET orders=? WHERE id=?", (sqlite3.Binary(pickle.dumps(orders_data)), user_id))
        self.db.commit()

        await ctx.send(f"Order added for {user.display_name} (ID: {user_id}).") # type: ignore

    @commands.hybrid_command(aliases=['del_oddhist', 'delete_order'])
    async def delete_orderhist(self, ctx):
        # Step 2: Retrieve user's order history from the database
        user_id = str(ctx.author.id)
        self.cursor.execute("SELECT orders FROM users WHERE id=?", (user_id,))
        result = self.cursor.fetchone()
        if not result or not result[0]:
            await ctx.send("You don't have any order history.")
            return

        # Step 3: Deserialize user's order history from the bytes retrieved from the database
        orders_data = pickle.loads(result[0])
        if not isinstance(orders_data, dict):
            await ctx.send("Error: Invalid order data format in the database.")
            return

        orders_list = list(orders_data.keys())
        if not orders_list:
            await ctx.send("You don't have any order history.")
            return

        # Step 4: Display user's order history and ask them to choose the order to delete
        orders_str = "\n".join(f"{index + 1}. {order}" for index, order in enumerate(orders_list))
        await ctx.send(f"Your order history:\n{orders_str}\n\nPlease enter the number of the order you want to delete.")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            reply = await self.bot.wait_for("message", check=check, timeout=30)
            index = int(reply.content) - 1
            if 0 <= index < len(orders_list):
                # Step 5: Delete the chosen order from the user's order history in the database
                del orders_data[orders_list[index]]
                self.cursor.execute("UPDATE users SET orders=? WHERE id=?", (sqlite3.Binary(pickle.dumps(orders_data)), user_id))
                self.db.commit()
                await ctx.send("Order deleted successfully.")
            else:
                await ctx.send("Invalid input. Please enter a valid number.")
        except ValueError:
            await ctx.send("Invalid input. Please enter a valid number.")
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. The command has been canceled.")

    @commands.has_any_role(*dcfg.bot_dev)  # Check if the user has any role in the bot_dev list
    @commands.hybrid_command(aliases=['orderhist', 'oh'])
    async def order_history(self, ctx, user: commands.UserConverter):
        """
        Show a user's order history along with other details in an embed.
        """
        user_id = user.id #type: ignore
        self.cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        result = self.cursor.fetchone()
        if not result:  # User does not exist in the database
            await ctx.send(f"{user.display_name} does not have a PixelShield account. They need to register first.") #type: ignore
            return

        orders_data = json.loads(result[2]) if result[2] else {}
        order_history = "\n".join(f"{order}: {details}" for order, details in orders_data.items())

        embed = Embed(title=f"Order History for {user.display_name}") #type: ignore
        embed.add_field(name="User ID", value=user_id, inline=False)
        embed.add_field(name="Order History", value=order_history or "No orders found.", inline=False)

        await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Auth(bot))
