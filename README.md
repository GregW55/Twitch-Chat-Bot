# InterStellarsBot
# InterStellarsBot is a Twitch bot designed to enhance viewer engagement by providing various interactive features, including a slot machine game, trivia questions, song requests, and leaderboards. The bot tracks viewers' watch time and rewards them with "stars" that they can use for various interactions and commands.

Features
Slot Machine Game
Viewers can gamble their stars using the !gamba command to play a slot machine game.

Trivia
Viewers can participate in trivia games using the !trivia command. Correct answers are rewarded with stars.

Song Requests
Viewers can request songs from Spotify using the !SR command.

Leaderboards
The bot provides leaderboards for the top viewers based on stars, watch time, and correct trivia answers using the !leaderboard command.

Viewing Time and Stars
The bot tracks viewers' watch time and rewards them with stars over time.

Installation
Clone the Repository:

git clone https://github.com/yourusername/InterStellarsBot.git
cd InterStellarsBot

Set Up Spotify API Credentials:
Create a new application in the Spotify Developer Dashboard and obtain your client ID, client secret, and redirect URI. Replace the placeholders in the code with your actual Spotify API credentials.

Configure Bot:
Update the bot's token, client secret, and initial channel in the Bot class initialization.

Run the Bot:

python bot.py
Configuration
Spotify API Credentials
Set your Spotify API credentials in the code:

S_CLIENT_ID = 'YOUR CLIENT ID'
S_CLIENT_SECRET = 'YOUR CLIENT SECRET'
REDIRECT_URI = 'http://localhost:8888/callback'
Twitch Bot Token and Client Secret
Set your Twitch bot's token and client secret in the code:

super().__init__(token='YOUR OAUTH TOKEN', client_secret='YOUR SECRET', prefix='!', initial_channels=['YOUR CHANNEL'])
Data Files
data.json: Stores viewers' watch time, stars, and correct trivia guesses.
category_id_map.json: Stores the ID map for trivia categories.

Commands
Slot Machine
!gamba <amount>: Gamble a specified amount of stars in the slot machine.

Trivia
!trivia <category>: Start a trivia game in the specified category.
!categories: List available trivia categories.
Answer the trivia question by typing the correct answer in the chat.

Song Requests
!SR <Spotify link>: Request a song from Spotify by providing a Spotify track link.

Leaderboards
!leaderboard stars: Show the top 5 users by stars.
!leaderboard time: Show the top 5 users by watch time.
!leaderboard trivia: Show the top 5 users by correct trivia answers.

General
!stars: Check the number of stars you have.
!commands: List available commands.

Additional Features and Planned Enhancements
Duel Events: Allow users to duel each other in mini-games.
Insults and Compliments: Randomly insult or compliment users with !insult or !compliment commands.
Polls: Create and vote on polls.
Quote Management: Add and retrieve quotes from the stream.
User Challenges: Challenge other users to mini-games.
Random Fact Generator: Generate random facts based on user input.
Achievements: Unlock achievements based on watch time and other metrics.
Interactive Commands: Trigger sound effects, display memes, or change overlays.
Shop and Redeem: Spend stars on various rewards and commands.
Loyalty Rewards: Recognize and reward loyal viewers with badges, special privileges, and commands.
