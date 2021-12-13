"""
Ari's Test Bot for learning the Discord API
"""
import discord                     # Discord API
from replit import db ; import os  # For Replit
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
    try:
        # print(db["curse_words"]); print(db) ;print(db["curse_words"].keys())
        return random.choice(list(db["curse_words"].keys()))
    except KeyError:
        return "I don't know any curse words!"

# sets values in database (am I accidentally reinventing a class in this dict lol? bc this is def a setter)
def update_database(list_name, entry, check_by=None, is_dict=False, is_non_iterable=False):
    """ Checks if 'target_list' exists yet in the db, and is a list, if it doesn't exist, adds it as a list containing
        'entry' only. Otherwise, checks if 'entry' is already in the list, (or if the corresponding index
         of it is). If it is not, 'entry' is appended.
    :param list_name: key to the list in the db to be updated, expected string, but only must reference a list
    :param entry: entry to append to the list in the db
    :param check_by: optional param, if given, entry will be treated as existing only if the check_by index matched db,
                     meant for entries that are tuples or lists themselves.
    :param is_dict: optional param, if true, entry should be a dict with one key/value pair, and will be compared by key
                    db will also be instantiated as a dict
    :return: False for if the database was not updated, or an error was found before it could be.
             True if it was, and either a new list was added to the db, or an entry was appended to the list in the db.
    """  #                                                                                                              (This description may be too long, but this is still complicated to me, so It seems like itd be helpful until I'm more experienced)
    if list_name in db.keys():
        temp_list = db[list_name]
        if is_dict is False and type(temp_list) != list:
            print("Could not update value! Target value is not a list; returning False")
            return False
        if is_dict:
            check = list(entry.keys())[0]
            check_list = list(temp_list.keys())
        elif check_by is not None:
            try:
                print(f"(True: comparing by Index {check_by}) ", end='')
                check, check_list = entry[check_by], [value[check_by] for value in temp_list]
            except IndexError:
                print("\nINDEX OUT OF RANGE ERROR, revise check_by or db/entry values\n")
                return False
        else:
            print("(False: comparing by Whole Tuple) ", end='')
            check, check_list = entry, temp_list
        print(f"check is:'{check}' and check_list is:'{check_list}'")
        if check not in check_list:
            if is_dict:
                db[list_name][list(entry.keys())[0]] = list(entry.values())[0]
                print(f"Added K/V pair:'{entry}' to '{list_name}'; returning True")
                return True
            temp_list.append(entry)
            db[list_name] = temp_list
            print(db)
            print(f"Added Entry:'{entry}' entry to '{list_name}'; returning True")
            return True
        else:
            print(f"Entry:'{entry}' is already in '{list_name}'; returning False")
            return False
    else:
        if is_dict:
            db[list_name] = {}
            db[list_name] = entry
        else:
            db[list_name] = []
            db[list_name].append(entry)
        print(db)
        print(f"Added New Key/Value Pair to db: key is '{list_name}' and value is a list/dict containing a single"
              f" entry '{entry}'; returning True")
        return True

def get_current_memory():
    if len(list(db.keys())) == 0:
        return "I'm remembering absolutely nothing right now"
    output = "I know:\n"
    for key in list(db.keys()):
        output += f"{str(key)}: {str(db[key])}\n"
    return output


def remove_from_database(target_list, index): #                                                                         Todo: finish implementing this
    temp_list = db[target_list]
    if len(temp_list) > index:
        print(f"Removing Item:'{temp_list[index]}' from list '{target_list}'")
        del temp_list[index]
        db[target_list] = temp_list
        print(db)
        return True
    else:
        return False




# incomplete argument extractor for user commands, might finish if it seems like it could be useful
# def extract_command_args(command, command_length, parameter_count=None):
#   command_split = command.split(" ")[1:]
#   parameters = (parameter for parameter in)

@client.event
async def on_ready():  # Runs after startup
    if is_replit: print("Detected running on Replit, db entries will be saved to Replit database")
    else:         print("Detected running outside of Replit, db is a temporary variable")
    print(f"Logged in as {client.user}")


@client.event  # Event loop for every message the bot sees, idk how this works or what this decorator is for
async def on_message(message):
    # Ensure that the bot does nothing for its own messages
    if message.author == client.user:
        return None

    # Shorthand variable assignments
    msg_text = message.content
    send = message.channel.send
    # list of greetings for hello response TODO: convert to a dictionary with regex patterns, (or a separate list of em)
    greetings = ["Hello", "What Up", "hello", "HI", "hi", "Hi" "Salutations", "How do you do fellow Human?", "howdy",
                 "heyo", "Howdy", "I am not a Bivalve Mollusk, er, I mean Hello!", "hey there", "Parsnips", "'sup",
                 "sup"]

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
                                    "!is_online" : f"{client.user} Status: Active",
                                    "/throw @Aríel #5310":"/throw @Unillama #5116",
                                    "!collect": "/collect",
                                    "!throw John": "/throw @Unillama #5116"
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

    # Commands which return more than just a message:
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

            roll_list = [] #                                                                                            (The rest of this block could prolly be its own function, but eh)
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
        """ Takes a word from the user and saves it to db as a tuple which also contains the first user to submit 
            the entry to the database as the second element, gives relevant messages depending on if it exists already. 
            Calls update_database() with the key "curse_words" and a check_by of 0 """
        curse_word = str(msg_text[18:])                 # Extract Argument                                              (maybe this could be done with split or a variable to make refactoring easier, but this seems like less effort)
        word_teacher_dict = {curse_word: str(message.author)}  # Then pack it into a dict to save it with the user name       (would saving as a dict be better? Yes, I think so?? Nope it isn't actually, but I don't feel like putting it back)
        print(f"Curse Word is:{curse_word}, and is packed into dictionary {word_teacher_dict}")
        if curse_word == "" or None:
            print("No argument given")
            await send(">>>No word given (Format is /teach_curse_word [word])")
            success = None
        else:
            success = update_database("curse_words", word_teacher_dict, None, True)
            print(f"Was database updated ({success})")
        if success:  # update_db call
            print("New Word")
            await send(f'"{curse_word}"? Oh I\'ve never heard that one before, that seems like a fun word')
        elif success is None:
            print("Success is None")
        else:
            print("Heard Before")
            teacher = db["curse_words"][curse_word]
            await send(f"Oh {curse_word}? I've heard that one before, @{teacher} , taught me that.")

@client.event
async def on_socket_raw_receive(msg):
  """"""

@client.event
async def run():
    print("running")



""" 
Working Theory for event loops. Adding the decorator makes the function name significant, and causes it to be called
whenever the event corresponding to the name is seen by the program.
Still no clue what 'await' is for, or how to send a message without using it, which would be handy for sending messages
from functions, and compacting the event loop, as well as implementing other features.
(maybe that could be bodged with message editing lol. except idk how to do that yet either)
Could not work it out by looking through autocomplete values that appear when trying to create my own loop.
Working Theory for Replit db: data is saved even after a restart
"""


def main(): #                                                                                                           todo: try uploading this to github or using git in replit so i can learn how github works, and also share with Lycos
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