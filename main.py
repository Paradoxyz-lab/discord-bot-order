import os
import discord
from discord.ext import commands
from discord import app_commands

from views.buttons import RegisterView
from core.utils import (
    format_list,
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

# /menu — отдельно, если нужно
@bot.tree.command(name="menu", description="Показать меню регистрации (admin only)")
async def menu(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Только администраторы могут использовать эту команду.", ephemeral=True)
        return

    await interaction.response.send_message("Меню регистрации:", view=RegisterView(), ephemeral=True)

# /list — показать текущий список (эпхемерально)
@bot.tree.command(name="list", description="Показать текущий список участников")
async def show_list(interaction: discord.Interaction):
    text = await format_list(interaction.guild)
    await interaction.response.send_message(f"📋 СПИСОК УЧАСТНИКОВ\n\n{text}", ephemeral=True)

# /сбор — создать мероприятие
@bot.tree.command(name="сбор", description="Создать мероприятие с кнопками и лимитом")
@app_commands.describe(
    название="Название мероприятия",
    дата="Дата проведения",
    слоты="Максимум участников"
)
async def create_event(
    interaction: discord.Interaction,
    название: str,
    дата: str,
    слоты: int
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Только админ может создать сбор.", ephemeral=True)
        return

    embed = await build_registration_embed(interaction.guild, interaction.user)
    message = await interaction.channel.send(embed=embed, view=RegisterView())

    # Сохраняем message_id + данные сбора
    save_data({
        "main_list": [],
        "extra_list": [],
        "max_main": слоты,
        "title": название,
        "date": дата,
        "message_id": message.id
    })

    await interaction.response.send_message("✅ Сбор создан!", ephemeral=True)
    await update_status_channel(bot, interaction.guild)

# Запуск
def run_bot(token: str):
    bot.run(token)
