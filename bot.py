import logging
import requests
from aiogram import Bot, Dispatcher, executor, types
from config import TELEGRAM_BOT_TOKEN, FOOTBALL_API_KEY, TENNIS_API_KEY

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

MAIN_MENU = types.ReplyKeyboardMarkup(resize_keyboard=True)
MAIN_MENU.add(
    types.KeyboardButton("⚽ Live Football"),
    types.KeyboardButton("📅 Pre-Match Football")
)
MAIN_MENU.add(
    types.KeyboardButton("🎾 Live Tennis"),
    types.KeyboardButton("🎾 Pre-Match Tennis")
)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я AI-бот по прогнозам. Выбери режим:", reply_markup=MAIN_MENU)

@dp.message_handler(lambda m: m.text == "⚽ Live Football")
async def live_football(message: types.Message):
    matches = get_live_football()
    if matches:
        await message.answer(matches)
    else:
        await message.answer("Нет текущих футбольных матчей в лайве.")

@dp.message_handler(lambda m: m.text == "📅 Pre-Match Football")
async def prematch_football(message: types.Message):
    matches = get_prematch_football()
    if matches:
        await message.answer(matches)
    else:
        await message.answer("Нет предстоящих футбольных матчей.")

@dp.message_handler(lambda m: m.text == "🎾 Live Tennis")
async def live_tennis(message: types.Message):
    matches = get_live_tennis()
    if matches:
        await message.answer(matches)
    else:
        await message.answer("Нет текущих теннисных матчей в лайве.")

@dp.message_handler(lambda m: m.text == "🎾 Pre-Match Tennis")
async def prematch_tennis(message: types.Message):
    matches = get_prematch_tennis()
    if matches:
        await message.answer(matches)
    else:
        await message.answer("Нет предстоящих теннисных матчей.")

def get_live_football():
    try:
        url = "https://v3.football.api-sports.io/fixtures?live=all"
        headers = {"x-apisports-key": FOOTBALL_API_KEY}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        matches = []
        for fixture in data.get("response", []):
            league = fixture['league']['name']
            teams = f"{fixture['teams']['home']['name']} - {fixture['teams']['away']['name']}"
            score = fixture['goals']['home'], fixture['goals']['away']
            time = fixture['fixture']['status']['elapsed']
            matches.append(f"{league}: {teams} | {score[0]}:{score[1]} ({time} мин)")
        return "\n".join(matches) if matches else None
    except Exception:
        return None

def get_prematch_football():
    try:
        url = "https://v3.football.api-sports.io/fixtures?next=10"
        headers = {"x-apisports-key": FOOTBALL_API_KEY}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        matches = []
        for fixture in data.get("response", []):
            league = fixture['league']['name']
            teams = f"{fixture['teams']['home']['name']} - {fixture['teams']['away']['name']}"
            date = fixture['fixture']['date'].replace("T", " ")[:16]
            matches.append(f"{league}: {teams} | {date}")
        return "\n".join(matches) if matches else None
    except Exception:
        return None

def get_live_tennis():
    try:
        url = "https://api.the-odds-api.com/v4/sports/tennis/events/?regions=eu&oddsFormat=decimal"
        headers = {"x-apisports-key": TENNIS_API_KEY}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        matches = []
        for event in data:
            teams = f"{event['home_team']} - {event['away_team']}"
            matches.append(f"{teams} | LIVE")
        return "\n".join(matches) if matches else None
    except Exception:
        return None

def get_prematch_tennis():
    try:
        url = "https://api.the-odds-api.com/v4/sports/tennis/events/?regions=eu&oddsFormat=decimal"
        headers = {"x-apisports-key": TENNIS_API_KEY}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        matches = []
        for event in data:
            teams = f"{event['home_team']} - {event['away_team']}"
            matches.append(f"{teams} | {event.get('commence_time', '')}")
        return "\n".join(matches) if matches else None
    except Exception:
        return None

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
