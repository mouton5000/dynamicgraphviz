"""Provide useful functions to animate objects.

This module provides the function `animate` that animates an object with an easing function and the function
`get_nb_animating` to get the number of current animated objects. Finally, it provides multiple classic easing
functions. Each function is normalized from 0 to 1.
"""


from math import cos, pi, sin
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject

_animating = 0
"""The number of current playing animations."""


class __EasingAnimation:
    """Animation an object using the specified easing function.

    This class allows to animate an object from one value to another. The object should be a member of a vector space
    implementing the addition of vectors and the multiplication to a real scalar. If u and v are two such vectors, it
    should satisfy u = u * 1 + v * 0 and v = u * 0 + v * 1. For any l from 0 to 1, u * l + v * (1 - l) should represent
    an 'intermediate' vector so that the animation smoothly transforms u into v while smoothly moving l from 0 to 1.

    This class should not be manually instantiated. Use the `easing_function.animate` function instead.

    It is possible to specify the easing_function, the duration of the animation in number of frames and the callback
    to act with the animated vector.
    """

    def __init__(self, begin, end, easing_function, number_frames, callback):
        self.begin = begin
        """Origin vector of the animation."""

        self.end = end
        """Ending vector of the animation."""

        self.easing_function = easing_function
        self.number_frames = number_frames
        self.current_frame = 0
        self.callback = callback

    def animate(self):
        """Build the current value of the animated vector, call the callback with it and return True if this vector is
        the ending vector and False otherwise."""
        global _animating

        scale = self.easing_function(self.current_frame / self.number_frames)
        self.current_frame += 1

        # Call the callback with the current value of the animated vector
        self.callback(self.begin * (1 - scale) + self.end * scale)

        # Stop the animation when all the frames where calculated (scale = 1)
        if self.current_frame > self.number_frames:
            _animating -= 1  # GObject.timeout_add do not need locking, every thing is done in the Gtk main loop.
            if _animating == 0:
                Gtk.main_quit()  # End one of the Gtk inner loops
            return False  # Animation finished

        return True  # Animation not finished


_FPS = 24


def animate_with_easing(begin, end, easing_function, duration, callback):
    """Animate an object using the specified easing function during the given duration.

    Animate an object from one value to another. The object should be a member of a vector space
    implementing the addition of vectors and the multiplication to a real scalar. If u and v are two such vectors, it
    should satisfy u = u * 1 + v * 0 and v = u * 0 + v * 1. For any l from 0 to 1, u * l + v * (1 - l) should represent
    an 'intermediate' vector so that the animation smoothly transforms u into v while smoothly moving l from 0 to 1.

    The animation is computed 24 times per seconds using the `GObject.timeout_add` function. At each tick, the current
    value of the animated vector is computed and a callback is called with that value. That callback should act with
    that value to 'do' the animation (updating a drawn vector, print a value, ...)

    :param begin: the origin object of the animation.
    :param end: the ending object of the animation.
    :param easing_function: the function to compute the intermediate vectors from begin to end. This parameter
    determines the speed of animation from begin to end.
    :param duration: The duration of the animation in milliseconds.
    :param callback: The callback function that will be called with each intermediate vector of the animation.
    """
    global _animating
    animation = __EasingAnimation(begin, end, easing_function, duration / 1000 * _FPS, callback)
    _animating += 1
    GObject.timeout_add(1000 / _FPS, animation.animate)


def get_nb_animating_with_easing():
    """Return the number of currently animated vectors."""
    return _animating


def linear(x):
    """Return the value at x of the 'linear' easing function between 0 and 1."""
    return x


def quadin(x):
    """Return the value at x of the 'quadratic in' easing function between 0 and 1."""
    return x**2


def quadout(x):
    """Return the value at x of the 'quadratic out' easing function between 0 and 1."""
    return -x*(x-2)


def quadinout(x):
    """Return the value at x of the 'quadratic in out' easing function between 0 and 1."""
    if x < 0.5:
        return 2*x**2
    else:
        return 1/2 - x*(2*x-2)


def cubicin(x):
    """Return the value at x of the 'cubic in' easing function between 0 and 1."""
    return x**3


def cubicout(x):
    """Return the value at x of the 'cubic out' easing function between 0 and 1."""
    return (x-1)**3 + 1


def cubicinout(x):
    """Return the value at x of the 'cubic in out' easing function between 0 and 1."""
    if x < 0.5:
        return 4 * x**3
    else:
        return 1/2 * ((2*x - 2)**3 + 2)


def sinin(x):
    """Return the value at x of the 'sinusoid in' easing function between 0 and 1."""
    return 1 - cos(x * pi / 2)


def sinout(x):
    """Return the value at x of the 'sinusoid out' easing function between 0 and 1."""
    return sin(x * pi / 2)


def sininout(x):
    """Return the value at x of the 'sinusoid in out' easing function between 0 and 1."""
    return 1/2 * (1 - cos(x * pi))
