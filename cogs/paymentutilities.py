import discord
from discord.ext import commands
from discord.ui import View, Button
import os
import io
import qrcode
import pyshorteners
from bhimupipy import verify_upi

class UPIView(View):
    def __init__(self, upi_url):
        super().__init__()

        self.upi_url = upi_url

        # Create the blurple button
        self.button = Button(style=discord.ButtonStyle.blurple, label="Make Payment", url=self.upi_url)

        self.add_item(self.button)

class UPI(commands.Cog):
    """
    UPI Utility Commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def upi(self, ctx, amount: int):
        """
        Generates Payment QR Code
        """
        # Generate the UPI link
        upi_url = f"https://pay.upilink.in/pay/pheonixelite1@okaxis?am={amount}"
        upi_link = f"upi://pay?pa=pheonixelite1@okaxis&pn=Aero&am={amount}"

        # Shorten the UPI link using TinyURL
        upi_shortened = self.shorten_link(upi_url)

        # Create the 'qrcodes' directory if it doesn't exist
        if not os.path.exists("qrcodes"):
            os.makedirs("qrcodes")

        # Create a QR code image
        qr_code = qrcode.QRCode()
        qr_code.add_data(upi_link)
        qr_code_image = qr_code.make_image(fill_color="black", back_color="white")
        qr_code_image = qr_code_image.resize((200, 200))  # Resize the QR code to 200x200 pixels

        # Save the QR code as a file
        qr_code_path = f"qrcodes/upi_qr_{amount}.png"  # QR code file path
        qr_code_image.save(qr_code_path)

        # Create an embed message
        embed = discord.Embed(title="UPI", description=f"Amount: {amount}")
        embed.add_field(name=f"UPI Link", value=f"[Click Here]({upi_shortened})")
        embed.set_footer(text="💳 UPI ID: akshatt@fam")

        # Convert the QR code to bytes
        qr_bytes = io.BytesIO()
        qr_code_image.save(qr_bytes, format='PNG')
        qr_bytes.seek(0)

        # Send the embed message with the QR code as an attachment and the button
        view = UPIView(upi_shortened)
        qr_file = discord.File(qr_code_path, filename='qr_code.png')
        await ctx.send(content="Click the button below to make the payment:", embed=embed, view=view, file=qr_file)

        # Delete the generated QR code file
        os.remove(qr_code_path)

    def shorten_link(self, link):
        s = pyshorteners.Shortener()
        shortened_url = s.tinyurl.short(link)
        return shortened_url
    
    @commands.command()
    async def check_upi(self, ctx, upi_id: str):
        """
        Checks the validity and shows information regarding a vpa
        """
        # Verify the UPI ID using the bhimupipy library
        result = verify_upi(upi_id)

        # Create an embed message with the UPI details
        embed = discord.Embed(title="UPI Verification")

        if result and result["result"]:
            embed.add_field(name="Result", value=str(result["result"]), inline=False)
            embed.add_field(name="Status", value=result["data"]["status"], inline=False)
            embed.add_field(name="VPA", value=result["data"]["vpa"], inline=False)
            embed.add_field(name="Payee Account Name", value=result["data"]["payeeAccountName"], inline=False)
            embed.set_footer(text=f"UPI ID: {upi_id}", icon_url="https://cdn.discordapp.com/emojis/1126125282311553044.webp?size=96&quality=lossless")
        else:
            embed.description = "Failed to verify UPI ID"

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UPI(bot))
