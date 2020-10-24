from typing import Optional

from telegram import Message, Update, Bot, User
from telegram import MessageEntity
from telegram.ext import Filters, MessageHandler, run_async

from tg_bot import dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler, DisableAbleRegexHandler
from tg_bot.modules.sql import channel_join_sql as sql
from tg_bot.modules.users import get_user_id
from tg_bot.modules.helper_funcs.chat_status import is_user_admin, is_user_in_chat, user_admin



@run_async
@user_admin
def set_channel_for_force_join(bot: Bot, update: Update):
    args = update.effective_message.text.split(None, 1)
    if len(args) >= 2:
        channel_id = args[1]
    else:
        sql.rm_force_channel_join(update.message.chat.id)
        update.effective_message.reply_text("پەیوەستبوونی ناچاریی کەناڵ ناچالاککرا.")
        return
        
    channel_id = channel_id.replace("@", "")

    sql.set_channel_for_force_join(update.message.chat.id, reason)
    update.effective_message.reply_text("کەناڵی پەیوەستبوون بەناچاری گۆڕدرا. دڵنیابە کە من لەو کەناڵە بەڕێوەبەرم بۆ ئەوەی کارەکەم بە ڕێکی بەجێبهێنم.")


@run_async
def check_user(bot: Bot, update: Update):
	chat_id = str(update.message.chat.id)
	user_id = update.message.from_user.id
	user_full_name = update.message.from_user.full_name
	
	if is_user_admin(int(chat_id), user_id):
		return
	
	if not sql.force_channel_join_is_enabled(chat_id):
		return
	
	channel_id = "@" + sql.ENABLED_CHARS[chat_id]
	
	
	if is_user_in_chat(channel_id, user_id):
		return
	
	update.message.delete()
	
	mention = f'<a href="tg://user?id={user_id}">{user_full_name}</a>'
	
	message = """
بەڕێز {} دەبێت سەرەتا بچیتە ناو ئەم کەناڵە پێش قسەکردن لێرە:
{}
	""".format(mention, channel_id)
	reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("کەناڵەکە", url='http://t.me/{}'.format(channel_id.replace("@", "")))]])
	
	bot.send_message(chat_id=int(chat_id), text=message, reply_markup=reply_markup, parse_mode="HTML")




__help__ = """
 - 
"""

__mod_name__ = "FCJ"

SET_CHANNEL_FOR_FORCE_JOIN_HANDLER = CommandHandler("scffj", set_channel_for_force_join)
CHECK_IF_USER_IS_JOINED_THE_CHANNEL_HANDLER = MessageHandler(Filters.all & ~Filters.status_update & Filters.group, check_user)


dispatcher.add_handler(SET_CHANNEL_FOR_FORCE_JOIN_HANDLER)
dispatcher.add_handler(CHECK_IF_USER_IS_JOINED_THE_CHANNEL_HANDLER)
