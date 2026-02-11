import discord
from discord.ext import commands
import requests
from datetime import datetime
import os

TOKEN = os.environ.get("TOKEN")  # берём токен из переменной окружения

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

COINPOKER_URL = "https://coinpoker.com/wp-admin/admin-ajax.php"

# функция для получения UTC времени
def get_utc_date_time_slot():
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    hour = now.hour
    # делим сутки на 4-часовые слоты
    time_slot = f"{hour//4*4}-{hour//4*4+4}"
    return date_str, time_slot

# функция получения лидерборда
def get_leaderboard(board_type="high-4hr"):
    date_str, time_slot = get_utc_date_time_slot()
    data = {
        "action": "get_current_leaderboard_ajax",
        "date": date_str,
        "time_slot": time_slot,
        "leaderboard": board_type
    }
    response = requests.post(COINPOKER_URL, data=data)
    if response.status_code == 200:
        return response.json().get("data", {}).get("data", [])
    return []

# команда для Discord
@bot.slash_command(description="Показать текущий лидерборд CoinPoker")
async def leaderboard(ctx):
    high_board = get_leaderboard("high-4hr")[:10]   # верхний топ-10
    low_board = get_leaderboard("low-4hr")[:15]    # нижний топ-15

    msg = "**🏆 Верхний лидерборд (High Stakes)**\n"
    for i, p in enumerate(high_board, start=1):
        msg += f"{i}. {p['nick_name']} - {p['points']}\n"

    msg += "\n**🥈 Нижний лидерборд (Low Stakes)**\n"
    for i, p in enumerate(low_board, start=1):
        msg += f"{i}. {p['nick_name']} - {p['points']}\n"

    await ctx.respond(msg)

bot.run(TOKEN)