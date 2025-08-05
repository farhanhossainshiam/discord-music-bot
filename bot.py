import os
import discord
from discord.ext import commands
from utils.config import load_config

async def main():
    config = load_config()
    
    intents = discord.Intents.default()
    intents.guilds = True
    intents.voice_states = True
    intents.messages = True
    intents.message_content = True
    
    bot = commands.Bot(
        command_prefix='!',
        intents=intents,
        help_command=None
    )
    
    bot.config = config
    
    # Load cogs
    initial_extensions = [
        'cogs.commands',
        'cogs.ui'
    ]
    
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Loaded extension: {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}: {e}")
    
    @bot.event
    async def on_ready():
        print(f'{bot.user} has connected to Discord!')
        print("Loaded commands:")
        for command in bot.commands:
            print(f"  !{command.name}")
        print(f"Total commands: {len(bot.commands)}")
    
    await bot.start(config['DISCORD_TOKEN'])

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())