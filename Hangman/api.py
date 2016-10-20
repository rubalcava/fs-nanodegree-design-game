# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, UserGamesForm
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='hangman', version='v1')
class HangmanApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key, request.min, request.max)
        except ValueError:
            raise endpoints.BadRequestException('Maximum must be greater '
                                                'than minimum!')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Hangman!')

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=UserGamesForm,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all active games for a user"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(ancestor=user.key).filter(Game.game_over != True)

        return UserGamesForm(games=[game.to_user_games_form() for game in games])


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        is_game_over = game.game_over

        if is_game_over:
            return game.to_form('Game Over!')
        elif not is_game_over:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        # Temporary lists
        answer_as_list = list(game.target)
        hidden_answer_as_list = list(game.obscured_target)
        # Pull properties into local variables to reduce ndb reads
        tried_letters = game.tried_letters_were_wrong

        # Game is already over, no need to do anything but let the user know
        if game.game_over:
            return game.to_form('Game already over!')

        # Check if guess is 1 character long
        if len(request.guess) == 1:
            # Once we know that guess is correct length, check if its a letter
            if request.guess.isalpha():
                # Check if guess is in word, and if it's already been found
                if request.guess in game.target and request.guess not in game.obscured_target:
                    for index in range(len(answer_as_list)):
                        if answer_as_list[index] == request.guess:
                            hidden_answer_as_list[index] = request.guess
                    # Update game property with found letter
                    game.obscured_target = ''.join(hidden_answer_as_list)

                    # Since $ is not a letter, we can safely say that if there is a $ char
                    # in the current game, the game is ongoing. If not, it's over.
                    if "$" not in game.obscured_target:
                        game.end_game(True)
                        return game.to_form('You win!')
                    else:
                        # Update game entity and give user updated word status
                        game.put()
                        return game.to_form('Nice! This is what you have left: %s' % game.obscured_target)
                # Let user know they already found letter. No attempt penalty.
                elif request.guess in game.obscured_target:
                    return game.to_form('You already got that letter! This is what you have left: %s' % game.obscured_target)
                # Let user know they already tried letter. No attempt penalty.
                elif request.guess in tried_letters:
                    return game.to_form('You already tried that letter! This is what you have left: %s' % game.obscured_target)
                # Guess wrong, reduce tries left, add guess to string of tries
                else:
                    game.tried_letters_were_wrong = tried_letters + request.guess
                    game.attempts_remaining -= 1
                # Is game over? Let's check.
                if game.attempts_remaining < 1:
                    game.end_game(False)
                    return game.to_form('Game over!')
                # Update game entity, let user know guess wrong.
                else:
                    game.put()
                    return game.to_form('Try again! This is what you have left: %s' % game.obscured_target)
            else:
                return game.to_form('Letters only!')
        else:
            return game.to_form('Valid guesses are one letter only!')

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                        for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([HangmanApi])
