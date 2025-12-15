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
from tkinter import simpledialog
from tkinter import ttk
from tkinter import scrolledtext as st
# Optional argument
from typing import Optional

# Set up the GUI
class MultiChat:
    def __init__(self):
        # Prep work to get up and running
        self.build_logs()
        #self.make_logfile()
        self.users = {}
        # Colors
        if os.path.isfile("colors.cfg") == False: # Build color config file
            with open("colors.cfg", "w") as cfg:
                bg_color = "#4A708B"
                button_color = "#d0d8dc"
                scrollbar_trough_color = "#43647b"
                text_bg = "#f1f3f4"
                text_fg = "#000000"
                cfg.write(f'bg_color={bg_color}\n')
                cfg.write(f'lighter_bg={button_color}\n')
                cfg.write(f'scrollbar_trough_color={scrollbar_trough_color}\n')
                cfg.write(f'text_bg={text_bg}\n')
                cfg.write(f'text_fg={text_fg}\n')
        else: # Get colors from file
            with open("colors.cfg", "r") as cfg:
                # TODO: Rework this so it actually cares what
                # variables are called instead of going by position
                bg_color = cfg.readline().strip().split("=")[1]
                button_color = cfg.readline().strip().split("=")[1]
                scrollbar_trough_color = cfg.readline().strip().split("=")[1]
                text_bg = cfg.readline().strip().split("=")[1]
                text_fg = cfg.readline().strip().split("=")[1]
        # Set up windows for display
        self.ROOT = tk.Tk()
        self.ROOT.title("MultiChat")
        self.ROOT.geometry("800x800")
        self.ROOT.configure(bg=bg_color)
        self.ROOT.protocol("WM_DELETE_WINDOW", self.handle_close)
        self.inputfr = tk.Frame(self.ROOT)
        self.outputfr = tk.Frame(self.ROOT)
        self.inputfr.configure(bg=bg_color)
        self.outputfr.configure(bg=bg_color)

        # Setup- users for chat
        adding_users = True
        while adding_users == True:
            self.ROOT.withdraw() # Hide main window
            entry = self.add_user()
            if entry == "q" or entry == "n" or entry == "": # We're done here
                adding_users = False
            # There's got to be a better way. Got to. For now, this works.
            if self.users == {}: # User entered nothing at all
                try: # See if we have saved users first
                    self.load_users()
                    if self.users == {}:
                        self.users["Me"] = 1
                except: # Nope? Okay, population 1: Me
                    self.users["Me"] = 1
        self.active_user = next(iter(self.users))

        # Get the logfile
        self.make_logfile()
        self.ROOT.deiconify() # Get the main window back

        # Input
        # Menu containing all users
        self.switchmenu = ttk.Combobox(self.inputfr, postcommand=self.update_switch_list, width=80)

        self.input = st.ScrolledText(self.inputfr, wrap=tk.WORD, width=70, height=4, bg='white', padx=5, pady=5)
        self.input.vbar.configure(troughcolor=scrollbar_trough_color, bg=button_color)
        self.entry = tk.StringVar()
        self.submit = tk.Button(self.inputfr, text="Send", command=self.send, height=4, width=5, bg=button_color)
        # Output
        self.chatlog = tk.StringVar()
        self.output = st.ScrolledText(self.outputfr, wrap=tk.WORD, height=30, width=80, bg='white', padx=5, pady=5)
        self.output.vbar.configure(troughcolor=scrollbar_trough_color, bg=button_color)

        # Pack it up
        self.output.pack(side="left")
        self.outputfr.pack(pady=15)
        self.switchmenu.pack(side=tk.TOP, pady=5)
        self.input.pack(side="left")
        self.submit.pack(side="left")
        self.inputfr.pack()

        # Set default values for user selection box
        self.switchmenu.set(self.active_user)
        self.switchmenu.bind('<<ComboboxSelected>>', self.update_active_user)
        # Enter key sends message
        self.ROOT.bind_all('<Return>', self.send)

        # And the header for the session- the --Sunday, June whatever 20XX--
        now = date.today()
        session_header = "\n-----" + str(now.strftime("%A, %B %d, %Y")) + "-----\n"
        # Pull in the old logfile's contents
        file_contents = self.log_file.read() + session_header # Get the log file
        # Write the header to the file
        self.log_file.write(session_header)
        print(f"Session started on {now}.")
        # Set up the output
        self.output.insert(tk.INSERT, chars=file_contents)
        self.output.yview_moveto( 1 ) # Scroll to bottom for new messages
        self.output.configure(state ='disabled') # Disable input
        self.chatlog.set(file_contents)

        # Main application time!
        tk.mainloop()

    # Update list of users to pick from
    def update_switch_list(self):
        switchlist = list(self.users.keys())
        self.switchmenu['values'] = switchlist

    # Change user messages are sent under
    def update_active_user(self, event):
        self.active_user = self.switchmenu.get()

    # Open a dialogue and get the name of a new user
    # Saved in cross-compatible format with CLI version!
    def add_user(self):
        # the input dialog
        user_num = len(self.users) + 1
        prompt = "Enter the name of user " + str(user_num) + "\n or hit enter to chat: "
        new_user = simpledialog.askstring(title="MultiChat", prompt=prompt)
        if new_user == "/load":
            self.load_users()
            return ""
        elif new_user != "":
            self.users[new_user] = user_num
        return new_user

    # Test if a message has special content, then save to the log
    def send(self, *args):
        # Send a message, saving it to the log file
        message = str(self.input.get("1.0", "end-1c"))
        save_message = True # Default; overriden by special cases
        save_message = self.test_message(message)
        if save_message:
            # Update the log, both onscreen and in file
            preface = self.get_preface(True)
            message = message.replace("\n", "")
            self.log_file.write(preface + message + "\n")
            self.update_chatlog(preface + message)
        self.input.delete(1.0, "end-1c")

    # Set up message preface (used to identify messages)
    def get_preface(self, with_user: bool):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if with_user:
            return str(self.active_user) + ", " + current_time + ": "
        else:
            return current_time + ": "

    # Update the log
    def update_chatlog(self, message):
        # Update the onscreen log
        self.output.configure(state ='normal') # Allow entry
        self.output.insert(tk.INSERT, chars=str(message + "\n"))
        self.chatlog.set(str(self.chatlog.get() + "\n" + message))
        self.output.configure(state ='disabled') # Stop entry
        self.output.yview_moveto( 1 ) # Scroll to bottom for new messages

    # Check message for any special cases
    def test_message(self, chat_message):
        # Handle special cases and easter eggs
        match chat_message.lower():
            case "/help":
                self.update_chatlog("\n--------Help--------\nWelcome to MultiChat GUI!\nTo switch users, use the dropdown menu.\nTo add a new user, type their name into the dropdown menu.\nTo view more commands, send /commands .\n--------------------\n")
            case "/commands":
                self.update_chatlog("\n-------Commands------")
                self.update_chatlog("/add: Add new user.")
                self.update_chatlog("/commands: View this message.")
                self.update_chatlog("/dice: Roll a die.")
                self.update_chatlog("/exit: Save and quit MultiChat.")
                self.update_chatlog("/load: Load saved users from file. Overwrites current user list!")
                self.update_chatlog("/help: View a help message.")
                self.update_chatlog("/random: Change to a random user.")
                self.update_chatlog("/save: Save list of current users to file.")
                self.update_chatlog("/shrug: Send a shrug emote.")
                self.update_chatlog("--------------------\n")
                return False
            case "/add":
                self.add_user()
                return False
            case "/save":
                with open("saved-users.pkl", "wb") as savefile:
                    try:
                        pickle.dump(self.users, savefile)
                        self.update_chatlog("Users saved.")
                    except Exception as ex: # Something went wrong with saving
                        self.update_chatlog("Could not save users; please notify the developers of what went wrong.")
                        self.update_chatlog(f"Exception: {ex}")
                    return False
            case "/load":
                output = self.load_users()
                self.update_chatlog(output)
                return False
            case "/random":
                if len(self.users) > 1:
                    self.active_user = random.choice(list(self.users.keys()))
                    # We keep things fun around here
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
                        ", time to talk!"
                    ]
                    # Used to notify on which user got picked... the fun way!
                    random_flavor = self.active_user + random.choice(flavor_options) + "!"
                    self.update_chatlog(random_flavor)
                    self.log_file.write(self.get_preface(False) + random_flavor + "\n")
                    return True
            case "flips table" | "tableflip" | "table flip":
                message = self.get_preface(True) + "(╯°□°）╯︵ ┻━┻" + "\n"
                self.update_chatlog(message)
                self.log_file.write(message)
                return False
            case "shrug" | "shrugs" | "/shrug":
                if random.randrange(0,255) == 100:
                    message = self.get_preface(True) + f"Inexplicably, {self.active_user}'s shoulders fail to rise. The power of /shrug is beyond them." + "\n"
                else:
                    message = self.get_preface(True) + "¯\\_('u')_/¯" + "\n"
                self.update_chatlog(message)
                self.log_file.write(message)
                return False
            case "the game":
                message = self.get_preface(False) + "!!! THE GAME HAS BEEN LOST! !!!\nDays since last incident: 0\n" + "\n"
                self.update_chatlog(message)
                self.log_file.write(self.active_user + " has unleashed an infohazard!\n")
                return False
            case "eyes":
                message = self.get_preface(True) + "👀" + "\n"
                self.update_chatlog(message)
                self.log_file.write(message)
                return False
            case "beetlejuice":
                self.update_chatlog("Say it again!")
                self.log_file.write("Say it again!")
                return True
            case "/dice" | "/die":
                dice_sides = simpledialog.askinteger(title="MultiChat Dice Roller 2000", prompt="How many sides?")
                if dice_sides == 1:
                    dice_roll = 1
                else:
                    random.seed()
                    dice_roll = str(random.randrange(1, dice_sides))
                message = self.get_preface(False) + f"{active_user} rolled a {dice_roll}!"
                self.update_chatlog(message)
                self.log_file.write(message)
                return False
            case "/exit" | "/quit":
                self.handle_close()
            case __:
                return True
    
    # Cleanup on window close
    def handle_close(self):
        print("User(s) exited. Wrapping up...")
        self.log_file.close()
        self.ROOT.destroy()

    # Pull in users from file
    def load_users(self):
        if os.path.isfile("saved-users.pkl") == False: 
            print("/load failed: no users found.")
            return {}, "No users to load. Save current users by sending /save. Add users with /add."
        else:
            with open("saved-users.pkl", "rb") as savefile:
                self.users = pickle.load(savefile)
        return "Loaded users from file."

    # Ensure there's a working log directory to store convos in
    def build_logs(self):
        # Set up a log directory
        if platform.system() == "Windows":
            env_home = os.getenv('APPDATA') # Easy
        else: # Linux or MacOS
            try:
                env_home = os.environ['XDG_DATA_HOME']
            except: # Maybe they don't have that set
                env_home = os.environ['HOME'] + "/.local/share"
            if os.path.isdir(env_home) == False: # ...Documents, then?
                env_home = os.environ['HOME'] + "/Documents"
            if os.path.isdir(env_home) == False: # Fine, home directory it is
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
    
    # Build the chat file to log things to
    def make_logfile(self):
        prompt = "Enter a name for this chat, or hit enter to\nselect the default (chat): "
        log_file_name = simpledialog.askstring(title="MultiChat", prompt=prompt)
        if log_file_name == "":
            log_file_name = "chat"
        log_file_name += ".txt"
        log_file = open(log_file_name, "a")
        log_file.close()
        # Now that we are 100% certain the file exists:
        # Attempt to open the log file as read-append.
        self.log_file = open(log_file_name, 'r+')
        return self.log_file


multichat = MultiChat()