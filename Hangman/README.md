#Full Stack Nanodegree - Game API - Hangman


##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists. Will raise a BadRequestException is no user_name is provided.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, min, max
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Min and Max correspond to the limits on the length of the random word that will be used for the game. Min must be less than max. Also adds a task to a task queue to update the average moves remaining
    for active games.

 - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name, email (optional)
    - Returns: UserGamesForm with active user games.
    - Description: Returns all of a user's active games. Will raise a NotFoundException if a user with the provided user_name does not exist.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/delete'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: DeleteGameForm with confirmation of game cancellation.
    - Description: Cancels a game that has not yet ended. If game has already ended, will return a message that the game is already over. Will raise NotFoundException if game is not found.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForm with history of moves made in a game.
    - Description: Returns all guesses made (in order), correct guesses made (in order), incorrect guesses made (in order), and current state of the game.

 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

 - **get_user_rankings**
    - Path: 'userrankings'
    - Method: GET
    - Parameters: None
    - Returns: MultiUserRankingForm
    - Description: Returns users ranked by proprietary ranking metric "user_score".

 - **get_high_scores**
    - Path: 'scoreboard'
    - Method: GET
    - Parameters: number_of_results (optional)
    - Returns: ScoreBoard
    - Description: Returns games ranked by proprietary ranking metric "game_score".

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **get_average_attempts**
    - Path: 'games/average_attempts'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.

##Forms Included:
 - **GameHistoryForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
   game_over flag, message, user_name).

 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).

 - **DeleteGameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
       game_over flag, message, user_name).

 - **UserGamesForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
          game_over flag, message, user_name).

 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)

 - **MakeMoveForm**
    - Inbound make move form (guess).

 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).

 - **ScoreForms**
    - Multiple ScoreForm container.

 - **ScoreBoard**
    - Multiple ScoreForm container, sorted by game_score.

 - **UserRankingForm**
    - Representation of a user ranking.

 - **MultiUserRankingForm**
    - Multiple UserRankingForm container.

 - **StringMessage**
    - General purpose String container.
