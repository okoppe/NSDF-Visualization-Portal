# NSDF-Data-Portal
Repo for the code for the NSDF example data portal.

For the inline data display to function properly a Bokeh Server must be set up. To run a Bokeh Server locally follow these steps:

1. Open the project directory in terminal or command line (cd \folder-dirctory (on mac)).

2. Run the Bokeh server files with the following comand:

```
bokeh serve --show Bokeh_Server
```
This should create a bokeh server at the location of: http://localhost:5006/Bokeh_Server


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
