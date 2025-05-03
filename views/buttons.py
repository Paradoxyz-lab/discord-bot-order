# views/buttons.py
import discord

class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(JoinButton())
        self.add_item(LeaveButton())
        self.add_item(CloseButton())

class JoinButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Присоединиться", style=discord.ButtonStyle.success, custom_id="join")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Вы нажали 'Присоединиться'", ephemeral=True)

class LeaveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Выйти", style=discord.ButtonStyle.danger, custom_id="leave")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Вы нажали 'Выйти'", ephemeral=True)

class CloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Закрыть", style=discord.ButtonStyle.secondary, custom_id="close")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Вы нажали 'Закрыть'", ephemeral=True)
