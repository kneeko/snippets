import webapp2
import json
import sys
import os

from google.appengine.ext import ndb
from google.appengine.ext.db import stats
from idsentence import IdSentence
from idsentence import IntIdSentence
from rate_limit.lib import Limiter, QuotaKey

EXPIRE_SNIPPETS = os.environ['EXPIRE_SNIPPETS']
EXPIRATION_TIME_IN_DAYS = os.environ['EXPIRATION_TIME_IN_DAYS']
MAX_BYTES_PER_SNIPPET = os.environ['MAX_BYTES_PER_SNIPPET']
ALLOW_UUID_OVERRIDE = os.environ['ALLOW_UUID_OVERRIDE']
READS_PER_MINUTE = os.environ['READS_PER_MINUTE']
WRITES_PER_MINUTE = os.environ['WRITES_PER_MINUTE']
LISTS_PER_MINUTE = os.environ['LISTS_PER_MINUTE']

class Events:
    USER_READ = 1
    USER_WRITE = 2
    USER_LIST = 3

RATE_LIMIT_SPEC = {
    Events.USER_READ: (READS_PER_MINUTE, 60),
    Events.USER_WRITE: (WRITES_PER_MINUTE, 60),
    Events.USER_LIST: (LISTS_PER_MINUTE, 60),
}

limiter = Limiter(RATE_LIMIT_SPEC)
generator = IntIdSentence()

def uuid_is_unique(uuid):
    if uuid is None or uuid == 'list':
        return False
    query = Snippet.query(Snippet.uuid == uuid)
    if query.get() is None:
        return True
    return False

def generate_uuid():
    uuid = None
    while (uuid_is_unique(uuid) == False):
        generator.generate()
        sentence = generator.generate()
        uuid = sentence[1].replace(' ','-')
    return uuid

class Snippet(ndb.Model):
    uuid = ndb.StringProperty()
    data = ndb.TextProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

class SnippetHandler(webapp2.RequestHandler):
    def post(self, uuid):
        q = QuotaKey(self.request.remote_addr, Events.USER_WRITE)
        if limiter.CanSpend(q) == False:
            return self.error(500)
        data = self.request.body
        if data is None or data == '':
            return self.error(500)
        if sys.getsizeof(data) > MAX_BYTES_PER_SNIPPET:
            return self.error(500)
        if uuid is None or uuid == '':
            uuid = generate_uuid()
        elif uuid_is_unique(uuid) == False or ALLOW_UUID_OVERRIDE == False:
            return self.error(500)
        snippet = Snippet(uuid = uuid, data = data)
        snippet.put()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers.add_header('Access-Control-Allow-Origin', '*')
        self.response.out.write(uuid)

    def get(self, uuid):
        q = QuotaKey(self.request.remote_addr, Events.USER_READ)
        if limiter.CanSpend(q) == False:
            return self.error(500)
        if uuid is None:
            return self.error(404)
        query = Snippet.query(Snippet.uuid == uuid)
        snippet = query.get()
        if snippet is None:
            return self.error(404)
        try:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.headers.add_header('Access-Control-Allow-Origin', '*')
            self.response.out.write(snippet.data)
        except:
            return self.error(404)

    def options(self, uuid):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET'

class ListHandler(webapp2.RequestHandler):
    def get(self):
        q = QuotaKey(self.request.remote_addr, Events.USER_LIST)
        if limiter.CanSpend(q) == False:
            return self.error(500)
        query = Snippet.query()
        snippets = query.fetch()
        self.response.headers['Content-Type'] = 'text/plain'
        for snippet in snippets:
            self.response.out.write('%s\n' % (snippet.uuid))

application = webapp2.WSGIApplication([
    ('/list', ListHandler),
    ('/([^\s]*)', SnippetHandler)])
