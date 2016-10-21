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
                               user_score=self.user_score)


class Game(ndb.Model):
    """Game object"""
    target = ndb.StringProperty(required=True)
    obscured_target= ndb.StringProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=8)
    game_over = ndb.BooleanProperty(required=True, default=False)
    tried_letters_were_wrong = ndb.StringProperty(required=True)
    correct_letters = ndb.StringProperty(required=True)
    all_guesses = ndb.StringProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user, min, max):
        """Creates and returns a new game"""

        if max < min:
            raise ValueError('Maximum must be greater than minimum')

        # Use min and max to make a list of acceptable words
        # from a dictionary file
        acceptable_words = []
        for word in WORDS:
            if len(word) >= min and len(word)<=max:
                acceptable_words.append(word)

        # Make the word lower case
        word_to_use = random.choice(acceptable_words).lower()
        hidden_word = ''
        # Make a copy of the word with letters obscured
        for letter in word_to_use:
            hidden_word = hidden_word + "$"

        game = Game(user=user,
                    target=word_to_use,
                    obscured_target=hidden_word,
                    tried_letters_were_wrong="",
                    correct_letters="",
                    all_guesses="",
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

    def to_game_history_form(self):
        """Returns a form representation of the history of a game"""

        formatted_all_letters = "Order of guesses: "
        formatted_correct_letters = "Order of correct guesses: "
        formatted_wrong_letters = "Order of incorrect guesses: "

        correct_list = list(self.correct_letters)
        wrong_list = list(self.tried_letters_were_wrong)
        all_list = list(self.all_guesses)

        # Make formatted strings for all, good, bad guesses
        for idx, val in enumerate(all_list):
            if (idx + 1) == len(all_list):
                formatted_all_letters = formatted_all_letters + \
                                            ("%s: %s" % ((idx+1), val))
            else:
                formatted_all_letters = formatted_all_letters + \
                                            ("%s: %s, " % ((idx+1), val))

        for idx, val in enumerate(correct_list):
            if (idx + 1) == len(correct_list):
                formatted_correct_letters = formatted_correct_letters + \
                                            ("%s: %s" % ((idx+1), val))
            else:
                formatted_correct_letters = formatted_correct_letters + \
                                            ("%s: %s, " % ((idx+1), val))

        for idx, val in enumerate(wrong_list):
            if (idx + 1) == len(wrong_list):
                formatted_wrong_letters = formatted_wrong_letters + \
                                          ("%s: %s" % ((idx+1), val))
            else:
                formatted_wrong_letters = formatted_wrong_letters + \
                                          ("%s: %s, " % ((idx+1), val))

        return GameHistoryForm(urlsafe_key=self.key.urlsafe(),
                               attempts_remaining=self.attempts_remaining,
                               game_over=self.game_over,
                               user_name=self.user.get().name,
                               correct_moves=formatted_correct_letters,
                               wrong_moves=formatted_wrong_letters,
                               all_moves=formatted_all_letters,
                               last_game_state=self.obscured_target)



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

        # Give game score
        if won is True:
            game_score = self.attempts_remaining * len(self.target)
        else:
            game_score = 0

        # Add game score and game to user properties
        user = self.user.get()
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

class GameHistoryForm(messages.Message):
    """Form for displaying game history"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    user_name = messages.StringField(4, required=True)
    correct_moves = messages.StringField(5, required=True)
    wrong_moves = messages.StringField(6, required=True)
    all_moves = messages.StringField(7, required=True)
    last_game_state = messages.StringField(8, required=True)

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
    user_score = messages.FloatField(4, required=True)


class MultiUserRankingForm(messages.Message):
    """Form for returning multiple user ranking forms"""
    rankings = messages.MessageField(UserRankingForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
