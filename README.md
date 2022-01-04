# NSDF-Data-Portal
Repo for the code for the NSDF example data portal.

For the inline data display to function properly a Bokeh Server must be set up. To run a Bokeh Server locally follow these steps (steps for running the server on an  ARM64 CPU machine):

```
git clone okoppe/NSDF-Data-Portal (github.com)
cd NSDF-Data-Porta

python3 -m pip install bokeh numpy matplotlib scipy OpenVisusNoGui

# change as needed
PUBLIC_HOSTNAME= node1.nsdf-k8s.nsdf-testbed-pg0.utah.cloudlab.us
python3 -m bokeh serve --show Bokeh_Server --allow-websocket-origin=$PUBLIC_HOSTNAME:5006\
```
Now you can run the flask app by following these instructions:

This page utilizes flask which is a python micro framework. To view the site locally you must run it on a local host.
Process to run locally:

1: open the project directory in terminal or command line

2: set up a virtual enviroment: 

```
python3 -m venv venv
```

3. Next, activate the virtual enviroment:

```
source venv/bin/activate
```

4. Install the requirments:

```
python3 -m pip install -r requirements.txt
```

5. Start the Flask server and local host:

```
python3 main.py
```

6. Navigate to the url for your local host (should be outputed in the terminal)
