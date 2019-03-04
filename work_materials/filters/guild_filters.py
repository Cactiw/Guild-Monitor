from telegram.ext import BaseFilter
from work_materials.globals import admin_ids, dispatcher, CHAT_WARS_ID, access_list
import datetime


class FilterIsAdmin(BaseFilter):
    def filter(self, message):
        return message.from_user.id in admin_ids

filter_is_admin = FilterIsAdmin()


class FilterHasAccess(BaseFilter):
    def filter(self, message):
        return message.from_user.id in admin_ids or message.from_user.id in access_list

filter_has_access = FilterHasAccess()




class FilterAwaitingGuildInfo(BaseFilter):
    def filter(self, message):
        if message.forward_from and message.forward_from.id == CHAT_WARS_ID:
            user_data = dispatcher.user_data.get(message.from_user.id)
            if user_data and user_data.get("status") == "awaiting_new_guild" and "Commander:" in message.text and \
                    "🎖Glory:" in message.text:
                return True
        return False

filter_awaiting_new_guild = FilterAwaitingGuildInfo()

