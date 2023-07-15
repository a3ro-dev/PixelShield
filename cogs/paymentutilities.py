import discord
from discord.ext import commands
from discord.ui import View, Button
import configuration.discordConfig as dcfg
import os
import io
import qrcode
import pyshorteners
from bhimupipy import verify_upi
import requests
import json
import paytmchecksum

mid = dcfg.mid
merchant_key = dcfg.merchant_key

def create_payment_link(amount: int, description: str):
    # Prepare the request parameters
    paytm_params = {
        "body": {
            "mid": mid,
            "linkType": "GENERIC",
            "linkDescription": description,
            "linkName": "Payment",
            "amount": amount
        },
        "head": {
            "tokenType": "AES"
        }
    }

    # Generate checksum by parameters
    checksum = paytmchecksum.generateSignature(json.dumps(paytm_params["body"]), merchant_key)
    paytm_params["head"]["signature"] = checksum

    # Make the API request
    url = "https://securegw-stage.paytm.in/link/create"  # Use the staging URL for testing
    response = requests.post(url, json=paytm_params)

    # Parse the response
    response_data = response.json()
    if response_data.get("body") and response_data["body"].get("shortUrl"):
        return response_data["body"]["shortUrl"]
    else:
        return None

def is_payment_received(payment_id):

    # Prepare the request parameters
    paytm_params = {
        "body": {
            "mid": mid,
            "orderId": payment_id
        },
        "head": {
            "tokenType": "AES"
        }
    }

    # Generate checksum by parameters
    checksum = paytmchecksum.generateSignature(json.dumps(paytm_params["body"]), merchant_key)
    paytm_params["head"]["signature"] = checksum

    # Make the API request
    url = "https://securegw-stage.paytm.in/v3/order/status"  # Use the staging URL for testing
    response = requests.post(url, json=paytm_params)

    # Parse the response
    response_data = response.json()
    if response_data.get("body") and response_data["body"].get("resultInfo"):
        result = response_data["body"]["resultInfo"]
        if result.get("resultStatus") == "TXN_SUCCESS":
            return True
        else:
            return False
    else:
        return False


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

    @commands.hybrid_command()
    async def upi(self, ctx, amount: int, description: str):
        """
        Generates Payment QR Code
        """
        # Generate the UPI link
        upi_url = create_payment_link(amount=amount, description=description)
        upi_link = f"upi://pay?pa=&pn=PixelShield&am={amount}"

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
        embed.set_footer(text="💳 UPI ID: ")

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
    
    @commands.hybrid_command()
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
