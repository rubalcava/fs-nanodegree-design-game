#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import HangmanApi
from models import Game, User

from models import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to users with active games.
        Called every 24 hours using a cron job"""
        app_id = "my-hangman-game"
        # Get active games
        active_games = Game.query(Game.game_over != True)
        users = []
        # Use the active games to get user keys to get the users
        for game in active_games:
            user = User.query(User.key == game.user).get()
            # If the user has an email, add the user object to users list
            if user not in users and user.email:
                users.append(user)
        if len(users) != 0:
            for user in users:
                subject = 'This is a reminder!'
                body = 'Hello {}, come back and finish playing ' \
                       'Hangman!'.format(user.name)
                print body
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        HangmanApi._cache_average_attempts()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
