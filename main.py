"""
Ari's Test Bot for learning the Discord API
"""
import discord                     # Discord API
from replit import db; import os   # For Replit
import requests, json              # For get_quote()
import random, math, re, sys       # General use modules
import time
from keep_alive import keep_alive  # For pinging the bot
try: from TOKEN import TOKEN       # Private token for use outside of replit
except ImportError: TOKEN = None; pass
"""ASSIGNMENTS"""
# Just a shorthand assignment
client = discord.Client()
# db assignment if not using db from Replit, tbh it should prolly be a class but idk how Replit's db works so its a dict (also the class syntax is still confusing to me, which I know is only all the more reason to use a class to learn it better, but eh, maybe later)
is_replit = True
if db is None: db = {}; is_replit = False


"""FUNCTIONS"""
def get_quote():  # Returns a random quote from ZenQuotes
    response = requests.get("https://zenquotes.io/api/random")  # snag a quote from this api, it will be in json
    json_data = json.loads(response.text)                       # just need to unpack it into a string, though,
    quote = f"> \"{json_data[0]['q']}\"\n- {json_data[0]['a']}" # even the tutorial said it was a guess how this works
    return quote

def get_random_curse_word():
    if Curse.count > 0:
        return random.choice(Curse.word_strings)
    return "I don't know any curse words!"

# sets values in database (am I accidentally reinventing a class in this dict lol? bc this is def a setter)
def update_database(key_name, entry, check_by=None, is_dict=False, is_non_iterable=False): #fuckin spaghetti
    """ Checks if 'target_list' exists yet in the db, and is a list, if it doesn't exist, adds it as a list containing
        'entry' only. Otherwise, checks if 'entry' is already in the list, (or if the corresponding index
         of it is). If it is not, 'entry' is appended.
    :param is_non_iterable: To be implemented
    :param key_name: key to the list in the db to be updated, expected string, but only must reference a list
    :param entry: entry to append to the list in the db
    :param check_by: optional param, if given, entry will be treated as existing only if the check_by index matched db,
                     meant for entries that are tuples or lists themselves.
    :param is_dict: optional param, if true, entry should be a dict with one key/value pair, and will be compared by key
                    db will also be instantiated as a dict
    :return: False for if the database was not updated, or an error was found before it could be.
             True if it was, and either a new list was added to the db, or an entry was appended to the list in the db.
    """  #                                                                                                              (This description may be too long, but this is still complicated to me, so It seems like itd be helpful until I'm more experienced)
    if key_name in db.keys():
        if is_non_iterable:
            db[key_name] = entry
        temp_list = db[key_name]
        if is_dict is False and type(temp_list) != list:
            # print("Could not update value! Target value is not a list; returning False")
            return False
        if is_dict:
            check = list(entry.keys())[0]
            check_list = list(temp_list.keys())
        elif check_by is not None:
            try:
                # print(f"(True: comparing by Index {check_by}) ", end='')
                check, check_list = entry[check_by], [value[check_by] for value in temp_list]
            except IndexError:
                # print("\nINDEX OUT OF RANGE ERROR, revise check_by or db/entry values\n")
                return False
        else:
            # print("(False: comparing by Whole Tuple) ", end='')
            check, check_list = entry, temp_list
        # print(f"check is:'{check}' and check_list is:'{check_list}'")
        if check not in check_list:
            if is_dict:
                db[key_name][list(entry.keys())[0]] = list(entry.values())[0]
                print(f"Added K/V pair:'{entry}' to '{key_name}'; returning True")
                return True
            temp_list.append(entry)
            db[key_name] = temp_list
            # print(db)
            # print(f"Added Entry:'{entry}' entry to '{key_name}'; returning True")
            return True
        else:
            # print(f"Entry:'{entry}' is already in '{key_name}'; returning False")
            return False
    else:
        if is_dict:
            db[key_name] = {}
            db[key_name] = entry
        else:
            db[key_name] = []
            db[key_name].append(entry)
        # print(db)
        print(f"Added New Key/Value Pair to db: key is '{key_name}' and value is a list/dict containing a single"
              f" entry '{entry}'; returning True")
        return True


def get_from_db(key):
    try:
        value = db[key]
        return value
    except KeyError:
        return None


