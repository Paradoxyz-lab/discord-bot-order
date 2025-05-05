import os
import discord
from discord.ui import Button
from core.registration import handle_join, handle_leave
from core.utils import (
    load_data,
    save_data,
    update_registration_message,
    get_mention,
    set_mention,
    get_priority_and_role
)

class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(JoinButton())
        self.add_item(LeaveButton())
        self.add_item(CloseButton())
        self.add_item(AdminButton())

class AdminButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Управление", style=discord.ButtonStyle.primary, custom_id="admin_menu")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только администраторы могут управлять сбором.", ephemeral=True)
            return

        await interaction.response.send_message("🛠 Панель управления:", view=AdminView(), ephemeral=True)

class JoinButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Присоединиться", style=discord.ButtonStyle.success, custom_id="join")

    async def callback(self, interaction):
        from main import bot
        msg = await handle_join(interaction.user, bot)
        await update_registration_message(bot, interaction.guild, interaction.user)
        await interaction.response.send_message(msg, ephemeral=True)

class LeaveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Выйти", style=discord.ButtonStyle.danger, custom_id="leave")

    async def callback(self, interaction: discord.Interaction):
        from main import bot
        msg = handle_leave(interaction.user)
        await update_registration_message(bot, interaction.guild, interaction.user)
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

class AdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ClearButton())
        self.add_item(FinishButton())
        self.add_item(AnnounceButton())
        self.add_item(ExportButton())
        self.add_item(MentionSelect())

class ClearButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Очистить список", style=discord.ButtonStyle.danger, custom_id="admin_clear")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только админ может очищать список.", ephemeral=True)
            return

        data = {
            "main_list": [],
            "extra_list": [],
            "max_main": 32,
            "title": "Сбор",
            "date": "не указана",
            "message_id": load_data().get("message_id"),
            "mention_mode": get_mention()
        }
        save_data(data)

        from main import bot
        await update_registration_message(bot, interaction.guild, interaction.user)
        await interaction.response.send_message("✅ Список очищен!", ephemeral=True)

class FinishButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Завершить сбор", style=discord.ButtonStyle.secondary, custom_id="admin_finish")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только админ может завершить сбор.", ephemeral=True)
            return

        from core.utils import load_data, build_registration_embed
        from datetime import datetime
        import os

        data = load_data()
        message_id = data.get("message_id")
        channel_id = int(os.getenv("STATUS_CHANNEL_ID", 0))

        channel = interaction.guild.get_channel(channel_id)
        if not channel or not message_id:
            await interaction.response.send_message("❌ Канал или сообщение не найдены.", ephemeral=True)
            return

        try:
            message = await channel.fetch_message(message_id)
            embed = await build_registration_embed(interaction.guild, interaction.user, finished=True)
            await message.edit(embed=embed, view=None)

            now = datetime.now()
            localized_date = now.strftime("%A, %d %B %Y г. в %H:%M").capitalize()
            text = f"**Набор завершён!**\n**Дата:** {localized_date}"

            await channel.send(text)
            await interaction.response.send_message("✅ Сбор завершён и сообщение обновлено!", ephemeral=True)

        except Exception as e:
            print("Ошибка при завершении сбора:", e)
            await interaction.response.send_message("❌ Не удалось завершить сбор.", ephemeral=True)

class AnnounceButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Сделать анонс", style=discord.ButtonStyle.success, custom_id="admin_announce")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только админ может отправлять анонсы.", ephemeral=True)
            return

        from core.utils import load_data, get_mention
        data = load_data()

        title = data.get("title", "Мероприятие")
        date = data.get("date", "не указана")
        max_main = data.get("max_main", 0)
        mention = get_mention()

        preview = mention if mention else "без тега"

        embed = discord.Embed(
            title="📢 Новый сбор открыт!",
            description=f"**{title}**\n🗓 Дата: **{date}**\n👥 Мест: **{max_main}**",
            color=0x57F287
        )
        embed.add_field(name="Пинг при анонсе", value=preview, inline=False)
        embed.set_footer(text="Нажмите /сбор чтобы зарегистрироваться")

        await interaction.channel.send(embed=embed, content=mention if mention else None)
        await interaction.response.send_message("✅ Анонс отправлен!", ephemeral=True)


class ExportButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="📄 Экспорт списка", style=discord.ButtonStyle.secondary, custom_id="admin_export")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только админ может экспортировать список.", ephemeral=True)
            return

        data = load_data()
        main_ids = data["main_list"]

        lines = []
        guild = interaction.guild
        for uid in main_ids:
            try:
                member = await guild.fetch_member(int(uid))
                priority, role = get_priority_and_role(member)
                lines.append((priority, f"{member.name}#{member.discriminator} — {role}"))
            except:
                continue

        lines.sort(key=lambda x: -x[0])
        content = "\n".join([line for _, line in lines]) or "список пуст"

        with open("export.txt", "w", encoding="utf-8") as f:
            f.write(content)

        file = discord.File("export.txt", filename="список_участников.txt")
        await interaction.response.send_message("📎 Вот экспортированный список:", file=file, ephemeral=True)

class MentionSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="@everyone", value="@everyone"),
            discord.SelectOption(label="@here", value="@here"),
            discord.SelectOption(label="@роль", value="role"),
            discord.SelectOption(label="Без тега", value="none")
        ]
        super().__init__(placeholder="Настроить тег для анонса", options=options)

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только админ может менять настройки.", ephemeral=True)
            return

        from core.utils import set_mention
        value = self.values[0]
        set_mention(value)

        if value == "role":
            await interaction.response.send_message("🧩 Выберите нужную роль для тега:", view=RoleSelectorView(), ephemeral=True)
        else:
            label = "никого" if value == "none" else value
            await interaction.response.send_message(f"✅ Тег установлен: **{label}**", ephemeral=True)

class RoleSelector(discord.ui.Select):
    def __init__(self, roles):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles if not role.is_bot_managed()
        ]
        super().__init__(placeholder="Выберите роль...", options=options)

    async def callback(self, interaction: discord.Interaction):
        from core.utils import set_mention_role
        role_id = int(self.values[0])
        set_mention_role(role_id)
        await interaction.response.send_message(f"✅ Будет тегаться роль: <@&{role_id}>", ephemeral=True)

class RoleSelectorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        # фильтруем только роли, которые не админские и не everyone
        from main import bot
        guild = bot.guilds[0]
        roles = [role for role in guild.roles if role.name != "@everyone"]
        self.add_item(RoleSelector(roles))
