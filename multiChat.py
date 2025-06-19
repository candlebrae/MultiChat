#!/usr/bin/env python3
# Used to display date and time for messages.
from datetime import date, datetime
# Used to set home directory for chat logs.
import platform
# Used to make sure chat directory exists.
import os
from pathlib import Path
# Proper arrow key scrolling on Un*x
try:
    if platform.system() != "Windows": import readline
except:
    print("Could not import readline.")
# Used for dice rolling
import random
# Used to save/load users
import pickle
# Colored names!
# TODO: pip dependency. Check if installed. If not, warn user.
from termcolor import colored;

# Decide where to look for the settings file
def get_settings_dir():
    if platform.system() == "Windows":
        env_home = os.getenv('APPDATA')
    else:
        try:
            basepath = os.environ['XDG_CONFIG_HOME']
        except:
            basepath = os.environ['HOME'] + "/.config"
            if os.path.isdir(basepath) == False: # ...Documents, then?
                basepath = os.environ['HOME'] + "/Documents"
            if os.path.isdir(basepath) == False: # Fine, home directory it is
                basepath = os.environ['HOME']
    settingpath = basepath + "/multichat"
    if os.path.isdir(settingpath) == False: os.mkdir(settingpath)
    return settingpath

# Make the default settings
def build_default_settings():
    # Figure out default chatlog file location- distinct from settings location!
    log_dir = get_log_dir()
    # Build the settings dict
    default_settings = {"savedir": log_dir, "timestamps": True}
    return default_settings

# Either get the user's existing settings, or assign the defaults
def retrieve_settings():
    settings_dir = get_settings_dir()
    print(settings_dir)
    if os.path.isfile(settings_dir + "/settings.pkl") == False: 
        return build_default_settings()
    else:
        with open(settings_dir + "/settings.pkl", "rb") as settingsfile:
            settings = pickle.load(settingsfile)
        return settings

# Save user settings to file
def save_settings(settings, settings_dir):
    if os.path.isdir(settings_dir) == False: os.mkdir(settings)
    with open (settings_dir + "/settings.pkl", "wb") as settingfile:
        pickle.dump(settings, settingfile)
    return True

# Decide where the (default) chatlog save directory should be
def get_log_dir():
    if platform.system() == "Windows":
        env_home = os.getenv('APPDATA')
    else:
        try:
            env_home = os.environ['XDG_DATA_HOME']
        except:
            env_home = os.environ['HOME'] + "/.local/share"
        if os.path.isdir(env_home) == False: # ...Documents, then?
            env_home = os.environ['HOME'] + "/Documents"
        if os.path.isdir(env_home) == False: # Fine, home directory it is
            env_home = os.environ['HOME']
    log_dir = env_home + "/multichat"
    return log_dir

# Add a new user, updating both the user list and count (used to more easily
# iterate users- yes, len() would be better. This is old code. I'll fix it 
# eventually.)
def add_user(user, user_list):
    if user:
        new_user_number = len(user_list) + 1
        user_list.update({str(new_user_number): str(user)})
        print()
        print(user + " added!")
        print("Type " + str(new_user_number) + " to send messages as " + user + ".")
        print()
    else:
        print("Please enter a username when adding a new user.")
    return user_list

# Load existing users
def load_users(output: bool):
    settings_dir = get_settings_dir()
    if os.path.isfile(settings_dir + "/saved-users.pkl") == False: 
        print("No saved users found. Save current users by sending /save\nwhile in chat.")
        return {}
    else:
        with open(settings_dir + "/saved-users.pkl", "rb") as savefile:
            user_list = pickle.load(savefile)
            print("Loaded users from file.")
            if output == True:
                for user in user_list.keys():
                    print("Type " + str(user) + " to send messages as " + str(user_list[user]["username"]))
    return user_list

# List out all users in list- output for the user to figure out who's there
def list_users(user_list):
    for user in user_list.keys():
        # Fix old data format
        if not isinstance(user_list[user], dict):
            user_list[user] = {"username": str(user_list[user]), "color": "default"}
        # Information for the user :D
        print("Type " + str(user) + " to send messages as " + user_list[user]["username"])

