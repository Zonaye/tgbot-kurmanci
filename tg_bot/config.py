from tg_bot.sample_config import Config


class Development(Config):
    OWNER_ID = 951435494  # my telegram ID
    OWNER_USERNAME = "su_Theta"  # my telegram username
    API_KEY = "1334224865:AAH0efEPDzvOR7B941mdnVPvnGsiUIfAiPo"  # my api key, as provided by the botfather
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pass@localhost:5432/tgbot'  # sample db credentials
    MESSAGE_DUMP = '-1234567890' # some group chat that your bot is a member of
    USE_MESSAGE_DUMP = False
    SUDO_USERS = [951435494]  # List of id's for users which have sudo access to the bot.
    LOAD = []
    NO_LOAD = ['translation']
