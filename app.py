import os, logging, subprocess, threading, glob, signal, time, traceback,random, yaml
from flask import Flask, render_template, request, Response, send_from_directory, redirect
from multiprocessing import Process,Queue,Pipe
from update_repo_files_pipe import f
from envyaml import EnvYAML

selectedValue2 = " "

# global config
config={}

app = Flask(__name__)
logger=app.logger

#hone directory
@app.route("/")
def index():
    parent_conn,child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()

    BokehLinkDictFlaskCopy = parent_conn.recv()
    p.join()
    return render_template("index.html", noteBookNames=list(BokehLinkDictFlaskCopy.keys()), BokehLinkDictFlaskCopy = BokehLinkDictFlaskCopy,
        bool_files = len(BokehLinkDictFlaskCopy.keys()), selectedValue = "select a notebook")

#path for veiwing data set inline
@app.route('/chooseDataSet/<noteBookName>', methods = ['POST', 'GET'])
def chooseDataSet(noteBookName):
    global selectedValue2
    selectedValue2 = noteBookName

    parent_conn,child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()

    BokehLinkDictFlaskCopy2 = parent_conn.recv()
    p.join()

    return render_template("index.html", noteBookNames=list(BokehLinkDictFlaskCopy2.keys()),
        bool_files = len(BokehLinkDictFlaskCopy2.keys()), selectedValue = selectedValue2,
        linkToBokeh = BokehLinkDictFlaskCopy2[selectedValue2])

#path for downloading file
@app.route("/download", methods=['GET', 'POST'])
def download():

    return send_from_directory(directory=os.getcwd()+"/notebooks", path=selectedValue2, as_attachment=True)

# //////////////////////////////////////////////////////////////////////////
def LoadConfigFile():
    '''
    Loads in the env variables from the config file
    '''
    return EnvYAML('config.yaml')

if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    config=LoadConfigFile()
    logger.info(f"Notebooks {config}")
    logger.info(os.environ)
    app.run(host="0.0.0.0", port=config["port"], debug=bool(config["debug"]))