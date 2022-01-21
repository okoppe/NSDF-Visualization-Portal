# NSDF-Data-Portal
Repo for the code for the NSDF example data portal.

For the inline data display to function properly a Bokeh Server must be set up. To run a Bokeh Server locally follow these steps (steps for running the server on an  ARM64 CPU machine):

```
git clone https://github.com/okoppe/NSDF-Data-Portal.git
cd NSDF-Data-Portal

sudo apt-get update -y
sudo apt-get install -y python3-pip

python3 -m pip install bokeh numpy matplotlib scipy OpenVisusNoGui

# change as needed
PUBLIC_HOSTNAME=$(hostname -f)
PORT=5006
echo URL: http://$PUBLIC_HOSTNAME:$PORT/Bokeh_Server"
python3 -m bokeh serve --show Bokeh_Server --allow-websocket-origin=$PUBLIC_HOSTNAME:$PORT
```
Now you can run the flask app by following these instructions:

This page utilizes flask which is a python micro framework. To view the site locally you must run it on a local host.
Process to run locally:

1: open the project directory in terminal or command line

2: set up a virtual enviroment: 

```
sudo apt-get update -y
sudo apt-get install -y python3-venv
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
# NOTE to access from outside localhost (NOTE: dangerous!) replace the line 
# app.run(debug=True)
# with the line
# app.run(host="0.0.0.0", port=5000, debug=True)

python3 main.py
```

6. Navigate to the url for your local host (should be outputed in the terminal)
