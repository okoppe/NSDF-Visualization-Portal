from flask import Flask, render_template, request, Response
#from flask import request, Response
import os,sys,io,random
from io import BytesIO
from PIL import Image
from urllib.request import urlopen
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from OpenVisus import *
import base64


### defining cashing and the stuff we need to make plots
def Assert(cond):
    if not cond:
        raise Exception("Assert failed")

# class for loading a dataset and create some cache (typical usage: cloud datasets)
class CachedDataset(PyDataset):

    # constructor
    def __init__(self, args):
        self.local_filename=os.path.abspath(args["local"]).replace("\\","/")
        self.remote_url=args["url"]
        self.remote_access_type = args["access"]
        self.description=args["description"]

        #print("local_filename"    ,self.local_filename)
        #print("remote_url"        ,self.remote_url)
        #print("remote_access_type",self.remote_access_type)
        #print("description",       self.description)

        super().__init__(LoadDatasetCpp(self.remote_url))

        self.num_blocks = len(self.getFields()) * self.getTotalNumberOfBlocks() * len(self.getTimesteps().asVector())
        self.num_blocks_cached = 0

        self.stop_thread=False
        self.thread=None

        self.progress=None
        self.progress_display=None

        #print("Database size",self.getWidth(),self.getHeight(),self.getDepth())
        #print("Fields:",self.getFields())
        #print("Loaded cached dataset")

    # __del__
    def __del__(self):
        self.stopCaching()

    # createAccess
    def createAccess(self, ):

        access_config="""
            <access type='multiplex'>
                    <access type='disk' chmod='rw' url='file://{}' />
                    <access type='{}' url='{}' chmod="r" />
            </access>
        """.format(
            self.local_filename.replace("&","&amp;"),
            self.remote_access_type,
            self.remote_url.replace("&","&amp;"))

        # print("Creating access",access_config)

        access= self.createAccessForBlockQuery(StringTree.fromString(access_config))

        # at this point the cache is enabled with the new local idx file
        Assert(os.path.isfile(self.local_filename))

        return access

    # startCaching
    def startCaching(self, background=True):

        if background:
            self.thread = threading.Thread(target=self.startCaching, args=(False,))
            self.stop_thread=False
            self.thread.start()
            return

        #print("start caching","...")

        access=self.createAccess()

        access.beginRead()

        for field in self.getFields():
            for blockid in range(self.getTotalNumberOfBlocks()):
                for time in self.getTimesteps().asVector():
                    # print("Copying block","time",time,"field",field,"blockid",blockid,"...")
                    buffer =  self.readBlock(blockid, field=field, time=time, access=access)

                     # to debug missing blocks
                    if  False and buffer is None :
                        read_block = db.createBlockQuery(blockid, ord('r'))
                        msg="# {} {} \n".format(blockid,read_block.getLogicBox().toString())
                        os.write(1, bytes(msg,'utf-8'))

                    self.num_blocks_cached += 1
                    self.updateProgress()
                    if self.stop_thread:
                        # print("thread stopped")
                        access.endRead()
                        return

        access.endRead()
        self.thread=None
        #print("caching finished done")

    # stopCaching
    def stopCaching(self):
        #print("stopping caching...")
        self.stop_thread=True
        if self.thread:
            self.thread.join()
            self.thread=None
    # getWidth
    def getWidth(self):
        p2=self.getLogicBox()[1]
        return p2[0]

    # getHeight
    def getHeight(self):
        p2=self.getLogicBox()[1]
        return p2[1]

    # getDepth
    def getDepth(self):
        p2=self.getLogicBox()[1]
        return p2[2]

    # readSlice
    def readSlice(self,dir=0, slice=0,quality=-3, time=0, access=None):

        W,H,D=self.getWidth(), self.getHeight(), self.getDepth()
        x=[0,W] if dir!=0 else [slice,slice+1]
        y=[0,H] if dir!=1 else [slice,slice+1]
        z=[0,D] if dir!=2 else [slice,slice+1]
        ret=self.read(x=x, y=y,z=z, quality=quality,time=time,access=access)

        width,height=[value for value in ret.shape if value>1]
        return ret.reshape([width,height])

    # setProgress
    def setProgress(self,progress, progress_display):
        self.progress=progress
        self.progress_display=progress_display
        self.progress.min=0
        self.progress.max =self.num_blocks

    # updateProgress
    def updateProgress(self):

        if self.progress:
            self.progress.value = self.num_blocks_cached

        if self.progress_display:
            self.progress_display.value = (
                "Caching progress %.2f%% (%d/%d)" % (
                    100 * self.num_blocks_cached/self.num_blocks,
                    self.num_blocks_cached,
                    self.num_blocks))

local_cache="./visus-cache/foam/visus.idx"

sources = [
    {
        "url":"https://mghp.osn.xsede.org/vpascuccibucket1/visus-server-foam/visus.idx?compression=zip&layout=hzorder",
        "access":"CloudStorageAccess",
        "local": local_cache,
        "description":'Open Storage Network (OSN) Pod'
    },
    {
        "url":"http://atlantis.sci.utah.edu/mod_visus?dataset=foam&compression=zip&layout=hzorder",
        "access":"network",
        "local": local_cache,
        "description":'University of Utah Campus Server'
    },
    {
        "url" : "https://s3.us-west-1.wasabisys.com/visus-server-foam/visus.idx?compression=zip&layout=hzorder",
        "access":"CloudStorageAccess",
        "local": local_cache,
        "description": 'Wasabi Commercial Cloud Storage'
    },
    # special random==take any of the above
    {
        "url":"random",
        "access":"random",
        "local":"random",
        "description":"random"
    }
]

def PickSource(index):
    N=len(sources)
    if index==N-1:
        index=random.randint(0,N-2)
    return sources[index]

colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis','ocean', 'gist_earth', 'terrain', 'gist_stern',
             'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
             'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
             'gist_ncar']

# function to plot the image data with matplotlib
def ShowData_buffered(data, cmap=None, plot=None,width = 6):
    ratio = float(data.shape[1])/data.shape[0] #just a scalar

    fig = Figure(figsize=(width,width*ratio))
    axis = fig.add_subplot(1, 1, 1)
    axis.imshow(data,origin='lower', cmap=cmap)
    axis.axis('off')

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    imgs = f"<img src='data:image/png;base64,{data}'/>"
    text = "yes"
    return data

def ShowData_download(data, cmap="viridis", plot=None,width = 6): #saves figure to static
    ratio = float(data.shape[1])/data.shape[0] #just a scalar

    fig = Figure(figsize=(width,width*ratio))
    axis = fig.add_subplot(1, 1, 1)
    axis.imshow(data,origin='lower', cmap=cmap)
    axis.axis('off')
    fig.savefig("static/foam_slice.png")
    return "yes"

def plot_it(cmap):
    first_query=db.readSlice(dir=2, slice=512, access=access, time=0, quality=-3)
    text = ShowData_download(first_query, cmap=cmap, plot=None,width = 6)
    return render_template("index.html", text=text)

db=CachedDataset(sources[0])
access=db.createAccess()


#### start flask section

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/load_img")
def plot_it0():
    return plot_it("viridis")

@app.route('/update_img',  methods=["GET", "POST"])
def updatePlot():
    if request.method == "POST":

        select = request.form
        print(req)

        return plot_it(select['value'])
    return plot_it("viridis")


if __name__ == "__main__":
    app.run(debug=True)
