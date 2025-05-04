import os
import json
import discord
from data.roles import ROLE_PRIORITY

def load_data():
    with open("database/storage.json", "r") as f:
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

# Генерация embed-сообщения регистрации
async def build_registration_embed(guild, author):
    data = load_data()
    main_ids = data["main_list"]
    title = data.get("title", "Мероприятие")
    date = data.get("date", "не указана")
    max_main = data.get("max_main", 0)

    members = []
    for uid in main_ids:
        try:
            member = await guild.fetch_member(int(uid))
            priority, role_name = get_priority_and_role(member)
            members.append((priority, role_name, member))
        except:
            continue

    sorted_members = sorted(members, key=lambda x: -x[0])

    mentions = [
        f"{member.mention} — **{role}**"
        for _, role, member in sorted_members
    ]

    embed = discord.Embed(title=title, color=0x5865F2)
    embed.add_field(name="Создал", value=author.mention, inline=True)
    embed.add_field(name="Дата", value=date, inline=True)
    embed.add_field(name="Роли", value="Без ограничений", inline=False)
    embed.add_field(
        name=f"Участники ({len(main_ids)}/{max_main})",
        value="\n".join(mentions) if mentions else "_пусто_",
        inline=False
    )
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
