from datetime import datetime

from tinydb import TinyDB
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization import Serializer


class DateTimeSerializer(Serializer):
    # The class this serializer handles
    OBJ_CLASS = datetime

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


class TinyDBDal():
    def __init__(self):
        self.serialization = SerializationMiddleware()
        self.serialization.register_serializer(
            DateTimeSerializer(), 'TinyDate')
        self.db = TinyDB('db.json', storage=self.serialization)
        self.pastes = self.db.table('pastes')
        self.settings = self.db.table('settings')

    def insert_new_paste(self, paste):
        self.pastes.insert(paste)

    def get_last_crawl_date(self):
        settings = self.settings.all()
        return settings and settings[0].get('last_crawl_date')

    def update_last_crawl_date(self, date):
        if not self.get_last_crawl_date():
            self.settings.insert({'last_crawl_date': date})
        else:
            self.settings.update({'last_crawl_date': date})
