from telethon import TelegramClient, events
from config import phone, username, password, api_id, api_hash
import time, datetime, random, logging
from threading import Timer

from libs.guild import GuildChange

from work_materials.globals import moscow_tz, guilds, CHAT_WARS_ID, guild_change_queue


def script_work():
    global client
    admin_client = TelegramClient(username, api_id, api_hash, update_workers=1, spawn_read_thread=False)
    admin_client.start(phone, password)

    client = admin_client
    admin_client.get_entity("ChatWarsBot")
    start_countdown()

    print("started timer")
    #timer = Timer(interval=5, function=update_guild_stats, args=[client]).start()

    admin_client.idle()


def get_time_remaining(hours = 0, minutes = 0, seconds = 0):
    now = datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None) - datetime.datetime.combine(
        datetime.datetime.now().date(), datetime.time(hour=0))
    print(now)
    if now < datetime.timedelta(hours=hours, minutes=minutes, seconds = seconds):
        return (datetime.timedelta(hours=hours, minutes=minutes, seconds = seconds) - now).total_seconds()
    else:
        time_from_first_battle = now - datetime.timedelta(hours=hours, minutes=minutes, seconds = seconds)
        while time_from_first_battle > datetime.timedelta(hours=8):
            time_from_first_battle -= datetime.timedelta(hours=8)
        time_remaining = datetime.timedelta(hours=8) - time_from_first_battle
        return time_remaining.total_seconds()


def start_countdown():
    time_remaining = get_time_remaining(hours=1, minutes=10)
    timer = Timer(interval=time_remaining - random.random() * 13.3790437,
                      function=update_guild_stats, args=[client, True])
    timer.start()


def start_updating():
    time_remaining = get_time_remaining(hours=0, minutes=58)
    timer = Timer(interval=time_remaining - random.random() * 19.8356421,
                  function=update_guild_stats, args=[client, False])
    timer.start()


def update_guild_stats(client, send):
    global answered
    answered = False
    logging.info("updating_guild_stats")
    guild_list = list(guilds.values())
    for guild in guild_list:
        client.add_event_handler(guild_info_handler, events.NewMessage)
        client.send_message(CHAT_WARS_ID, "/guild {0}".format(guild.tag))
        while not answered:
            time.sleep(1)
        answered = False
        time.sleep(random.random()*3.96578)
    end = GuildChange("", 0, end = True, send = send)
    guild_change_queue.put(end)


def guild_info_handler(event):
    global answered
    if event.is_private:
        # print(time.asctime(), '-', event.message)  # optionally log time and message
        print(time.asctime(), '-', event.message.from_id)
        print(event.message.message)
        text = event.message.message
        if event.message.from_id == CHAT_WARS_ID and "Commander:" in text and "🎖Glory:" in text:
            guild_tag = text.partition("]")[0].partition("[")[2]
            guild_glory = int(text.partition("🎖Glory: ")[2].split()[0])
            print("YES")
            current = GuildChange(guild_tag, guild_glory)
            guild_change_queue.put(current)
            answered = True
            client.remove_event_handler(guild_info_handler)
            return
#script_work()
