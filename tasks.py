import webapp2
import datetime
import os

from main import Snippet
from main import EXPIRE_SNIPPETS
from main import EXPIRATION_TIME_IN_DAYS

class CleanupHandler(webapp2.RequestHandler):
    def get(self):
        if EXPIRE_SNIPPETS == False:
            return
        now = datetime.datetime.now()
        query = Snippet.query()
        snippets = query.fetch()
        for snippet in snippets:
            age_in_days = (now - snippet.timestamp).days
            if (age_in_days >= EXPIRATION_TIME_IN_DAYS):
                snippet.key.delete()

application = webapp2.WSGIApplication([
    ('/tasks/cleanup', CleanupHandler),
    ], debug = True)
