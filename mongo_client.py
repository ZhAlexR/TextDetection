from pymongo import MongoClient

from settings import settings

class SingletonBase:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

class BotMongoClient(SingletonBase):

    def __init__(self):
        self.client = MongoClient(settings.MONGO_URL)

    @property
    def nutri_base(self):
        return self.client[settings.DATA_BASE_NAME]


bot_mongo_client = BotMongoClient().nutri_base
