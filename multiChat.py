#!/usr/bin/env python3
# Used to display date and time for messages.
from datetime import date
from datetime import datetime
# Used to set home directory for chat logs.
import platform
# Used to make sure chat directory exists.
import os
# Proper arrow key scrolling on Un*x
try:
    if platform.system() != "Windows": import readline
except:
    print("Could not import readline.")
# Used for dice rolling
import random
# Used to save/load users
import pickle

def add_user(user, user_list, user_count):
    if user:
        user_count += 1
        new_user_number = user_count
        user_list.update({new_user_number: user})
        print()
        print(user + " added!")
        print("Type " + str(new_user_number) + " to send messages as " + user + ".")
        print()
    else:
        print("Please enter a username when adding a new user.")
    return user_list, user_count

def load_users():
    if os.path.isfile("saved-users.pkl") == False: 
        print("No users to load. Save current users by sending /save.")
    else:
        with open("saved-users.pkl", "rb") as savefile:
            user_list = pickle.load(savefile)
            print("Loaded users from file.")
            user_counter = 1
            while user_counter in user_list:
                print("Type " + str(user_counter) + " to send messages as " + user_list[user_counter])
                user_counter += 1
    return user_list, user_counter

def list_users(user_list):
    for user in user_list:
        print("Type " + str(user) + " to send messages as " + user_list[user])

# Set up main function
def main():
    # Set up a log directory
    if platform.system() == "Windows":
        env_home = os.getenv('APPDATA')
    else:
        env_home = os.environ['HOME']
    log_dir = env_home + "/.multichat"

    try:
        if os.path.isdir(log_dir) == False: os.mkdir(log_dir)
        os.chdir(log_dir)
    except Exception as error:
        print("Error creating or accessing chatlogs folder.")
        print("Please report this error to the creator.")
        print("Error code:", error)

    # Get user names and the file to log to.
    user_list, user_count = get_users()
    log_file = get_log_file(log_dir)
    # Chat and log to file.
    chat(user_list, log_dir, log_file, user_count)
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
    while continue_entry == True:
        # Get user name and add to dictionary
        # Dictionary format:
        # Number: Name
        user_name = input("Otherwise, enter the name of user " + str(user_number) + " or q to quit: ")
        # Allow for insta-quitting.
        if user_name == "q":
            clear()
            raise SystemExit
        elif user_name == "/load":
            user_list, user_counter = load_users()
            user_number = user_counter
            continue_entry = False
            return user_list, user_counter
        elif user_name =="n" and user_number > 1:
            user_number -= 1
            return user_list, user_number
        elif user_name:
            # Add user.
            user_list.update({str(user_number): str(user_name)})
            continue_check = input("Would you like to add another user? (Y/n): " )
            # Check if they want to add another user.
            if continue_check.lower() == "n" or continue_check.lower() == "":
                return user_list, user_number
            if continue_check.lower() == "y":
                print("If you mistyped, enter n to stop adding users.")
                user_number += 1
            else:
                # Deal with nonsense inputs.
                while continue_check.lower() != "y" and continue_check.lower() != "n":
                    continue_check = input("Enter y or n: ")
                    if continue_check.lower() == "n":
                        return user_list, user_number
                    if continue_check.lower() == "y":
                        user_number += 1
        else:
            print("Please enter a username.")
            continue_entry = True
            
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

def chat(user_list, log_dir, log_file, user_count):
    # Read off the existing chat lines.
    chat_message = ""
    # Set first active user to be user 1, as this is the
    # most expected behavior and prevents sending messages
    # as no one.
    active_user = next(iter(user_list))

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
        preface = str(active_user) + ", " + current_time + ": "
        # Get chat message.
        chat_message = input(preface)

        # SWITCH ACTIVE USER  
        # Do not record the number in the log file.
        try:
            if chat_message in user_list.keys():
                active_user = user_list[chat_message]
                log_file.write("\n")
                print()
            else:
                chat_message = chat_message
            #chat_message = int(chat_message)
        except:
            chat_message = chat_message
        else:
            # Try switching to the user indicated by the number.
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
            user_list, user_count = add_user(new_user, user_list, user_count)
        elif chat_message.startswith("/add ") == True:
            new_user = chat_message.removeprefix("/add ")
            user_list, user_count = add_user(new_user, user_list, user_count)

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
            with open("saved-users.pkl", "wb") as savefile:
                pickle.dump(user_list, savefile)
            print("Saved users to file.")

        # Load users from file
        elif chat_message == "/load":
            user_list, user_counter = load_users()

        # Load users from file
        elif chat_message.startswith("/proxy") == True:
            tag = chat_message.removeprefix("/proxy ")
            if len(tag) > 0 and len(chat_message) > 6 and "/proxy" not in tag:
                if tag not in ["/add", "/clear", "/commands", "/dice", "/exit", "/quit", "/random", "/help", "/load", "/save", "/nolog", "/quote", "/shrug", "/switch", "/users"]:
                    reverse_user_lookup = res = dict((v,k) for k,v in user_list.items())
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
            print("/commands: View this message.")
            print("/dice <number>: Roll a die with <number> faces.")
            print("/exit: Save and quit MultiChat.")
            print("/random: Change to a random user.")
            print("/help: View a help message.")
            print("/load: Load saved users from file. Overwrites current user list!") 
            print("/nolog: Do not save the following message.")
            print("/proxy <tag>: Change the current user's proxy to <tag>.")
            print("/quit: Save and quit MultiChat.")
            print("/quote: View random quotes you've added.")
            print("/quote <text>: Add text to the quotes list.") 
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
            if user_count < 3:
                print("Changing to a random user is useful only if there are more than two users.")
            else:
                while True:
                    # Choose a random number from 1 to user_count.
                    random_number = random.randrange(1, user_count + 1)
                    # Change to the random user only if it's different than the current active_user. Otherwise choose a random user again. Repeat until a different user is found.
                    if active_user != user_list[random_number]:
                        active_user = user_list[random_number]
                        break

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
            eyes = "👀"
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
            preface = active_user + ", " + current_time + ": "
            # Get chat message.
            chat_message = input(preface)
            print("/nolog: Back to logging messages.")
        
        # Patas (Spanish for feet, inside joke reference)
        elif "patas" in chat_message.lower():
            print("\nMultiChat: You know what you did.")
            print("MultiChat: ( ´･ω･)\n")
            log_file.write(preface + chat_message + "\n") 

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
