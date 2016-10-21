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
