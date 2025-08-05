import discord
from discord.ui import Button, View
from discord import Interaction
from discord.ext import commands

class PlayerControls(View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player
    
    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary, custom_id="prev")
    async def previous_button(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
    
    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.primary, custom_id="pause")
    async def pause_button(self, interaction: Interaction, button: Button):
        if self.player.pause():
            button.label = "▶️"
            button.style = discord.ButtonStyle.success
        elif self.player.resume():
            button.label = "⏸️"
            button.style = discord.ButtonStyle.primary
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary, custom_id="next")
    async def skip_button(self, interaction: Interaction, button: Button):
        if self.player.skip():
            await interaction.response.send_message("⏭️ Skipped", ephemeral=True)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="🔈", style=discord.ButtonStyle.secondary, custom_id="vol_down")
    async def vol_down_button(self, interaction: Interaction, button: Button):
        self.player.set_volume(self.player.volume - 0.1)
        await interaction.response.send_message(
            f"🔈 Volume: {int(self.player.volume * 100)}%", 
            ephemeral=True
        )
    
    @discord.ui.button(label="🔊", style=discord.ButtonStyle.secondary, custom_id="vol_up")
    async def vol_up_button(self, interaction: Interaction, button: Button):
        self.player.set_volume(self.player.volume + 0.1)
        await interaction.response.send_message(
            f"🔊 Volume: {int(self.player.volume * 100)}%", 
            ephemeral=True
        )


class Controls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Controls(bot))