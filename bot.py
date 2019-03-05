from telegram.ext import MessageHandler, CommandHandler, InlineQueryHandler

import traceback, logging, datetime
from threading import Thread, Timer
from multiprocessing import Process, Queue
from telegram.error import TelegramError

from script import script_work

import work_materials.globals as globals
from work_materials.globals import updater, dispatcher, moscow_tz, processes, conn, cursor, guilds, guild_change_queue, admin_ids

from libs.guild import Guild

from work_materials.filters.guild_filters import filter_is_admin, filter_awaiting_new_guild, filter_has_access, filter_del_guild

from bin.service_functions import status
from bin.guild import add_guild, adding_guild, handling_guild_changes, list_guilds, del_guild, recashe_guilds


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


def not_allowed(bot, update):
    mes = update.message
    title = update.message.chat.title
    if title is None:
        title = update.message.chat.username
    if (mes.text and '@Rock_Centre_Order_bot' in mes.text) or mes.chat_id > 0:
        bot.send_message(chat_id = admin_ids[0],
                     text = "Несанкционированная попытка доступа, от @{0}, telegram id = <b>{1}</b>,\n"
                        "Название чата - <b>{2}</b>, chat id = <b>{3}</b>".format(mes.from_user.username, mes.from_user.id,
                                                                                title, mes.chat_id), parse_mode = 'HTML')



dispatcher.add_handler(MessageHandler(~filter_has_access, not_allowed, pass_user_data=False))
dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('status', status, pass_user_data=False))
dispatcher.add_handler(CommandHandler('add_guild', add_guild, pass_user_data=True))
dispatcher.add_handler(CommandHandler('list_guilds', list_guilds, pass_user_data=True))
dispatcher.add_handler(MessageHandler(filter_awaiting_new_guild, adding_guild, pass_user_data=True))
dispatcher.add_handler(MessageHandler(filter_del_guild, del_guild, pass_user_data=True))


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