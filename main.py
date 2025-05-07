from datetime import datetime
import os
import discord
from discord.ext import commands
from discord import app_commands

from views.buttons import RegisterView
from core.utils import (
    format_list,
    load_data,
    save_data,
    update_status_channel,
    build_registration_embed
)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    bot.add_view(RegisterView())

    try:
        synced = await bot.tree.sync()
        print(f"🔧 Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Slash sync failed: {e}")

@bot.tree.command(name="menu", description="Показать меню регистрации (admin only)")
async def menu(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Только администраторы могут использовать эту команду.", ephemeral=True)
        return

    await interaction.response.send_message("Меню регистрации:", view=RegisterView(), ephemeral=True)

@bot.tree.command(name="list", description="Показать текущий список участников")
async def show_list(interaction: discord.Interaction):
    text = await format_list(interaction.guild)
    await interaction.response.send_message(f"📋 СПИСОК УЧАСТНИКОВ\n\n{text}", ephemeral=True)

@bot.tree.command(name="сбор", description="Создать мероприятие с кнопками и лимитом")
@app_commands.describe(
    название="Название мероприятия",
    дата="Дата проведения",
    слоты="Максимум участников"
)
async def create_event(interaction: discord.Interaction, название: str, дата: str, слоты: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Только админ может создать сбор.", ephemeral=True)
        return
    try:
        datetime.strptime(дата, "%d.%m.%Y %H:%M")
    except ValueError:
        await interaction.response.send_message(
            "❌ Неверный формат даты. Используй формат: `дд.мм.гггг чч:мм` (например, 05.05.2025 18:30)",
            ephemeral=True
        )
        return

    save_data({
        "main_list": [],
        "extra_list": [],
        "max_main": слоты,
        "title": название,
        "date": дата,
        "message_id": None,
        "mention_mode": None
    })

    from core.utils import build_registration_embed

    embed = await build_registration_embed(interaction.guild, interaction.user)
    message = await interaction.channel.send(embed=embed, view=RegisterView())


    data = load_data()
    data["message_id"] = message.id
    save_data(data)

    await interaction.response.send_message("✅ Сбор создан и опубликован!", ephemeral=True)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    bot.add_view(RegisterView())  


def run_bot(token: str):
    bot.run(token)
