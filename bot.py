import pandas as pd
import telebot
from telebot import types
import zipfile

import work_with_cvs
# from pyunpack import Archive

from work_with_cvs import *

bot = telebot.TeleBot('5944321076:AAErW98ZKZUm-D8zMpxqtCbMF6JF_DMQlHA')
#356883896 - катя
# 6268363941 - я
user_white_list = [6268363941, 315540688]
check = False
password = False
block = False


@bot.message_handler(commands=['start'])
def start(message):
    global check
    user_id = message.from_user.id
    print(user_id, message.from_user.username)
    if user_id in user_white_list:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text="Попытки подбора пароля")
        btn2 = types.KeyboardButton(text="Блокировки УЗ")
        kb.add(btn1, btn2)

        bot.send_message(message.chat.id, "У вас есть доступ! Удачной работы 😎", reply_markup=kb)
        bot.send_message(message.chat.id, "Если знаете как работать с ботом, то выберите тип инцидента.\nЕсли не знаете, то отправьте: /help")

        check = True
    else:
        kb = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Написать создателю 🤡', url="https://t.me/qumin163")
        kb.add(btn1)
        bot.send_message(message.chat.id, f"Напишите мне для предоставления доступа к боту.\nВаш ID: {user_id}", reply_markup=kb)

@bot.message_handler(commands=['help'])
def help(message):
    user_id = message.from_user.id
    if user_id in user_white_list:
        bot.send_message(message.chat.id, "Привет! Данный бот разработан для ускорения работы с инцидентами ИБ.\nЧтобы я смог корректно прочитать выгрузку, то отправь её в меня в формате <b>.csv</b>. Если же она очень большая (<b>>20MB</b>), то запакуй её в <b>.zip</b> и все равно присылый мне.\nЯ смогу ее прочитать 🤖",
                         parse_mode='html')
        bot.send_message(message.chat.id, "Чтобы начать выбери ниже какой тип инцидента ты хочeшь обработать ⬇\n(Если кнопочек нет, то жми /start)")
    else:
        kb = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Написать создателю 🤡', url="https://t.me/qumin163")
        kb.add(btn1)
        bot.send_message(message.chat.id, f"Напишите мне для предоставления доступа к боту.\nВаш ID: {user_id}",
                         reply_markup=kb)


@bot.message_handler(content_types=['text'])
def message_reply(message):
    global password
    global block
    user_id = message.from_user.id
    if user_id in user_white_list:
        if message.text == 'Попытки подбора пароля':
            password = True
            block = False
            bot.send_message(message.chat.id, "Еблан1")


        elif message.text == 'Блокировки УЗ':
            block = True
            password = False
            bot.send_message(message.chat.id, "Еблан2")
    else:
        kb = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Написать создателю 🤡', url="https://t.me/qumin163")
        kb.add(btn1)
        bot.send_message(message.chat.id, f"Напишите мне для предоставления доступа к боту.\nВаш ID: {user_id}", reply_markup=kb)



@bot.message_handler(content_types=['document'])
def document(message):
    user_id = message.from_user.id
    if user_id in user_white_list:
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
            if password:
                bot.send_message(message.chat.id, pizda5())
            elif block:
                bot.send_message(message.chat.id, main(path))
            # if not (".csv" in name_file):
            #     Archive(src).extractall(path)

            # stories_zip = zipfile.ZipFile(src)
            # for file in stories_zip.namelist():
            #     bot.send_message(message.chat.id, {stories_zip.getinfo(file).filename})

            # bot.send_message(message.chat.id, {name_file})
            # bot.send_message(message.chat.id, len)


        except pd.errors.ParserError:
            bot.reply_to(message, "Не могу прочитать файл, который вы отправили.\n Я принимаю .csv или .zip")

        except Exception as e:
            bot.reply_to(message, e)



    else:
        kb = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Написать создателю 🤡', url="https://t.me/qumin163")
        kb.add(btn1)
        bot.send_message(message.chat.id, f"Напишите мне для предоставления доступа к боту.\nВаш ID: {user_id}", reply_markup=kb)


print('BOT STARTED')
bot.polling(none_stop=True)
