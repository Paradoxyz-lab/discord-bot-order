import discord
from discord.ext import commands
from discord import app_commands
from views.buttons import RegisterView
from core.utils import format_list

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


@bot.tree.command(name="menu", description="Показать меню регистрации")
async def menu(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Только администраторы могут использовать эту команду.", ephemeral=True)
        return

    await interaction.response.send_message("Меню регистрации:", view=RegisterView(), ephemeral=True)


@bot.tree.command(name="list", description="Показать текущий список участников")
async def show_list(interaction: discord.Interaction):
    text = await format_list(interaction.guild)
    await interaction.response.send_message(text, ephemeral=True)

def run_bot(token: str):
    bot.run(token)

