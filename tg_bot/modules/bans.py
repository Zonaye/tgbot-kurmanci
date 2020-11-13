import html
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User
from telegram.error import BadRequest
from telegram.ext import run_async, CommandHandler, Filters
from telegram.utils.helpers import mention_html

from tg_bot import dispatcher, BAN_STICKER, LOGGER
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import bot_admin, user_admin, is_user_ban_protected, can_restrict, \
    is_user_admin, is_user_in_chat
from tg_bot.modules.helper_funcs.extraction import extract_user_and_text
from tg_bot.modules.helper_funcs.string_handling import extract_time
from tg_bot.modules.log_channel import loggable


@run_async
@bot_admin
@can_restrict
@user_admin
def ban(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("بەکارهێنەرێکت دیارینەکردووە.")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("ئەم بەکارهێنەرە نادۆزمەوە")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Birêvebir nayê qedexe kirin.")
        return ""

    if user_id == bot.id:
        message.reply_text("Nikarim xwe qedexe bikim.")
        return ""

                                              
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        #bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        message.reply_text("Hat qedexe kirin!")
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Hat qedexe kirin!', quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Min nekarî ew qedexe bikim.")

    return ""



@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
def kick(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("ئەم بەکارهێنەرە نادۆزمەوە")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id):
        message.reply_text("Birêvebir nayê qedexe kirin.")
        return ""

    if user_id == bot.id:
        message.reply_text("دەمم پیس مەکە، خۆم خۆم دەرناکەم!")
        return ""

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        message.reply_text("Hat der kirin!")
    else:
        message.reply_text("Min nekarî ew der bikim.")
    return ""


@run_async
@bot_admin
@can_restrict
def kickme(bot: Bot, update: Update):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Bi xwe derkeve birêvebir efendî.")
        return

    res = update.effective_chat.unban_member(user_id)
    if res:
        update.effective_message.reply_text("Keremke.")
    else:
        update.effective_message.reply_text("Nikarim.")


@run_async
@bot_admin
@can_restrict
@user_admin
def unban(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("ئەم بەکارهێنەرە نادۆزمەوە")
            return ""
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Bibore?")
        return ""

    if is_user_in_chat(chat, user_id):
        message.reply_text("Ew nehatiye qedexe kirin.")
        return ""

    chat.unban_member(user_id)
    message.reply_text("Temam! Niha dikare dîsa tevl bibe.")

    
                                                       member.user.id)
    
    return ""


__help__ = """
 - /kickme: kicks the user who issued the command

*Admin only:*
 - /ban <userhandle>: bans a user. (via handle, or reply)
 - /tban <userhandle> x(m/h/d): bans a user for x time. (via handle, or reply). m = minutes, h = hours, d = days.
 - /unban <userhandle>: unbans a user. (via handle, or reply)
 - /kick <userhandle>: kicks a user, (via handle, or reply)
"""

__mod_name__ = "Bans"

BAN_HANDLER = CommandHandler("ban", ban, pass_args=True, filters=Filters.group)
TEMPBAN_HANDLER = CommandHandler(["tban", "tempban"], temp_ban, pass_args=True, filters=Filters.group)
KICK_HANDLER = CommandHandler("kick", kick, pass_args=True, filters=Filters.group)
UNBAN_HANDLER = CommandHandler("unban", unban, pass_args=True, filters=Filters.group)
KICKME_HANDLER = DisableAbleCommandHandler("kickme", kickme, filters=Filters.group)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
