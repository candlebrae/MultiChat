#!/usr/bin/env python3
from datetime import date
from datetime import datetime
import os

# Set up main function
def main():
    # Set up a notes directory
    try:
        if os.path.isdir("./chatlogs") == False: os.mkdir("chatlogs")
        os.chdir("chatlogs")
    except Exception as error:
        print("Error creating or accessing chatlogs folder.")
        print("Please report this error to the creator.")
        print("Error code:", error)

    # Get user names and the file to log to.
    user1, user2 = get_users()
    log_file = get_log_file()
    # Chat and log to file.
    chat(user1, user2, log_file)
    # Close file and finish up.
    log_file.close()

def get_users():
    # While we don't have usable user names and a log file:
    have_information = False
    while have_information == False:
        # Set up as space strings for the verification loops.
        user1 = " "
        user2 = " "
        # Get user names.
        print("Enter q at any point to quit.")
        while user1.isspace() or not user1:
            user1 = input("Enter the name of user 1: ")
            if user1 == "q":
                exit()
        while user2.isspace() == True or not user2:
            user2 = input("Enter the name of user 2: ")
            if user2 == "q":
                exit()
        have_information = True
        return user1, user2
            
def get_log_file():
    # Get or create log file.
    print("Enter a name for this chat, or hit enter to")
    log_file_name = input("select the default (chat): ")
    # Check for empty input.
    if log_file_name.isspace() == True or not log_file_name:
        log_file_name = "chat"
    # Check for quitting.
    if log_file_name == "q":
        exit()
    try:
        # Make sure the file exists so r+ mode won't throw a fit
        # Yes, this is clumsy and a horrible way to do this
        # But it's 5 pm and I've been at this all day, and it's
        # not really intended for capitalism or anything, so.
        # As long as it works!
        log_file = open(log_file_name + ".txt", "a")
        log_file.close()
        # Now that we are 100% certain the file exists:
        # Attempt to open the log file as read-append.
        log_file = open(log_file_name + ".txt", 'r+')
        # If something goes wrong, retry the loop.
    except Exception as error:
        print("Error:", error)
        print("Please try again.")
    # Stop the loop and return the needed information.
    else:
        return log_file

def chat(user1, user2, log_file):
    # Read off the existing chat lines.
    chat_message = ""
    # Set first active user to be user 1, as this is the
    # most expected behavior and prevents sending messages
    # as no one.
    active_user = user1

    # Add a date marker to the top of the log file
    # (or if appending to an existing file, to the end of it).
    try:
        # Clear the terminal to make it look nicer.
        os.system('cls' if os.name == 'nt' else 'clear')
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
    print("Type 1 to send messages as " + user1 + ",")
    print("2 to send messages as " + user2 + ",")
    print("or type q to quit (case sensitive).")
    print()

    # Check for special inputs and handle accordingly
    while chat_message != "q":
        # Get the time.
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # Set up message preface (used to identify messages)
        preface = active_user + ", " + current_time + ": "
        # Get chat message.
        chat_message = input(preface)
        # If message is 1, switch active user to 1.
        # Do not record the number in the log file.
        if chat_message == "1" and active_user != user1:
            active_user = user1
            log_file.write("\n")
            print()
        # If message is 2, switch active user to 2.
        # Do not record the number in the log file.
        elif chat_message == "2" and active_user != user2:
            active_user = user2
            log_file.write("\n")
            print()
        # If message equals q, let the user know the
        # chat is saved, then exit the loop.
        elif chat_message == "q":
            print("\nChat saved.")
            try:
                log_file.write("\n\n")
            except Exception as error:
                print("Error adding text separator to end of file.")
                print("Your log should still be okay, but any later")
                print("additions will not be separated by a line.")
        
        # Easter eggs and references
        # Table flipping
        elif chat_message.lower() == "flips table" or chat_message.lower() == "tableflip" or chat_message.lower() == "table flip":
            tableflip = preface + "(╯°□°）╯︵ ┻━┻"
            print(tableflip)
            log_file.write(tableflip + "\n")

        # Shrug
        elif chat_message.lower() == "shrug" or chat_message.lower() == "shrugs":
            shrug = preface + "¯\\_(ツ)_/¯"
            print(shrug)
            log_file.write(shrug + "\n")

        # Losing the Game (sorry)
        elif chat_message.lower() == "the game":
            print("\n!!! THE GAME HAS BEEN LOST! !!!")
            print("Days since last incident: 0\n")
            you_lost = active_user + " has unleashed an infohazard!\n"
            log_file.write(you_lost)
        
        # Eyes emoji
        elif chat_message.lower() == "eyes":
            eyes = "👀"
            print(preface + eyes)
            log_file.write(preface + "Eyes emoji\n")
        
        # Patas (Spanish for feet, inside joke reference)
        elif "patas" in chat_message.lower():
            print("You know what you did.")
            print("( ´･ω･)\n")
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
