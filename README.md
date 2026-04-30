It is recommended to use a virtual environment (venv) to manage the installation of python packages used to run the code in this folder. This is a simple way of keeping everything contained and organized and will not take up space on your computer. 
To start a virtual environment, run the following command in your terminal while in the folder you will be working in (cd /{path_to_your_folder}/), which asks python to run a command "venv" creating a new virtual environment, which we're naming "venv": 
    python3 -m venv venv
This creates the files for and starts up the environment, adding a folder called "venv", which will contain info the computer uses to run things (we won't have to do anything with it, the computer takes care of the rest).
Next, run the following command, which tells the computer to activate the venv. 
    source ./venv/bin/activate
After running that, you should see (venv) in front of your prompter in your terminal window. You are now in venv mode! 
Double check that this is the case by running: 
    which python 
You should see something like /{path_to_your_folder}/venv/bin/python, and you should NOT see /usr/local/bin/python or /usr/bin/python (that would mean the venv hasn't properly activated, troubleshoot with the internet/AI). 
You are now ready to install the python packages used by the code, which are mainly matplotlib (for plotting), numpy (for faster math), and pandas (for data table storing). These are all super common packages. To install, you will ask pip (the package manager) to install everything in the requirements.txt file. If you have not used pip recently, it may ask you to update, I think you are welcome to do that or ignore it. To install: 
    pip install -r requirements.txt 
Lots of things should happen here as your computer downloads and installs all the preexisting code that this folder relies on. 
If you are using an IDE to run the code, make sure it is pointing at the right python (google this, for example with VS code you will go to the command palette cmd/ctrl + shift + p and then type "python: select interpreter" and choose the one that starts with ./venv/ and is labeled "workspace"). 
Should be good to go! As a summary: 
    python3 -m venv venv
    source ./venv/bin/activate
    which python 
    pip install -r requirements.txt 
Once the venv exists, you can move into or out of the venv with the "source ./venv/bin/activate" or "deactivate" commands. Make sure that the (venv) precedes the prompt whenever running code from this folder to keep everything running smoothly. 
To delete the venv, which can be done whenever you want and will not touch your files (only remove the virtual box where the code runs, not the outputs or the files themselves), run the following command from your project folder, which tells the computer to remove recursively all folders within the folder venv: 
    rm -rf venv
And then you can set it back up using the four commands above. 

Adding all required packages and updating the requirements.txt file: 
requirements.txt:
This file lists the major dependencies for this folder. To update, simply add the package to the list. To install them, run:
    pip install -r requirements.txt

full-requirements.txt: 
This file represents a version snapshot of all dependencies for this folder. If you are getting errors or things are breaking because of dependencies, run the pip install above but replace requirements.txt with full-requirements.txt. 
To update the version snapshot of full-requirements.txt, run:
    python -m pip freeze > full-requirements.txt