def get_current_memory():
    if len(list(db.keys())) == 0:
        return "I'm remembering absolutely nothing right now"
    output = "I know:\n"
    for key in list(db.keys()):
        output += f"{str(key)}: {str(db[key])}\n"
    return output


def remove_from_database(target_list, index=None): #                                                                         Todo: finish implementing this
    try:
        temp_list = db[target_list]
    except KeyError:
        return False
    if index is None:
        del db[target_list]
        print(f"Removing List:'{temp_list[index]}' from db")
    elif len(temp_list) > index:
        print(f"Removing Item:'{temp_list[index]}' from list '{target_list}'")
        del temp_list[index]
        db[target_list] = temp_list
        print(db)
        return True
    else:
        return False


def print_board(coords):
    print(coords)
    tl, tm, tr, ml, mm, mr, bl, bm, br = coords
    print(tl, tm, tr, ml, mm, mr, bl, bm, br)
    return f"```fix\n" + \
           f" {tr} | {tm}  | {tl} \n" + \
           f"————————————\n" + \
           f" {mr} | {mm}  | {ml} \n" + \
           f"————————————\n" + \
           f" {br} |  {bm} | {bl} \n" + \
           f"```"


"""CLASSES"""
class TicTac:
    leaderboard = []

    def __init__(self):
        self._symbol = None
        self._choose_symbol = True
        self._allow_play = False
        self._coords = None

    @property
    def choose_symbol(self):
        return self._choose_symbol

    def set_symbols(self, player_symbol, ai_symbol):
        print(player_symbol, ai_symbol)
        self._symbol = (player_symbol, ai_symbol)
        self._choose_symbol = False
        self._coords = [" " for _ in range(9)]
        print(self._coords)
        self._allow_play = True

    def get_board(self):
        if self._coords is not None:
            return self._coords
        raise IndexError

    def game_defined(self):
        return self._allow_play

    def update_board(self, play, p=0):
        [TL, TM, TR, ML, MM, MR, BL, BM, BR] = self._coords
        if play == "TR":
            TR = self._symbol[p]
        elif play == "TM":
            TM = self._symbol[p]
        elif play == "TL":
            TL = self._symbol[p]
        elif play == "MR":
            MR = self._symbol[p]
        elif play == "MM":
            MM = self._symbol[p]
        elif play == "ML":
            ML = self._symbol[p]
        elif play == "BR":
            BR = self._symbol[p]
        elif play == "BM":
            BM = self._symbol[p]
        elif play == "BL":
            BL = self._symbol[p]
        else:
            raise ValueError
        self._coords = [TL, TM, TR, ML, MM, MR, BL, BM, BR]
        # print([TL, TM, TR, ML, MM, MR, BL, BM, BR])
        # print(self._coords)

    def ai_turn(self, strategy=None):
        if strategy == 0 or None:
            print("Random Placement strategy selected")
        elif strategy == 1:
            print("Random Placement - Rule Breaking 1 selected")
            play = random.choice(["TL", "TM", "TR", "ML", "MM", "MR", "BL", "BM", "BR"])
            self.update_board(play, 1)
            return play





class Curse:
    words_known = []
    word_strings = []
    leaderboard = {}
    count = 0

    def __init__(self, word, teacher=None):
        if type(word) is str:
            self._word = word
            Curse.word_strings.append(word)
        else:
            raise ValueError
        print(type(teacher))
        self._teacher = teacher
        if teacher.name not in Curse.leaderboard:
            Curse.leaderboard[teacher.name] = 1
        else:
            Curse.leaderboard[teacher.name] += 1

        Curse.words_known.append(self)
        Curse.count += 1

        self.is_phrase = None #TODO: Implement these
        self.is_four_letter_word = None
        self.is_adjective = None

    def __str__(self):
        return self._word

    @property
    def word(self):
        return self._word

    @property
    def teacher(self, mention=True):
        if mention:
            return self._teacher.mention
        return self._teacher.name


# incomplete argument extractor for user commands, might finish if it seems like it could be useful
# def extract_command_args(command, command_length, parameter_count=None):
#   command_split = command.split(" ")[1:]
#   parameters = (parameter for parameter in)

@client.event
async def on_ready():  # Runs after startup
    if is_replit:
        print("Detected running on Replit, db entries will be saved to Replit database")
    else:
        print("Detected running outside of Replit, db is a temporary variable")
    print(f"Logged in as {client.user}")
    client.allowed_mentions = discord.AllowedMentions()


