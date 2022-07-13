# NSDF-Data-Portal
Repository for the code for the NSDF example data portal.

This data portal automaticly makes avalible data visulizations and interactive data visulizations from Juypter Notebook stored on a GitHub repository. It automates the process of going from Juypter Notebook code to an easily sharable data visulization. 

It accomplishes this using Bokeh servers and Git Python.

This code generates a data portal using the flask web framework. It runs a script that reads in Juypter Notebooks from a GitHub repository and then servers the bokeh servers automaticly. A pipe is run between the flask app and the script to pass the list of running notebooks to the data portal. This allows the data portal to automaticly allow any notebook uploaded to the repo to be viewed and interacted with.

Setting up the data portal to run on a Ubuntu server:

```
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv

REPO=https://github.com/nsdf-fabric/simple-jupyter-notebooks
git clone ${REPO}

git clone https://github.com/okoppe/NSDF-Data-Portal.git
cd NSDF-Data-Portal
```

Set up a virtual enviroment:

```
cd flask_app
python3 -m venv venv
```
activate the virtual enviroment:

```
source venv/bin/activate
```

Install the requirments:

```
python3 -m pip install flask pandas bokeh requests multiprocess notebook numpy scipy OpenVisusNoGui GitPython
```

Edit the `server_pipe_test.py` and edit the first part, for example:

```
your_servers_ip = "155.101.6.68"
local_git_hub_repo_dir = "/home/u0705839/simple-jupyter-notebooks"
link_to_git_hub_repo_to_pull_from = "https://github.com/nsdf-fabric/simple-jupyter-notebooks"
```

Start the Flask server:
- if you want to run locally, modify `app.py` to use `app.run(debug=True)`
- if you want to run globally, modify `app.py` to have `app.run(host="0.0.0.0", port=4999, debug=True)`
  - also: `sudo ufw allow 4999 && sudo ufw reload`

```
python3 app.py
```

You may be prometed to enter your sudo password.

6. Navigate to the url for your local host (should be outputed in the terminal)
