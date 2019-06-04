import work_materials.globals as globals
from work_materials.globals import guilds, cursor, guild_change_queue, moscow_tz, admin_ids, dispatcher, GUILD_CHAT_ID
from libs.guild import Guild
import time, datetime, traceback, logging


def add_guild(bot, update, user_data):
    user_data.update({"status" : "awaiting_new_guild"})
    bot.send_message(chat_id = update.message.chat_id,
                     text = "Теперь пришли мне форвард ответа @chatwarsbot на /guild {TAG}")


def list_guilds(bot, update, user_data):
    response = "Отслеживаемые гильдии:\n"
    request = "select guild_id, castle, tag, name, lvl, glory, num_players from guilds"
    cursor.execute(request)
    row = cursor.fetchone()
    while row:
        response += "{0}<b>{1}</b> 🏅: {2} 🎖: {3}\nУдалить гильдию: /del_guild_{4}\n\n".format(row[1], row[2], row[4], row[5], row[0])
        row = cursor.fetchone()
    bot.send_message(chat_id = update.message.chat_id, text = response, parse_mode = 'HTML')


def adding_guild(bot, update, user_data):
    mes = update.message
    guild_castle = mes.text[0]
    guild_tag = mes.text.partition("]")[0].partition("[")[2]
    guild_name = mes.text.partition(" ")[2].splitlines()[0]
    guild_lvl = int(mes.text.partition("🏅Level: ")[2].split()[0])
    guild_glory = int(mes.text.partition("🎖Glory: ")[2].split()[0])
    guild_num_players = int(mes.text.partition("👥 ")[2].split("/")[0])
    guild = guilds.get(guild_tag)
    if guild is not None:
        bot.send_message(chat_id=mes.chat_id, text="Эта гильдия уже отслеживается!")
        return
    print(guild_castle, guild_tag, guild_name, guild_lvl, guild_glory, guild_num_players)
    request = "insert into guilds(castle, tag, name, lvl, glory, num_players) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(request, (guild_castle, guild_tag, guild_name, guild_lvl, guild_glory, guild_num_players))
    bot.send_message(chat_id=mes.chat_id, text="Гильдия <b>{0}</b> успешно добавлена!\n"
                                               "Вы можете отправлять следующие гильдии".format(guild_tag),
                     parse_mode = 'HTML')
    recashe_guilds()


def del_guild(bot, update, user_data):
    try:
        guild_id = int(update.message.text.split("_")[2])
    except ValueError:
        bot.send_message(chat_id = update.message.chat_id, text = "Неверный синтаксис")
        return
    request = "delete from guilds where guild_id = %s"
    cursor.execute(request, (guild_id,))
    bot.send_message(chat_id = update.message.chat_id, text = "Удаление успешно")


def handling_guild_changes():
    data = guild_change_queue.get()
    while globals.processing and data:
        try:
            tag = data.tag
            end = data.end
            if end:
                worldtop_castles = data.additional_info
                globals.worldtop_castles = worldtop_castles
                print("updating worltop_castles, ", globals.worldtop_castles)
                if data.send:
                    send_results()
                else:
                    dispatcher.bot.send_message(chat_id = admin_ids[0], text="Глори гильдий обновлены!")
                data = guild_change_queue.get()
                continue
            guild = guilds.get(tag)
            if guild is None:
                logging.error("No guild with tag {0}".format(tag))
                data = guild_change_queue.get()
                continue
            if guild.new_glory:
                guild.glory = guild.new_glory
                print("updated {} {}".format(guild.tag, guild.new_glory))
            guild.new_glory = data.glory
        except Exception:
            logging.error(traceback.format_exc())
        data = guild_change_queue.get()


def send_results():
    message_datetime = datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None)
    current_time = message_datetime - message_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    if current_time < datetime.timedelta(hours=1):  #   Дневная битва прошлого дня
        message_datetime -= datetime.timedelta(days=1)
        battle_time = message_datetime.replace(hour = 17, minute = 0, second = 0, microsecond = 0)
    else:
        battle_time = datetime.datetime.combine(message_datetime.date(), datetime.time(hour=1))
        while message_datetime - battle_time >= datetime.timedelta(hours=8):
            battle_time += datetime.timedelta(hours = 8)
    response = "Изменение 🎖глори за битву {0}:\n".format(battle_time.strftime("%D %H:%M"))
    guild_list = list(guilds.values())
    guild_list.sort(key=lambda guild: guild.new_glory - guild.glory if guild.new_glory is not None else -1, reverse=True)
    worldtop_castles = sorted(globals.worldtop_castles.items(), key=lambda elem: elem[1], reverse=True)
    for i, guild in enumerate(guild_list):
        if guild.new_glory is None:
            response += "<b>{2}:</b> {1}<b>{0}</b>: 🎖???".format(guild.tag, guild.castle, i)
            continue
        try:
            glory_change = guild.new_glory - guild.glory
            response += "<b>{3}:</b> {2}<code>{0:3<}</code>: 🎖<code>{1:3<}</code>".format(guild.tag, glory_change,
                                                                                           guild.castle, i)
            print(worldtop_castles)
            if worldtop_castles:
                relative_glory_change = glory_change / guild.num_players
                print(guild.tag, relative_glory_change)
                for i, castle in enumerate(worldtop_castles):
                    glory_for_castle = castle[1]
                    print("glory for castle = {}, castle = {}, i = {}".format(glory_for_castle, castle, i))
                    if glory_for_castle < 0:
                        response += "📌 ???\n\n"
                        break
                    if glory_for_castle <= relative_glory_change:
                        if i == 0:
                            response += "📌 {}\n\n".format(castle[0])
                            break
                        k = i - 1
                        new_castle = worldtop_castles[k]
                        if guild.castle == new_castle[0]:
                            if k == 0:
                                response += " 📌 {}\n".format(castle[0])
                                break
                            k -= 1
                            new_castle = worldtop_castles[k]

                        response += " 📌 {} {}\n".format(new_castle[0], "🔼" if k > 0 else "")
                        break

        except TypeError:
            response += "{1}<b>{0}</b>: 🎖ERROR\n".format(guild.tag, guild.castle)
            logging.error(traceback.format_exc() + guild.new_glory)

        guild.glory = guild.new_glory
        guild.new_glory = None
    dispatcher.bot.send_message(chat_id = admin_ids[0], text = response, parse_mode = "HTML")
    guild_message = dispatcher.bot.send_message(chat_id = GUILD_CHAT_ID, text = response, parse_mode = "HTML")
    try:
        dispatcher.bot.pinChatMessage(chat_id=GUILD_CHAT_ID, message_id=guild_message.message_id, disable_notification=True)
    except Exception:
        logging.error(traceback.format_exc())
    update_guilds()


def update_guilds():
    guild_list = list(guilds.values())
    for guild in guild_list:
        request = "update guilds set glory = %s, num_players = %s, lvl = %s where tag = %s"
        cursor.execute(request, (guild.glory, guild.num_players, guild.lvl, guild.tag))
    logging.info("guilds in database updated")


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
