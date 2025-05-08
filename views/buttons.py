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
from babel.dates import format_datetime
from babel import Locale
from datetime import datetime
import os

class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  
        self.add_item(JoinButton())
        self.add_item(JoinExtraButton())
        self.add_item(LeaveButton())
        self.add_item(CloseButton())
        self.add_item(AdminPanelButton())


class AdminButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Управление", style=discord.ButtonStyle.primary, custom_id="join_main")  

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только администраторы могут управлять сбором.", ephemeral=True)
            return

        await interaction.response.send_message("🛠 Панель управления:", view=AdminView(), ephemeral=True)

class JoinButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Присоединиться", style=discord.ButtonStyle.primary, custom_id="join_main")

    async def callback(self, interaction):
        from core.utils import (
            load_data, save_data, update_registration_message, get_priority_and_role
        )

        data = load_data()
        uid = str(interaction.user.id)


        data["main_list"] = [i for i in data["main_list"] if i != uid]
        data["extra_list"] = [i for i in data["extra_list"] if i != uid]

        max_main = data.get("max_main", 0)

        if len(data["main_list"]) < max_main:
            data["main_list"].append(uid)
            save_data(data)
            await update_registration_message(interaction.client, interaction.guild, interaction.user)
            await interaction.response.send_message("✅ Вы добавлены в основной список.", ephemeral=True, delete_after=5)
            return


        guild = interaction.guild
        user_priority, _ = get_priority_and_role(interaction.user)

        weakest_member = None
        weakest_priority = 999

        for i in data["main_list"]:
            try:
                member = await guild.fetch_member(int(i))
                prio, _ = get_priority_and_role(member)
                if prio < weakest_priority:
                    weakest_priority = prio
                    weakest_member = i
            except:
                continue

        if weakest_member and user_priority > weakest_priority:

            data["main_list"].remove(weakest_member)
            data["extra_list"].append(weakest_member)  
            data["main_list"].append(uid)

            save_data(data)
            await update_registration_message(interaction.client, interaction.guild, interaction.user)

            await interaction.response.send_message("🔁 Вы заменили участника с меньшим уровнем. Он перемещён в доп.слот.", ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message("❌ Основной список заполнен. У вас недостаточный уровень для замены.", ephemeral=True, delete_after=5)



class JoinExtraButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Присоединиться в доп.слот", style=discord.ButtonStyle.secondary, custom_id="join_extra")

    async def callback(self, interaction):
        from core.utils import load_data, save_data, update_registration_message

        data = load_data()
        uid = str(interaction.user.id)


        data["main_list"] = [i for i in data["main_list"] if i != uid]
        data["extra_list"] = [i for i in data["extra_list"] if i != uid]

        data["extra_list"].append(uid)
        save_data(data)
        await update_registration_message(interaction.client, interaction.guild, interaction.user)
        await interaction.response.send_message("📘 Вы добавлены в доп.слот.", ephemeral=True, delete_after=5)


class LeaveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Выйти", style=discord.ButtonStyle.danger, custom_id="leave")

    async def callback(self, interaction):
        from core.utils import load_data, save_data, update_registration_message
        data = load_data()
        uid = str(interaction.user.id)
        before = len(data["main_list"]) + len(data["extra_list"])

        data["main_list"] = [i for i in data["main_list"] if i != uid]
        data["extra_list"] = [i for i in data["extra_list"] if i != uid]
        after = len(data["main_list"]) + len(data["extra_list"])

        if before == after:
            await interaction.response.send_message("Вы и так не в списке.", ephemeral=True, delete_after=5)
            return

        save_data(data)
        await update_registration_message(interaction.client, interaction.guild, interaction.user)
        await interaction.response.send_message("🚪 Вы удалены из списков.", ephemeral=True, delete_after=5)


class CloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Закрыть", style=discord.ButtonStyle.danger, custom_id="close")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только админ может закрыть сбор.", ephemeral=True,delete_after=5)
            return
        try:
            await interaction.message.delete()
        except:
            await interaction.response.send_message("❌ Не удалось удалить сообщение.", ephemeral=True, delete_after=5)

class AdminPanelButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Управление", style=discord.ButtonStyle.secondary, custom_id="admin_panel")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только для админа.", ephemeral=True)
            return

        await interaction.response.send_message("🔧 Панель администратора:", view=AdminView(), ephemeral=True)


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
            await interaction.response.send_message(
                "⛔ Только админ может очищать список.", ephemeral=True, delete_after=5
            )
            return

        from core.utils import load_data, save_data, update_registration_message, get_mention
        from main import bot

        old_data = load_data()
        data = {
            "main_list": [],
            "extra_list": [],
            "max_main": old_data.get("max_main", 32),
            "title": old_data.get("title", "Сбор"),
            "date": old_data.get("date", "не указана"),
            "message_id": old_data.get("message_id"),
            "mention_mode": get_mention()
        }
        save_data(data)

        await update_registration_message(bot, interaction.guild, interaction.user)

        # Удаляем админ-панель
        await interaction.message.edit(view=None)

        await interaction.response.send_message("✅ Список очищен!", ephemeral=True, delete_after=5)


class FinishButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Завершить сбор", style=discord.ButtonStyle.secondary, custom_id="admin_finish")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только админ может завершить сбор.", ephemeral=True, delete_after=5)
            return

        from core.utils import load_data, build_registration_embed
        from datetime import datetime
        from babel.dates import format_datetime
        from babel import Locale
        import os

        data = load_data()
        message_id = data.get("message_id")
        channel_id = int(os.getenv("STATUS_CHANNEL_ID", 0))

        channel = interaction.guild.get_channel(channel_id)
        if not channel or not message_id:
            await interaction.response.send_message("❌ Канал или сообщение не найдены.", ephemeral=True, delete_after=5)
            return

        try:
            message = await channel.fetch_message(message_id)
            embed = await build_registration_embed(interaction.guild, interaction.user, finished=True)
            await message.edit(embed=embed, view=None)

            now = datetime.now()
            locale = Locale("ru")
            localized_date = format_datetime(now, "EEEE, d MMMM y 'г.' в HH:mm", locale=locale)
            localized_date = localized_date[0].upper() + localized_date[1:]

            text = f"**Набор завершён!**\n**Дата:** {localized_date}"
            await channel.send(text, delete_after=10)

            await interaction.message.edit(view=None)
            await interaction.response.send_message("✅ Сбор завершён и сообщение обновлено!", ephemeral=True, delete_after=5)

        except Exception as e:
            print("Ошибка при завершении сбора:", e)
            await interaction.response.send_message("❌ Не удалось завершить сбор.", ephemeral=True, delete_after=5)

class AnnounceButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Сделать анонс", style=discord.ButtonStyle.success, custom_id="admin_announce")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только админ может отправлять анонсы.", ephemeral=True, delete_after=5)
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
        await interaction.message.edit(view=None)
        await interaction.response.send_message("✅ Анонс отправлен!", ephemeral=True, delete_after=5)


class ExportButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="📄 Экспорт списка", style=discord.ButtonStyle.secondary, custom_id="admin_export")

    async def callback(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Только админ может экспортировать список.", ephemeral=True, delete_after=5)
            return

        from core.utils import load_data, get_priority_and_role
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
        await interaction.message.edit(view=None)
        await interaction.response.send_message("📎 Вот экспортированный список:", file=file, ephemeral=True)

class MentionSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="@everyone", value="@everyone"),
            discord.SelectOption(label="@here", value="@here"),
            discord.SelectOption(label="@роль", value="role"),
            discord.SelectOption(label="Без тега", value="none")
        ]
        super().__init__(placeholder="Настроить тег для анонса", options=options, custom_id="join_main")  

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "⛔ Только админ может менять настройки.", ephemeral=True, delete_after=5
            )
            return

        from core.utils import set_mention
        value = self.values[0]
        set_mention(value)

        # Удаляем админ-панель
        await interaction.message.edit(view=None)

        if value == "role":
            await interaction.response.send_message(
                "🧩 Выберите нужную роль для тега:", view=RoleSelectorView(), ephemeral=True
            )
        else:
            label = "никого" if value == "none" else value
            await interaction.response.send_message(
                f"✅ Тег установлен: **{label}**", ephemeral=True, delete_after=5
            )

class RoleSelector(discord.ui.Select):
    def __init__(self, roles):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles if not role.is_bot_managed()
        ]
        super().__init__(placeholder="Выберите роль...", options=options, custom_id="join_main")

    async def callback(self, interaction: discord.Interaction):
        from core.utils import set_mention_role
        role_id = int(self.values[0])
        set_mention_role(role_id)
        await interaction.response.send_message(f"✅ Будет тегаться роль: <@&{role_id}>", ephemeral=True, delete_after=5)

class RoleSelectorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        from main import bot
        guild = bot.guilds[0]
        roles = [role for role in guild.roles if role.name != "@everyone"]
        self.add_item(RoleSelector(roles))