import threading

from sqlalchemy import Column, String

from tg_bot.modules.sql import BASE, SESSION


class Channel(BASE):
    __tablename__ = "chat_channels"

    chat_id = Column(String(100), primary_key=True)
    channel_id = Column(String(100))


Channel.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()

ENABLED_CHATS = {}

def force_channel_join_is_enabled(chat_id):
    return chat_id in ENABLED_CHATS


def set_channel_for_force_join(chat_id, channel_id):
    with INSERTION_LOCK:
        curr = SESSION.query(Channel).get(chat_id)
        if not curr:
            curr = Channel(chat_id, channel_id)
        else:
            curr.channel_id = channel_id

        ENABLED_CHATS[chat_id] = channel_id

        SESSION.add(curr)
        SESSION.commit()

def rm_force_channel_join(chat_id):
    with INSERTION_LOCK:
        curr = SESSION.query(Channel).get(chat_id)
        if curr:
            if chat_id in ENABLED_CHATS:  # sanity check
                del ENABLED_CHATS[chat_id]

            SESSION.delete(curr)
            SESSION.commit()
            return True

        SESSION.close()
        return False

def __load_enabled_chats():
    global ENABLED_CHATS
    try:
        all_enabled = SESSION.query(Channel).all()
        for chat in all_enabled:
        	ENABLED_CHATS[chat.chat_id] = chat.channel_id
    finally:
        SESSION.close()


__load_enabled_chats()
