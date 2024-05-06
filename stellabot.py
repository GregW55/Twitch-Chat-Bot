import os
import json
import random
from twitchio.ext import commands
import twitchio
import asyncio
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

#
# Spotify api credentials
S_CLIENT_ID = 'YOUR CLIENT ID
S_CLIENT_SECRET = 'YOUR CLIENT SECRET'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-modify-playback-state user-read-currently-playing'
#s_username = 'YOUR USERNAME'

# Create Spotipy object with SpotifyOAuth
sp_oauth = SpotifyOAuth(client_id=S_CLIENT_ID,
                        client_secret=S_CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)
'''username=s_username,'''


sp = spotipy.Spotify(auth_manager=sp_oauth)


#
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token='YOUR OAUTH TOKEN', client_secret='YOUR SECRET', prefix='!', initial_channels=['YOUR CHANNEL'])
        self.slot_machine = SlotMachine()  # Initialize the slot machine class
        self.trivia = Trivia()  # Initialize the trivia class
        if os.path.exists('data.json'):  # Check if data file exists
            with open('data.json', 'r') as file:  # Open data file
                data = json.load(file)
                self.stars = data.get("stars", {})  # Set self.stars = to stars inside data file
                self.view_time = data.get("view_time", {})  # Set self.viewtime to view time inside data file
                self.trivia_correct_guesses = data.get("correct_guesses", {})  # Initialize and get the data from file
        else:
            self.stars = {}  # Dictionary to store stars for each user
            self.view_time = {}  # Dictionary to store view time for each user
            self.trivia_correct_guesses = {}
        self.tasks = {}  # Dictionary to store tasks for each user
        self.trivia_answer = ""
        self.b_commands = [
            '!trivia',
            '!categories',
            '!gamba',
            '!SR(costs 1000 stars)',
            '!leaderboard',
            '!stars',
            '!dire'
        ]
        self.achieve = False

    async def event_message(self, message) -> None:
        try:
            # Respond to commands
            if message.author is None:
                return
            # Make !viewtime
            author = message.author.name  # Set author = to channels username

            if message.content.startswith('!gamba'):
                # Split the message content by space to extract the amount
                parts = message.content.split(maxsplit=1)
                if len(parts) == 2:
                    # Second part should be the amount
                    amount_str = parts[1]
                    amount_str = ''.join(filter(str.isdigit, amount_str))  # Keep only digits
                    if amount_str.isdigit():
                        amount = int(amount_str)
                        if amount > 0:
                            if amount <= self.stars[author]:
                                # Proceed with the slots game
                                # You can call your deposit function or perform other actions here
                                # For now, just print the amount
                                self.stars[author] -= amount
                                result = self.slot_machine.spin(amount)
                                winnings = result['winnings']
                                if winnings == -10000 * amount:   # Check if user got scammed
                                    symbols_flat = [symbol for column in result['symbols'] for symbol in column]
                                    symbols_str = ' | '.join(symbols_flat)
                                    self.stars[author] += winnings
                                    self.save_data()
                                    await message.channel.send(
                                        f"Symbols:       {symbols_str} {author} Got scammed and now has {self.stars[author]}: stars! Nerdge")
                                    return
                                self.stars[author] += winnings
                                self.save_data()
                                if winnings > 0:
                                    # Flatten the slots list and remove the brackets and quotation marks
                                    symbols_flat = [symbol for column in result['symbols'] for symbol in column]
                                    symbols_str = ' | '.join(symbols_flat)
                                    await message.channel.send(
                                        f"Symbols:        {symbols_str} Congratulations {author}, you won {result['winnings']} stars!")
                                else:
                                    # Flatten the slots list and remove the brackets and quotation marks
                                    symbols_flat = [symbol for column in result['symbols'] for symbol in column]
                                    symbols_str = ' | '.join(symbols_flat)
                                    await message.channel.send(
                                        f"Symbols:       {symbols_str} {author} lost Better luck next time!")
                            else:
                                await message.channel.send(f"{author}, You don't have enough stars!")
                        else:
                            await message.channel.send(f"{author}, Amount must be greater than 0.")
                    else:
                        await message.channel.send(f"{author}, Please enter a valid number.")
                else:
                    await message.channel.send(f"{author}Usage: !gamba <amount>")

            # Print how many stars someone has
            if message.content.startswith('!stars'):
                if message.author.name in self.stars:
                    stars = round(self.stars[author])
                    await message.channel.send(f'{author}, you currently have:  {stars}, stars!')
                else:
                    await message.channel.send(f'{author}, you currently have 0 stars :*(')

            if message.content.startswith('!leaderboard'):
                if message.content.startswith('!leaderboard stars'):
                    # Sort users by stars in descending order
                    sorted_users = sorted(self.stars.items(), key=lambda x: x[1], reverse=True)
                    # Filter out users you don't want in the list
                    sorted_users = [(user, stars) for user, stars in sorted_users if user != 'interstellar_ow']
                    # Take the top 5 users
                    top_5_stars = sorted_users[:5]
                    # Format the leaderboard message
                    leaderboard_message = ""
                    for idx, (user, stars) in enumerate(top_5_stars, start=1):
                        stars = round(stars)  # Round stars to nearest integer
                        leaderboard_message += f"{idx}. {user}: {stars} stars "
                    # Send leaderboard message
                    await message.channel.send(leaderboard_message)
                elif message.content.startswith('!leaderboard time'):
                    # Sort users by view time in descending order
                    sorted_users = sorted(self.view_time.items(), key=lambda x: x[1], reverse=True)
                    # Filter out users you dont want in the list
                    sorted_users = [(user, view_time) for user, view_time in sorted_users if user != 'interstellar_ow']
                    # Take the top 5 users
                    top_5_view_time = sorted_users[:5]
                    # Format the leaderboard message
                    leaderboard_message = ""
                    for idx, (user, view_time) in enumerate(top_5_view_time, start=1):
                        # Round viewtime to nearest integer
                        view_time = round(view_time)
                        minutes_watched = view_time / 60
                        minutes_watched = round(minutes_watched)
                        leaderboard_message += f'{idx}. {user}: {minutes_watched} minutes watched '
                    # Send leaderboard message
                    await message.channel.send(leaderboard_message)
                elif message.content.startswith('!leaderboard trivia'):
                    # Sort users by correct guesses in descending order
                    correct_guesses = self.trivia_correct_guesses
                    sorted_users = sorted(self.trivia_correct_guesses.items(), key=lambda x: x[1], reverse=True)
                    sorted_users = [(user, correct_guesses) for user, correct_guesses in sorted_users if user != 'interstellar_ow' and correct_guesses > 0]
                    top_5_trivia = sorted_users[:5]
                    leaderboard_message = ""
                    for idx, (user, correct_guesses) in enumerate(top_5_trivia, start=1):
                        leaderboard_message += f'{idx}. {user}: {correct_guesses} Correct Answers '
                    await message.channel.send(leaderboard_message)
                else:
                    await message.channel.send(f'{author}, Usage: !leaderboard <stars> or <time>')

            if message.content.startswith('!trivia'):
                # Split the message content by space to extract the amount
                if self.trivia_answer == "":
                    parts = message.content.split(maxsplit=1)
                    if len(parts) == 2:
                        # Second part should be the amount
                        category_name = parts[1]
                        category_id = self.trivia.get_category_id(category_name)
                        print(category_id)
                        question_data = self.trivia.get_question(category_id)
                        print(question_data)
                        if question_data:
                            question = question_data['question']
                            answers = question_data['incorrect_answers']
                            correct_answer = question_data['correct_answer']
                            self.trivia_answer = correct_answer
                            # You can format the question and send it to the chat
                            # Potentially add answers to the message
                            # You can also shuffle the answers so they're not always in the same order
                            all_answers = answers + [correct_answer]
                            random.shuffle(all_answers)
                            '''# Send all the answers to the chat
                            await message.channel.send(f"Options: {' | '.join(all_answers)}")
                            return correct_answer'''
                            await message.channel.send(f"Category: {category_name}, Question: {question}")
                        else:
                            await message.channel.send("Sorry, I couldn't retrieve a question for you!")
                    else:
                        await message.channel.send(f'{author}, Usage: !trivia <category>')
                else:
                    await message.channel.send(f'{author}, Please finish the current trivia question!')

            if message.content.lower() == self.trivia_answer.lower():
                self.stars[author] += 250
                self.trivia_correct_guesses[author] += 1
                await message.channel.send(
                    f"Congratulations! {author} guessed the right answer: {self.trivia_answer} and has won 250 stars! "
                    f"Correct guesses: {self.trivia_correct_guesses[author]}")
                self.trivia_answer = ""

            if message.content.startswith('!categories'):
                '''categories = self.trivia.get_key_map()
                categories_string = ', '.join(categories)'''
                await message.channel.send('Trivia Categories: 1: General Knowledge, 2: Entertainment, 3: Science, '
                                           '4: Mythology, 5: Sports, 6: Geography, 7: History, 8: Politics, '
                                           '9: Art, 10: Celebrities, 11: Animals, 12: Vehicles')

            if message.content.startswith('!SR') or message.content.startswith('!sr'):
                user_stars = round(self.stars[author])
                if self.stars[author] >= 100:
                    parts = message.content.split(maxsplit=1)
                    if len(parts) == 2:
                        # Second part should be the song
                        song = parts[1]
                        if song.startswith('https://open.spotify.com/track/'):
                            # Add track to queue
                            self.stars[author] -= 100
                            track_uri = song  # Example track URI
                            sp.add_to_queue(uri=track_uri)
                            await message.channel.send(f'{author}, has queued a song and now has {user_stars}')
                        else:
                            await message.channel.send(f'{author}, Make sure you are sending a spotify link!')
                    else:
                        await message.channel.send(f'{author}, Usage: !SR <spotify share link>')
                else:

                    await message.channel.send(f'{author}, You currently have {user_stars} out of 100 stars!')

            '''if message.content == '!song':
                try:
                    # Get current playback information from spotify
                    current_playback = sp.current_playback()
                    # Check if a song is playing
                    if current_playback is not None and 'item' in current_playback:
                        # Extract relevant information from the current playback
                        current_track = current_playback['item']['name']
                        current_artist = current_playback['item']['artists'][0]['name']
                        current_album = current_playback['item']['album']['name']
                        await message.channel.send(f'{author}, The current song is {current_track} by {current_artist} on '
                                                   f'the {current_album} album')
                except Exception as e:
                    print("Error getting current playback information:", e)
                    await message.channel.send(
                        f'{author}, An error occurred while fetching current playback information. Please try again later.')'''

            if message.content.lower() == '!commands':
                commands_list = ', '.join(self.b_commands)
                await message.channel.send(f'Available commands: {commands_list}')

            for user in self.view_time:
                if 360000 <= self.view_time[user] < 36060:  # If viewtime > 360000
                    await message.channel.send(f'{user} has earned VIP status for watching over 100 hours!')

        except Exception as e:
            print("Error in event_message", e)

    async def update_viewing_time(self, user):
        # Update viewing time, and stars for each user
        while True:
            stars_per_second = 0.0833  # Increment stars by 5 every 60 seconds
            if user in self.view_time:
                self.view_time[user] += 1  # Increment viewing time by 1 second
            if user in self.stars:
                self.stars[user] += stars_per_second
            self.save_data()
            await asyncio.sleep(1)  # Update viewing time every second

    async def event_join(self, channel, user):
        print(f'{user.name} has joined the chat.')
        # Filter out bots
        if user.name == '8hvdes' or user.name == '8roe':
            return
        if user.name == 'streamlabs' or user.name == 'interstellarsbot':
            return
        if user.name == 'd0nk7' or user.name == 'drapsnatt':
            return
        if user.name == '00_ava' or user.name == '00_darla':
            return
        if user.name == 'regressz' or user.name == 'asmr_miyu':
            return
        if user.name == '0__sophia' or user.name == '0_lonely_egirl':
            return
        if user.name == '00_aaliyah' or user.name == 'psh_aa':
            return
        if user.name == 'tarsai' or user.name == 'vlmercy':
            return
        if user.name == 'kksnejejeb' or user.name == 'yosharpia':
            return

        if user.name not in self.stars:  # Add username to stars dictionary if not already inside
            self.stars[user.name] = 0
        if user.name not in self.view_time:  # Add username to view time dictionary if not already inside
            self.view_time[user.name] = 0
        if user.name not in self.trivia_correct_guesses:
            self.trivia_correct_guesses[user.name] = 0
        task = self.loop.create_task(self.update_viewing_time(user.name))
        self.tasks[user.name] = task

    async def event_part(self, user):
        print(f'{user.name} has left the chat.')
        # Cancel the task for the user if it exists
        if user.name in self.tasks:
            self.tasks[user.name].cancel()
            del self.tasks[user.name]

    def save_data(self):
        data = {"stars": self.stars, "view_time": self.view_time, "correct_guesses": self.trivia_correct_guesses}
        try:
            with open('data.json', 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print("Error saving data to JSON file:", e)

    async def event_ready(self):
        print(f'InterStellarsBot is Online!')


class SlotMachine:
    def __init__(self):
        self.lines = 1
        self.max_lines = 1
        self.max_bet = 100
        self.min_bet = 1
        self.rows = 1
        self.cols = 3
        self.symbol_count = {
            "peepoDJ": 6,
            "KirikoGasm": 6,
            "COCKA": 9,
            "BUSSERS": 9,
            "AYO": 9,
            "SCAMMED": 3,
            "PogOff": 3,
        }
        self.symbol_value = {
            "peepoDJ": 100,
            "KirikoGasm": 200,
            "COCKA": 200,
            "BUSSERS": 250,
            "AYO": 300,
            "SCAMMED": -10000,
            "PogOff": 10000,
        }

    def check_winnings(self, columns, lines, bet, values):
        winnings = 0
        winning_lines = []
        for line in range(lines):
            symbol = columns[0][line]
            for column in columns:
                symbol_to_check = column[line]
                if symbol != symbol_to_check:
                    break
            else:
                winning_lines.append(line + 1)  # Append the winning line
                if values[symbol] == -10000:
                    winnings -= bet * 10000  # Subtract 10k times their bet
                else:
                    winnings += values[symbol] * bet  # Increment winnings based on symbol value
        return winnings, winning_lines

    def get_slot_machine_spin(self, rows, cols, symbols):
        all_symbols = []
        for symbol, symbol_count in symbols.items():
            for _ in range(symbol_count):
                all_symbols.append(symbol)
        columns = []
        for _ in range(cols):
            column = []
            current_symbols = all_symbols[:]
            for _ in range(rows):
                value = random.choice(current_symbols)
                current_symbols.remove(value)
                column.append(value)  # Append the symbol to the column
            columns.append(column)  # Append the column to the list of columns
        return columns

    def print_slot_machine(self, columns):
        for row in range(len(columns[0])):
            for i, column in enumerate(columns):
                if i != len(columns) - 1:
                    print(column[row], end="|")
                else:
                    print(column[row], end="")
            print()

    '''def deposit():
        while True:
            amount = input("What would you like to deposit? $")
            if amount.isdigit():  # determine if amount is a valid digit(a number that is positive)
                amount = int(amount)  # covert to an integer
                if amount > 0:
                    break  # if amount more than 0$, break the while loop
                else:
                    print("Amount must be greater than 0.")
            else:
                print("Please enter a number.")
        return amount'''

    def get_bet(self):
        while True:
            amount = input("What would you like to bet on each line? $")
            if amount.isdigit():  # determine if amount is a valid digit(a number that is positive)
                amount = int(amount)  # covert to an integer
                if self.min_bet <= amount <= self.max_bet:
                    break  # if amount more than 0$, break the while loop
                else:
                    print(f"Amount must be between ${self.min_bet} - ${self.max_bet}.")
            else:
                print("Please enter a number.")
        return amount

    def spin(self, amount):
        lines = self.lines
        bet = amount
        slots = self.get_slot_machine_spin(self.rows, self.cols, self.symbol_count)
        self.print_slot_machine(slots)
        winnings, winnings_lines = self.check_winnings(slots, lines, bet, self.symbol_value)
        outcome = "win" if winnings > 0 else "loss"
        return {'winnings': winnings, 'outcome': outcome, 'symbols': slots}


class Trivia:
    def __init__(self):
        self.trivia_category_id = 'https://opentdb.com/api_category.php'
        if os.path.exists('category_id_map.json'):  # Check if data file exists
            with open('category_id_map.json', 'r') as file:  # Open data file
                data = json.load(file)
                self.category_id_map = data if isinstance(data, dict) else {}

    def get_question(self, category_id):
        trivia_base_url = f'https://opentdb.com/api.php?amount=10&category={category_id}'
        # Use the Open Trivia Database API to get a random question based on the category
        response = requests.get(trivia_base_url)
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
            print(data['response_code'])
            if data['response_code'] == 0:
                return data['results'][0]  # Return a single random question
        return None

    def get_category_id(self, category_name):
        if category_name in self.category_id_map:
            category_id = self.category_id_map[category_name]
            return category_id
        if category_name == "science":
            science_id = ['17', '18', '19', '29']
            category_id = random.choice(science_id)
            return category_id
        if category_name == 'entertainment':
            entertainment_id = ['10', '11', '12', '13', '14', '15', '16', '29', '31', '32']
            category_id = random.choice(entertainment_id)
            return category_id



    '''def get_category_id(self, category_name):
        response = requests.get(self.trivia_category_id)
        category_data = response.json()
        print(category_data['trivia_categories'])
        if 'trivia_categories' in category_data:
            categories = category_data['trivia_categories']
            for category in categories:
                category_id = category['id']
                print(category_id)
                name = category['name']
                self.category_id_map[name] = category_id
            self.save_category_id_map()'''

    def save_category_id_map(self):
        # Load existing data from the JSON file
        try:
            with open('category_id_map.json', 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = {}

        # Update the existing data with new values
        existing_data.update(self.category_id_map)

        # Check if the new data is different from the existing data
        if existing_data != self.category_id_map:
            # Save the updated data back to the JSON file
            with open('category_id_map.json', 'w') as file:
                json.dump(existing_data, file, indent=4)
        else:
            print("No new data to save.")

    def get_key_map(self):
        key_map = list(self.category_id_map.keys())
        return key_map


bot = Bot()
bot.run()
# Add a trivia function(Complete)
# Add a song request / current song function (Song Request Completed) (Maybe put a cd on it)
# Add a !commands (Complete)
# Add some sort of !duel event between to users
# Add some sort of funny !insult or ! compliment where the user gets insulted or complimented
# Add a poll function (and in event message function add a way to vote onto the pull)
# Add a !quote function to pull random funny quotes from stream over time (need to add some way to store the quotes)
# Add a !quoteadd <quote> function where moderators can add quotes
# Add a challenge user function where a user can challenge another user to a mini game(maybe build the duel into this)
# Add a random fact generator based on the users input (if the user types !fact frog get frog facts for example)
# Add a function !challengebot to start an event where users play against the bot in a minigame
# Add a !achievements [name] [description], where users can unlock certain things for view time etc
# (maybe minigames or commands or VIP status)
# Interactive Commands: Incorporate commands that allow viewers to interact with the stream,
# such as triggering sound effects, displaying memes or gifs on the screen, or changing overlays.
# Create commands that allow viewers to vote on certain decisions or outcomes during gameplay.
# !redeem and !shop to allow users to spend star points on things like picking a game, vod reviews etc
# Maybe buy commands and then that user can use the command for the bot to do something
#  viewers can earn, spend, trade, or gamble virtual currency within the stream
# Implement features that recognize and reward loyal viewers,
# such as leaderboards, badges, or special privileges for long-time subscribers or active community members.
# Add a view time limit to certain commands: (I.E. 1000 hours of view time and you get certain command)
