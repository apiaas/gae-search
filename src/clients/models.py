from google.appengine.ext import ndb

from util.models import BaseUser


class User(BaseUser):
    name = ndb.StringProperty(required=True)
    is_super_admin = ndb.BooleanProperty()

    def get_full_name(self):
        return unicode(self.name)

    def get_short_name(self):
        return unicode(self.name).split()[0]
