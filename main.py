# main.py
import discord
from discord.ext import commands

from views.buttons import RegisterView

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Команда для проверки
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")

def run_bot(token: str):
    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        bot.add_view(RegisterView())  # Регистрация вьюх (кнопок)

    bot.run(token)
