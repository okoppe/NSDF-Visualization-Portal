# NSDF-Data-Portal
Repo for the code for the NSDF example data portal.

The website utilizes flask which is a python micro framework. To view the site locally you must run it on a local host.
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

TODO:
fix the download button, add funcitonality so that drop down menu for data sets changes what code is show when in-line button is run (currently always displays the foam slice data set, also need to generlize the foam slice vis code so I can use it for other data sets), add interactivity to the inline vis (all buttons that appear do not work at the moment.) Add cloud lab links once we have them.
