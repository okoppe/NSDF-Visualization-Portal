#imports
import os,io,random
import sys
from io import BytesIO
from PIL import Image
from urllib.request import urlopen
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from OpenVisus import *
import base64
import numpy as np
import time as tm
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput, Dropdown, LinearColorMapper, Text
from bokeh.plotting import figure


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
]

#---------------------------------------------------bokeh server Code-----------------------------------------------------------

# Set up data
data_source_dict = {"Open Storage Newtork (OSN) Pod":0, "University of Utah Campus Server":1, "Wasabi Commercial Cloud Storage":2}
slice_orthogonal_dict = {"X":0, "Y":1, "Z":2}

data_source_names = ['Open Storage Newtork (OSN) Pod', 'University of Utah Campus Server', 'Wasabi Commercial Cloud Storage']
slice_orthogonal_names = ['X', 'Y', 'Z']

slice_orthogonal_value = "Z"
ds_source = "University of Utah Campus Server"
color_0 = "Viridis256"

#inital slice
db=CachedDataset(sources[int(data_source_dict[ds_source])])
access=db.createAccess()
data = db.readSlice(dir=slice_orthogonal_dict[slice_orthogonal_value], slice=512, access=access, time=0, quality=-3)

#set up ColumnDataSource's
plot_text2 = "Data Source: " + ds_source
text = [plot_text2]

source_text = ColumnDataSource(data=dict(text=text))
source = ColumnDataSource(data=dict(image=[data], color_palette=[color_0]))
color_mapper = LinearColorMapper(palette=color_0)

# Create plot

plot = figure(height=500, width=500, title="Slice: 512, Time: 0, Resolution: -3, Colormap: " + str(color_0) + ", Direction: " + str(slice_orthogonal_value),
             tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])

glyph = Text(x=0, y=-1, text="text", angle=0)
plot.add_glyph(source_text, glyph)

#remove toolbar
plot.toolbar_location = None
plot.axis.visible = False
plot.grid.visible = False
plot.outline_line_color = None

#create the image
fig = plot.image(image='image', x=0, y=0, dw=10, dh=10, source=source, color_mapper=color_mapper)


# Set up widgets

#dropdown menus
color_scale = Dropdown(label='Colormap', menu=['Magma256', 'Inferno256', 'Plasma256', 'Viridis256', 'Cividis256', 'Spectral11'])
data_source = Dropdown(label='Data Source', menu=data_source_names)
orthogonal_axis_value = Dropdown(label='Slice orthogonal to axis', menu=slice_orthogonal_names)

#sliders
slice = Slider(title="slice", value=512, start=0, end=1023, step=1)
time = Slider(title="time", value=0, start=0, end=3, step=1)
quality = Slider(title="Resolution ", value=-3, start=-5, end=0, step=1)

sys.setrecursionlimit(100000) #change recursion limit (bumps up to default limit on occasion when caching data)

# Set up callbacks

def colormap_change(event):
    '''
    This function defines what happens when the color_scale dropdown menu's value is changed.
    It changes the colormap of the plot.
    '''
    fig.glyph.color_mapper = LinearColorMapper(palette=event.item)
    global color_0
    color_0 = event.item
    slice_num = slice.value
    time_val = time.value
    quality_val = quality.value
    plot.title.text = "Slice: " + str(slice_num) + ", Time: " + str(time_val) + ", Resolution: " + str(quality_val) + ", Colormap: " + str(color_0) + ", Direction: " + str(slice_orthogonal_value)

color_scale.on_click(colormap_change)

def set_source(event):
    '''
    This function defines what happens when the data_source dropdown menu's value is changed.
    It changes the data source used to get the data. It creates a new access.
    '''
    global ds_source
    ds_source = event.item

    slice_num = slice.value
    time_val = time.value
    quality_val = quality.value

    db=CachedDataset(sources[int(data_source_dict[ds_source])])
    access=db.createAccess()
    new_data = db.readSlice(dir=slice_orthogonal_dict[slice_orthogonal_value], slice=slice_num, access=access, time=time_val, quality=quality_val)
    source.data = dict(image=[new_data])
    plot.title.text = "Slice: " + str(slice_num) + ", Time: " + str(time_val) + ", Resolution: " + str(quality_val) + ", Colormap: " + str(color_0) + ", Direction: " + str(slice_orthogonal_value)

    new_text = ["Data Source: " + ds_source]
    source_text.data = dict(text=new_text)

data_source.on_click(set_source)

def set_orthagonal_axis(event):
    '''
    This function defines what happens when the orthogonal_axis_value dropdown menu's value is changed.
    It changes the orthogonal axis of the plot.
    '''
    global slice_orthogonal_value
    slice_orthogonal_value = event.item

    slice_num = slice.value
    time_val = time.value
    quality_val = quality.value

    new_data = db.readSlice(dir=int(slice_orthogonal_dict[slice_orthogonal_value]), slice=slice_num, access=access, time=time_val, quality=quality_val)
    source.data = dict(image=[new_data])
    plot.title.text = "Slice: " + str(slice_num) + ", Time: " + str(time_val) + ", Resolution: " + str(quality_val) + ", Colormap: " + str(color_0) + ", Direction: " + str(slice_orthogonal_value)

orthogonal_axis_value.on_click(set_orthagonal_axis)



def update_data(attrname, old, new):
    '''
    This function defines what happens when any of the sliders values are changed.
    It updates the plot with the new values from the sliders.
    '''

    slice_num = slice.value
    time_val = time.value
    quality_val = quality.value

    new_data = db.readSlice(dir=slice_orthogonal_dict[slice_orthogonal_value], slice=slice_num, access=access, time=time_val, quality=quality_val)
    source.data = dict(image=[new_data])
    plot.title.text = "Slice: " + str(slice_num) + ", Time: " + str(time_val) + ", Resolution: " + str(quality_val) + ", Colormap: " + str(color_0) + ", Direction: " + str(slice_orthogonal_value)


def loading_title(attrname, old, new):
    plot.title.text = "Loading..."

#listen for a change in a slider
for w in [time, slice, quality]:

    w.on_change('value', loading_title)
    tm.sleep(3)
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = column(slice, time, quality, color_scale, orthogonal_axis_value, data_source)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "NSDF Foam Slice Bokeh Server"
