import pandas as pd
import telebot
from telebot import types
import sqlite3
import zipfile

import work_with_cvs
# from pyunpack import Archive

from work_with_cvs import *

bot = telebot.TeleBot('5944321076:AAErW98ZKZUm-D8zMpxqtCbMF6JF_DMQlHA')
# 356883896 - катя
# 6268363941 - я
# 315540688 - vadim

def extract_arg(arg):
    return arg.split()[1:]


def check_status(id_user):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT id FROM login_id WHERE id = {id_user}")
    result_in_db = cursor.fetchone()
    if result_in_db is None:
        return False
    else:
        return True


def first_start(message, user_id):
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Написать создателю 🤡', url="https://t.me/qumin163")
    kb.add(btn1)
    bot.send_message(message.chat.id, f"Напишите мне для предоставления доступа к боту.\nВаш ID: {user_id}",
                     reply_markup=kb)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    print(user_id, message.from_user.username)
    if check_status(user_id):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text="Попытки подбора пароля")
        btn2 = types.KeyboardButton(text="Блокировки УЗ")
        kb.add(btn1, btn2)

        bot.send_message(message.chat.id, "У вас есть доступ! Удачной работы 😎", reply_markup=kb)
        bot.send_message(message.chat.id,
                         "Если знаете как работать с ботом, то выберите тип инцидента.\nЕсли не знаете, то отправьте: /help")

        check = True
    else:
        first_start(message, user_id)


@bot.message_handler(commands=['help'])
def help(message):
    user_id = message.from_user.id
    if check_status(user_id):
        bot.send_message(message.chat.id,
                         "Привет! Данный бот разработан для ускорения работы с инцидентами ИБ.\n\nЧтобы я смог корректно прочитать выгрузку, то отправь её в меня в формате <b>.csv</b>. "
                         "Если же она очень большая (<b>>20MB</b>), то запакуй её в <b>.zip</b> и все равно присылый мне.\nЯ смогу ее прочитать 🤖"
                         "\n\nСовсем забыл сказать...\nОбязательно, чтобы в выгрузке была колока <b><u>body</u></b>",
                         parse_mode='html')
        bot.send_message(message.chat.id,
                         "Чтобы начать выбери ниже какой тип инцидента ты хочeшь обработать ⬇\n(Если кнопочек нет, то жми /start)")
    else:
        first_start(message, user_id)


@bot.message_handler(commands=['insert'])
def insert(message):
    user_id = message.from_user.id
    flag = "NULL"
    if user_id == 6268363941:
        status = extract_arg(message.text)

        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
            id INTEGER,
            flag TEXT,
            fio TEXT,
            whoappend TEXT
        )""")
        connect.commit()
        users_list = [status[0], flag, status[1], message.from_user.username]
        cursor.execute(f"SELECT id FROM login_id WHERE id = {users_list[0]}")
        data_id = cursor.fetchone()
        # cursor.execute(f"SELECT flag FROM login_id WHERE id = {users_list[0]}")
        # data_flag = cursor.fetchone()
        if data_id is None:
            cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?);", users_list)
            connect.commit()
        else:
            bot.send_message(message.chat.id, f"Пользователь с данным {data_id[0]} уже есть")
            # bot.send_message(message.chat.id, data_flag)

    else:
        bot.send_message(message.chat.id, "У тебя нет доступа. К сожалению и не будет, потому что админская команда.")


@bot.message_handler(commands=['delete'])
def insert(message):
    user_id = message.from_user.id
    if user_id == 6268363941:
        status = extract_arg(message.text)
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()

        cursor.execute(f"DELETE FROM login_id WHERE id = {status[0]}")
        connect.commit()
    else:
        bot.send_message(message.chat.id, "У тебя нет доступа. К сожалению и не будет, потому что админская команда.")

@bot.message_handler(commands=['showall'])
def insert(message):
    user_id = message.from_user.id
    if user_id == 6268363941:
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()

        cursor.execute("SELECT id, fio FROM login_id;")
        all_results = cursor.fetchall()
        list = []
        for res in all_results:
            list.append(str(str(res[0]) + "   --->   " + str(res[1])))
        bot.send_message(message.chat.id, '\n'.join(list))
    else:
        bot.send_message(message.chat.id, "У тебя нет доступа. К сожалению и не будет, потому что админская команда.")


@bot.message_handler(content_types=['text'])
def message_reply(message):
    user_id = message.from_user.id
    if check_status(user_id):
        if message.text == 'Попытки подбора пароля':
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()

            cursor.execute(f"UPDATE login_id SET flag =? WHERE id =?", ("password", user_id))
            connect.commit()
            bot.send_message(message.chat.id, "Еблан1")

        elif message.text == 'Блокировки УЗ':
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()

            cursor.execute(f"UPDATE login_id SET flag =? WHERE id =?", ("block", user_id))
            connect.commit()
            bot.send_message(message.chat.id, "Еблан2")
    else:
        first_start(message, user_id)


@bot.message_handler(content_types=['document'])
def document(message):
    start_time_bot = datetime.now()
    user_id = message.from_user.id
    if check_status(user_id):
        try:
            chat_id = message.chat.id

            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            name_file = message.document.file_name
            print('file name: ' + name_file)

            path = 'C:/Users/ArVip/Desktop/1/' + name_file

            print('path: ' + path)
            with open(path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, "Пожалуй, я сохраню это")

            print('executing main')
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()

            cursor.execute(f"SELECT flag FROM login_id WHERE id = {user_id}")
            data_flag = cursor.fetchone()
            print(data_flag[0])

            bot.send_message(message.chat.id, main(path, data_flag[0]))


        except pd.errors.ParserError:
            bot.reply_to(message, "Не могу прочитать файл, который вы отправили.\nЯ принимаю .csv или .zip")

        except Exception as e:
            if str(e) == "'body'":
                bot.reply_to(message, 'Вы забыли выгрузить поле "body" 🫤')
            else:
                bot.reply_to(message, e)
                print(type(str(e)))



    else:
        first_start(message, user_id)


print('BOT STARTED')
bot.polling(none_stop=True)
