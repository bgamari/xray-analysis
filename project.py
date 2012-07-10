import sys
from PIL import Image
import numpy as np
from numpy import cos, sin, pi, r_, c_
from scipy.interpolate import griddata
from matplotlib import pyplot as pl
from circle_fit import fit_circle

def prompt_center(d):
    points = []
    fig = pl.figure()

    def onclick(event):
        points.append((event.xdata, event.ydata))
        pl.plot([event.xdata], [event.ydata], 'w+')
        fig.canvas.draw()

    def key_press(event):
        if event.key == "enter":
            pl.close()

    fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('key_press_event', key_press)
    pl.imshow(np.log1p(d))
    pl.autoscale(enable=False)
    pl.show()
    ((cx,cy), r) = fit_circle(np.array(points))
    return (cx,cy)

def cartesian_projection(d, center, r_min=None, r_max=None, nphi=300, nr=100):
    r_max = min([center[0], center[1], d.shape[0]-center[0], d.shape[1]-center[1]] + ([r_max] if r_max is not None else []))
    if r_min is None: r_min = 0
    xs,ys = np.indices(d.shape)
    rs, phis = np.meshgrid(np.linspace(r_min, r_max, nr), np.linspace(0, 2*pi, nphi))
    sample_pts = (rs * cos(phis) + center[0], rs * sin(phis) + center[1])
    samples = griddata((xs.flatten(),ys.flatten()), d.flatten(), sample_pts, method='linear')
    return np.rec.fromarrays([rs, phis, samples], names='r,phi,i')

img = Image.open(sys.argv[1]).convert('F')
print "Value extrema", img.getextrema()
img = np.array(img, dtype='f')
print "Image size", img.shape
center = np.array(img.shape) / 2

center = prompt_center(img)
print "Image center", center
pl.figure()
pl.imshow(img)
pl.savefig('proj1.png')

p = cartesian_projection(img, center)
pl.figure()
pl.imshow(p['i'], aspect='auto')
pl.savefig('proj.png')

pl.figure()
p = p[np.logical_and(100 < p['r'], p['r'] < 400)]
pl.errorbar(p['r'][0,:], np.mean(p['i'], axis=0), yerr=np.std(p['i'], axis=0))
pl.savefig('i.png')
