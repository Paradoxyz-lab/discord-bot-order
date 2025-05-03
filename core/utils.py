import json
import os
import discord

def load_data():
    with open("database/storage.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("database/storage.json", "w") as f:
        json.dump(data, f, indent=2)

def get_priority(member):
    from data.roles import ROLE_PRIORITY
    for role in member.roles:
        name = role.name.lower()
        if name in ROLE_PRIORITY:
            return ROLE_PRIORITY[name]
    return 0


async def format_list(guild):
    data = load_data()
    main = data["main_list"]
    extra = data["extra_list"]

    def mention_list(user_ids):
        if not user_ids:
            return "_никого_"
        return "\n".join(f"<@{uid}>" for uid in user_ids)

    msg = (
        f"**🎯 Основной список ({len(main)}):**\n"
        f"{mention_list(main)}\n\n"
        f"**📥 Доп.слоты ({len(extra)}):**\n"
        f"{mention_list(extra)}"
    )
    return msg

async def update_status_channel(bot: discord.Client, guild: discord.Guild):
    channel_id = int(os.getenv("STATUS_CHANNEL_ID", 0))
    if not channel_id:
        return

    channel = guild.get_channel(channel_id)
    if channel is None:
        return

    async for msg in channel.history(limit=10):
        if msg.author == bot.user:
            await msg.delete()

    text = await format_list(guild)
    await channel.send(text)
