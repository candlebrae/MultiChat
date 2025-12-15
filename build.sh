git add *
echo -n "Commit message: "
read message
git commit -m "$message"

echo -n "Build executables? y/n: "
read buildit
if [ $buildit == "y" ]; then
    pyinstaller -F --icon=icon.ico -c -n=multichat multiChat.py
    cd GUI-version
    pyinstaller -w --icon=icon.ico -n=multichat_graphical -F multichat_gui.py
    echo "Done."
fi
