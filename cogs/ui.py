import discord
from discord.ui import Button, View, Select
from discord import Interaction, Embed
from discord.ext import commands
import asyncio

class ControlPanel(View):
    def __init__(self, player, bot):
        super().__init__(timeout=None)
        self.player = player
        self.bot = bot
        self.update_buttons()
    
    def update_buttons(self):
        for child in self.children:
            if child.custom_id == "play_pause":
                if self.player.current and any(vc.is_playing() for vc in self.bot.voice_clients):
                    child.label = "⏸️"
                    child.style = discord.ButtonStyle.primary
                else:
                    child.label = "▶️"
                    child.style = discord.ButtonStyle.success
                break
    
    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary, custom_id="prev")
    async def previous_button(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
    
    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.primary, custom_id="play_pause")
    async def play_pause_button(self, interaction: Interaction, button: Button):
        voice_client = interaction.guild.voice_client
        
        if not voice_client:
            await interaction.response.send_message("❌ Bot is not connected to a voice channel", ephemeral=True)
            return
        
        if voice_client.is_playing():
            voice_client.pause()
            button.label = "▶️"
            button.style = discord.ButtonStyle.success
        else:
            voice_client.resume()
            button.label = "⏸️"
            button.style = discord.ButtonStyle.primary
        
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary, custom_id="next")
    async def skip_button(self, interaction: Interaction, button: Button):
        voice_client = interaction.guild.voice_client
        
        if not voice_client or not voice_client.is_playing():
            await interaction.response.send_message("❌ No song is currently playing", ephemeral=True)
            return
        
        voice_client.stop()
        await interaction.response.send_message("⏭️ Skipped to next song", ephemeral=True)
    
    @discord.ui.button(label="🔈", style=discord.ButtonStyle.secondary, custom_id="vol_down")
    async def vol_down_button(self, interaction: Interaction, button: Button):
        self.player.set_volume(max(0.0, self.player.volume - 0.1))
        
        if self.player.current:
            self.player.current.volume = self.player.volume
        
        await interaction.response.send_message(
            f"🔈 Volume: {int(self.player.volume * 100)}%", 
            ephemeral=True
        )
    
    @discord.ui.button(label="🔊", style=discord.ButtonStyle.secondary, custom_id="vol_up")
    async def vol_up_button(self, interaction: Interaction, button: Button):
        self.player.set_volume(min(2.0, self.player.volume + 0.1))
        
        if self.player.current:
            self.player.current.volume = self.player.volume
        
        await interaction.response.send_message(
            f"🔊 Volume: {int(self.player.volume * 100)}%", 
            ephemeral=True
        )
    
    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.danger, custom_id="stop")
    async def stop_button(self, interaction: Interaction, button: Button):
        voice_client = interaction.guild.voice_client
        
        if not voice_client:
            await interaction.response.send_message("❌ Bot is not connected to a voice channel", ephemeral=True)
            return
        
        voice_client.stop()
        self.player.clear_queue()
        await interaction.response.send_message("⏹️ Stopped playback and cleared queue", ephemeral=True)
    
    @discord.ui.button(label="📋", style=discord.ButtonStyle.secondary, custom_id="queue")
    async def queue_button(self, interaction: Interaction, button: Button):
        commands_cog = self.bot.get_cog('Commands')
        if not commands_cog:
            await interaction.response.send_message("❌ Commands cog not loaded", ephemeral=True)
            return
        
        player = commands_cog.player
        
        if not player.queue and not player.current:
            await interaction.response.send_message("❌ The queue is empty", ephemeral=True)
            return
        
        embed = Embed(
            title="Music Queue",
            description=f"Total songs: {len(player.queue)}",
            color=discord.Color.blue()
        )
        
        if player.current:
            embed.add_field(
                name="Now Playing",
                value=f"**{player.current.title}** ({player.current.duration//60}:{player.current.duration%60:02d})",
                inline=False
            )
        
        for i, song in enumerate(player.queue[:5]):
            if isinstance(song, dict):
                title = song.get('title', 'Unknown')
                duration = song.get('duration', 0)
            else:
                title = song.title
                duration = song.duration
            
            embed.add_field(
                name=f"{i+1}. {title}",
                value=f"Duration: {duration//60}:{duration%60:02d}",
                inline=False
            )
        
        if len(player.queue) > 5:
            embed.set_footer(text=f"And {len(player.queue) - 5} more songs...")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class UI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.control_panels = {}
        self.auto_show = True
    
    async def show_control_panel(self, ctx, player=None):
        if player is None:
            commands_cog = self.bot.get_cog('Commands')
            if not commands_cog:
                return None
            player = commands_cog.player
        
        view = ControlPanel(player, self.bot)
        
        embed = Embed(
            title="🎵 Music Control Panel",
            description="Use the buttons below to control the music player",
            color=discord.Color.blue()
        )
        
        if player.current:
            embed.add_field(
                name="Current Song",
                value=f"**{player.current.title}**",
                inline=False
            )
            embed.add_field(
                name="Duration",
                value=f"{player.current.duration // 60}:{player.current.duration % 60:02d}",
                inline=True
            )
            embed.add_field(
                name="Requested by",
                value=player.current.requester,
                inline=True
            )
            embed.set_thumbnail(url=player.current.thumbnail)
        else:
            embed.description = "No song is currently playing. Use !play to start playing music!"
        
        embed.set_footer(text=f"Volume: {int(player.volume * 100)}% | Queue: {len(player.queue)} songs")
        
        if ctx.guild.id in self.control_panels:
            try:
                message = self.control_panels[ctx.guild.id]
                await message.edit(embed=embed, view=view)
                return message
            except:
                pass
        
        message = await ctx.send(embed=embed, view=view)
        self.control_panels[ctx.guild.id] = message
        return message
    
    async def update_control_panel(self, guild_id, player=None):
        if guild_id not in self.control_panels:
            return
        
        if player is None:
            commands_cog = self.bot.get_cog('Commands')
            if not commands_cog:
                return
            player = commands_cog.player
        
        message = self.control_panels[guild_id]
        view = ControlPanel(player, self.bot)
        
        embed = Embed(
            title="🎵 Music Control Panel",
            description="Use the buttons below to control the music player",
            color=discord.Color.blue()
        )
        
        if player.current:
            embed.add_field(
                name="Current Song",
                value=f"**{player.current.title}**",
                inline=False
            )
            embed.add_field(
                name="Duration",
                value=f"{player.current.duration // 60}:{player.current.duration % 60:02d}",
                inline=True
            )
            embed.add_field(
                name="Requested by",
                value=player.current.requester,
                inline=True
            )
            embed.set_thumbnail(url=player.current.thumbnail)
        else:
            embed.description = "No song is currently playing"
            embed.set_footer(text="Queue is empty")
        
        embed.set_footer(text=f"Volume: {int(player.volume * 100)}% | Queue: {len(player.queue)} songs")
        
        try:
            await message.edit(embed=embed, view=view)
        except:
            del self.control_panels[guild_id]
    
    @commands.command(name='controls', aliases=['ui', 'panel'])
    async def show_controls(self, ctx):
        commands_cog = self.bot.get_cog('Commands')
        if not commands_cog:
            return await ctx.send("❌ Music system not available")
        
        await self.show_control_panel(ctx, commands_cog.player)
        await ctx.message.add_reaction("✅")
    
    @commands.command(name='hide_controls', aliases=['hide'])
    async def hide_controls(self, ctx):
        if ctx.guild.id in self.control_panels:
            try:
                await self.control_panels[ctx.guild.id].delete()
                del self.control_panels[ctx.guild.id]
                await ctx.send("✅ Control panel hidden")
            except:
                await ctx.send("❌ Could not hide control panel")
        else:
            await ctx.send("❌ No control panel is currently visible")
    
    @commands.command(name='auto_controls', aliases=['auto'])
    async def toggle_auto_controls(self, ctx):
        self.auto_show = not self.auto_show
        status = "enabled" if self.auto_show else "disabled"
        await ctx.send(f"🔄 Automatic control panel display {status}")
    
    @commands.command(name='update_controls', aliases=['update'])
    async def update_controls(self, ctx):
        if ctx.guild.id not in self.control_panels:
            return await ctx.send("❌ No control panel is currently visible. Use !controls to show it")
        
        commands_cog = self.bot.get_cog('Commands')
        if not commands_cog:
            return await ctx.send("❌ Music system not available")
        
        await self.update_control_panel(ctx.guild.id, commands_cog.player)
        await ctx.message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(UI(bot))