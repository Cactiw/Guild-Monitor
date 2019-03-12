import psycopg2, pytz, tzlocal
from multiprocessing import Queue

from telegram.ext import Updater

from config import ProductionToken, request_kwargs, psql_creditals

processing = True

conn = psycopg2.connect("dbname={0} user={1} password={2}".format(psql_creditals['dbname'], psql_creditals['user'], psql_creditals['pass']))
conn.set_session(autocommit = True)
cursor = conn.cursor()

updater = Updater(token=ProductionToken, request_kwargs=request_kwargs)

dispatcher = updater.dispatcher
job = updater.job_queue

CHAT_WARS_ID = 265204902
GUILD_CHAT_ID = -1001377426029

admin_ids = [231900398]
access_list = [116028074, 618831598]

processes = []
guilds = {}
guild_change_queue = Queue()


moscow_tz = pytz.timezone('Europe/Moscow')
try:
    local_tz = tzlocal.get_localzone()
except pytz.UnknownTimeZoneError:
    local_tz = pytz.timezone('Europe/Andorra')


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu