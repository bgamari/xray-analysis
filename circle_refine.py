import numpy as np
from numpy import sum, trunc, pi, sin, cos, exp
import scipy.optimize

def refine_circle((cx0,cy0), r0, img):
    thetas = np.linspace(0, 2*pi, 100)
    sigma = 2
    delta = 3*sigma
    
    def opt((cx,cy,r)):
        def f(theta):
            x = int(cx + r*cos(theta))
            y = int(cy + r*sin(theta))
            xs,ys = np.ogrid[x-delta:x+delta:1, y-delta:y+delta:1]
            weights = 1./2/pi * exp(-((xs-x)**2 + (ys-y)**2) / 2 * sigma)
            return np.average(img[xs,ys], weights=weights)
        return -sum(f(theta) for theta in thetas)

    (cx,cy,r) = scipy.optimize.fmin(opt, np.array([cx0, cy0, r0]))
    print "Refined circle", (cx,cy), "radius", r
    return ((cx,cy),r)
