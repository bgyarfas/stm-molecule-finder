import os
import glob
import stat
import subprocess
import gc
from itertools import chain
from shutil import copyfile
from operator import methodcaller
from collections import OrderedDict
from datetime import datetime, timezone

from tornado import gen

import numpy as np
import gwyfile
from scipy.optimize import curve_fit

from processing import (
    apply_gaussian_blur
)

import logging
logging.basicConfig(filename='example.log',level=logging.DEBUG)
log = logging.getLogger(__name__)

IMAGE_FOLDER = os.environ.get('IMAGE_FOLDER') or './images'
IMAGE_SIZE = 512
IMAGE_X, IMAGE_Y = np.meshgrid(np.linspace(0, 1.0, IMAGE_SIZE), np.linspace(0, 1.0, IMAGE_SIZE))
IMAGE_XX, IMAGE_YY = IMAGE_X.flatten(), IMAGE_Y.flatten()
IMAGE_XX_YY = np.stack([IMAGE_XX, IMAGE_YY], axis=1)

@gen.coroutine
def update_bokeh_props(bokeh_obj, **kwargs):
    for prop, val in kwargs.items():
        setattr(bokeh_obj, prop, val)

@gen.coroutine
def update_bokeh_dict(bokeh_obj, **kwargs):
    bokeh_obj.update(kwargs)

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def level_image(image):
    def lin_func(x, a, b, c):
        return x[:,0]*a + x[:,1]*b + c

    popt, _ = curve_fit(lin_func, IMAGE_XX_YY, image.flatten())

    bg_fit = lin_func(IMAGE_XX_YY, *popt).reshape(IMAGE_X.shape)

    # subtract it from the original image
    background_sub_image = image - bg_fit

    # Apply a very large Gaussian Blur and subtract it
    # TODO: Do this after detecting the molecule spacing to make the kernel
    # at least 5x the molecule spacing
    background_sub_image -= apply_gaussian_blur(background_sub_image, 127)

    # Make all values positive
    background_sub_image -= background_sub_image.min()

    return background_sub_image

# def normalize_image(image, dtype=np.uint16):
#     ''' Returned a normalized image (dtype=, full range) for proper display '''

#     norm_image = (image - np.min(image)) / np.ptp(image)
#     scaled_image = dtype(np.iinfo(dtype).max * norm_image)
#     return scaled_image

def load_image(image_path):
    ''' Load the image from image_path. Return the leveled height data and the
    extents of the image in nanometers '''
    gwyobj = gwyfile.load(image_path)
    channels = gwyfile.util.get_datafields(gwyobj)
    topography = channels['Topography']
    data = topography.data * 1e9  # Convert to nm
    assert data.shape == (IMAGE_SIZE,IMAGE_SIZE)
    
    data_leveled = level_image(data)
    extent = topography.xreal * 1e9  # Convert to nm
    return data_leveled, extent

def get_image(bokeh_obj):
    ''' Use the CDS of the bokeh image as the global store '''
    return bokeh_obj.data_source.data['image'][0]
