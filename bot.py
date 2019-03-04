from telegram.ext import MessageHandler, CommandHandler, InlineQueryHandler

import traceback, logging, datetime
from threading import Thread, Timer
from multiprocessing import Process, Queue
from telegram.error import TelegramError

from script import script_work

import work_materials.globals as globals
from work_materials.globals import updater, dispatcher, moscow_tz, processes, conn, cursor, guilds, guild_change_queue

from libs.guild import Guild

from work_materials.filters.guild_filters import filter_is_admin, filter_awaiting_new_guild

from bin.service_functions import status
from bin.guild import add_guild, adding_guild, handling_guild_changes


#   Выставляем логгироввание
console = logging.StreamHandler()
console.setLevel(logging.INFO)

log_file = logging.FileHandler(filename='error.log', mode='a')
log_file.setLevel(logging.ERROR)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO, handlers=[log_file, console])



def start(bot, update, user_data):
    user_data.clear()
    bot.send_message(chat_id=update.message.chat_id,
                     text="Добро пожаловать! Чтобы начать работу, добавьте гильдию для отслеживания: /add_guild")


def recashe_guilds():
    logging.info("Recaching guilds...")
    request = "select guild_id, castle, tag, name, lvl, glory, num_players from guilds"
    cursor.execute(request)
    guilds.clear()
    row = cursor.fetchone()
    while row:
        current = Guild(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        guilds.update({current.tag : current})
        row = cursor.fetchone()
    logging.info("Guilds recashed")




dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('status', status, pass_user_data=False))
dispatcher.add_handler(CommandHandler('add_guild', add_guild, pass_user_data=True))
dispatcher.add_handler(MessageHandler(filter_awaiting_new_guild, adding_guild, pass_user_data=True))


recashe_guilds()
script = Process(target=script_work, args=(), name="Script")
script.start()
processes.append(script)

handling_guild_changes = Thread(target=handling_guild_changes, args=(), name="Handling Guild Changes")
handling_guild_changes.start()
processes.append(handling_guild_changes)

updater.start_polling(clean=False)
# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
# Разрываем подключение к базе данных
globals.processing = 0
guild_change_queue.put(None)
conn.close()