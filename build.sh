pyinstaller -F --icon=icon.ico -c -n=multichat multiChat.py
pyinstaller -w --icon=icon.ico -n=multichat_graphical -F multichat_gui.py
#pyinstaller multichat_graphical.spec
