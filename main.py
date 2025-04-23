import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import random
from datetime import datetime

BOT_TOKEN = '7365810160:AAF37qXcW7K0gp7GfdI5JoCSDKOtK72cuTg'
KANAL1 = "@TeazerEnginee"
KANAL2 = "@Teazerss"
bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

def load_data():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("users.json", "w") as f:
        json.dump(data, f)

users = load_data()

def check_daily(user_id):
    today = datetime.today().date()
    last_request_date = users[user_id].get("last_random_date")
    if last_request_date == str(today):
        return False
    return True

def update_last_request_date(user_id):
    today = datetime.today().date()
    users[user_id]["last_random_date"] = str(today)
    save_data(users)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {"ref": 0, "verified": False, "last_random_date": None}
        save_data(users)

    if message.text.startswith("/start="):
        ref_id = message.text.split("=")[1]
        if ref_id != user_id and ref_id in users:
            users[ref_id]["ref"] += 1
            save_data(users)

    if users[user_id].get("verified"):
        bot.send_message(message.chat.id, "**Komutlar:**\n/referans\n/hesap\n/siralama\n/random", parse_mode="Markdown")
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Kanal 1", url="https://t.me/TeazerEnginee"))
        markup.add(InlineKeyboardButton("Kanal 2", url="https://t.me/Teazerss"))
        markup.add(InlineKeyboardButton("Kontrol Et", callback_data="check"))
        bot.send_message(message.chat.id, "Başlamadan önce iki kanala katılmalısın:", reply_markup=markup)

@bot.message_handler(commands=["referans"])
def referans(message):
    user_id = str(message.from_user.id)
    ref_count = users.get(user_id, {}).get("ref", 0)
    ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    msg = f"Referansım:\n{ref_link}\n\nReferansla Katılan: {ref_count} kişi"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=["hesap"])
def hesap(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("PUBG", callback_data="select_pubg"),
        InlineKeyboardButton("PreDunya", callback_data="select_predunya")
    )
    bot.send_message(message.chat.id, "Hesap türünü seç:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def select_category(call):
    if call.data == "select_pubg":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("1 Random (3 ref)", callback_data="hesap_3"),
            InlineKeyboardButton("1 Garanti (10 ref)", callback_data="hesap_10")
        )
        bot.edit_message_text("PUBG hesap türünü seç:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "select_predunya":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("1 Garanti (4 ref)", callback_data="predunya_4")
        )
        bot.edit_message_text("PreDunya hesap türünü seç:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "predunya_4")
def predunya_ver(call):
    user_id = str(call.from_user.id)
    if users[user_id]["ref"] < 4:
        bot.answer_callback_query(call.id, "Yeterli referans yok.")
        return

    try:
        with open("predunyam.txt", "r") as f:
            lines = f.readlines()
    except:
        bot.send_message(call.message.chat.id, "PreDunya dosyası bulunamadı.")
        return

    if not lines:
        bot.send_message(call.message.chat.id, "PreDunya hesabı kalmadı.")
        return

    line = lines[0]
    email, password = line.strip().split(":")
    lines.remove(line)

    with open("predunyam.txt", "w") as f:
        f.writelines(lines)

    msg = f"**Email:** {email}\n**Şifre:** {password}"
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

    users[user_id]["ref"] -= 4
    save_data(users)

@bot.message_handler(commands=["random"])
def random_hesap(message):
    user_id = str(message.from_user.id)

    if not check_daily(user_id):
        bot.send_message(message.chat.id, "Bugün zaten bir random hesap aldın. Yarın tekrar deneyebilirsin.")
        return

    if users[user_id]["ref"] < 3:
        bot.send_message(message.chat.id, "Yeterli referansın yok. 3 referans gereklidir.")
        return

    with open("hesaplar.txt", "r") as f:
        lines = f.readlines()

    if not lines:
        bot.send_message(message.chat.id, "Hesap kalmadı.")
        return

    line = random.choice(lines)
    parts = line.strip().split(":")
    email, password, name = parts[0], parts[1], parts[2]
    lines.remove(line)

    with open("hesaplar.txt", "w") as f:
        f.writelines(lines)

    msg = f"**Email:** {email}\n**Şifre:** {password}\n**İsim:** {name}"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    users[user_id]["ref"] -= 3
    update_last_request_date(user_id)
    save_data(users)

@bot.callback_query_handler(func=lambda call: call.data.startswith("hesap_"))
def hesap_ver(call):
    user_id = str(call.from_user.id)
    ref_required = int(call.data.split("_")[1])
    if users[user_id]["ref"] < ref_required:
        bot.answer_callback_query(call.id, "Yeterli referans yok.")
        return

    users[user_id]["ref"] -= ref_required
    save_data(users)

    if ref_required == 10:
        with open("garanti.txt", "r") as f:
            lines = f.readlines()
        if not lines:
            bot.send_message(call.message.chat.id, "Garanti hesap kalmadı.")
            return

        line = lines[0]
        parts = line.strip().split(":")
        email, password, name = parts[0], parts[1], parts[2]
        lines.remove(line)

        with open("garanti.txt", "w") as f:
            f.writelines(lines)

    else:
        with open("hesaplar.txt", "r") as f:
            lines = f.readlines()
        if not lines:
            bot.send_message(call.message.chat.id, "Hesap kalmadı.")
            return

        line = random.choice(lines)
        parts = line.strip().split(":")
        email, password, name = parts[0], parts[1], parts[2]
        lines.remove(line)

        with open("hesaplar.txt", "w") as f:
            f.writelines(lines)

    msg = f"**Email:** {email}\n**Şifre:** {password}\n**İsim:** {name}"
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=["siralama"])
def siralama(message):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["ref"], reverse=True)
    msg = ""
    for i, (uid, data) in enumerate(sorted_users[:10], start=1):
        try:
            user = bot.get_chat(uid)
            name = user.username or user.first_name
        except:
            name = f"ID:{uid}"
        msg += f"{i}. {name} - {data['ref']} ref\n"
    bot.send_message(message.chat.id, msg)

bot.infinity_polling()
