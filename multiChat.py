#!/usr/bin/env python3
# Used to display date and time for messages.
from datetime import date
from datetime import datetime
# Used to make sure chat directory exists.
import os
# Used to exit safely.
import sys
# Used to set home directory for chat logs.
import platform
# Used for dice rolling
import random

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
    while continue_entry == True:
        # Get user name and add to dictionary
        # Dictionary format:
        # Number: Name
        print()
        user_name = input("Enter the name of user " + str(user_number) + ", or q to quit: ")
        # Allow for insta-quitting.
        if user_name == "q":
            clear()
            sys.exit(0)
        elif user_name =="n" and user_number > 1:
            user_number -= 1
            return user_list, user_number
        else:
            # Add user.
            user_list.update({user_number: user_name})
        continue_check = input("Would you like to add another user? (Y/n): " )
        # Check if they want to add another user.
        if continue_check.lower() == "n":
            return user_list, user_number
        if continue_check.lower() == "y":
            print("User added.")
            print("If you mistyped, enter n to stop adding users.")
            user_number += 1
        else:
            # Deal with nonsense inputs.
            while continue_check.lower() != "y" and continue_check.lower() != "n":
                continue_check = input("Enter y or n: ")
                if continue_check.lower() == "n":
                    return user_list, user_number
            
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
        sys.exit(0)
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
    active_user = user_list[1]

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
    counter = 1
    print("Welcome to MultiChat!")
    while counter in user_list:
        print("Type " + str(counter) + " to send messages as " + user_list[counter] + ",")
        counter += 1
    print("Or type /quit to quit (case sensitive).")
    print("Type /help to view a help message,")
    print("and /users to see a list of all users.")
    print()

    # Check for special inputs and handle accordingly
    while chat_message != "/quit":
        # Get the time.
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # Set up message preface (used to identify messages)
        preface = active_user + ", " + current_time + ": "
        # Get chat message.
        chat_message = input(preface)
        # If message is just a number, switch active user to that entry.
        # Do not record the number in the log file.
        try:
            chat_message = int(chat_message)
        except:
            chat_message = chat_message
        else:
            # Try switching to the user indicated by the number.
            # If it doesn't work, tell the user it's not working.
            # Then make sure that chat_message is a string so as
            # not to mess up other checks.
            try:
                active_user = user_list[chat_message]
            except:
                print("Cannot switch to a user that doesn't exist!")
            else:
                log_file.write("\n")
                print()
            finally:
                chat_message = str(chat_message)
        # If we're quitting, add space in the text file, and notify user.
        if chat_message == "/quit":
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
            new_user_number = user_count + 1
            user_list.update({new_user_number: new_user})
            print()
            print(new_user + " added!")
            print("Type " + str(new_user_number) + " to send messages as " + new_user + ".")
            print()

        # List all users
        elif chat_message == "/users" or chat_message == "/switch":
            user_counter = 1
            print("Users:")
            while user_counter in user_list:
                print("Type " + str(user_counter) + " to send messages as " + user_list[user_counter])
                user_counter += 1
         
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
            
            # Add to quote file

        # List commands
        elif chat_message == "/commands":
            print()
            print("Commands:")
            print("/add: Add new user.")
            print("/commands: View this message.")
            print("/dice <number>: Roll a die with <number> faces.")
            print("/help: View a help message.")
            print("/nolog: Do not save the following message.")
            print("/quit: Save and quit MultiChat.")
            print("/quote: View random quotes you've added.")
            print("/quote <text>: Add text to the quotes list.") 
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
                random.seed()
                dice_roll = str(random.randrange(1, dice_sides))
                print("You rolled a " + dice_roll + "!")
                log_file.write(active_user + " rolled a " +  str(dice_sides) + "-sided die and rolled a " + dice_roll + "!\n")
            except:
                print("Can't roll die! " + str(dice_sides) + " is not a number!")
        
        # Easter eggs and references
        # Table flipping
        elif chat_message.lower() == "flips table" or chat_message.lower() == "tableflip" or chat_message.lower() == "table flip":
            tableflip = preface + "(╯°□°）╯︵ ┻━┻"
            print(tableflip)
            log_file.write(tableflip + "\n")

        # Shrug
        elif chat_message.lower() == "shrug" or chat_message.lower() == "shrugs" or chat_message == "/shrug":
            shrug = preface + "¯\\_(ツ)_/¯"
            print(shrug)
            log_file.write(shrug + "\n")

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
main()
