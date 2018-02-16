"""Provide some useful functions about geometry."""

from euclid3 import Vector2
import math

__author__ = "Dimitri Watel"
__copyright__ = "Copyright 2018, dynamicgraphviz"


def rotate(v, alpha):
    """Return a new 2D vector equal to v rotated with the angle alpha."""
    cs = math.cos(alpha)
    sn = math.sin(alpha)
    return Vector2(v.x * cs - v.y * sn, v.x * sn + v.y * cs)


def intersect(rect1, rect2):
    """ Return True if the two rectangles rect1 and rect2 intersect. """
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return (x1 + w1 > x2 and x2 + w2 > x1) and (y1 + h1 > y2 and y2 + h2 > y1)