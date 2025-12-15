# MultiChat
A simple, personal chat program that runs on a single computer. No Internet, just you.

!! For existing users: the prompt_toolkit library is now a required dependency. If you're using MultiChat as a script (ending in .py), please make sure that you install this! !!

## Simple and Local
MultiChat was created with ease of use in mind. You add a few users of your choice to the session, and specify the name of the chat log. After that, it's a  chat application that's simple to use. Type a number to change who's talking, and ``/quit`` to quit. Hit enter to send messages. 

There's only one computer using MultiChat: yours. It will never connect to the Internet, and you can't chat with someone on the other side of the world with it. This is your chat program, and yours alone.

## Self-talk
MultiChat was intended for folks that need to talk to the voices within them for one reason or another. Maybe you think better when you talk to yourself. Maybe it's a handy tool for simulating social interactions ahead of time. Maybe you need a tool for roleplay, or want to write as though your characters were in a chat room. Maybe you have DID and need a tool for interacting with alters. Maybe you just want to mess around. Whatever the reason, MultiChat was made to let you have that conversation.

## Commands
There are a handful of commands you can use in MultiChat, ranging from adding more users to the session to hiding messages from the log file. All of these commands can be viewed by sending ``/commands`` in the chat. You can also view a help message by sending ``/help`` at any time.

## Dependencies and Usage
[Executables can be found here](https://codeberg.org/Candlebrae/MultiChat/releases), and have no additional dependencies. You should be able to download the executable for your operating system and run it as per usual (double click the .exe for Windows, and run `multiChat` or `./multichat` in the terminal for Linux). Note that executables can be a bit buggy, as Python is an interpreted language and it took some workarounds to "compile" it.

If you'd like to run the Python program from source, you'll need Python 3. [You can get the latest version of Python here.](https://www.python.org/downloads/) You'll also need to install the termcolor library (e.g. ``pip install termcolor``) and the [prompt-toolkit library](https://github.com/prompt-toolkit/python-prompt-toolkit/tree/main) (``pip install prompt_toolkit``). To run MultiChat, navigate to the folder you saved it to and open a console there. Type ``python multiChat.py`` and you're good to go. If you're on Windows, you could also double-click the .py file to run it.

Regardless of which version you use, chat logs are stored in a folder called .multichat. This folder is in .local/share/multichat on Linux, and AppData on Windows. They are stored in plaintext for easy browsing.

## How to Download

If you're not familiar with Git repositories, there are a few ways that you can download this! Here are the easiest two:

- If you don't have Git installed, there's a little button with a download icon on it on this page. It's on the right, above the list of files and below the bar that says "Commits." Click that, and select your preferred format to download the files.
- If you have Git installed, you can run ``git clone https://codeberg.org/Candlebrae/MultiChat.git`` in a terminal/console. That will download a copy of this repository.

## Custom Flavortext

The /random command uses a list of flavortext to make its random selections more interesting. If you'd like to add your own flavortext:

1. Create a file with the name, "random_flavortext.txt".
2. Write your flavortext of choice in this file. One piece of flavortext per line. Any instances of "NAME" (all caps!) will be replaced with the randomly selected user.
3. Place the random_flavortext.txt file in one of two places: either the same directory multiChat is located in, or in your settings directory. (To find your settings directory, run /settings)
