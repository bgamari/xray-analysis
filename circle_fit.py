""" circle_fit -- Ben Gamari (2012)
    Based on,
      L. Maisonobe. "Finding the circle that best fits a set of points" (2007).
      <http://www.spaceroots.org/documents/circle/circle-fitting.pdf>
"""

import numpy as np
from numpy import sqrt, mean, sum
import scipy.optimize

def est_center(points):
    sx = 0
    sy = 0
    q = 0
    n = points.shape[0]
    for i in xrange(0, n-2):
        for j in xrange(i+1, n-1):
            for k in xrange(j+1, n):
                (xi,yi) = points[i]
                (xj,yj) = points[j]
                (xk,yk) = points[k]
                d = (xk-xj)*(yj-yi) - (xj-xi)*(yk-yj)
                if abs(d) < 1e-6: continue
                xc = (yk-yj) * (xi**2+yi**2) \
                   + (yi-yk) * (xj**2+yj**2) \
                   + (yj-yi) * (xk**2+yk**2)

                yc = (xk-xj) * (xi**2+yi**2) \
                   + (xi-xk) * (xj**2+yj**2) \
                   + (xj-xi) * (xk**2+yk**2)
                sx  += +xc / 2 / d
                sy  += -yc / 2 / d
                q += 1
    if q == 0:
        raise RuntimeError("Not enough non-aligned points")
    else:
        return sx/q, sy/q

def est_radius(points, center):
    return mean(sqrt(sum((points - center[newaxis,:])**2, axis=0)))
    
def fit_circle(points, c0=None):
    ps = points
    if c0 is None:
        c0 = est_center(points)
    print 'Estimated center', c0
    
    d = lambda (cx, cy, r): sqrt((points[:,0]-cx)**2 + (points[:,1]-cy)**2) - r
    out = scipy.optimize.leastsq(d, (c0[0], c0[1], 1))
    xopt = out[0]
    print 'Fitted', xopt
    return ((xopt[0], xopt[1]), xopt[2])

