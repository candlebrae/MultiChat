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
# The default option will be one of the following on Linux systems:
# - $XDG_CONFIG_HOME/multichat
# - $HOME/.config/multichat
# - $HOME/Documents/multichat
# - $HOME/multichat
# On Windows:
# $APPDATA\multichat
# C:\Program Files (x86)\multichat
def get_settings_dir():
    if platform.system() == "Windows":
        try:
            basepath = os.getenv('APPDATA')
        except:
            basepath = "C:/Program Files (x86)"
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
    if os.path.isdir(settingpath) == False: Path(settingpath).mkdir(parents=True, exist_ok=True)
    # Deal with permission errors
    while not os.access(settingpath, os.W_OK):
        print(f"Default settings path ({settingpath}) is not accessible: permission denied.")
        settingpath = input("Please enter a save location for Multichat settings files: ").rstrip() + "/multichat"
        if os.path.isdir(settingpath) == False: Path(settingpath).mkdir(parents=True, exist_ok=True)
    return settingpath

# Make the default settings
def build_default_settings():
    # Figure out default chatlog file location- distinct from settings location!
    log_dir = get_log_dir()
    settings_dir = get_settings_dir()
    # Build the settings dict
    default_settings = {"savedir": log_dir, "timestamps": True, "backread_linecount": 100, "case_sensitive_proxies": True}
    return default_settings

# Either get the user's existing settings, or assign the defaults
def retrieve_settings():
    settings_dir = get_settings_dir()
    print(settings_dir)
    if os.path.isfile(settings_dir + "/settings.pkl") == False: 
        settings = build_default_settings()
    else:
        with open(settings_dir + "/settings.pkl", "rb") as settingsfile:
            settings = pickle.load(settingsfile)
        # Deal with backwards compatibility for new settings
        try:
            test = settings["backread_linecount"]
        except:
            settings["backread_linecount"] = 100
            settings_dir = get_settings_dir()
            save_settings(settings, settings_dir)
        try:
            casesensitive = settings["case_sensitive_proxies"]
        except:
            settings["case_sensitive_proxies"] = True
            settings_dir = get_settings_dir()
            save_settings(settings, settings_dir)
    # Add random flavortext
    settings["random_flavortext"] = get_flavortext(settings_dir)
    return settings

# Save user settings to file
def save_settings(settings, settings_dir):
    if os.path.isdir(settings_dir) == False: Path(settings).mkdir(parents=True, exist_ok=True)
    # Remove options that we don't want to store in the settings file
    if "random_flavortext" in settings.keys():
        del settings["random_flavortext"]
    with open (settings_dir + "/settings.pkl", "wb") as settingfile:
        pickle.dump(settings, settingfile)
    return True

# Decide where the (default) chatlog save directory should be
# The default locations will be one of the following depending on the file system and environment variable setup. 
# On Linux:
# - $XDG_DATA_HOME/multichat
# - $HOME/.local/share/multichat
# - $HOME/Documents/multichat
# - $HOME/multichat
# On Windows:
# $APPDATA\multichat
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
    while not os.access(log_dir, os.W_OK):
        print("Cannot access default log save location ({log_dir}): permission denied.")
        log_dir = input("Enter valid log save location: ").rstrip() + "/multichat"
    return log_dir

def change_log_dir(settings, log_file, log_file_name, user_list):
    save_dir = input("Enter new chatlog save location (absolute path): ").rstrip() # Remove trailing slash, if present
    # if save_dir[-1] in ["/", "\\"]: save_dir = save_dir[:-1]
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
            print(f"Saved. MultiChat's chat logs will now be saved to {save_dir}.")
            print(log_file)
            log_file.write("\n\n")
            log_file.close() # Kill the old file, on to the new!
            log_file = open_log(save_dir, log_file_name)
            chat(user_list, save_dir, log_file, log_file_name, settings)
        else:
            print(f"Cannot access log file: permission denied. Do you have permission to write to files in {save_dir}?")

