import os
import json
import discord
from data.roles import ROLE_PRIORITY
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
from babel.dates import format_datetime


# Устанавливаем русскую локаль (только один раз в файле)
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

def load_data():
    if not os.path.exists("database/storage.json") or os.path.getsize("database/storage.json") == 0:
        return {
            "main_list": [],
            "extra_list": [],
            "max_main": 0,
            "title": "",
            "date": "",
            "message_id": None,
            "mention_mode": None
        }

    with open("database/storage.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open("database/storage.json", "w") as f:
        json.dump(data, f, indent=2)

def get_priority_and_role(member: discord.Member) -> tuple[int, str]:
    best_priority = 0
    best_role = "без роли"

    for role in member.roles:
        name = role.name.lower()
        if name in ROLE_PRIORITY:
            prio = ROLE_PRIORITY[name]
            if prio > best_priority:
                best_priority = prio
                best_role = role.name

    return best_priority, best_role


def get_priority(member):
    return get_priority_and_role(member)[0]

async def format_list(guild):
    data = load_data()
    main = data["main_list"]
    extra = data["extra_list"]

    def mention_list(user_ids):
        if not user_ids:
            return "_никого_"
        return "\n".join(f"<@{uid}>" for uid in user_ids)

    return (
        f"**🎯 Основной список ({len(main)}):**\n{mention_list(main)}\n\n"
        f"**📥 Доп.слоты ({len(extra)}):**\n{mention_list(extra)}"
    )




async def build_registration_embed(guild, author, finished=False):
    data = load_data()
    main_ids = data.get("main_list", [])
    extra_ids = data.get("extra_list", [])
    title = data.get("title", "Мероприятие")
    raw_date = data.get("date", "не указана")
    max_main = data.get("max_main", 0)

    # Форматируем дату и считаем отсчёт
    try:
        dt = datetime.strptime(raw_date, "%d.%m.%Y %H:%M")
        date = format_datetime(dt, "EEEE, d MMMM y 'г.' H:mm", locale="ru")
        date = date[0].upper() + date[1:]

        now = datetime.now()
        delta = dt - now
        if delta.total_seconds() < 0:
            countdown = "⏱ Уже началось"
        else:
            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            parts = []
            if days > 0:
                parts.append(f"{days} д.")
            if hours > 0:
                parts.append(f"{hours} ч.")
            if minutes > 0 and days == 0:
                parts.append(f"{minutes} мин.")
            countdown = "⏳ До события: " + ", ".join(parts)
    except:
        date = raw_date
        countdown = ""

    # Сбор участников
    main = []
    extra = []
    for uid in main_ids:
        try:
            member = await guild.fetch_member(int(uid))
            prio, role = get_priority_and_role(member)
            main.append((prio, role, member))
        except:
            continue
    for uid in extra_ids:
        try:
            member = await guild.fetch_member(int(uid))
            prio, role = get_priority_and_role(member)
            extra.append((prio, role, member))
        except:
            continue

    main.sort(key=lambda x: -x[0])
    extra.sort(key=lambda x: -x[0])

    main_text = "\n".join(f"{m.mention} — {r}" for _, r, m in main) if main else "_пусто_"
    extra_text = "\n".join(f"{m.mention} — {r}" for _, r, m in extra) if extra else "_пусто_"

    # Embed
    header = f"🔴 ЗАВЕРШЕН 🔴\n{title}" if finished else title
    embed = discord.Embed(title=header, color=0xFF9900)
    embed.add_field(name="\u200b", value=f"**Создал:** {author.mention}\n**Дата:** {date}\n{countdown}", inline=False)
    embed.add_field(name=f"Участники ({len(main)}/{max_main})", value=main_text, inline=False)
    embed.add_field(name=f"Доп. слоты ({len(extra)})", value=extra_text, inline=False)
    return embed


async def update_registration_message(bot, guild, author):
    data = load_data()
    channel_id = int(os.getenv("STATUS_CHANNEL_ID", 0))
    message_id = data.get("message_id")

    if not channel_id or not message_id:
        return

    channel = guild.get_channel(channel_id)
    if channel is None:
        return

    try:
        message = await channel.fetch_message(message_id)
        embed = await build_registration_embed(guild, author)
        await message.edit(embed=embed)
    except Exception as e:
        print("Ошибка обновления embed:", e)

async def update_status_channel(bot: discord.Client, guild: discord.Guild):
    pass

async def try_notify_full(bot, guild):
    data = load_data()
    channel_id = int(os.getenv("STATUS_CHANNEL_ID", 0))
    if not channel_id:
        return

    channel = guild.get_channel(channel_id)
    if channel:
        await channel.send("🚨 **Основной список заполнен. Новые участники попадают в доп.слоты.**")

def get_mention():
    data = load_data()
    tag = data.get("mention_mode", "@everyone")
    if tag == "role":
        role_id = data.get("mention_role_id")
        return f"<@&{role_id}>" if role_id else None
    return None if tag == "none" else tag

def set_mention(value: str):
    data = load_data()
    data["mention_mode"] = value
    if value != "role":
        data.pop("mention_role_id", None)
    save_data(data)

def set_mention_role(role_id: int):
    data = load_data()
    data["mention_role_id"] = role_id
    save_data(data)
