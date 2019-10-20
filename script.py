from telethon.sync import TelegramClient, events
from telethon.tl.types import PeerChannel
from config import phone, username, password, api_id, api_hash
import time, datetime, random, logging, traceback
from threading import Timer

from libs.guild import GuildChange

from work_materials.globals import moscow_tz, guilds, CHAT_WARS_ID, guild_change_queue, castles, worldtop_castles,\
    RESULTS_REPORT_CHAT_ID, TEST_CHANNEL_ID

import asyncio

loop:asyncio.AbstractEventLoop = None


def script_work():
    global client
    global loop
    loop = asyncio.get_event_loop()
    admin_client = TelegramClient(username, api_id, api_hash)
    admin_client.start(phone, password)
    with admin_client as client:
        client = admin_client
        admin_client.get_entity("ChatWarsBot")
        start_updating()
        start_countdown()

        print("started timer")
        #timer = Timer(interval=5, function=update_guild_stats, args=[client, True]).start()

        admin_client.run_until_disconnected()


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
    loop.call_later(delay=time_remaining - random.random() * 13.3790437, callback=update_guild_stats(client, True))
    timer.start()


def start_updating():
    time_remaining = get_time_remaining(hours=0, minutes=58)
    time_remaining = 1
    timer = Timer(interval=time_remaining - random.random() * 19.8356421,
                  function=update_guild_stats, args=[client, False])

    timer.start()


async def update_guild_stats(client, send):
    global answered
    answered = False
    logging.info("updating_guild_stats")
    guild_list = list(guilds.values())
    for guild in guild_list:
        client.add_event_handler(guild_info_handler, events.NewMessage)
        await client.send_message(CHAT_WARS_ID, "/guild {0}".format(guild.tag))
        while not answered:
            time.sleep(1)
        answered = False
        client.remove_event_handler(guild_info_handler)
        .sleep(random.random()*3.96578)
    try:
        if send:
            start_countdown()
            start_updating()
        else:
            client.add_event_handler(worldtop_handler, events.NewMessage)
            client.send_message(CHAT_WARS_ID, "/worldtop")
            answered = False
            while not answered:
                time.sleep(1)
            answered = False
            client.remove_event_handler(worldtop_handler)
            client.add_event_handler(results_handler, events.NewMessage)
    except Exception:
        logging.error(traceback.format_exc())
    end = GuildChange("", 0, end=True, send=send, additional_info=worldtop_castles)
    guild_change_queue.put(end)


async def worldtop_handler(event):
    global answered
    if event.is_private:
        text = event.message.message
        #print(event.message)
        if event.message.from_id == CHAT_WARS_ID and text.find("🏅# 1") == 0 and "🏆 очков" in text:
            print("updating worldtop")
            answered = True
            lines = text.splitlines()
            glory = 10
            for line in lines:
                for castle in castles:
                    if castle in line:
                        worldtop_castles.update({castle: glory})
                glory -= 1
            print(worldtop_castles)


async def results_handler(event):
    text = event.message.message
    #print(text)
    #if event.message.to_id == PeerChannel(TEST_CHANNEL_ID):
    #print(event.message)
    if event.message.to_id == PeerChannel(RESULTS_REPORT_CHAT_ID):
        client.remove_event_handler(results_handler)
        print("received stats...")
        print(worldtop_castles)
        for castle in list(worldtop_castles):
            if "🛡" in text.partition(castle)[2].splitlines()[0]:
                worldtop_castles.update({castle: -10})
        print(worldtop_castles)
        return


async def guild_info_handler(event):
    global answered
    if event.is_private:
        # print(time.asctime(), '-', event.message)  # optionally log time and message
        print(time.asctime(), '-', event.message.from_id)
        print(event.message.message)
        text = event.message.message
        if event.message.from_id == CHAT_WARS_ID and "Commander:" in text and "🎖Glory:" in text:
            guild_tag = text.partition("]")[0].partition("[")[2]
            guild_glory = int(text.partition("🎖Glory: ")[2].split()[0])
            guild_castle = text[0]
            print("YES")
            current = GuildChange(guild_tag, guild_glory, castle=guild_castle)
            guild_change_queue.put(current)
            answered = True
            client.remove_event_handler(guild_info_handler)
            return
#script_work()
