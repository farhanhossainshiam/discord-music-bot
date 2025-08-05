import discord
from discord.ext import commands
from typing import Dict, List, Optional

class CommandManager:
    def __init__(self):
        self.commands: Dict[str, dict] = {
            "join": {
                "name": "join",
                "description": "Joins the voice channel you're in",
                "usage": "!join",
                "category": "Music Control",
                "aliases": ["j"]
            },
            "leave": {
                "name": "leave",
                "description": "Leaves the voice channel",
                "usage": "!leave",
                "category": "Music Control",
                "aliases": ["l", "disconnect"]
            },
            "play": {
                "name": "play",
                "description": "Plays a song from YouTube",
                "usage": "!play <song name or YouTube URL>",
                "category": "Music Control",
                "aliases": ["p"]
            },
            "skip": {
                "name": "skip",
                "description": "Skips the current song",
                "usage": "!skip",
                "category": "Music Control",
                "aliases": ["s", "next"]
            },
            "pause": {
                "name": "pause",
                "description": "Pauses the current song",
                "usage": "!pause",
                "category": "Music Control",
                "aliases": []
            },
            "resume": {
                "name": "resume",
                "description": "Resumes the paused song",
                "usage": "!resume",
                "category": "Music Control",
                "aliases": []
            },
            "stop": {
                "name": "stop",
                "description": "Stops playback and clears the queue",
                "usage": "!stop",
                "category": "Music Control",
                "aliases": []
            },
            "clear": {
                "name": "clear",
                "description": "Clears the music queue",
                "usage": "!clear",
                "category": "Queue Management",
                "aliases": []
            },
            "remove": {
                "name": "remove",
                "description": "Removes a song from the queue",
                "usage": "!remove <song number>",
                "category": "Queue Management",
                "aliases": ["rm", "delete"]
            },
            "shuffle": {
                "name": "shuffle",
                "description": "Shuffles the music queue",
                "usage": "!shuffle",
                "category": "Queue Management",
                "aliases": []
            },
            "now": {
                "name": "now",
                "description": "Shows the currently playing song",
                "usage": "!now",
                "category": "Information",
                "aliases": ["np", "current"]
            },
            "help": {
                "name": "help",
                "description": "Shows this help message",
                "usage": "!help [command]",
                "category": "Information",
                "aliases": ["h", "commands"]
            },
            "volume": {
                "name": "volume",
                "description": "Sets the volume (0-200)",
                "usage": "!volume <0-200>",
                "category": "Settings",
                "aliases": ["vol", "v"]
            },
            "loop": {
                "name": "loop",
                "description": "Toggles loop mode for current song",
                "usage": "!loop",
                "category": "Settings",
                "aliases": []
            },
            "playlist": {
                "name": "playlist",
                "description": "Save or load a playlist",
                "usage": "!playlist <save|load|list> [name]",
                "category": "Advanced",
                "aliases": ["pl"]
            },
            "stats": {
                "name": "stats",
                "description": "Shows bot statistics",
                "usage": "!stats",
                "category": "Advanced",
                "aliases": []
            },
            "youtube_test": {
                "name": "youtube_test",
                "description": "Test YouTube API connection",
                "usage": "!youtube_test",
                "category": "Advanced",
                "aliases": []
            },
            "quality": {
                "name": "quality",
                "description": "Set audio quality (low, medium, high)",
                "usage": "!quality <low|medium|high>",
                "category": "Settings",
                "aliases": []
            },
            "optimize": {
                "name": "optimize",
                "description": "Optimize streaming settings",
                "usage": "!optimize",
                "category": "Settings",
                "aliases": []
            },
            "buffer": {
                "name": "buffer",
                "description": "Set buffer size (small, medium, large)",
                "usage": "!buffer <small|medium|large>",
                "category": "Settings",
                "aliases": []
            },
            "diag": {
                "name": "diag",
                "description": "Run network diagnostics",
                "usage": "!diag",
                "category": "Advanced",
                "aliases": []
            },
            "streaming_help": {
                "name": "streaming_help",
                "description": "Show tips for reducing lag",
                "usage": "!streaming_help",
                "category": "Information",
                "aliases": []
            },
            "controls": {
                "name": "controls",
                "description": "Show the music control panel",
                "usage": "!controls",
                "category": "UI Control",
                "aliases": ["ui", "panel"]
            },
            "hide_controls": {
                "name": "hide_controls",
                "description": "Hide the music control panel",
                "usage": "!hide_controls",
                "category": "UI Control",
                "aliases": ["hide"]
            },
            "auto_controls": {
                "name": "auto_controls",
                "description": "Toggle automatic control panel display",
                "usage": "!auto_controls",
                "category": "UI Control",
                "aliases": ["auto"]
            },
            "update_controls": {
                "name": "update_controls",
                "description": "Update the music control panel",
                "usage": "!update_controls",
                "category": "UI Control",
                "aliases": ["update"]
            }
        }
    
    def get_command(self, name: str) -> Optional[dict]:
        for cmd_name, cmd_data in self.commands.items():
            if name == cmd_name or name in cmd_data["aliases"]:
                return cmd_data
        return None
    
    def get_commands_by_category(self, category: str) -> List[dict]:
        return [cmd for cmd in self.commands.values() if cmd["category"] == category]
    
    def get_all_categories(self) -> List[str]:
        categories = set()
        for cmd in self.commands.values():
            categories.add(cmd["category"])
        return sorted(list(categories))
    
    def create_help_embed(self, command_name: Optional[str] = None) -> discord.Embed:
        if command_name:
            cmd = self.get_command(command_name)
            if not cmd:
                return discord.Embed(
                    title="❌ Command Not Found",
                    description=f"Command `{command_name}` not found.",
                    color=discord.Color.red()
                )
            
            embed = discord.Embed(
                title=f"Command: !{cmd['name']}",
                description=cmd["description"],
                color=discord.Color.blue()
            )
            embed.add_field(name="Usage", value=f"`{cmd['usage']}`", inline=False)
            embed.add_field(name="Category", value=cmd["category"], inline=True)
            
            if cmd["aliases"]:
                embed.add_field(
                    name="Aliases", 
                    value=", ".join([f"`!{alias}`" for alias in cmd["aliases"]]), 
                    inline=True
                )
            
            return embed
        else:
            embed = discord.Embed(
                title="🎵 Music Bot Commands",
                description="Here are all available commands:",
                color=discord.Color.blue()
            )
            
            for category in self.get_all_categories():
                commands = self.get_commands_by_category(category)
                cmd_list = "\n".join([
                    f"`!{cmd['name']}` - {cmd['description']}" 
                    for cmd in commands
                ])
                embed.add_field(name=category, value=cmd_list, inline=False)
            
            embed.set_footer(text="Use !help <command> for more info on a specific command")
            return embed