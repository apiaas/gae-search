from google.appengine.ext import ndb

from util.models import BaseModel


class Endpoint(BaseModel):
    properties = ndb.TextProperty()


class Data(ndb.Expando):
    pass
