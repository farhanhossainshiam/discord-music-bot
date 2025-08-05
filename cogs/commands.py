import discord
from discord.ext import commands
from utils.commands import CommandManager
from utils.music_player import MusicPlayer
from utils.api_clients import APIClients
from utils.ytdl_source import YTDLSource
import asyncio
import random
import json
import os

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.player = MusicPlayer()
        self.api = APIClients(self.config)
        self.cmd_manager = CommandManager()
        self.playlists = {}
        self.disconnect_tasks = {}
        self.load_playlists()
        print("Commands cog initialized!")
    
    def load_playlists(self):
        if os.path.exists("playlists.json"):
            with open("playlists.json", "r") as f:
                self.playlists = json.load(f)
    
    def save_playlists(self):
        with open("playlists.json", "w") as f:
            json.dump(self.playlists, f)
    
    async def send_control_panel(self, ctx):
        """Send or update the control panel"""
        ui_cog = self.bot.get_cog('UI')
        if ui_cog:
            await ui_cog.show_control_panel(ctx, self.player)
    
    async def update_control_panel(self, guild_id):
        """Update the control panel for a guild"""
        ui_cog = self.bot.get_cog('UI')
        if ui_cog and ui_cog.auto_show:
            await ui_cog.update_control_panel(guild_id, self.player)
            
    async def auto_disconnect(self, ctx, seconds):
        """Automatically disconnect from voice channel after specified seconds if queue is empty"""
        # Cancel any existing disconnect task for this guild
        if ctx.guild.id in self.disconnect_tasks:
            self.disconnect_tasks[ctx.guild.id].cancel()
            
        # Store the new task
        self.disconnect_tasks[ctx.guild.id] = asyncio.current_task()
        
        try:
            # Wait for the specified time
            await asyncio.sleep(seconds)
            
            # Check if we should still disconnect
            if ctx.voice_client and ctx.voice_client.is_connected() and not self.player.queue and not ctx.voice_client.is_playing():
                await ctx.voice_client.disconnect()
                self.player.current = None
                await ctx.send("⏱️ Auto-disconnected due to inactivity", delete_after=5.0)
                await self.update_control_panel(ctx.guild.id)
        except asyncio.CancelledError:
            # Task was cancelled, do nothing
            pass
        finally:
            # Remove the task from the dictionary
            if ctx.guild.id in self.disconnect_tasks:
                del self.disconnect_tasks[ctx.guild.id]
    
    @commands.command(name='join', aliases=['j'])
    async def join(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("❌ You are not connected to a voice channel", delete_after=5.0)
        
        channel = ctx.author.voice.channel
        
        if ctx.voice_client:
            if ctx.voice_client.channel == channel:
                return await ctx.send("❌ I'm already in this voice channel!", delete_after=5.0)
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        
        # Cancel any auto-disconnect task when manually joining
        if ctx.guild.id in self.disconnect_tasks:
            self.disconnect_tasks[ctx.guild.id].cancel()
        
        await ctx.send(f"✅ Connected to {channel.name}", delete_after=5.0)
        await self.send_control_panel(ctx)
    
    @commands.command(name='leave', aliases=['l', 'disconnect'])
    async def leave(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("❌ I'm not connected to a voice channel", delete_after=5.0)
        
        await ctx.voice_client.disconnect()
        self.player.clear_queue()
        self.player.current = None
        
        await ctx.send("👋 Disconnected from voice channel", delete_after=5.0)
        await self.update_control_panel(ctx.guild.id)
    
    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, query):
        if not ctx.voice_client:
            await self.join(ctx)
        
        # Cancel any auto-disconnect task when playing a song
        if ctx.guild.id in self.disconnect_tasks:
            self.disconnect_tasks[ctx.guild.id].cancel()
        
        # Send search message outside the typing context and set it to delete after 5 seconds
        if "youtube.com/watch" in query or "youtu.be/" in query:
            url = query
            status_msg = await ctx.send("🎵 Processing YouTube URL...", delete_after=5.0)
        else:
            status_msg = await ctx.send("🔍 Searching on YouTube...", delete_after=5.0)
            
        async with ctx.typing():
            if not ("youtube.com/watch" in query or "youtu.be/" in query):
                url = await self.api.search_youtube(query)
                
                if not url:
                    url = f"ytsearch:{query}"
                    await ctx.send("⚠️ Using fallback search method...", delete_after=5.0)
                else:
                    await ctx.send("✅ Found on YouTube!", delete_after=5.0)
            
            if "playlist" in url or "list=" in url:
                await ctx.send("🔄 Processing playlist...", delete_after=5.0)
                entries = await YTDLSource.from_url(
                    url, 
                    loop=self.bot.loop, 
                    stream=True, 
                    requester=ctx.author.name,
                    ytdl_options=self.config['YTDL_OPTIONS']
                )
                
                if isinstance(entries, list):
                    self.player.queue.extend(entries)
                    await ctx.send(f"✅ Added {len(entries)} songs to the queue", delete_after=5.0)
                    if not ctx.voice_client.is_playing():
                        await self.play_next(ctx)
                else:
                        await ctx.send("❌ Could not process playlist", delete_after=5.0)
            else:
                try:
                    await asyncio.sleep(0.5)
                    
                    song = await YTDLSource.from_url(
                        url, 
                        loop=self.bot.loop, 
                        stream=True, 
                        requester=ctx.author.name,
                        ytdl_options=self.config['YTDL_OPTIONS']
                    )
                    self.player.add_to_queue(song)
                    
                    if not ctx.voice_client.is_playing():
                        await self.play_next(ctx)
                    else:
                        await ctx.send(f'✅ Added to queue: {song.title}', delete_after=5.0)
                        
                except Exception as e:
                    await ctx.send(f"❌ Error playing song: {e}", delete_after=5.0)
                    print(f"Play error: {e}")
    
    async def play_next(self, ctx):
        if self.player.queue:
            next_song = self.player.queue.pop(0)
            
            if isinstance(next_song, dict):
                ffmpeg_options = {
                    'options': '-vn -b:a 128k -ar 44100',
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -threads 2'
                }
                source = discord.FFmpegPCMAudio(next_song['url'], **ffmpeg_options)
                self.player.current = YTDLSource(source, data=next_song, volume=self.player.volume)
            else:
                self.player.current = next_song
                self.player.current.volume = self.player.volume
            
            ctx.voice_client.play(
                self.player.current, 
                after=lambda e: self.bot.loop.create_task(self.play_next(ctx))
            )
            
            # Only update the control panel, don't send now playing message
            await self.update_control_panel(ctx.guild.id)
        else:
            self.player.current = None
            # Update the control panel to show empty state
            await self.update_control_panel(ctx.guild.id)
            # Start auto-disconnect timer when queue is empty
            if ctx.voice_client and ctx.voice_client.is_connected():
                await ctx.send("⏱️ No songs in queue. Bot will disconnect in 50 seconds if queue remains empty.", delete_after=5.0)
                self.bot.loop.create_task(self.auto_disconnect(ctx, 50))
    
    @commands.command(name='skip', aliases=['s', 'next'])
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('⏭️ Skipped the current song', delete_after=5.0)
        else:
            await ctx.send('❌ No song is currently playing', delete_after=5.0)
    
    @commands.command(name='pause')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send('⏸️ Paused the current song', delete_after=5.0)
        else:
            await ctx.send('❌ No song is currently playing', delete_after=5.0)
    
    @commands.command(name='resume')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send('▶️ Resumed the current song', delete_after=5.0)
        else:
            await ctx.send('❌ No song is paused', delete_after=5.0)
    
    @commands.command(name='stop')
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.player.clear_queue()
            await ctx.send('⏹️ Stopped playback and cleared queue', delete_after=5.0)
        else:
            await ctx.send('❌ No song is currently playing', delete_after=5.0)
    
    @commands.command(name='clear')
    async def clear(self, ctx):
        if not self.player.queue:
            return await ctx.send("❌ The queue is already empty", delete_after=5.0)
        
        self.player.clear_queue()
        await ctx.send("✅ Queue cleared", delete_after=5.0)
    
    @commands.command(name='remove', aliases=['rm', 'delete'])
    async def remove(self, ctx, index: int):
        if not self.player.queue:
            return await ctx.send("❌ The queue is empty", delete_after=5.0)
        
        if index < 1 or index > len(self.player.queue):
            return await ctx.send(f"❌ Invalid song number. Please enter a number between 1 and {len(self.player.queue)}", delete_after=5.0)
        
        removed = self.player.queue.pop(index - 1)
        await ctx.send(f"✅ Removed **{removed['title'] if isinstance(removed, dict) else removed.title}** from the queue", delete_after=5.0)
    
    @commands.command(name='shuffle')
    async def shuffle(self, ctx):
        if not self.player.queue:
            return await ctx.send("❌ The queue is empty", delete_after=5.0)
        
        random.shuffle(self.player.queue)
        await ctx.send("🔀 Queue shuffled", delete_after=5.0)
    
    @commands.command(name='now', aliases=['np', 'current'])
    async def now_playing(self, ctx):
        if self.player.current:
            embed = discord.Embed(
                title="Now Playing",
                description=f"**{self.player.current.title}**",
                color=discord.Color.blue()
            )
            embed.add_field(name="Duration", value=f"{self.player.current.duration // 60}:{self.player.current.duration % 60:02d}")
            embed.add_field(name="Requested by", value=self.player.current.requester)
            embed.set_thumbnail(url=self.player.current.thumbnail)
            embed.set_footer(text=f"Volume: {int(self.player.volume * 100)}% | Loop: {'On' if self.player.loop else 'Off'}")
            await ctx.send(embed=embed, delete_after=5.0)
        else:
            await ctx.send("❌ No song is currently playing", delete_after=5.0)
    
    
    @commands.command(name='volume', aliases=['vol', 'v'])
    async def volume(self, ctx, vol: int):
        if not 0 <= vol <= 200:
            return await ctx.send("❌ Volume must be between 0 and 200", delete_after=5.0)
        
        self.player.set_volume(vol / 100)
        await ctx.send(f"🔊 Volume set to {vol}%", delete_after=5.0)
    
    @commands.command(name='loop')
    async def loop(self, ctx):
        self.player.loop = not self.player.loop
        status = "enabled" if self.player.loop else "disabled"
        await ctx.send(f"🔁 Loop mode {status}", delete_after=5.0)
    
    @commands.command(name='playlist', aliases=['pl'])
    async def playlist(self, ctx, action: str, *, name: str = None):
        if action == "save":
            if not name:
                return await ctx.send("❌ Please provide a playlist name", delete_after=5.0)
            
            if not self.player.queue:
                return await ctx.send("❌ The queue is empty", delete_after=5.0)
            
            self.playlists[name] = {
                "songs": self.player.queue.copy(),
                "created_by": ctx.author.name
            }
            self.save_playlists()
            await ctx.send(f"✅ Playlist '{name}' saved with {len(self.player.queue)} songs", delete_after=5.0)
        
        elif action == "load":
            if not name:
                return await ctx.send("❌ Please provide a playlist name", delete_after=5.0)
            
            if name not in self.playlists:
                return await ctx.send(f"❌ Playlist '{name}' not found", delete_after=5.0)
            
            playlist = self.playlists[name]
            self.player.queue.extend(playlist["songs"])
            await ctx.send(f"✅ Loaded playlist '{name}' with {len(playlist['songs'])} songs", delete_after=5.0)
            
            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)
        
        elif action == "list":
            if not self.playlists:
                return await ctx.send("❌ No saved playlists", delete_after=5.0)
            
            embed = discord.Embed(
                title="Saved Playlists",
                description=f"Total playlists: {len(self.playlists)}",
                color=discord.Color.blue()
            )
            
            for name, data in self.playlists.items():
                embed.add_field(
                    name=name,
                    value=f"{len(data['songs'])} songs | Created by {data['created_by']}",
                    inline=False
                )
            
            await ctx.send(embed=embed, delete_after=5.0)
        
        else:
            await ctx.send("❌ Invalid action. Use save, load, or list", delete_after=5.0)
    
    @commands.command(name='stats')
    async def stats(self, ctx):
        total_songs = len(self.player.queue)
        if self.player.current:
            total_songs += 1
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.blue()
        )
        embed.add_field(name="Songs in Queue", value=str(total_songs), inline=True)
        embed.add_field(name="Volume", value=f"{int(self.player.volume * 100)}%", inline=True)
        embed.add_field(name="Loop Mode", value="On" if self.player.loop else "Off", inline=True)
        embed.add_field(name="Saved Playlists", value=str(len(self.playlists)), inline=True)
        embed.add_field(name="Connected to VC", value="Yes" if ctx.voice_client else "No", inline=True)
        embed.add_field(name="Currently Playing", value="Yes" if ctx.voice_client and ctx.voice_client.is_playing() else "No", inline=True)
        
        await ctx.send(embed=embed, delete_after=5.0)
    
    @commands.command(name='youtube_test')
    async def youtube_test(self, ctx):
        if not self.api.youtube_api_key:
            return await ctx.send("❌ YouTube API key not configured", delete_after=5.0)
        
        result = await self.api.search_youtube("despacito")
        if result:
            await ctx.send(f"✅ YouTube API is working!\nFound: {result}", delete_after=5.0)
        else:
            await ctx.send("❌ YouTube API test failed", delete_after=5.0)
    
    @commands.command(name='quality')
    async def set_quality(self, ctx, quality: str):
        quality = quality.lower()
        
        if quality == 'low':
            bitrate = '64k'
            ar = '22050'
        elif quality == 'medium':
            bitrate = '128k'
            ar = '44100'
        elif quality == 'high':
            bitrate = '192k'
            ar = '48000'
        else:
            return await ctx.send("❌ Invalid quality. Use: low, medium, or high", delete_after=5.0)
        
        self.config['FFMPEG_OPTIONS']['options'] = f'-vn -b:a {bitrate} -ar {ar}'
        
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            if self.player.current:
                ctx.voice_client.play(self.player.current)
        
        await ctx.send(f"🔊 Audio quality set to {quality} ({bitrate})", delete_after=5.0)
    
    @commands.command(name='optimize')
    async def optimize(self, ctx):
        self.config['YTDL_OPTIONS'].update({
            'force-ipv4': True,
            'buffer-size': '16K',
            'concurrent_fragment_downloads': 3,
            'http_chunk_size': '10485760',
            'retries': 10,
            'fragment_retries': 10,
        })
        
        self.config['FFMPEG_OPTIONS'] = {
            'options': '-vn -b:a 128k -ar 44100',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -threads 2'
        }
        
        await ctx.send("🔧 Streaming settings optimized!", delete_after=5.0)
    
    @commands.command(name='buffer')
    async def set_buffer(self, ctx, size: str):
        size = size.lower()
        
        if size == 'small':
            buffer_size = '8K'
        elif size == 'medium':
            buffer_size = '16K'
        elif size == 'large':
            buffer_size = '32K'
        else:
            return await ctx.send("❌ Invalid buffer size. Use: small, medium, or large", delete_after=5.0)
        
        self.config['YTDL_OPTIONS']['buffer-size'] = buffer_size
        await ctx.send(f"📊 Buffer size set to {size}", delete_after=5.0)
    
    @commands.command(name='diag')
    async def diagnostics(self, ctx):
        import aiohttp
        import time
        
        await ctx.send("🔍 Running network diagnostics...", delete_after=5.0)
        
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.youtube.com', timeout=10) as response:
                    youtube_time = time.time() - start_time
                    await ctx.send(f"✅ YouTube response time: {youtube_time:.2f}s", delete_after=5.0)
        except:
            await ctx.send("❌ YouTube connection failed", delete_after=5.0)
        
        if ctx.guild:
            region = ctx.guild.region
            await ctx.send(f"🌍 Server region: {region}", delete_after=5.0)
        
        await ctx.send(f"📊 Current buffer size: {self.config['YTDL_OPTIONS'].get('buffer-size', '16K')}", delete_after=5.0)
        await ctx.send(f"🎵 Current bitrate: {self.config['FFMPEG_OPTIONS']['options'].split()[2]}", delete_after=5.0)
    
    @commands.command(name='streaming_help')
    async def streaming_help(self, ctx):
        embed = discord.Embed(
            title="🎵 Streaming Tips",
            description="How to reduce lag when playing music:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔧 Optimization Commands",
            value=(
                "`!optimize` - Reset to optimal settings\n"
                "`!quality low/medium/high` - Set audio quality\n"
                "`!buffer small/medium/large` - Set buffer size\n"
                "`!diag` - Run network diagnostics"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips",
            value=(
                "• Use `!quality medium` for balance\n"
                "• Use `!buffer large` if songs keep cutting out\n"
                "• Use `!buffer small` for faster start times\n"
                "• Run `!diag` if you experience lag"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed, delete_after=5.0)
    
    @commands.command(name='help', aliases=['h', 'commands'])
    async def help(self, ctx, command_name: str = None):
        embed = self.cmd_manager.create_help_embed(command_name)
        await ctx.send(embed=embed, delete_after=180.0)
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send('🏓 Pong! Commands cog is working!', delete_after=5.0)

async def setup(bot):
    await bot.add_cog(Commands(bot))