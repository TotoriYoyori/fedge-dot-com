# Creating New Python Environment Using Terminal
****

Bash terminal is the default choice for working with Linux-based system, which is often the case 
for production environments. You will not have access to a Windows IDE, and must rely purely on your
ability to navigate the terminal.

****

## Create your project folder
`pwd` to check your current working directory. `ls` to check contents. Navigate to
a folder you would like to begin coding in using `cd`.

```
C:/Users/stanm/>
$ cd OneDrive/Desktop/coding/hobby/

C:/Users/stanm/OneDrive/Desktop/coding/hobby/>
$ mkdir my-project

C:/Users/stanm/OneDrive/Desktop/coding/hobby/>
$ cd my-project
```

****

## Install Python .venv inside this folder
At any point when booting up your terminal the first time. Your Python is
only at its **global installation** environment. This global environment is depended on by 
your operating system. Any changes to your global Python have **SERIOUS CONSEQUENCES**. 

Therefore, it is important we use Python in virtual environments only per project.

```
python -m venv .venv
```

The following code means: 

1. `python` uses Python.

2. `-m` runs a module as a script.

3. `venv` uses the built-in venv module from your global Python installation.

4. Create a `.venv` folder inside your project root.

****

## Activate and switch to your new virtual environment
You must do this step every time you boot up the terminal to switch environment. Make
sure you are currently in the project folder.
```
C:/Users/stanm/OneDrive/Desktop/coding/hobby/my-project>
$ source .venv/Scripts/activate
```

****

## Double check you are in the virtual environment
Run this command. 
```
which python
```
If you see a path leading to your current directory, then you know you are using the
correct Python (in the correct virtual environment).

****

## Configure your IDE to use your virtual environment
For most purposes, you will use an IDE to automatically activate your virtual
environment for you. But for the first time to hook up your terminal-created 
virtual environment, do the following:

1. Open project folder in your IDE.

2. Settings > Add Interpreter > Add Local Interpreter

3. Navigate to your .venv/Scripts/python.exe file and select that.

Your IDE and IDE-terminal will now be configured to use that .venv everytime.

****

## Switching environments
If you want to manually switch environments with the terminal, make sure you deactivate
your currently active virtual environments. The terminal can only work inside one
virtual environments at a time.
```
deactivate
```
Moving to another one and activate that one...
```
C:/Users/stanm/OneDrive/Desktop/coding/hobby/>
$ cd my-different-project

C:/Users/stanm/OneDrive/Desktop/coding/hobby/my-different-project>
$ source .venv/Scripts/activate
```

****

## (Bonus) What actually happens?
Activating and switching your virtual environment like that actually only modify your global
`PATH` environment variable so that it shifts your current venv directory to first 
priority, so that next time you enter `python` to run a program, it will look inside
your virtual environment first.

```
# echo $PATH before source .venv/Scripts/activate
C:/my_global/python, etc...

# echo $PATH after
C:/Users/stanm/OneDrive/Desktop/coding/hobby/my-project/venv/Scripts/python, etc.
```