@client.event  # Event loop for every message the bot sees, idk how this works or what this decorator is for
async def on_message(message):
    # Ensure that the bot does nothing for its own messages
    if message.author == client.user:
        return

    # Shorthand variable assignments
    msg_text = message.content
    send = message.channel.send
    # list of greetings for hello response TODO: convert to a dictionary with regex patterns, (or a separate list of em)
    greetings = ["Hello", "What Up", "hello", "HI", "hi", "Hi" "Salutations", "How do you do fellow Human?", "howdy",
                 "heyo", "Howdy", "I am not a Bivalve Mollusk, er, I mean Hello!", "hey there", "Parsnips", "'sup",
                 "sup"]

    # Message Author Stuff
    if update_database("Server_Members", message.author):
        print(f"Updated DB of Server Members with {message.author}")

    # StartsWith Section:

    # <editor-fold desc="Simple Automated Replies/User Commands">
    # User input must take no arguments, and bot must only reply with a single message.
    # keys and values must be strings or functions that return strings.                                                 (should this dict be at the top with the other assignments? also is this really the neatest way to organize its contents?)
    simple_startswith_dictionary = {"Marco": "Polo!",
                                    "Marcus": "Polonius!",
                                    "What is Euler's Constant?": f"Euler's Constant is {math.e}",
                                    "!get_quote": get_quote(),
                                    "!curse": get_random_curse_word(),
                                    "What do you know?": get_current_memory(),
                                    "!is_online": f"{client.user} Status: Active",
                                    "/throw @Aríel #5310": "/throw @Unillama#5116",
                                    "!collect": "/collect",
                                    "!throw John": "/throw @Unillama#5116"
                                    }
    for phrase in simple_startswith_dictionary.keys():
        if msg_text.startswith(phrase):
            await send(simple_startswith_dictionary[phrase])
    if msg_text.startswith("!get_all_simplistic_commands"):
        await send("Simple replies list:")
        for command in list(simple_startswith_dictionary.keys()):
            await send(f"Call: {command} | Reply: {simple_startswith_dictionary[command]}")
    # </editor-fold>

    # Says a random greeting when it sees a greeting
    if any(msg_text.startswith(word) for word in greetings):
        await send(random.choice(greetings))
        return

    regex_dict = {#"Template": (r"Regex Pattern" , "Reply String" , re.KEY | re.WORD | re.ARGUMENTS),
                   "Greetings": (r"hi", random.choice(greetings), re.MULTILINE | re.IGNORECASE),
                   "Marco": (r"[Mm]arco\w?", "Polo"),
                   "Marcus": (r"\w*[Mm]arcus\w*", "Polonius!")}
    for pattern in list(regex_dict.values()):
        regex, reply, *arguments = pattern
        if re.match(regex, msg_text, *arguments):
            await send(pattern[1]) # TODO: make regex optionally store a tuple of patterns

    # Sample Regex Code
    # regex = r"hi"
    # test_str = ("hi\n"
    #             "hi\n"
    #             "Hi\n"
    #             "Hippo\n"
    #             "hippo\n"
    #             "oh hi there\n"
    #             "hi-lo\n"
    #             "high\n")
    # matches = re.finditer(regex, test_str, re.MULTILINE | re.IGNORECASE)
    # for matchNum, match in enumerate(matches, start=1):
    #     print(f"Match {matchNum} was found at {match.start()}-{match.end()}: {match.group()}")
    #     for groupNum in range(0, len(match.groups())):
    #         groupNum = groupNum + 1
    #         print(f"Group {groupNum} found at {match.start(groupNum)}-{match.end(groupNum)}: {match.group(groupNum)}")

    """Commands which return more than just a message:"""
    # (These can't be packed into functions because I don't understand how 'await' works)

    if msg_text.startswith("!press_alt_f4_to_win_lol"):
        # Deliberately crashes the bot with sys.exit
        await send("wait fr?")
        print("Gottem lmao \n(called manual crash command)")
        sys.exit() #TODO: figure out why sys.exit() here is not terminating the program

    # Rolls an arbitrary number of dice of any size (args: /roll [int]d[int])
    if msg_text.startswith("!roll "):
        try:
            param1, param2 = msg_text[6:].split("d", 2)  # Take everything after /roll and split on d, unpack to params
            if param1 == '': param1 = 1                  # Set param1 to a value of 1 if not given by the user
            roll_list = []
            for i in range(int(param1)):
                roll = random.randint(1, int(param2))
                roll_list.append(roll)
                await send(f">>> Roll {i} is: {roll}")
            await send(f"Total: {sum(roll_list)}  |  Mean: {sum(roll_list)/len(roll_list)}")
        except ValueError:
            await send(">>> Invalid Dice Roll! Please format as '/roll [Number]d[Size]' "
                       "(ie: '/roll 5d6' rolls 5 six-sided dice)")

    # Lets you be that one cool aunt/uncle your parents always hated
    if msg_text.startswith("!teach_curse_word "):
        word = str(msg_text[18:])
        if word == "" or None:
            await send(">>>No word given (Format is /teach_curse_word [word])")
            return
        if update_database("CURSES", {word: Curse(word, message.author)}, None, True):                                  # retooled this into a class, maybe should be a subclass
            await send(f'"{word}"? Oh I\'ve never heard that one before, that seems like a fun word')
        else:
            await send(f"Oh {word}? I've heard that one before, {db['CURSES'][word].teacher} , taught me that.")

    if msg_text.startswith("!tic_tac_toe"):

        if len(msg_text) == 12:
            await send("Tic_Tac_Toe commands:\n"
                       "`!tic_tac_toe new` - starts a new game (ends current game!)\n"
                       "`!tic_tac_toe X` - Choose Xs\n"
                       "`!tic_tax_toe O` - Choose Os\n"
                       "`!tic_tac_toe play` [Location] - Pick where to play on your turn, format is [T|M|B][R|M|L] ie TR "
                       "for Top-Right, MM for Middle-Middle, BL for Bottom-Left, etc.\n"
                       "")
            return

        argument1 = msg_text.split(" ")[1]
        print(argument1)

        if argument1 == "new":
            db["TicTac"] = TicTac()
            await send("`X's or O's?`")
            return
        try:
            game = db["TicTac"]
        except KeyError:
            return

        if argument1 == "X" and game.choose_symbol:
            game.set_symbols("X", "O")
            await send(">>> Chose X's")
            await send(print_board(game.get_board()), delete_after=120)
            await send(">>> Begin Game, player has first move. (Use `!tic_tac_toe play`)")
            return
        elif argument1 == "O" and game.choose_symbol:
            game.set_symbols("O", "X")
            await send(">>> Chose O's")
            await send(print_board(game.get_board()), delete_after=120)
            await send(">>> Begin Game, player has first move. (Use `!tic_tac_toe play`)")
            return
        elif game.choose_symbol:
            await send("Invalid symbol")
            return

        if argument1 == "play":
            if game.game_defined is False:
                await send("Game has not been started yet!")
                return
            try:
                play = msg_text[18:]
            except IndexError:
                await send("No location given for play")
                return
            try:
                game.update_board(play)
            except ValueError:
                await send("Invalid Play")
                return
            await send(f"Player Chose: {play}")
            await send(print_board(game.get_board()), delete_after=120)
            await send(f"AI Chose: {game.ai_turn(1)}")
            await send(print_board(game.get_board()), delete_after=120)





@client.event
async def on_typing(channel, user, when):
    if update_database("Server_Members", user):
        print(f"Updated Database with {user}")
    return


""" 
Working Theory for event loops. Adding the decorator makes the function name significant, and causes it to be called
whenever the event corresponding to the name is seen by the program.
Still no clue what 'await' is for, or how to send a message without using it, which would be handy for sending messages
from functions, and compacting the event loop, as well as implementing other features.
(maybe that could be bodged with message editing lol. except idk how to do that yet either)
Could not work it out by looking through autocomplete values that appear when trying to create my own loop.
Working Theory for Replit db: data is saved even after a restart
"""


def main():
    if os.getenv("TOKEN") is not None:  # use environment variable if running on Replit else use TOKEN constant
        keep_alive()  # pokes the bot every hour
        client.run(os.getenv("TOKEN"))
    elif TOKEN is not None:
        keep_alive()  # pokes the bot every hour
        client.run(TOKEN)
    else:
        print("ERROR No token given! \n Quitting Program")
        sys.exit()


if __name__ == '__main__':
    main()
