import discord
from discord.ui import Button, View
from discord import Interaction, Embed
from discord.ext import commands

class QueueView(View):
    def __init__(self, player):
        super().__init__(timeout=300)
        self.player = player
        self.page = 0
        self.items_per_page = 10
    
    async def update_message(self, interaction: Interaction):
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        queue_items = self.player.queue[start:end]
        
        embed = Embed(
            title="Music Queue",
            description=f"Showing {start+1}-{min(end, len(self.player.queue))} of {len(self.player.queue)} songs",
            color=discord.Color.blue()
        )
        
        if self.player.current:
            embed.add_field(
                name="Now Playing",
                value=f"**{self.player.current.title}** ({self.player.current.duration//60}:{self.player.current.duration%60:02d})",
                inline=False
            )
        
        for i, song in enumerate(queue_items, start=start+1):
            embed.add_field(
                name=f"{i}. {song['title'] if isinstance(song, dict) else song.title}",
                value=f"Duration: {song['duration']//60}:{song['duration']%60:02d if isinstance(song, dict) else song.duration//60}:{song.duration%60:02d} | Requested by: {song['requester'] if isinstance(song, dict) else song.requester}",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, custom_id="prev_page")
    async def previous_page(self, interaction: Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, custom_id="next_page")
    async def next_page(self, interaction: Interaction, button: Button):
        if (self.page + 1) * self.items_per_page < len(self.player.queue):
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Clear Queue", style=discord.ButtonStyle.danger, custom_id="clear_queue")
    async def clear_queue(self, interaction: Interaction, button: Button):
        self.player.clear_queue()
        await interaction.response.send_message("✅ Queue cleared!", ephemeral=True)
        await self.update_message(interaction)

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='queue', aliases=['q', 'list'])
    async def show_queue(self, ctx, page: int = 1):
        music_cog = self.bot.get_cog('Commands')
        if not music_cog:
            return await ctx.send("❌ Music cog not loaded", delete_after=5.0)
        
        player = music_cog.player
        
        if not player.queue and not player.current:
            return await ctx.send("❌ The queue is empty", delete_after=5.0)
        
        view = QueueView(player)
        items_per_page = 10
        total_pages = max(1, (len(player.queue) + items_per_page - 1) // items_per_page)
        page = max(1, min(page, total_pages))
        view.page = page - 1
        
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue_items = player.queue[start:end]
        
        embed = Embed(
            title="Music Queue",
            description=f"Page {page}/{total_pages} | Total songs: {len(player.queue)}",
            color=discord.Color.blue()
        )
        
        if player.current:
            embed.add_field(
                name="Now Playing",
                value=f"**{player.current.title}** ({player.current.duration//60}:{player.current.duration%60:02d})",
                inline=False
            )
        
        for i, song in enumerate(queue_items, start=start+1):
            embed.add_field(
                name=f"{i}. {song['title'] if isinstance(song, dict) else song.title}",
                value=f"Duration: {song['duration']//60}:{song['duration']%60:02d if isinstance(song, dict) else song.duration//60}:{song.duration%60:02d} | Requested by: {song['requester'] if isinstance(song, dict) else song.requester}",
                inline=False
            )
        
        embed.set_footer(text="Use the buttons below to navigate or clear the queue")
        await ctx.send(embed=embed, view=view, delete_after=5.0)

async def setup(bot):
    await bot.add_cog(Queue(bot))