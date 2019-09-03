import numpy as np
import scipy.stats
import cv2
import matplotlib.pyplot as plt

def auto_contrast_image(image, max_val=2.0, num_bins=2**12):
    final_image_depth = np.uint16
    final_image_depth_max = np.iinfo(final_image_depth).max
    
    # First normalize the image so the mode of the image is 0 (clip everything else)
    image_hist, image_bins = np.histogram(image, num_bins)
    image_mode_val = image_bins[np.argmax(image_hist)]
    image_mode = image - image_mode_val
    image_mode.flat[image_mode.flat < 0] = 0

    # Calculate the KDE for the clipped image.
    # When the density falls below a single normalized count in bin, that'll be our clip value
    image_mode_hist, image_mode_bins = np.histogram(image_mode.flatten(), num_bins, density=True)
    kde = scipy.stats.gaussian_kde(image_mode.flatten())
    kde.set_bandwidth(kde.factor * 3)

    # Extrapolate the KDE at reduce fidelity
    kde_x = np.linspace(0, image_mode_bins.max(), 70)
    kde_vals = kde(kde_x)

    hist_min = image_mode_hist[image_mode_hist > 0].min()
    hist_cutoff = hist_min / 4

    # We could just have a bright image...
    if any(kde_vals < hist_cutoff):
        image_mode_clip_val = kde_x[np.nonzero(kde_vals < hist_cutoff)[0][0]]
    else:
        image_mode_clip_val = kde_x[-1]

    image_clip_cv = final_image_depth(np.clip(final_image_depth_max * (image_mode / image_mode_clip_val), 0, final_image_depth_max))
    image_clip = np.clip(image_mode, 0, image_mode_clip_val)
    
    # Figs for debug
    fig, ax = plt.subplots(1, figsize=(8, 8))
    ax.bar(image_mode_bins[:-1], image_mode_hist, width=image_mode_bins[1], linewidth=0, alpha=0.5)
    ax.set_yscale('log')
    ax.plot(kde_x, kde_vals, '-r', linewidth=2)
    ax.hlines(hist_cutoff, 0, image_bins.max(), linestyles='dashed', alpha=0.8)
    ax.set_ylim((1e-10, 1e3))
    fig.canvas.draw()
    autocontrast_plot = np.frombuffer(fig.canvas.buffer_rgba())

    return {'image_clip': image_clip, 'image_clip_cv': image_clip_cv, 
            'image_mode_val': image_mode_val, 'image_mode_clip_val': image_mode_clip_val,
            'kde_x': kde_x, 'kde_vals': kde_vals, 'autocontrast_plot': autocontrast_plot.copy()}


def apply_gaussian_blur(image, kernel_size=3):
    ''' Apply a Gaussian Blur to the image.
    TODO: Memoize this function
    '''
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

def apply_average_blur(image, kernel_size=3):
    ''' Apply an Averaging Blur to the image.
    TODO: Memoize this function
    '''
    return cv2.blur(image, (kernel_size, kernel_size))