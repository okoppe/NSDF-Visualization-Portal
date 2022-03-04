# NSDF-Data-Portal
Repository for the code for the NSDF example data portal.

This data portal automaticly makes avalible data visulizations and interactive data visulizations from Juypter Notebook stored on a GitHub repository. It automates the process of going from Juypter Notebook code to an easily sharable data visulization. 

It accomplishes this using Bokeh servers and Git Python.

This code generates a data portal running using the flask web framework. It runs a script that reads in Juypter Notebooks from a GitHub repository and then servers the bokeh servers automaticly. A pipe is run between the flask app and the script to pass the list of running notebooks to the data portal. This allows the data portal to automaticly allow any notebook uploaded to the repo to be viewed and interacted with.

Setting up the data portal to run on a Ubuntu server:

```
git clone https://github.com/okoppe/NSDF-Data-Portal.git
git clone LINK TO YOUR REPOSITORY WITH JUYPTER NOTEBOOKS

cd NSDF-Data-Portal

sudo apt-get update -y
sudo apt-get install -y python3-pip
```

Set up a virtual enviroment:

```
cd flask_app

sudo apt-get update -y
sudo apt-get install -y python3-venv
python3 -m venv venv
```
activate the virtual enviroment:

```
source venv/bin/activate
```

Install the requirments:

```
python3 -m pip install -r requirements.txt
```

Start the Flask server and local host:

```
# NOTE to access from outside localhost (NOTE: dangerous!) replace the line 
# app.run(debug=True)
# with the line
# app.run(host="0.0.0.0", port=4999, debug=True)
# set port 4999 open to outside traffic using:
# sudo ufw allow 4999

python3 main.py
```

You may be prometed to enter your sudo password.

6. Navigate to the url for your local host (should be outputed in the terminal)
