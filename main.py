from flask import Flask, render_template, request, Response, send_from_directory
import os

####flask app

app = Flask(__name__)
#hone directory
@app.route("/")
def index():
    return render_template("index.html")

#path for veiwing data set inline
@app.route("/inline_data")
def plot_it0():
    return render_template("index.html", text="yes")

#path for downloading file
@app.route('/download', methods=['GET', 'POST'])
def download():
    return send_from_directory(directory=os.getcwd()+"/static/downloads", path="demo_slice_foam_dataset_from_cloud_sources.py", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
