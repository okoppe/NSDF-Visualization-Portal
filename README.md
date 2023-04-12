# NSDF-Visualization-Portal

Live demo of a visualization portal using this repository: http://155.101.6.68:5999.

Docker hub project for this repository: https://hub.docker.com/repository/docker/okoppe/nsdf-data-portal/general


## Overview:

This data portal monitors a GitHub repository where it scans for new Jupyter Notebooks with visualizations created with Bokeh or Panel. When a new notebook is added to the GitHub repository, it is read in and the data visualization is automatically made available on the web. 
This automates the process of sharing Jupyter Notebook visualizations to the web.


## Tools used:
This code generates a data portal using the flask web framework. It runs a script that reads in Jupyter Notebooks from a GitHub repository and then utilizes bokeh’s server capabilities to share notebooks to the web. A pipe is run between the flask app and the script to pass the list of running notebooks to the data portal. This allows the data portal to automatically allow any notebook uploaded to the repo to be viewed and interacted with.


## Running via Docker:

```docker build -t nsdf-data-portal .```
```docker run -p 5999-6005:5999-6005 -e HOST_IP={YOUR_IP} -e REPO_LINK='https://github.com/okoppe/Juypter-Notebook-Repo' -d nsdf-data-portal```


## Running on a Ubuntu server without Docker:

```
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv

git clone https://github.com/okoppe/NSDF-Data-Portal.git
cd NSDF-Data-Portal
```

Set up a virtual environment:

```
cd flask_app
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r app/requirements.txt
```

Edit the `config.yaml` file and change as needed

```

# do the first clone, change as needed
git clone https://github.com/okoppe/Juypter-Notebook-Repo /tmp/nsdf-data-portal/Juypter-Notebook-Repo

# before running allow some port range, e.g
sudo ufw allow 5000:6000/tcp

# run the flask app
cd app
source venv/bin/activate

# this may be helpful to release old processes
# sudo killall python3

./run.sh
```

You may be prompted to enter your sudo password.

6. Navigate to the url for your local host (should be outputted in the terminal)


## Requirements for notebooks that can be used with the NSDF-Data-Portal:

1. Visualizations must be created with Bokeh or Panel.

2. Add the following package install function to your code and use it to install all packages your code requires. Each notebook gets its own virtual environment so packages must be installed in this new environment.

def install(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        subprocess.call(['pip3', 'install', package_name])

install('numpy')
install('bokeh')

3. Add the following code snippet to check if your notebook is being run for the web:
from bokeh.plotting import output_notebook, show, curdoc

def in_notebook():
    from IPython import get_ipython
    if get_ipython():
        return True
    else:
        return False 
    
ShowWebpage = True

if in_notebook():
    ShowWebpage = False

if ShowWebpage:
    pass
else:
    output_notebook()

4. Add the following code snippet at the end of your notebook. It determines if the notebook should serve the data visualization in line or in a web compatible way.

if ShowWebpage:
    modify_doc(curdoc())
else:
    show(modify_doc)


