import os
import binascii
from google.appengine.ext import ndb


class Token(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    endpoint_path = ndb.StringProperty()
    permissions = ndb.StringProperty(repeated=True)
    user = ndb.KeyProperty(kind='User')
    note = ndb.StringProperty()

    @classmethod
    def generate_key(cls):
        return ndb.Key(
            cls, binascii.hexlify(os.urandom(30)).decode()
        )

    def delete(self):
        self.key.delete()

    def __str__(self):
        return str(self.key.id())