# Get list of flavortext used by /random
def get_flavortext(settings_dir):
    # Check for a custom flavor text file
    if os.path.isfile(settings_dir + "/random_flavortext.txt"):
        with open(settings_dir + "/random_flavortext.txt", "r") as flavor_file:
            flavor_options = flavor_file.readlines()
    elif os.path.isfile("random_flavortext.txt"):
        with open("random_flavortext.txt", "r") as flavor_file:
            flavor_options = flavor_file.readlines()
    else:
        # If not found, use a short default list of flavor text
        flavor_options = [
            "NAME's turn!",
            "NAME has been chosen by the gods of randomness!",
            "NAME was hand-picked by the algorithm!",
            "NAME has been chosen!",
            "NAME won the lottery!",
            "NAME spawned in!",
            "NAME, I choose you!",
            "NAME joins the game!",
            "NAME gets the talking stick!"
            ]
    return flavor_options

# Add a new user, updating the user list
def add_user(user, user_list):
    if user:
        new_user_number = len(user_list) + 1
        user_list.update({str(new_user_number): {"username": str(user), 'color': 'default'}})
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
    return log_file, log_file_name

# Test if a message is a switch. If it is, return the key to switch with.
def check_for_switch(message: str, user_list: dict, case_sensitivity: bool):
    try:
        proxies = user_list.keys()
        if case_sensitivity == False:
            insensitive_proxies = [proxy.casefold() for proxy in proxies]
            if message.casefold() in insensitive_proxies: # Removes case differences
                return True
            else:
                return False
        elif message in proxies:
            return True
        else:
            return False
    except Exception as ex:
        print("Please report the following error:", "check for switch failed,", ex)
        # If all else fails, don't switch
        return False

# CHANGE ACTIVE USER
def switch(user):
    active_user = user["username"]
    active_color = user["color"]
    chat_message = ""
    return active_user, active_color, chat_message

