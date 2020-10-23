import html
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html

from tg_bot import dispatcher, LOGGER
from tg_bot.modules.helper_funcs.chat_status import bot_admin, user_admin, is_user_admin, can_restrict
from tg_bot.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from tg_bot.modules.helper_funcs.string_handling import extract_time
from tg_bot.modules.log_channel import loggable


@run_async
@bot_admin
@user_admin
@loggable
def mute(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("دەبێت ناوی بەکارهێنەری کەسێکم بدەیتێ، یان وەڵامی پەیامێکی بدەیتەوە بۆ ئەوەی بێدەنگیبکەم.")
        return ""

    if user_id == bot.id:
        message.reply_text("خۆم بێدەنگ ناکەم!")
        return ""

    member = chat.get_member(int(user_id))

    if member:
        if is_user_admin(chat, user_id, member=member):
            message.reply_text("ویی! من ناتوانم بەڕێوەبەرێک لە قسەکردن بێبەش بکەم!")

        elif member.can_send_messages is None or member.can_send_messages:
            bot.restrict_chat_member(chat.id, user_id, can_send_messages=False)
            message.reply_text("بێدەنگکرا!")
            return "<b>{}:</b>" \
                   "\n#بێدەنگکردن" \
                   "\n<b>بەڕێوەبەر:</b> {}" \
                   "\n<b>بەکارهێنەر:</b> {}".format(html.escape(chat.title),
                                              mention_html(user.id, user.first_name),
                                              mention_html(member.user.id, member.user.first_name))

        else:
            message.reply_text("خۆی هەر ناتوانێت قسەبکات!")
    else:
        message.reply_text("ئەم بەکارهێنەرە لەم چاتە نییە!")

    return ""


@run_async
@bot_admin
@user_admin
@loggable
def unmute(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("دەبێت ناوی بەکارهێنەری کەسێکم بدەیتێ، یان وەڵامی پەیامێکی بدەیتەوە بۆ ئەوەی مافی قسەکردنی پێبدەمەوە.")
        return ""

    member = chat.get_member(int(user_id))

    if member:
        if is_user_admin(chat, user_id, member=member):
            message.reply_text("ئەمە بەڕێوەبەرە، دەتەوێت چیی لێبکەم؟")
            return ""

        elif member.status != 'kicked' and member.status != 'left':
            if member.can_send_messages and member.can_send_media_messages \
                    and member.can_send_other_messages and member.can_add_web_page_previews:
                message.reply_text("ئەمە هەر خۆی مافی قسەکردنی هەیە.")
                return ""
            else:
                bot.restrict_chat_member(chat.id, int(user_id),
                                         can_send_messages=True,
                                         can_send_media_messages=True,
                                         can_send_other_messages=True,
                                         can_add_web_page_previews=True)
                message.reply_text("مافی قسەکردنی پێبەخشرایەوە!")
                return "<b>{}:</b>" \
                       "\n#لابردنی_بێدەنگی" \
                       "\n<b>بەڕێوەبەر:</b> {}" \
                       "\n<b>بەکارهێنەر:</b> {}".format(html.escape(chat.title),
                                                  mention_html(user.id, user.first_name),
                                                  mention_html(member.user.id, member.user.first_name))
    else:
        message.reply_text("ئەم بەکارهينەرە لەم چاتە نییە، بەخشینی مافی قسەکردن پێیان وایان لێناکات لە ئێستا "
                           "زیاتر قسەبکەن!")

    return ""


@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
def temp_mute(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("هیچ بەکارهێنەرێکت دیارینەکردووە.")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("ناتوانم ئەم بەکارهێنەرە بدۆزمەوە")
            return ""
        else:
            raise

    if is_user_admin(chat, user_id, member):
        message.reply_text("ئم... بەڕێوەبەرە.")
        return ""

    if user_id == bot.id:
        message.reply_text("بە خەو دەیبینی خۆم بێدەنگبکەم.")
        return ""

    if not reason:
        message.reply_text("کاتێکت دیارینەکردووە!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    mutetime = extract_time(message, time_val)

    if not mutetime:
        return ""

    log = "<b>{}:</b>" \
          "\n#بێدەنگکردنی_کاتی" \
          "\n<b>بەڕێوەبەر:</b> {}" \
          "\n<b>بەکارهێنەر:</b> {}" \
          "\n<b>کات:</b> {}".format(html.escape(chat.title), mention_html(user.id, user.first_name),
                                     mention_html(member.user.id, member.user.first_name), time_val)
    if reason:
        log += "\n<b>هۆکار:</b> {}".format(reason)

    try:
        if member.can_send_messages is None or member.can_send_messages:
            bot.restrict_chat_member(chat.id, user_id, until_date=mutetime, can_send_messages=False)
            message.reply_text("بێدەنگکرا بۆ {}!".format(time_val))
            return log
        else:
            message.reply_text("ئەمە هەر خۆی ناتوانێت قسەبکات.")

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("بێدەنگکرا بۆ {}!".format(time_val), quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR muting user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("ناتانم ئەو بەکارهێنەرە بێدەنگبکەم.")

    return ""


__help__ = """
*تەنها بەڕێوەبەر:*
 - /mute <userhandle>: بەکارهێنەرێک بێدەنگدەکات. بە وەڵامدانەوەش دەبێت، بێدەنگردنی ئەو بەکارهێنەرەی وەڵامت داوەتەوە.
 - /tmute <userhandle> x(m/h/d): بدکارهێنەر بێدەنگ دەکات بۆ x. (بە ناسنامەیەکی، یان وەڵامدانەوە). m = خولەک, h = کاتژمێر, d = ڕۆژ.
 - /unmute <userhandle>: بەکارهێنەرێک. بە وەڵامدانەوەش دەبێت، دانەوەی مافی قسەکردن بە ئەو بەکارهێنەرەی وەڵامت داوەتەوە.
"""

__mod_name__ = "Muting"

MUTE_HANDLER = CommandHandler("mute", mute, pass_args=True, filters=Filters.group)
UNMUTE_HANDLER = CommandHandler("unmute", unmute, pass_args=True, filters=Filters.group)
TEMPMUTE_HANDLER = CommandHandler(["tmute", "tempmute"], temp_mute, pass_args=True, filters=Filters.group)

dispatcher.add_handler(MUTE_HANDLER)
dispatcher.add_handler(UNMUTE_HANDLER)
dispatcher.add_handler(TEMPMUTE_HANDLER)
