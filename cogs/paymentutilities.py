import discord
from discord.ext import commands
from discord.ui import View, Button
from PIL import Image
import configuration.discordConfig as dcfg
import os
import io
import qrcode.main as qrcode
from bhimupipy import verify_upi

class UPIView(View):
    def __init__(self, upi_url):
        super().__init__()

        self.upi_url = upi_url
        # Create the blurple button
        self.button = Button(style=discord.ButtonStyle.blurple, label="Make Payment", url=self.upi_url, emoji='<:upi:1126125282311553044>')
        self.add_item(self.button)

class UPI(commands.Cog):
    """
    UPI Utility Commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def upi(self, ctx, amount: int, description: str):
        """
        Generates Payment QR Code
        """
        if amount is None:
            await ctx.send('Please enter an Amount')

        if description is None:
            await ctx.send('Please enter the design name')
        upi_id = dcfg.upi_id
        # Generate the UPI link
        upi_url = f"https://tools.apgy.in/upi/PixelShield/{upi_id}/{amount}"
        upi_link = f"upi://pay?pa={upi_id}&pn=PixelShield&am={amount}tn={description}"
        # Create a QR code image
        qr_code = qrcode.QRCode()
        qr_code.add_data(upi_link)
        qr_code_image = qr_code.make_image(fill_color="black", back_color="white")
        qr_code_image = qr_code_image.resize((1000, 1000))  # Resize the QR code to 800x800 pixels
        # Load the border image
        border_path = "/home/ubuntu/PixelShield/assets/borders.png" 
        border_image = Image.open(border_path)
        # Create a blank image of the size of the space in the center of the border (800x800)
        blank_image = Image.new("RGBA", (1000, 1000), (255, 255, 255, 0))
        # Calculate the position to place the QR code in the center of the blank image
        offset = ((blank_image.width - qr_code_image.width) // 2, (blank_image.height - qr_code_image.height) // 2)
        # Paste the QR code onto the blank image
        blank_image.paste(qr_code_image, offset)
        # Calculate the position to place the blank image (with QR code) onto the border image
        border_offset = ((border_image.width - blank_image.width) // 2, (border_image.height - blank_image.height) // 2)
        # Paste the blank image (with QR code) onto the border image
        border_image.paste(blank_image, border_offset)
        # Save the final image with the QR code and border
        qr_code_with_border_path = f"qrcodes/upi_qr_{amount}_with_border.png"  # QR code with border file path
        border_image.save(qr_code_with_border_path)

        # Create an embed message
        embed = discord.Embed(title="UPI", description=f"Amount: {amount}")
        embed.add_field(name=f"UPI Link", value=f"[Click Here]({upi_url})")
        embed.set_footer(text=f"💳 UPI ID: {upi_id}")

        # Convert the QR code with border to bytes
        qr_bytes = io.BytesIO()
        border_image.save(qr_bytes, format='PNG')
        qr_bytes.seek(0)

        # Send the embed message with the QR code as an attachment and the button
        view = UPIView(upi_url)
        qr_file = discord.File(qr_code_with_border_path, filename='qr_code.png')
        await ctx.send(content="Click the button below to make the payment:", embed=embed, view=view, file=qr_file)

        # Delete the generated QR code file
        os.remove(qr_code_with_border_path)  
        # Wait for the interaction
        try:
            interaction = await self.bot.wait_for("button_click", timeout=60, check=lambda i: i.message == message and i.user == ctx.author)
            if interaction.component == view.button:
                await interaction.respond(type=InteractionType.OpenUrl, url=upi_url)
        except asyncio.TimeoutError:
            await ctx.send("The interaction timed out.")
     
    @commands.hybrid_command()
    async def check_upi(self, ctx, upi_id: str):          
        """
        Checks the validity and shows information regarding a vpa
        """
        if upi_id is None:
            await ctx.send('Enter upi id')
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
