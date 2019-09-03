import numpy as np
import os
import time
import gc
import glob
import colorcet as cc
from collections import OrderedDict
from functools import partial
from operator import methodcaller

from tornado import gen

from bokeh.document import without_document_lock
from bokeh.plotting import figure, curdoc
from bokeh.models.widgets import (
    Select,
    TextInput,
    Tabs,
    Panel,
    Toggle,
    Div,
    RangeSlider,
    Slider
)
from bokeh.models import (
    ColumnDataSource,
    Spacer
)
from bokeh.layouts import (
    layout,
    column,
    row
)

# from bokeh.events import LODStart, LODEnd

import helpers
from helpers import (
    IMAGE_SIZE,
    IMAGE_FOLDER,
    update_bokeh_props,
    update_bokeh_dict,
    load_image,
    get_image
)

from processing import (
    apply_gaussian_blur
)

from js_callbacks import (
    LoadingProps,
    get_loading_modal_update_callback,
    get_loading_modal_callback,
    get_loading_error_callback,
    get_loading_workflow_callback,
)

import logging
log = logging.getLogger(__name__)
doc = curdoc()
loading_props = LoadingProps()

RAW_FILES = [''] + sorted(
                map(os.path.basename,
                filter(os.path.isfile,
                glob.glob(os.path.join(IMAGE_FOLDER, '*')))))

raw_image_fig = None
processed_image_fig = None

TOOLTIPS = [
    ("(x,y)", "($x, $y)"),
    ("height (nm)", "@image")
]

raw_image_fig = figure(plot_width=IMAGE_SIZE, plot_height=IMAGE_SIZE, title=f"Image File: XXXXXXXXXXXXX",
                            tools="pan,box_zoom,wheel_zoom,save,reset,hover", 
                            active_scroll="wheel_zoom", y_range=(0,IMAGE_SIZE), 
                            x_range=(0,IMAGE_SIZE), tooltips=TOOLTIPS)

raw_image_fig.yaxis.axis_label = "Pixels"
raw_image_fig.xaxis.axis_label = "Pixels"

x_range = raw_image_fig.x_range
y_range = raw_image_fig.y_range

processed_image_fig = figure(plot_width=IMAGE_SIZE, plot_height=IMAGE_SIZE, title=f"Image File: XXXXXXXXXXXXX",
                            tools="pan,box_zoom,wheel_zoom,save,reset,hover", 
                            active_scroll="wheel_zoom", y_range=y_range, x_range=x_range,
                            tooltips=TOOLTIPS)

processed_image_fig.yaxis.axis_label = "Pixels"
processed_image_fig.xaxis.axis_label = "Pixels"

image_select = Select(title="Image File:", value="", options=list(RAW_FILES), min_height=50, max_width=300)

img = np.random.randint(0, 2**16, (IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint16).astype(np.float)

raw_image_obj = raw_image_fig.image(image=[img], x=[0], y=[0], dw=[IMAGE_SIZE], 
                                    dh=[IMAGE_SIZE], palette=cc.fire)
processed_image_obj = processed_image_fig.image(image=[img.T], x=[0], y=[0], 
                                                dw=[IMAGE_SIZE], dh=[IMAGE_SIZE],
                                                palette=cc.fire)

colormap_scale_slider = RangeSlider(start=0, end=2**16, value=(0,2**16), step=1, title="Colormap Scale (nm)")

blur_slider = Slider(start=1, end=255, step=2, value=3, title="Gaussian Blur Kernel Size")

@gen.coroutine
def update_loading_props(**kwargs):
    update_bokeh_props(loading_props, **kwargs)

@gen.coroutine
@without_document_lock
def image_change_callback(attr, _, image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    data, extent = load_image(image_path)    

    # Don't use the raw nanometers for display
    doc.add_next_tick_callback(partial(update_bokeh_dict, 
        raw_image_obj.data_source.data, image=[data]))

    doc.add_next_tick_callback(partial(update_bokeh_dict, 
        processed_image_obj.data_source.data, image=[data]))

    doc.add_next_tick_callback(partial(update_bokeh_props, 
        colormap_scale_slider, start=data.min(), end=data.max(),
        value=(data.min(), data.max()), step=1e-3))

def colormap_scale_callback(attr, _, new_range):
    ''' Adjust the low/high for the colormap '''
    doc.add_next_tick_callback(partial(update_bokeh_props, 
        raw_image_obj.glyph.color_mapper, low=new_range[0],
        high=new_range[1]))

    doc.add_next_tick_callback(partial(update_bokeh_props, 
        processed_image_obj.glyph.color_mapper, low=new_range[0],
        high=new_range[1]))

@gen.coroutine
@without_document_lock
def blur_slider_callback(attr, _, new_kernel):
    ''' Adjust the Gaussian Blur kernel size '''
    image = get_image(raw_image_obj)
    image_blur = apply_gaussian_blur(image, new_kernel)    

    doc.add_next_tick_callback(partial(update_bokeh_dict, 
        processed_image_obj.data_source.data, image=[image_blur]))

image_select.on_change('value', image_change_callback)
colormap_scale_slider.on_change('value', colormap_scale_callback)
blur_slider.on_change('value', blur_slider_callback)

# loading_props.js_on_change('num_loaded', get_loading_modal_update_callback())

image_select_widgets = row([image_select, colormap_scale_slider, blur_slider, Spacer()], sizing_mode='scale_width')
images_layout = layout([
    [raw_image_fig, processed_image_fig],
], sizing_mode='scale_width')

images_panel = Panel(child=images_layout, title='Images')
center_tabs = Tabs(tabs=[images_panel])

doc.add_root(column([image_select_widgets, center_tabs], sizing_mode='scale_width'))
doc.add_root(loading_props)