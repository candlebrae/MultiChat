# MultiChat
A simple, personal chat program that runs on a single computer. No Internet, just you.

## Simple and Local
MultiChat was created with ease of use in mind. You add a few users of your choice to the session, and specify the name of the chat log. After that, it's a  chat application that's simple to use. Type a number to change who's talking, and ``/quit`` to quit. Hit enter to send messages. 

There's only one computer using MultiChat: yours. It will never connect to the Internet, and you can't chat with someone on the other side of the world with it. This is your chat program, and yours alone.

## Self-talk
MultiChat was intended for folks that need to talk to the voices within them for one reason or another. Maybe you think better when you talk to yourself. Maybe you're a system and need to have a conversation externally. Maybe it's a handy tool for simulating social interactions ahead of time. Maybe you need a tool for roleplay, or want to write as though your characters were in a chat room. Maybe you just want to mess around. Whatever the reason, MultiChat was made to let you have that conversation.

## Commands
There are a handful of commands you can use in MultiChat, ranging from adding more users to the session to hiding messages from the log file. All of these commands can be viewed by sending ``/commands`` in the chat. You can also view a help message by sending ``/help`` at any time.

## Dependencies and Usage
All you need to have installed is Python 3. 

To run MultiChat, navigate to the folder you saved it to and open a console there. Type ``python multiChat.py`` and you're good to go. If you'd like, you could make a shortcut to the file so that you don't need to do this manually every time. If you're on Linux, you could chuck it in .local/bin to make it easier for you to execute (just be aware that chat log files are stored in a directory called "chatlogs" placed in the same directory as the program).

## How to Download

If you're not familiar with Git repositories, there are a few ways you can download this! Here are the easiest two:

- If you don't have Git installed, there's a little button with a download icon on it on this page. It's on the right, above the list of files and below the bar that says "Commits." Click that, and select your preferred format to download the files.
- If you have Git installed, you can run ``git clone https://codeberg.org/Candlebrae/MultiChat.git`` in a terminal/console. That will download a copy of this repository.