# Set up main function
def main():
    # Get user settings, including log directory location
    settings = retrieve_settings()
    # Set up a log directory
    log_dir = settings["savedir"]
    try:
        if os.path.isdir(log_dir) == False: os.mkdir(log_dir)
        os.chdir(log_dir)
    except Exception as error:
        print("Error creating or accessing chatlogs folder.")
        print("Please report this error to the creator.")
        print("Error code:", error)

    # Get user names and the file to log to.
    user_list = get_users()
    log_file = get_log_file(log_dir)
    # Chat and log to file.
    chat(user_list, log_dir, log_file, settings)
    # Close file and finish up.
    log_file.close()

# Clears the terminal.
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Get initial users.
def get_users():
    # Get at least one user. Dictionary format.
    user_list = {}
    # Variable is used to control a while loop that decides whether
    # to enter more users.
    continue_entry = True
    # Set up first user label
    user_number = 1
    clear()
    print("Welcome to MultiChat!")
    print()
    print("If you'd like to load saved users, enter /load.")

    user_name = input("Otherwise, enter the name of user " + str(user_number) + " or q to quit: ")

    # Get user name and add to dictionary
    # Dictionary format:
    # Number: Name
    while continue_entry == True:
        # Allow for insta-quitting.
        if user_name == "q":
            clear()
            raise SystemExit
        # We're done here- chat time
        elif user_name =="n" and user_number > 1:
            user_number -= 1
            return user_list
        # Fast bypass if users already are saved to file- else, complain
        if user_name == "":
            user_name = "/load"
        # Load existing users if they exist
        if user_name == "/load" and user_list == {}:
            user_list = load_users(False)
            if user_list != {}:
                user_number = len(user_list)
                continue_entry = False
                return user_list
        elif user_name == "/load":
            overwrite = input("Warning: loading saved users will overwrite current user list. Continue? y/n: ")
            if overwrite.lower == "y" or overwrite.lower == "yes":
                user_list = load_users(False)
        # We have a username!
        elif user_name:
            # Add user.
            user_list[str(user_number)] = {"username": str(user_name), "color": "default"}
            user_number += 1
            print("If you're done, enter n to stop adding users.")
        # Bogus inputs
        else:
            print("Please enter a username.")
            continue_entry = True
        user_name = input("Enter the name of user " + str(user_number) + " or q to quit: ")

# Separated into its own function to enable changing log dir in settings
def open_log(log_dir, log_file_name):
    try:
        log_file_name = log_dir + "/" + log_file_name + ".txt"
        print(log_file_name)
        # Make sure the file exists so r+ mode won't throw a fit
        # Yes, this is clumsy and a horrible way to do this
        # But it's 5 pm and I've been at this all day, and it's
        # not really intended for capitalism or anything, so.
        # As long as it works!
        log_file = open(log_file_name, "a")
        log_file.close()
        # Now that we are 100% certain the file exists:
        # Attempt to open the log file as read-append.
        log_file = open(log_file_name, 'r+')
        # If something goes wrong, retry the loop.
    except Exception as error:
        print("Error:", error)
        print("Please try again.")
    # Stop the loop and return the needed information.
    else:
        return log_file
            
def get_log_file(log_dir):
    # Get or create log file.
    print()
    print("Enter a name for this chat, or hit enter to")
    log_file_name = input("select the default (chat): ")
    # Check for empty input.
    if log_file_name.isspace() == True or not log_file_name:
        log_file_name = "chat"
    # Check for quitting.
    if log_file_name == "q":
        raise SystemExit
    log_file = open_log(log_dir, log_file_name)
    return log_file

