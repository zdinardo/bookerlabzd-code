# BookerLabZD-code 
Contains code for intaking and plotting FPLC, UV, and MS data from our instruments. This is very incomplete and is meant as a tool to get started. 
Please feel free to email me (zdinardo at sas.upenn.edu or zachdinardo at gmail.com) with questions or bugs. 

## Streamlit app for lightweight FPLC plotting 
For plotting FPLC traces, I have converted the FPLC plotting notebook into a web app. Going to https://bookerlabzd-code-fplc.streamlit.app/ will prompt you to upload your csv and then choose any parameters you want to plot, including axes, colors, fractions, peak labels, and more. Please let me know if other annotations or functionality would be helpful. It should be fairly self-explanatory. 

## Setup and virtual environment (for jupyter notebooks)
<details>
    <summary> Click to expand setup instructions </summary>

### First time setup of the Virtual Environment (venv) 
It is recommended to use a virtual environment (venv) to manage the installation of python packages used to run the code in this folder. This is a common, simple way of keeping everything contained and organized and will not take up space on your computer. AIs are super helpful for getting everything set up and any troubleshooting you might need. 
These are the commands you'll run: 
```bash
python3 -m venv venv
source ./venv/bin/activate
which python 
pip install -r requirements.txt 
```

#### Initiating the venv 
To start a virtual environment, run the following command in your terminal while in the folder you will be working in (`cd /{path_to_your_folder}/`), which asks python to run the command `venv` creating a new virtual environment, which we're naming "venv" (you can call it whatever you want by changing the second "venv" but either "venv" or "env" are common practice: 
```bash
python3 -m venv venv
```
This creates the files for and starts up the environment, adding a folder called "venv", which will contain info the computer uses to run things (we won't have to do anything with it, the computer takes care of the rest).
Next, run the following command, which tells the computer to activate the venv. 
```bash
source ./venv/bin/activate
```
After running that, you should see (venv) in front of your prompter in your terminal window. You are now in venv mode! 
Double check that this is the case by running: 
```bash
which python 
```
If that gives, an error, try `which python3` or troublshoot online. You should see something like `/{path_to_your_folder}/venv/bin/python`, and you should NOT see `/usr/local/bin/python` or `/usr/bin/python` (that would mean the venv hasn't properly activated, troubleshoot with the internet/AI). 

#### Installing packages 
You are now ready to install the python packages used by the code, which are mainly `matplotlib` (for plotting), `numpy` (for faster math), and `pandas` (for data table storing). These are all super common packages. To install, you will ask pip (the package manager) to install everything in the requirements.txt file. If you have not used pip recently, it may ask you to update, I think you are welcome to do that or ignore it. To install: 
```bash
pip install -r requirements.txt 
```
Lots of things should happen here as your computer downloads and installs all the preexisting code that this folder relies on. 
If you are using an IDE to run the code, make sure it is pointing at the right python (google this, for example with VS code you will go to the command palette cmd/ctrl + shift + p and then type `python: select interpreter` and choose the one that starts with `./venv/` and is labeled "workspace"). 

#### Adding all required packages / updating the requirements.txt file: 
`requirements.txt` lists the major dependencies for this folder. To update this list, simply add the package to the list and match the formatting. To install them, uncomment the jupyter line if you are using the notebooks, then run:
```bash
pip install -r requirements.txt
```
`full-requirements.txt` represents a version snapshot of all dependencies for this folder. If you are getting errors or things are breaking because of dependencies, run `pip install -r full-requirements.txt` to make sure all packages match what I was using when I wrote the code. 
To update the version snapshot of full-requirements.txt, run:
```bash
python -m pip freeze > full-requirements.txt
```

### Using the venv when relaunching 
Once the venv exists, you can move out of or into the venv by running `deactivate` or `source ./venv/bin/activate`. Make sure that `(venv)` precedes the prompt whenever running code from this folder to keep everything running smoothly. 

### Deleting the venv
To delete the venv, which can be done whenever you want and will not touch your files (only remove the virtual box where the code runs, not the outputs or the files themselves), run the following command from your project folder, which tells the computer to remove recursively all files and folders within the folder venv: 
```bash
rm -rf venv
```
And then you can set it back up using the four commands above. 
</details>