# The main chat sequence
def chat(user_list, log_dir, log_file, log_file_name, settings):
    # Setup
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
        # Setup
        read_line_count = int(settings["backread_linecount"])
        # Get the old chat logs
        oldchat = log_file.readlines()
        # If the user saved this as a setting, get it
        # Deal with improper values
        if read_line_count > len(oldchat) or read_line_count < 0:
            read_line_count = len(oldchat) - 1
        # Print up to N lines of any existing chat to terminal.
        for line in (oldchat[-read_line_count:]):
            print(line, end ='')
        #for line in log_file:
        #    print(line, end="")
        # Get the date and add formatting.
        now = date.today()
        todayDate = "-----" + str(now.strftime("%A, %B %d, %Y")) + "-----"
        # Display the date and add it to the log file.
        print(todayDate)
        log_file.write(todayDate + "\n\n")
    # Notify the user if an exception occurs while getting the date.
    except Exception as error:
        print("Error getting chat file or date.")
        print(error)
    
    # Print instructions for user
    print("Welcome to MultiChat!")
    list_users(user_list)
    print("Or type /quit to quit (case sensitive).")
    print()
    print("Type /help to view a help message,")
    print("/commands to view a list of commands,")
    print("or /users to see a list of all users.")
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
            # We have a switch:
            if check_for_switch(chat_message, user_list, settings["case_sensitive_proxies"]) == True:
                # Handle the actual switch
                if settings["case_sensitive_proxies"] == False:
                    # Find the match
                    for user in user_list:
                        # Case-insensitive matching and switching
                        if user.casefold() == chat_message.casefold():
                            active_user, active_color, chat_message = switch(user_list[user])
                            # Fix old user formats
                            if not isinstance(user_list[user], dict): # If user format is outdated
                                user_list[user] = {"username": user_list[user], "color": "default"}
                else: # Case sensitive is simpler
                    active_user, active_color, chat_message = switch(user_list[chat_message])
            else: # We're not switching right now
                chat_message = chat_message
        except Exception as ex:
            print(ex)
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
            raise SystemExit
        
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
            if new_user == "help":
                print("-------------")
                print("/add: Add a new user to the list. Will prompt for username.")
                print("Alternatively, /add <user> will add <user> to the list.")
                print("A default proxy will be assigned based on the number of users.")
                print("Examples:")
                print("    /add Alice: Add a user named Alice.")
                print("    /add Bob: Add a user named Bob.")
                print("    /add Eve: Add a user named Eve.")
                print("-------------")
            else:
                user_list = add_user(new_user, user_list)

        # Remove users from the list
        elif chat_message.startswith("/remove"):
            del_user = chat_message.removeprefix("/remove ")
            # Help message
            if del_user == "help":
                print("-------------")
                print("/remove <proxy>: delete the user with proxy <proxy>.")
                print("Past messages sent as this user will still be under their name, but they will be removed \nfrom the user list and you will not be able to send messages as them.")
                print("You will be asked to confirm deletion by typing their full name.")
                print("If you're not sure what a user's <proxy> is, see /users")
                print("-------------")
            # Delete the user, if they exist
            elif del_user in user_list:
                username = del_user["username"]
                print(f"Are you sure you'd like to delete {username}?")
                confirm = input(f"Type their name to confirm (case-sensitive): ").lower()
                if confirm == username:
                    user_list[del_user]
                    print(f"{username} deleted.")
                    list_users(user_list)
                else:
                    print("Name does not match. Did you make a typo?")
            # Oops, no user!
            else:
                print(f"Cannot find user with proxy {del_user}. Did you typo?")


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
            if chat_message == "/quote help":
                print("-------------")
                print("/quote: save chat messages or read a random saved message.")
                print("/quote <message> will store <message> as a quote that can be retrieved later.")
                print("This quote will be attributed to the current user and the current time.")
                print("/quote on its own will retrieve a random saved quote, if any exist.")
                print("-------------")
            elif chat_message == "/quote":
                # Read from quote file
                try:
                    quote_file = open(quote_path, "r")
                except: # Quotes broke, sorry. Start over.
                    # Save the broken one, if it exists
                    try:
                        from shutil import copyfile
                        shutil.copy(quote_path, quote_path + ".bak")
                        print("Error: quotes file missing or corrupt. \nSaving old file as backup, creating new file.")
                    except: # Can't save backup- file probably doesn't exist yet
                        pass # we'll just replace it.
                    # Make a new quotes file
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
                    print("Unable to access quotes; did you save any?")
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
        elif chat_message.startswith("/save"):
            if chat_message.endswith("help"):
                print("-------------")
                print("/save: Save the names, colors, and proxies of current users.")
                print("This allows these users to be loaded in a different chat with /load.")
                print("Saved users can be found in \n    %APPDATA/multichat/saved-users.pkl (Windows)")
                print("    ~/.config/multichat/saved-users.pkl (Linux, MacOS).")
                print("-------------")
            else:
                settings_dir = get_settings_dir()
                with open(settings_dir + "/saved-users.pkl", "wb") as savefile:
                    pickle.dump(user_list, savefile)
                print("Saved users to file.")

        # Load users from file
        elif chat_message.startswith("/load"):
            if chat_message.endswith("help"):
                print("-------------")
                print("/load: Retrieve saved user names, colors, and proxies.")
                print("Warning: old user list will be overwritten!")
                print("/save must have been used previously to create the file that /load looks for:")
                print("    %APPDATA/multichat/saved-users.pkl (Windows)")
                print("    ~/.config/multichat/saved-users.pkl (Linux, MacOS)")
                print("-------------")
            else:
                user_list = load_users(True)

        # Change settings
        elif chat_message == "/settings":
            # Retrieve settings
            print(f"Settings (saved at {get_settings_dir()}):")
            loc = settings["savedir"]
            timestat = settings["timestamps"]
            backread_linecount = settings["backread_linecount"]
            case_sensitivity = settings["case_sensitive_proxies"]
                
            print(f"1: Change chatlog save location (currently {loc})")
            print(f"2: Toggle timestamps (currently {timestat})")
            print(f"3: Set lines of old chatlog to display (currently {backread_linecount})")
            print(f"4: Toggle case-sensitivity for switch proxies (currently {case_sensitivity})")
            setnum = input("Enter number of setting to change: ")
            match setnum:
                # Changing where chatlogs are saved
                case "1":
                    print("Old files will not be copied over-")
                    print("please move these yourself if you'd like to access them.")
                    change_log_dir(settings, log_file, log_file_name, user_list)
                # Toggle timestamps
                case "2":
                    settings["timestamps"] = not settings["timestamps"]
                    settings_dir = get_settings_dir()
                    save_settings(settings, settings_dir)
                    print("Timestamps toggled. Currently:", settings["timestamps"])
                case "3":
                    backread_linecount = input("Enter number of lines to display when loading saved chats: ")
                    settings["backread_linecount"] = backread_linecount
                    settings_dir = get_settings_dir()
                    save_settings(settings, settings_dir)
                    print(f"Line count set to {backread_linecount}.")
                case "4":
                    settings["case_sensitive_proxies"] = not settings["case_sensitive_proxies"]
                    settings_dir = get_settings_dir()
                    save_settings(settings, settings_dir)
                    print("Case sensitivity toggled. Currently:", settings["case_sensitive_proxies"])


        # Change the user's prefix color
        elif chat_message.startswith("/color") == True:
            color = chat_message.removeprefix("/color ")
            # Valid colors
            color_list = ["red", "yellow", "green", "cyan", "blue", "magenta", "light_grey", "dark_grey", "black", "white", "light_red", "light_yellow", "light_green", "light_cyan", "light_blue", "light_magenta"]
            # Set up sample color display, accounting for availability differences
            color_samples = "\ndefault"
            for color_option in color_list:
                try: # Every color colored with itself
                    color_samples += ", \n" + colored(color_option, color_option)
                except:
                    pass # Color not available on this system
            # Help texts
            if color == "/color":
                print("\nTo set a color for the current user, run: /color (color name)")
                print("For example: /color red")
                color = "nonsense"
            if color == "help":
                print("-------------")
                print("/color <colorname>: set the color of the current user's name/timestamp.")
                print("<color> may be any standard ANSII terminal color name.")
                print("The following colors are allowed:")
                print(color_samples)
                print("Examples:")
                print("    /color red: set the current user's color to red.")
                print("    /color default: set the current user's color to the default text color.")
                print("-------------")
            # If we have a valid color
            if color in color_list and color != "default":
                # Get key for current user. I'm sorry. This is overkill.
                reverse_user_lookup = {}
                for user in user_list:
                    try:
                        reverse_user_lookup[user_list[user]["username"]] = user
                    except TypeError:
                        # String indices must be integers, not 'str'
                        print("Oops! Please let the maintainer know that you encountered an error: user lookup searching for wrong type.")
                tag = reverse_user_lookup[active_user]
                # Set new color for current user
                user_list[tag]["color"] = color
                active_color = color
            elif color != "help": # Invalid choice
                print("Please enter a valid color from the following:", color_samples, "\n")

        # Load users from file
        elif chat_message.startswith("/proxy") == True:
            tag = chat_message.removeprefix("/proxy ")
            if tag == "help":
                print("-------------")
                print("/proxy <tag>: Change the current user's proxy to <tag>.")
                print("This allows you to set the text used to switch to the current user.")
                print("If a message exactly matches a user's proxy text, then the next message is set \nas coming from their user. Matching is case-sensitive!")
                print("It's a good idea to choose proxies that you don't tend to type in \nnormal conversation.")
                print("Examples: ")
                print('    /proxy w>: Sets switch text for current user to "w>".')
                print('    /proxy Will: Sets switch text for current user to "Will".')
                print('    /proxy sudo: Sets switch text for current user to "sudo".')
                print("-------------")
            elif len(tag) > 0 and len(chat_message) > 6:
                if not tag.startswith("/"):
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
                    print("Proxies cannot start with / (sorry!).")
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
            print("/help: View a help message.")
            print("/load: Load saved users from file. Overwrites current user list!") 
            print("/nolog: Do not save the next message.")
            print("/proxy <text>: Change the current user's switch text to <text>.")
            print("/quit: Save and quit MultiChat.")
            print("/quote: View random quotes you've added.")
            print("/quote <text>: Add text to the quotes list.") 
            print("/random: Change to a random user.")
            print("/remove: Delete a user.")
            print("/save: Save list of current users to file.") 
            print("/settings: Change settings for MultiChat.")
            print("/shrug: Send a shrug emote.")
            print("/users: List users in session.")
            print()

        # Dice rolling
        elif chat_message == "/dice":
            print("MultiChat: /dice syntax: /dice <number>")
            print("MultiChat: For more information, see /dice help")
        elif chat_message.startswith("/dice ") == True:
            dice_sides = chat_message.removeprefix("/dice ")
            if dice_sides == "help":
                print("-------------")
                print("/dice <number>: roll a die with a set number of sides and shows the results.")
                print("<number> may be any integer greater than zero.")
                print("Examples:")
                print("    /dice 6: rolls a 6-sided die.")
                print("    /dice 20: rolls a 20-sided die.")
                print("    /dice 8675309: rolls a 8,675,309-sided die.")
                print("-------------")
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
                if dice_sides != "help":
                    print("Can't roll die! " + str(dice_sides) + " is not a valid number for rolling!")
        
        # Change to random user
        elif chat_message == "/random":
            # Pick the silly flavortext
            random_flavor = random.choice(settings["random_flavortext"]).strip()
            # Pick the random user
            random_user = random.choice(list(user_list.keys()))
            # Change to the random user only if it's different than the current active_user. Otherwise choose a random user again. Repeat until a different user is found.
            if active_user != random_user:
                active_user, active_color, chat_message = switch(user_list[random_user])
            # Let the user know who got picked
            print("Multichat: " + random_flavor.replace("NAME", active_user))

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
            if chat_message.removeprefix("/nolog") == " help": 
                print("-------------")
                print("/nolog: hide a single message from the chatlog.")
                print("The following message will not be saved in any chatlogs or records (not even with /quote).")
                print("Useful if you want to make sure something isn't saved in your records.")
                print("WARNING: the message is really, truly gone once MultiChat closes!")
                print("Don't use this for any messages that you want to read later.")
                print("-------------")
            else:
                print("/nolog: The next message will not be saved in the chatlog.")
                # Set up message preface (used to identify messages)
                preface = colored(active_user + ", " + current_time + ": ", "dark_grey")
                # Get chat message.
                chat_message = input(preface)
                print("/nolog: Back to normal logging.")

        elif chat_message.lower() == "thumbsupper":
            emote = """
´´´´´´´´´´´´´´´´´´´´´´@@@@@@@@@
´´´´´´´´´´´´´´´´´´´´@@´´´´´´´´´´@@
´´´´´´@@@@@´´´´´´´@@´´´´´´´´´´´´´´@@
´´´´´@´´´´´@´´´´@@´´´´´@@´´´´@@´´´´´@@
´´´´´@´´´´´@´´´@@´´´´´´@@´´´´@@´´´´´´´@@
´´´´´@´´´´@´´@@´´´´´´´´@@´´´´@@´´´´´´´´@@
´´´´´´@´´´@´´´@´´´´´´´´´´´´´´´´´´´´´´´´´@@
´´´´@@@@@@@@@@@@´´´´´´´´´´´´´´´´´´´´´´´´@@
´´´@´´´´´´´´´´´´@´@@´´´´´´´´´´´´´@@´´´´´@@
´´@@´´´´´´´´´´´´@´´@@´´´´´´´´´´´´@@´´´´´@@
´@@´´´@@@@@@@@@@@´´´´@@´´´´´´´´@@´´´´´´´@@
´@´´´´´´´´´´´´´´´@´´´´´@@@@@@@´´´´´´´´´@@
´@@´´´´´´´´´´´´´´@´´´´´´´´´´´´´´´´´´´´@@
´´@´´´@@@@@@@@@@@@´´´´´´´´´´´´´´´´´´´@@
´´@@´´´´´´´´´´´@´´@@´´´´´´´´´´´´´´´´@@
´´´@@@@@@@@@@@@´´´´´@@´´´´´´´´´´´´@@
´´´´´´´´´´´´´´´´´´´´´´´@@@@@@@@@@@"""
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
        elif chat_message != "":
            try:
                # Append to file.
                log_file.write(preface + chat_message + "\n")
            except PermissionError:
                print("Cannot save to file: permission denied. Do you have permission to write to your log save location?")
                change_loc = input("Would you like to change your log save location? y/n: ")
                if change_loc.casefold() == "y":
                    pass
            except Exception as error:
                print("Error:", error)
                print("Your message may not have been saved.")

# Set up main function
def main():
    # Get user settings, including log directory location
    settings = retrieve_settings()
    # Set up a log directory
    log_dir = settings["savedir"]
    try:
        if os.path.isdir(log_dir) == False: Path(log_dir).mkdir(parents=True, exist_ok=True)
        os.chdir(log_dir)
    except Exception as error:
        print("Error creating or accessing chatlogs folder.")
        print("Please report this error to the creator.")
        print("Error code:", error)

    # Get user names and the file to log to.
    user_list = get_users()
    log_file, log_file_name = get_log_file(log_dir)
    # Chat and log to file.
    chat(user_list, log_dir, log_file, log_file_name, settings)
    # Close file and finish up.
    log_file.close()

# Run main function
try:
    main()
except KeyboardInterrupt:
    clear()
    log_file.write("\n\n")
    print("Quitting.")