def chat(user_list, log_dir, log_file, settings):
    # Read off the existing chat lines.
    chat_message = ""
    # Deal with any goofs
    if isinstance(user_list, tuple): # If I missed any old user_counter passes
        user_list = user_list[0]
    while user_list == {}:
        user_list = get_users()
    # Set first active user to be user 1, as this is the
    # most expected behavior and prevents sending messages
    # as no one.
    # Also fix the old /save format to match the new format 
    # (so color can happen!)
    active_user = next(iter(user_list.keys()))
    if not isinstance(user_list[active_user], dict):
        username = user_list[active_user]
        user_list[active_user] = {"username": str(username), "color": "default"}
        #print(user_list[active_user])
        active_user = username
        active_color = "default"
    else:
        user_info = user_list[active_user]
        print(user_info)
        active_user = str(user_info["username"])
        active_color = str(user_info["color"])

    # Add a date marker to the top of the log file
    # (or if appending to an existing file, to the end of it).
    try:
        # Clear the terminal to make it look nicer.
        clear()
        # Print any existing chat to terminal.
        for line in log_file:
            print(line, end="")
        # Get the date and add formatting.
        now = date.today()
        todayDate = "-----" + str(now.strftime("%A, %B %d, %Y")) + "-----"
        # Display the date and add it to the log file.
        print(todayDate)
        log_file.write(todayDate + "\n\n")
    # Notify the user if an exception occurs while getting the date.
    except Exception as error:
        print("Error getting date.")
    
    # Print instructions for user
    print("Welcome to MultiChat!")
    list_users(user_list)
    print("Or type /quit to quit (case sensitive).")
    print()
    print("Type /help to view a help message,")
    print("and /users to see a list of all users.")
    print()

    # Check for special inputs and handle accordingly
    while chat_message not in ["/quit", "/exit"]:
        # Get the time.
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # Set up message preface (used to identify messages)
        if settings["timestamps"] == True:
            preface_contents = str(active_user) + ", " + current_time + ": "
        else:
            preface_contents = str(active_user) + ": "
        if active_color == "default": # No color set
            preface = preface_contents
        else: # Color set
            preface = colored(preface_contents, active_color)
        # Get chat message.
        chat_message = input(preface)

        # SWITCH ACTIVE USER  
        # Do not record the number in the log file.
        try: # Try switching to the user indicated by the number.
            if chat_message in user_list.keys():
                # Working with old format- if user is not a nested dict
                # (color storage and username storage), fix the format
                # and carry on
                if not isinstance(user_list[chat_message], dict):
                    user_list[chat_message] = {"username": user_list[chat_message], "color": "default"}
            
                active_user = user_list[chat_message]["username"]
                active_color = user_list[chat_message]["color"]
                log_file.write("\n")
                print()
            else:
                chat_message = chat_message
        except:
            chat_message = chat_message
        else:
            # If it doesn't work, tell the user it's not working.
            # Then make sure that chat_message is a string so as
            # not to mess up other checks.
            chat_message = str(chat_message)

        # If we're quitting, add space in the text file, and notify user.
        if chat_message == "/quit" or chat_message == "/exit":
            clear()
            print("Chat saved.")
            try:
                log_file.write("\n\n")
            except Exception as error:
                print("Error adding text separator to end of file.")
                print("Your log should still be okay, but any later")
                print("additions will not be separated by a line.")
        
        # Help message
        elif chat_message == "/help":
            print()
            print("Welcome to MultiChat!")
            print("To view a list of users, type /users")
            print("To add a new user to this session, type /add")
            print("To view more commands, type /commands")
            print()

        # Add a new user
        elif chat_message == "/add":
            print()
            new_user = input("Enter the name of the user to add: ")
            user_list = add_user(new_user, user_list)
        elif chat_message.startswith("/add ") == True:
            new_user = chat_message.removeprefix("/add ")
            user_list = add_user(new_user, user_list)

        # Clear the screen
        elif chat_message == "/clear":
            clear()

        # List all users
        elif chat_message == "/users" or chat_message == "/switch":
            print("Users:")
            list_users(user_list)
         
        # Quote saving and retrieval
        elif chat_message.startswith("/quote") == True:
            quote_path = log_dir + "/quotes.txt"
            if chat_message == "/quote":
                # Read from quote file
                try:
                    quote_file = open(quote_path, "r")
                except:
                    quote_file = open(quote_path, "w")
                    quote_file.close()
                    quote_file = open(quote_path, "r")
                # Put all lines in a list
                quote_list = []
                for line in quote_file:
                    quote_list.append(line)
                # Pick random line
                random.seed()
                try:
                    quote_count = len(quote_list)
                    random_quote = quote_list[random.randrange(0, quote_count)]
                    print(random_quote, end="")
                    log_file.write(preface + chat_message + "\n")
                    # Write to log file so it's not confusing later
                    chat_message = "MultiChat: " + random_quote
                    log_file.write(chat_message)
                except:
                    print("Unable to access quotes, do any exist?")
                # Close the file
                quote_file.close()
            elif "/quotes" in chat_message:
                print("MultiChat: Did you mean /quote?")
            elif chat_message.startswith("/quote ") == True:
                # Open quote file
                quote_file = open(quote_path, "a")
                # Remove /quote from message
                try:
                    chat_message = chat_message.removeprefix("/quote ")
                    # Add quote
                    today = str(now.strftime("%A, %B %d, %Y"))
                    quote_text =  "On " + today + ", " + active_user + " said: " + chat_message + "\n"
                    quote_file.write(quote_text)
                    # Write to log file so it's not confusing later
                    chat_message = chat_message
                    log_file.write(active_user + ' added: "' + chat_message + '" to the quotes!' + "\n")
                    print("Multichat: Quote added!")
                except:
                    print("Error: Could not remove /quote from message.")
                # Close file
                finally:
                    quote_file.close()
            else:
                print("MultiChat: Did you mean /quote?")
            
        # Save users to file
        elif chat_message == "/save":
            settings_dir = get_settings_dir()
            with open(settings_dir + "/saved-users.pkl", "wb") as savefile:
                pickle.dump(user_list, savefile)
            print("Saved users to file.")

        # Load users from file
        elif chat_message == "/load":
            user_list = load_users(True)

        # Change settings
        elif chat_message == "/settings":
            # Retrieve settings
            print("Settings:")
            loc = settings["savedir"]
            timestat = settings["timestamps"]
            print(f"1: Change chatlog save location (currently {loc}")
            print(f"2: Toggle timestamps (currently {timestat})")
            setnum = input("Enter number of setting to change: ")
            match setnum:
                # Changing where chatlogs are saved
                case "1":
                    save_dir = input("Enter new chatlog save location (absolute path): ")
                    if save_dir[-1] in ["/", "\\"]: save_dir = save_dir[:-1]
                    # DO SAFETY CHECKS
                    try: # Does it exist?
                        if os.path.isdir(save_dir) == False: # Nope, fix it
                            Path(save_dir + "/multichat").mkdir(parents=True, exist_ok=True)
                    except Exception as ex: # Nope, failed to fix it
                        print("Could not create save location.")
                    if os.path.isdir(save_dir) == True: # It exists!
                        # Can we write to it?
                        if os.access(save_dir, os.W_OK):
                            settings["savedir"] = save_dir + "/multichat"
                            settings_dir = get_settings_dir()
                            save_settings(settings, settings_dir)
                            clear()
                            print(f"Saved. MultiChat's chat logs will now be saved to {settings_dir}.")
                            print("Old files will not be copied over-")
                            print("please move these yourself if you'd like to access them.")
                            print("Restarting to ensure change takes effect.")
                            chat(user_list, log_dir, log_file, settings)
                    else:
                        print(f"Cannot access {save_dir}. Changes not saved.")
                # Toggle timestamps
                case "2":
                    settings["timestamps"] = not settings["timestamps"]
                    settings_dir = get_settings_dir()
                    save_settings(settings, settings_dir)
                    print("Timestamps toggled. Currently:", settings["timestamps"])

        # Change the user's prefix color
        elif chat_message.startswith("/color") == True:
            color = chat_message.removeprefix("/color ")
            color_list = ["red", "yellow", "green", "cyan", "blue", "magenta", "light_grey", "dark_grey", "black", "white", "light_red", "light_yellow", "light_green", "light_cyan", "light_blue", "light_magenta"]
            if color == "/color":
                print("\nTo set a color for the current user, run: /color (color name)")
                print("For example: /color red")
                color = "nonsense"
            if color in color_list and color != "default":
                # Get key for current user. I'm sorry
                reverse_user_lookup = {}
                for user in user_list:
                    reverse_user_lookup[user_list[user]["username"]] = user
                tag = reverse_user_lookup[active_user]
                # Set new color for current user
                user_list[tag]["color"] = color
                active_color = color
            else:
                color_samples = "\ndefault"
                for color in color_list:
                    color_samples += ", \n" + colored(color, color)
                print("Please enter a valid color from the following:", color_samples, "\n")

        # Load users from file
        elif chat_message.startswith("/proxy") == True:
            tag = chat_message.removeprefix("/proxy ")
            if len(tag) > 0 and len(chat_message) > 6 and "/proxy" not in tag:
                if tag not in ["/add", "/clear", "/commands", "/dice", "/exit", "/quit", "/random", "/help", "/load", "/save", "/nolog", "/quote", "/shrug", "/switch", "/users"]:
                    # Get key for current user. I'm sorry
                    reverse_user_lookup = {}
                    for user in user_list:
                        reverse_user_lookup[user_list[user]["username"]] = user
                    old_tag = reverse_user_lookup[active_user]
                    user_list[tag] = active_user
                    del user_list[old_tag]
                    print(active_user + "'s proxy changed to " + tag)
                    list_users(user_list)
                else:
                    print("Commands cannot be proxies.")
            else:
                print("Please supply a new tag: /proxy <tag>")

        # List commands
        elif chat_message == "/commands":
            print()
            print("Commands:")
            print("/add <username>: Add new user.")
            print("/clear: Clear the screen.")
            print("/color <color name>: Set a prefix color for this user.")
            print("/commands: View this message.")
            print("/dice <number>: Roll a die with <number> faces.")
            print("/exit: Save and quit MultiChat.")
            print("/help: View a help message.")
            print("/load: Load saved users from file. Overwrites current user list!") 
            print("/nolog: Do not save the following message.")
            print("/proxy <tag>: Change the current user's proxy to <tag>.")
            print("/quit: Save and quit MultiChat.")
            print("/quote: View random quotes you've added.")
            print("/quote <text>: Add text to the quotes list.") 
            print("/random: Change to a random user.")
            print("/save: Save list of current users to file.") 
            print("/shrug: Send a shrug emote.")
            print("/switch: Same as /users.")
            print("/users: List users in session.")
            print()

        # Dice rolling
        elif chat_message == "/dice":
            print("MultiChat: /dice syntax: /dice <number>")
        elif chat_message.startswith("/dice ") == True:
            dice_sides = chat_message.removeprefix("/dice ")
            try:
                dice_sides = int(dice_sides)
                if dice_sides == 1:
                    dice_roll = 1
                else:
                    random.seed()
                    dice_roll = str(random.randrange(1, dice_sides))
                print("You rolled a " + dice_roll + "!")
                log_file.write(active_user + " rolled a " +  str(dice_sides) + "-sided die and rolled a " + dice_roll + "!\n")
            except:
                print("Can't roll die! " + str(dice_sides) + " is not a valid number!")
        
        # Change to random user
        elif chat_message == "/random":
            flavor_options = [
                        " has been chosen by the gods of randomness",
                        " was selected by fate",
                        " was hand-picked by the algorithm",
                        " has been chosen",
                        " is the chosen one",
                        " is at the front of the conga line",
                        " fulfilled the prophecy",
                        " won the lottery",
                        " has RNG's favor",
                        " came forwards",
                        " won the game",
                        " got picked",
                        ", come on down",
                        ", get over here",
                        ", congratulations!!",
                        " was struck by Zeus",
                        " spawned in",
                        " experienced a canon event",
                        " was enlisted in the skeleton wars",
                        " came back from the soup store",
                        " joined the brawl",
                        " walks into a bar",
                        ' walks into a bar... and says "ouch"',
                        " materializes",
                        ", I choose you",
                        " was pulled from the gacha",
                        " joins the game",
                        ", it's your turn!",
                        ", it's your time!",
                        ", time to talk!",
                        " has a mouth- they can finally scream",
                        " gets the talking stick"
                    ]
            random_flavor = random.choice(flavor_options)
            # Choose a random number from 1 to user_count.
            random_number = str(random.randrange(1, len(user_list) + 1))
            # Change to the random user only if it's different than the current active_user. Otherwise choose a random user again. Repeat until a different user is found.
            if active_user != user_list[random_number]:
                active_user = user_list[random_number]["username"]
            print("Multichat: " + active_user + random_flavor + "!")

        # Easter eggs and references
        # Table flipping
        elif chat_message.lower() == "flips table" or chat_message.lower() == "tableflip" or chat_message.lower() == "table flip":
            tableflip = preface + "(╯°□°）╯︵ ┻━┻"
            print(tableflip)
            log_file.write(tableflip + "\n")

        # Shrug
        elif chat_message.lower() == "shrug" or chat_message.lower() == "shrugs" or chat_message == "/shrug":
            try:
                shrug = preface + "¯\\_('u')_/¯"
                print(shrug)
                log_file.write(active_user + " shrugs.")
            except:
                print("Inexplicably, your shoulders fail to rise. The power of /shrug is beyond you.")

        # Losing the Game (sorry)
        elif chat_message.lower() == "the game":
            print("\nMultiChat: !!! THE GAME HAS BEEN LOST! !!!")
            print("MultiChat: Days since last incident: 0\n")
            you_lost = active_user + " has unleashed an infohazard!\n"
            log_file.write(you_lost)
        
        # Eyes emoji
        elif chat_message.lower() == "eyes":
            eyes = """
                       wWWWWWWWww.
                    WWW'''::::::''WWw 
                wWWW" .,wWWWWWWw..  WWw. 
      ` `      wWW'   W888888888888W  'WXX.
       . `.  wWW'   M88888i#####888"8M  'WWX.
         ` wWWW'   M88888##d###'w8oo88M   WWMX.
       `  wWWW"   :W88888####*  #88888M;   WWIZ.
   - -- wWWWW"     W88888####42##88888W     WWWXx
         "WIZ       W8n889######98888W       WWXx.
      ' ' 'Wm,       W88888999988888W        >WWR'
       '   "WMm.      "WW88888888WW"        mmMM'
             'Wmm.       "WWWWWW"        ,whAT?'
              ''MMMmm..            _,mMMMM
                      MMMMMMMMMMMMMM

"""
            print(preface + eyes)
            log_file.write(preface + "Eyes emoji\n")

        # Beetlejuice
        elif "beetlejuice" in chat_message.lower():
            print("Say it again!")
            log_file.write(preface + chat_message)

        # Not an easter egg, too lazy to move it
        # Allows for not saving a message upon request
        elif "/nolog" in chat_message:
            print("/nolog: The following message will not be logged.")
            # Set up message preface (used to identify messages)
            preface = colored(active_user + ", " + current_time + ": ", "dark_grey")
            # Get chat message.
            chat_message = input(preface)
            print("/nolog: Back to logging messages.")

        elif chat_message.lower() == "thumbsupper":
            emote = """
´´´´´´´´´´´´´´´´´´´´´´¶¶¶¶¶¶¶¶¶
´´´´´´´´´´´´´´´´´´´´¶¶´´´´´´´´´´¶¶
´´´´´´¶¶¶¶¶´´´´´´´¶¶´´´´´´´´´´´´´´¶¶
´´´´´¶´´´´´¶´´´´¶¶´´´´´¶¶´´´´¶¶´´´´´¶¶
´´´´´¶´´´´´¶´´´¶¶´´´´´´¶¶´´´´¶¶´´´´´´´¶¶
´´´´´¶´´´´¶´´¶¶´´´´´´´´¶¶´´´´¶¶´´´´´´´´¶¶
´´´´´´¶´´´¶´´´¶´´´´´´´´´´´´´´´´´´´´´´´´´¶¶
´´´´¶¶¶¶¶¶¶¶¶¶¶¶´´´´´´´´´´´´´´´´´´´´´´´´¶¶
´´´¶´´´´´´´´´´´´¶´¶¶´´´´´´´´´´´´´¶¶´´´´´¶¶
´´¶¶´´´´´´´´´´´´¶´´¶¶´´´´´´´´´´´´¶¶´´´´´¶¶
´¶¶´´´¶¶¶¶¶¶¶¶¶¶¶´´´´¶¶´´´´´´´´¶¶´´´´´´´¶¶
´¶´´´´´´´´´´´´´´´¶´´´´´¶¶¶¶¶¶¶´´´´´´´´´¶¶
´¶¶´´´´´´´´´´´´´´¶´´´´´´´´´´´´´´´´´´´´¶¶
´´¶´´´¶¶¶¶¶¶¶¶¶¶¶¶´´´´´´´´´´´´´´´´´´´¶¶
´´¶¶´´´´´´´´´´´¶´´¶¶´´´´´´´´´´´´´´´´¶¶
´´´¶¶¶¶¶¶¶¶¶¶¶¶´´´´´¶¶´´´´´´´´´´´´¶¶
´´´´´´´´´´´´´´´´´´´´´´´¶¶¶¶¶¶¶¶¶¶¶"""
            print(preface + emote + "\n")
            log_file.write(preface + emote + "\n") 

        elif "thumbsup" in chat_message.lower():
            print(preface + "👍")
            log_file.write(preface + "👍" + "\n") 

        # Done with easter eggs, back to regular code.
        # If there are no special cases, try to append the
        # new message to the log file. Report and handle
        # errors if this doesn't succeed, and notify the
        # user that their message may not have saved.
        else:
            try:
                # Append to file.
                log_file.write(preface + chat_message + "\n")
            except Exception as error:
                print("Error:", error)
                print("Your message may not have been saved.")


# Run main function
try:
    main()
except KeyboardInterrupt:
    clear()
    log_file.write("\n\n")
    print("Quitting.")
