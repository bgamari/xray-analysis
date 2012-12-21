import sys
import numpy as np
from numpy import cos, sin, pi, r_, c_
from scipy.interpolate import griddata
from matplotlib import pyplot as pl
from circle_fit import fit_circle
from gaussian_smooth import blur_image
from libtiff import TIFFfile

with_errorbars = False

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
    pl.colorbar()
    pl.show()
    ((cx,cy), r) = fit_circle(np.array(points))
    return (cx,cy)

def cartesian_projection(d, center, r_min=None, r_max=None, nphi=100, nr=1000):
    r_max = min([center[0], center[1], d.shape[0]-center[0], d.shape[1]-center[1]] + ([r_max] if r_max is not None else []))
    if r_min is None: r_min = 0
    xs,ys = np.indices(d.shape)
    rs, phis = np.meshgrid(np.linspace(r_min, r_max, nr), np.linspace(0, 2*pi, nphi))
    sample_pts = (rs * cos(phis) + center[0], rs * sin(phis) + center[1])
    samples = griddata((xs.flatten(),ys.flatten()), d.flatten(), sample_pts, method='linear')
    return np.rec.fromarrays([rs, phis, samples], names='r,phi,i')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--center', metavar='X,Y', help='Center of field')
    parser.add_argument('-b', '--bg', type=argparse.FileType('r'), help='Background image to process')
    parser.add_argument('-q', '--q-min', type=float, help='Minimum momentum transfer to plot')
    parser.add_argument('-Q', '--q-max', type=float, help='Maximum momentum transfer to plot')
    parser.add_argument('files', type=argparse.FileType('r'), nargs='+', help='Files to process')
    args = parser.parse_args()

    center = None
    if args.center is not None:
        x,y = args.center.split(',')
        center = (float(x), float(y))

    background = None
    if args.bg is not None:
        background = None # TODO

    for f in args.files:
        print "Processing %s" % f
        tif = TIFFfile(f.name)
        samples, sample_names = tif.get_samples()
        img = samples[0][0,:,:]
        img = blur_image(img, 3)
        print "Image size", img.shape

        #center = np.array(img.shape) / 2
        if center is None:
            center = prompt_center(img)
            print "Image center", center

        pl.figure()
        pl.imshow(np.log1p(img))
        pl.colorbar()
        pl.savefig('proj1.png')

        p = cartesian_projection(img, center, r_min=args.q_min, r_max=args.q_max) # TODO: Fix scaling
        pl.figure()
        pl.imshow(np.log1p(p['i']), aspect='auto')
        pl.savefig('proj.png')

        pl.figure()
        #p = p[np.logical_and(50 < p['r'], p['r'] < 400)]
        pl.errorbar(p['r'][0,:], np.mean(p['i'], axis=0), marker='+',
                    yerr=np.std(p['i'], axis=0) if with_errorbars else None)
        pl.savefig('i.png')
