import discord
from discord.ext import commands
from discord.ui import View, Button

import configuration.discordConfig as cfg


class Greetings (commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed=discord.Embed(title="**PIXELSHIELD**")
        button1 = Button(label='Terms and Conditions', url="https://discord.com/channels/1117696325010587720/1120014819278463106",
                       emoji='<:termsofuse:1132587437957332992>')

        button2 = Button(label='Catalogue',
                       url="https://discord.com/channels/1117696325010587720/1117696326080135188",
                       emoji='📚')

        button3 = Button(label='Order',
                       url="https://discord.com/channels/1117696325010587720/1117696326386339860",
                       emoji='<:pixelshield:1126182274422026300>')

        view = View()
        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
        embed.description = f"""
⪦━━━━━━━━━━━━━━━━━━━━━━━⪧
**Thankyou for Joining as __{member.guild.member_count}th__ Member!**

<:pixelshield:1126182274422026300> __Go through the rules you need to follow__
<:pixelshield:1126182274422026300> **| Terms and conditions:** <#1120014819278463106>
<:pixelshield:1126182274422026300> __Checkout what all we offer__
<:pixelshield:1126182274422026300> **| Catalogue** <#1117696326080135188>
<:pixelshield:1126182274422026300> __Experience fashionable uniquenes__
<:pixelshield:1126182274422026300> **| Order Placement:** <#1117696326386339860>
⪦━━━━━━━━━━━━━━━━━━━━━━━⪧
**HAVE A GOOD STAY ♡**"""
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f'{member.guild.name} | {member.guild.id}', icon_url=member.guild.icon.url) #type: ignore
        channel = member.guild.get_channel(cfg.WELCOME) 
        await channel.send(content=member.mention,embed=embed, view=view) #type: ignore
        await member.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        description = (f'**{member.name}** just left us.\n'
                       f"We're now **{len(member.guild.members)}** members.\n")
        embed = discord.Embed(
            title='Farewell', description=description,)
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(
            text=f'{member.guild.name} | {member.guild.id}', icon_url=member.guild.icon.url) #type: ignore

        channel = member.guild.get_channel(cfg.FAREWELL)
        await channel.send(embed=embed) #type: ignore


async def setup(bot):
    await bot.add_cog(Greetings(bot))
