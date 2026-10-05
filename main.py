import os
import json
import random
import threading
import telebot

TOKEN = os.environ["8954516294:AAGtxEc-U0JfG_Cghzs22t778l8ALvf6vRQ"]
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
DATA_FILE = "ideas.json"

bot = telebot.TeleBot(TOKEN)
lock = threading.Lock()


def load():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save(ideas):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(ideas, f, ensure_ascii=False, indent=2)


@bot.message_handler(commands=["start", "help"])
def start(m):
    bot.reply_to(m, (
        "Привет! Это бот сериала «Мопс-бизнесмен» 🐶\n\n"
        "Предложи идею для серии:\n"
        "/idea мопс открыл парикмахерскую\n\n"
        "Крутить рулетку идей:\n"
        "/roulette"
    ))


@bot.message_handler(commands=["idea"])
def add_idea(m):
    text = m.text.partition(" ")[2].strip()
    if not text:
        bot.reply_to(m, "Напиши идею после команды: /idea мопс открыл кафе")
        return
    if len(text) > 200:
        bot.reply_to(m, "Слишком длинно, уложись в 200 символов.")
        return
    with lock:
        ideas = load()
        ideas.append({
            "text": text,
            "user": m.from_user.username or m.from_user.first_name,
            "used": False,
        })
        save(ideas)
        n = len(ideas)
    bot.reply_to(m, f"Записал! Идей всего: {n} 🌭")


@bot.message_handler(commands=["roulette"])
def roulette(m):
    with lock:
        ideas = load()
    free = [i for i in ideas if not i["used"]]
    if not free:
        bot.reply_to(m, "Идей пока нет. Предложи первым: /idea ...")
        return
    pick = random.choice(free)
    bot.reply_to(m, f"🎰 Выпало:\n\n«{pick['text']}»\n\nавтор: @{pick['user']}")


@bot.message_handler(commands=["list"])
def list_ideas(m):
    if m.from_user.id != OWNER_ID:
        return
    with lock:
        ideas = load()
    if not ideas:
        bot.reply_to(m, "Пусто.")
        return
    lines = []
    for n, i in enumerate(ideas, 1):
        mark = "✅" if i["used"] else "▫️"
        lines.append(f"{n}. {mark} {i['text']} (@{i['user']})")
    text = "\n".join(lines)
    for part in [text[x:x + 3500] for x in range(0, len(text), 3500)]:
        bot.send_message(m.chat.id, part)


@bot.message_handler(commands=["used"])
def mark_used(m):
    if m.from_user.id != OWNER_ID:
        return
    arg = m.text.partition(" ")[2].strip()
    if not arg.isdigit():
        bot.reply_to(m, "Укажи номер: /used 3")
        return
    n = int(arg)
    with lock:
        ideas = load()
        if not 1 <= n <= len(ideas):
            bot.reply_to(m, "Нет такого номера.")
            return
        ideas[n - 1]["used"] = True
        save(ideas)
    bot.reply_to(m, "Отметил как использованную ✅")


@bot.message_handler(commands=["myid"])
def myid(m):
    bot.reply_to(m, f"Твой id: {m.from_user.id}")


bot.infinity_polling(skip_pending=True)
