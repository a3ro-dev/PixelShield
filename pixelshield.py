import discord
from discord.ext import commands
import os
import logging
from datetime import datetime
import configuration.discordConfig as dconfig
from pretty_help import PrettyHelp
import psutil
import asyncio 

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

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(
            case_insensitive=False,
            command_prefix=commands.when_mentioned_or(dconfig.PREFIX),
            intents=intents,
            owner_ids=dconfig.botManagerID,
            auto_sync_commands=True,
            help_command=PrettyHelp()
        )

bot = Bot()
bot.launch_time = datetime.utcnow() #type: ignore


@bot.event
async def on_ready():
    bot.loop.create_task(update_presence())
    bot.startup_time = 0
    link = await bot.guilds[0].text_channels[0].create_invite()
    print(f'--------------------------------------------------------------')
    print(f'{link}')
    print(f'Logged in as {bot.user.name} | {bot.user.id}') #typ: ignore
    print(f'--------------------------------------------------------------')
    await bot.load_extension(f'jishaku')

    print(f'--------------------------------------------------------------')
    print("🔴🔴🔴🔴 Now loading Cogs! 🔴🔴🔴🔴")
    print(f'--------------------------------------------------------------')
    for file in os.listdir('cogs'):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{file[:-3]}')
                print(f' | ✅ | loaded {file[:-3]}')
            except Exception as e:
                logger.error(e)
                print(f' | ❌ | Failed to load {file[:-3]} because: {str(e)}')

async def update_presence():
    while True:
        # Get memory usage and CPU usage
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=None)

        # Set the presence with memory and CPU usage info
        await bot.change_presence(
            activity=discord.Streaming(
                name=f"Memory: {memory_usage:.1f}% | CPU: {cpu_usage:.1f}%",
                url="https://www.twitch.tv/pixelshield",  # Replace with your Twitch channel URL
            )
        )

        # Wait for 5 seconds before updating the presence again
        await asyncio.sleep(5)


bot.run(dconfig.TOKEN)