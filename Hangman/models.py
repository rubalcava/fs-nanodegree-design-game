"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

WORDS = open('words.txt').read().splitlines()

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    total_game_score = ndb.IntegerProperty(required=True, default=0)
    total_games_played = ndb.IntegerProperty(required=True, default=0)
    user_score = ndb.FloatProperty(required=True, default=0)

    def to_user_ranking_form(self):
        """Returns user info to ranking form"""

        return UserRankingForm(user_name=self.name,
                               total_game_score=self.total_game_score,
                               total_games_played=self.total_games_played,
                               user_score=self.user_score)


class Game(ndb.Model):
    """Game object"""
    target = ndb.StringProperty(required=True)
    obscured_target= ndb.StringProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=8)
    game_over = ndb.BooleanProperty(required=True, default=False)
    tried_letters_were_wrong = ndb.StringProperty(required=True)
    correct_letters = ndb.StringProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user, min, max):
        """Creates and returns a new game"""

        if max < min:
            raise ValueError('Maximum must be greater than minimum')

        # Use min and max to make a list of acceptable words
        acceptable_words = []
        for word in WORDS:
            if len(word) >= min and len(word)<=max:
                acceptable_words.append(word)

        word_to_use = random.choice(acceptable_words).lower()
        hidden_word = ''
        for letter in word_to_use:
            hidden_word = hidden_word + "$"

        game = Game(user=user,
                    target=word_to_use,
                    obscured_target=hidden_word,
                    tried_letters_were_wrong=" ",
                    correct_letters=" ",
                    game_over=False,
                    parent=user)

        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        return form

    def to_user_games_form(self):
        """Returns a UserGamesForm representation of the Game"""

        return GameForm(urlsafe_key=self.key.urlsafe(),
                        attempts_remaining=self.attempts_remaining,
                        game_over=self.game_over, message='Game in Progress',
                        user_name=self.user.get().name)


    def deleted_game_form(self, message):
        return DeleteGameForm(urlsafe_key=self.key.urlsafe(),
                              message=message)


    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()

        game_score = self.attempts_remaining * len(self.target)

        user = game.user.get()
        user.total_game_score = user.total_game_score + game_score
        user.total_games_played = user.total_games_played + 1

        user.user_score = (user.total_game_score/user.total_games_played)

        user.put()

        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      game_score=game_score)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    game_score = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), game_score=self.game_score)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)

class DeleteGameForm(messages.Message):
    """Form to report confirmation of deleted games"""
    urlsafe_key = messages.StringField(1, required=True)
    message = messages.StringField(2, required=True)


class UserGamesForm(messages.Message):
    """Form for outbound information about active user games"""
    games = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    min = messages.IntegerField(2, default=1)
    max = messages.IntegerField(3, default=10)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    game_score = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    scores = messages.MessageField(ScoreForm, 1, repeated=True)


class ScoreBoard(messages.Message):
    """Return high scores in descending order"""
    high_scores = messages.MessageField(ScoreForm, 1, repeated=True)


class UserRankingForm(messages.Message):
    """Form for returning user ranking"""
    user_name = messages.StringField(1, required=True)
    total_game_score = messages.IntegerField(2, required=True)
    total_games_played = messages.IntegerField(3, required=True)
    user_score = messages.FloatField(4, required=True)


class MultiUserRankingForm(messages.Message):
    """Form for returning multiple user ranking forms"""
    rankings = messages.MessageField(UserRankingForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
