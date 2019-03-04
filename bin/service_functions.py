from work_materials.globals import processes, dispatcher, moscow_tz
import datetime


def status(bot, update):
    OK = True
    response = "Status report for {0}:\n".format(datetime.datetime.now(tz=moscow_tz))
    for process in processes:
        response += "{0}{1}\n".format("✅" if process.is_alive() else "🛑", process.name)
        if not process.is_alive():
            OK = False
    workers_alive = 1#dispatcher.bot.check_workers()
    workers_total = 1#dispatcher.bot.num_workers
    if workers_alive != workers_total:
        OK = False
    response += "{2}bot workers: <b>{0}</b> of <b>{1}</b> are alive\n".format(workers_alive, workers_total,
                                                                              "✅" if workers_alive == workers_total else "🛑")
    response += "\n{0}".format("❇️ Everything is OK" if OK else "‼️‼️ ALERT ‼️‼️")
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
