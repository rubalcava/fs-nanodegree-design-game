#Full Stack Nanodegree - Game - Hangman


##Game Description:
Hangman is a game in with you try to uncover a word by guessing the letters in it. You get 8 guesses, and each incorrect guess takes you one step closer to the hangman! When you guess a letter correct, you will get a confirmation of "Nice!" and then that letter will be uncovered in the word. When all letters have been uncovered, the game has been won. If all guesses have been used before the word has been completely revealed, the game ends and you lose. Note: There is no guess penalty for retrying a letter that you've already tried, you will just be told that you've already tried it.

##How Scoring works
When a game is won, that game is given a score which is calculated by multiplying the number of guesses left by the length of the word. This was done so that users who are successful with longer, more difficult words would be rewarded accordingly. If a game is lost, ie all guesses are used but the word has not been completely uncovered, the user is given a game_score of 0.

The Scoreboard is simple, as it ranks the highest game scores.

User rankings are calculated by taking the sum of a user's game scores and dividing it by the total number of games they've played. This value is a user's user_score. If a user hasn't played any games yet, they will have a user_score of 0.

##How to Run:
This app is currently live at http://my-hangman-game.appspot.com
    - However, it is only an api, so going to this website will (correctly) tell you there is no page here.

To test with API Explorer, visit http://my-hangman-game.appspot.com/_ah/api/explorer

If you wish to run it in the development environment, please follow the next steps:

##Prerequisites for running in development mode
1. Google Cloud SDK for Python 2.7
2. Python 2.7

##Steps
1. Download this project's zip file, or clone it to anywhere on your local machine.

2. Fire up your terminal and navigate to the root project folder
    - It should be fs-nanodegree-design-game-master if downloaded
    - Or, fs-nanodegree-design-game if you cloned it

3. From within this folder, you should see a folder called "Hangman" and if so, you are in the right place.

4. Type the following in your terminal and press enter: dev_appserver.py Hangman

5. Fire up your chrome browser and navigate to http://localhost:8080/_ah/api/explorer
    - You will get a warning about the development server being served on http. To fix the underlying issue, at the right of the address bar in chrome, you will see a little shield icon next to the bookmark star. Click the shield and then click 'load unsafe scripts.' Don't worry, this is just because the development environment isn't served over https.

6. Play a game!

7. To view the development datastore, navigate chrome to http://localhost:8000/datastore

8. When you're done, head back to the terminal and type the following Ctrl+C

9. Thanks for trying my game out!




#API Information


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
