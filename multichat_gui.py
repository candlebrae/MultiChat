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
# GUI!
import tkinter as tk


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

# Set up the GUI
class MultiChat:
    def __init__(self):
        # Prep work to get up and running
        self.build_logs()
        self.make_logfile()
        # Set up windows for display
        self.mainwin = tkinter.Tk()
        self.inputfr = tkinter.Frame(self.mainwin)
        self.outputfr = tkinter.Frame(self.mainwin)
        # Input
        self.input = tkinter.Entry(self.inputfr, width=60)
        self.entry = tkinter.StringVar()
        self.input_label = tkinter.Label(self.inputfr, textvariable = self.input)
        self.submit = tkinter.Button(self.mainwin, text="Send", command=self.send)
        # Output
        self.output = tkinter.Label(self.outputfr, textvariable = self.input)
        # Pack it up
        self.output.pack(side="left")
        self.input_label.pack(side="left")
        self.input.pack(side="left")
        self.submit.pack(side="right")
        self.outputfr.pack()
        self.inputfr.pack()
        # Run the window
        tkinter.mainloop()

    def send(self, outfile):
        message = str(self.entry.get())
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # Set up message preface (used to identify messages)
        preface = str(self.active_user) + ", " + current_time + ": "
        self.log_file.write(preface + message + "\n")
        # TODO may need to be a StringVar, not a label?
        self.entry.set(str(self.output.get() + "/n" + preface + message))

    def test_message(self, chat_message):
        # Handle special cases and easter eggs
        pass

    # Ensure there's a working log directory to store convos in
    def build_logs(self):
        # Set up a log directory
        if platform.system() == "Windows":
            env_home = os.getenv('APPDATA') # Easy
        else: # Linux or MacOS
            env_home = os.environ('XDG_DATA_HOME')
            if os.path.isdir(log_dir) == False: # Maybe they don't have that set
                env_home = os.environ['HOME'] + "/.local/share"
            if os.path.isdir(log_dir) == False: # ...Documents, then?
                env_home = os.environ['HOME'] + "/Documents"
            if os.path.isdir(log_dir) == False: # Fine, home directory it is
                env_home = os.environ['HOME']
        # Regardless, we get our own folder
        self.log_dir = env_home + "/multichat"
        try: # Ensure the folder exists and get in there
            if os.path.isdir(self.log_dir) == False: os.mkdir(self.log_dir)
            os.chdir(self.log_dir)
        except Exception as error:
            print("Error creating or accessing chatlogs folder.")
            print("Please report this error to the creator.")
            print("Error code:", error)
    
    def make_logfile(self):
        log_file_name = "test.txt"
        log_file = open(log_file_name, "a")
        log_file.close()
        # Now that we are 100% certain the file exists:
        # Attempt to open the log file as read-append.
        self.log_file = open(log_file_name, 'r+')
        return self.log_file

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

multichat = MultiChat()