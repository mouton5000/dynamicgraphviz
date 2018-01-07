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
