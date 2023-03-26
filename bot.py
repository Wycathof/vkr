import pandas as pd
import telebot
import zipfile
from pyunpack import Archive

from work_with_cvs import *

bot = telebot.TeleBot('5944321076:AAErW98ZKZUm-D8zMpxqtCbMF6JF_DMQlHA')

user_white_list = [6268363941]
check = False


@bot.message_handler(commands=['start'])
def start(message):
    global check
    user_id = message.from_user.id
    if user_id in user_white_list:
        bot.send_message(message.chat.id, "Вы приняты")
        check = True
    else:
        bot.send_message(message.chat.id, f"Напишите @qumin163 для предоставления доступа к боту.\nВаш ID: {user_id} ")


@bot.message_handler(commands=['hello'])
def hello(message):
    if check:
        bot.send_message(message.chat.id, "Hello")
    else:
        bot.send_message(message.chat.id, "not dostyp")


@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    try:
        chat_id = message.chat.id

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        name_file = message.document.file_name

        path = 'C:/Users/ArVip/Desktop/1/' + name_file
        with open(path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "Пожалуй, я сохраню это")

        # if not (".csv" in name_file):
        #     Archive(src).extractall(path)

        # stories_zip = zipfile.ZipFile(src)
        # for file in stories_zip.namelist():
        #     bot.send_message(message.chat.id, {stories_zip.getinfo(file).filename})

        bot.send_message(message.chat.id, {name_file})
        # bot.send_message(message.chat.id, {src})

        # csv_data = pd.read_csv(r'C:/Users/ArVip/Desktop/1/' + name_file, delimiter=';', encoding="",
        #                        encoding_errors="ignore")
        # new_dict = {}
        # for i, body in enumerate(csv_data['body']):
        #     start = '{"Event"'
        #     check = body.startswith(start)
        #     if not check:
        #         csv_data = csv_data.drop(index=i)
        #
        # csv_data.reset_index(drop=True, inplace=True)
        # bot.send_message(message.chat.id, len(csv_data))




    except Exception as e:
        bot.reply_to(message, e)


bot.polling(none_stop=True)
