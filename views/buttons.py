import discord
from core.registration import handle_join, handle_leave
from core.utils import update_status_channel

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
        from main import bot  
        msg = await handle_join(interaction.user)
        await update_status_channel(bot, interaction.guild)
        await interaction.response.send_message(msg, ephemeral=True)


class LeaveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Выйти", style=discord.ButtonStyle.danger, custom_id="leave")

    async def callback(self, interaction: discord.Interaction):
        from main import bot  
        msg = handle_leave(interaction.user)
        await update_status_channel(bot, interaction.guild)
        await interaction.response.send_message(msg, ephemeral=True)

class CloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Закрыть", style=discord.ButtonStyle.secondary, custom_id="close")

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только администратор может закрыть меню.", ephemeral=True)
            return

        try:
            await interaction.message.delete()
        except discord.NotFound:
            await interaction.response.send_message("Сообщение уже удалено или не найдено ❌", ephemeral=True)
            return

        await interaction.response.send_message("Меню закрыто 🔒", ephemeral=True)
