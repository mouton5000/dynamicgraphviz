"""Provide a class to display and animate graphs.

This module provide the class `GraphDrawer` that display and animate graphs. This class is a Gtk window containing a
drawing area. That area is used to draw a graph given as a parameter and is updated each time the graph is changing
or when it is manually asked to.

The module also provide all the default parameters of the drawing :
- the width and the height of the window
- the internal and external colors, the external line width, and the radius of the nodes
- the color, the line width of the edges and arcs
- the arrow length of the arcs
- the color, the font and the font size of the labels of the nodes, edges and arcs.
- the distance between an edge or an arc and its label.

The class `GraphDrawer` contains method to override those properties and update the drawings.

Finally, that class also provide a method `GraphDrawer.pause` to pause the execution of the code until the user click
on the window.

"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import math
import cairo
from pubsub import pub
from euclid3 import Point2, Vector2
from dynamicgraphviz.gui.animations.easing_animations import get_nb_animating_with_easing, animate_with_easing, sininout
from copy import copy
from dynamicgraphviz.exceptions.graph_errors import *
from dynamicgraphviz.graph.undirectedgraph import UndirectedNode, Edge
from dynamicgraphviz.graph.directedgraph import DirectedNode, Arc
import random

__author__ = "Dimitri Watel"
__copyright__ = "Copyright 2018, dynamicgraphviz"

WIDTH = 1400
"""Width of the shown window."""
HEIGHT = 800
"""Height of the shown window."""

NODE_COLOR = (0, 0, 0)
"""Default color of the external line of the drawn nodes."""
NODE_FILL_COLOR = (255, 255, 255)
"""Default internal color of the drawn nodes."""
NODE_LINE_WIDTH = 2
"""Default width of the external line of the drawn nodes."""
NODE_RADIUS = 20
"""Default radius of the drawn nodes."""

NODE_LABEL_COLOR = (0, 0, 0)
"""Default color of the label of a node."""
NODE_LABEL_FONT = ("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
"""Default font of the label of a node."""
NODE_LABEL_FONT_SIZE = 20
"""Default font size of the label of a node."""

LINK_COLOR = (0, 0, 0)
"""Default color of a drawn edge/arc."""
LINK_LINE_WIDTH = 2
"""Default width of the lines of a drawn edge/arc."""
LINK_ARROW_LENGTH = 10
"""Default size of the arrow of a drawn edge/arc."""

LINK_LABEL_DISTANCE = 20
"""Default distance from the center of the edge/arc to its label."""
LINK_LABEL_COLOR = (0, 0, 0)
"""Default color of the label of an edge/arc."""
LINK_LABEL_FONT = ("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
"""Default font of the label of an edge/arc."""
LINK_LABEL_FONT_SIZE = 20
"""Default font size of the label of an edge/arc."""


class GraphDrawer(Gtk.Window):
    """A Gtk window used to draw a graph.

    This class is a Gtk window containing a drawing area. That area is used to draw a graph given as a parameter and
    is updated each time the graph is changing or when it is manually asked to.

    The drawing are done using the cairo library.

    The automatic updates are the following:
    - when a node, an edge or an arc is added, the drawing area is updated;
    - when a node, an edge or an arc is removed, the drawing area is updated.
    Those automatic updates are done using the `pubsub` library. The drawer subscribes to the following topic where
    id_graph is the id of the current drawn graph (computed with the `id` function):
    - 'id_graph.add_node' with one argument corresponding to the added node, and one keyword argument name `draw` (see
    below)
    - 'id_graph.add_arc' with one argument corresponding to the added edge or arc, and one keyword argument name `draw`
    (see below)
    - 'id_graph.remove_node' with one argument corresponding to the removed node, and one keyword argument name `draw`
    (see below)
    - 'id_graph.remove_arc' with one argument corresponding to the removed edge or arc, and one keyword argument name
    `draw` (see below)

    The manually updates are done using the following methods:
    - `set_color`: change the external color of a node or the color of an edge or an arc, the default
    color is black;
    - `set_node_color_fill`: change the internal color of a node, the default color is white
    - `set_line_width`: change the width of the external line of a node or the width of the lines of
    an edge or an arc, the default width is 2 pixels;
    - `set_node_color_fill`: change the internal color of a node, the default color is white
    - `set_node_radius`: change the radius of a node, the default radius is 20 pixels;
    - `set_label`: change the text of the label associated with a node or an edge or an arc, the
    default value for a node is its index, and the default value for an edge or an arc is the empty string;
    - `set_label_color`: change the color of the label associated with a node or an edge or an arc; the
    default value is black;
    - `set_label_font`: change the font of the label associated with a node or an edge or an arc; the
    default value is a 'Courier' font with normal style;
    - `set_label_font_size`: change the font_size of the label associated with a node or an edge or an
    arc; the default value is 20;
    - `move_node`: change the drawn coordinated of a node; the default positions of the nodes are
    concentric circles, the first node is on the center of the window, the next nodes are placed on a circle around
    that center and when that circle is filled, the next nodes are placed on a larger circle, ...;
    - `move_node` and `animate`: animate the moving of a node;
    - `place_nodes`: automatically place the nodes on the window using a force-directed graph drawing.

    The user is highly encouraged to move the nodes of the graph manually or to use the method `place_nodes` as the
    default positions are not really nice.

    Except `place_nodes` and `animate`, every method has a keyword argument named 'draw' that can be used to tell the
    drawer not to update the drawing immediately. It is then possible to draw multiple updates at the same time. To
    update the drawing, use the method `redraw`. Note that when the moving of a node is animated, the drawing is
    necessarily updated to show the animation.

    Finally, the window has a method `pause` that pauses the current execution until the user click on the window.

    WARNING : if the graph is inconsistent (for instance, if it was not edited using only the methods `add_node`,
    `remove_node, `UndirectedGraph.add_edge`, `UndictedGraph.remove_edge`, `DirectedGraph.add_arc` and
    `DirectedGraph.remove_arc`), an unexpected behaviour may occurs.
    """

    def __init__(self, g):
        """Build a new drawer for the graph g.

        Build a new drawer for the graph g. Every update on that graph will be automatically drawn on the window."""
        super().__init__()
        self.__drawingarea = None
        self.__init_ui()
        self.__graph = g

        self.__init_pub()

        self.__nodeitems = {}
        self.__arcitems = {}

        self.__current_x = WIDTH / 2
        self.__current_y = HEIGHT / 2
        self.__current_radius = 0
        self.__current_angle = 2 * math.pi
        self.__delta_angle = 0

        self.__dragged_node = None

        for node in self.__graph.nodes:
            self.__add_node(node)
        for arc in self.__graph.links:
            self.__add_arc(arc)

        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()
        self.set_keep_above(True)
        self.__exited = False
        self.__paused = None

        self.redraw()

    def __next_coords(self):
        """Compute the next place where a node should be drawn when added to the graph."""
        self.__current_angle += self.__delta_angle
        if self.__current_angle >= 2 * math.pi:
            self.__current_angle = 0
            self.__current_radius += 4 * NODE_RADIUS
            self.__delta_angle = (2 * math.pi) * 4 * NODE_RADIUS / (2 * math.pi * self.__current_radius)

        self.__current_x, self.__current_y = \
            WIDTH / 2 + self.__current_radius * math.cos(self.__current_angle), \
            HEIGHT / 2 + self.__current_radius * math.sin(self.__current_angle)

        if self.__current_y == HEIGHT / 2 and self.__current_x > WIDTH:
            # reboot, too much nodes.
            self.__current_x = WIDTH / 2
            self.__current_y = HEIGHT / 2
            self.__current_radius = 0
            self.__current_angle = 2 * math.pi
            self.__delta_angle = 0
        elif self.__current_y > HEIGHT or self.__current_y < 0 or self.__current_x > WIDTH or self.__current_x < 0:
            self.__next_coords()

    def __init_ui(self):
        """Init the graphical interface of the window, add a drawing area, a status bar and set the events."""
        self.set_title('Graph drawer')

        self.connect('delete_event', self.press_on_exit)

        self.__drawingarea = Gtk.DrawingArea()
        self.__drawingarea.set_size_request(WIDTH, HEIGHT)
        self.__drawingarea.connect('draw', self.__draw_graph)

        self.__drawingarea.set_can_focus(True)

        self.__drawingarea.set_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.__drawingarea.connect('button_press_event', self.on_button_press)
        self.__drawingarea.connect('button_release_event', self.on_button_release)
        self.__drawingarea.connect('motion_notify_event', self.on_mouse_move)
        self.__drawingarea.connect('key_press_event', self.on_key_press)

        self.__statusbar = Gtk.Statusbar()

        vbox = Gtk.VBox()
        vbox.add(self.__drawingarea)
        vbox.add(self.__statusbar)

        self.add(vbox)

    def __init_pub(self):
        """Subscribe to the pubsub topics in order to listen to any update of the graph."""
        pub.subscribe(self.__add_node, str(id(self.__graph)) + '.add_node')
        pub.subscribe(self.__add_arc, str(id(self.__graph)) + '.add_arc')
        pub.subscribe(self.__remove_node, str(id(self.__graph)) + '.remove_node')
        pub.subscribe(self.__remove_arc, str(id(self.__graph)) + '.remove_arc')

    def __add_node(self, node, draw=False):
        """Add one node to the drawing and update it if draw is True. Called with a pubsub event when a node was added
        to the graph."""
        try:
            item = _NodeItem(self.__current_x, self.__current_y)
            self.__next_coords()
            item.label = str(node.index)
            self.__nodeitems[node] = item
            if draw:
                self.redraw()
        except KeyError:
            pass

    def __add_arc(self, arc, draw=False):
        """Add one edge or arc to the drawing and update it if draw is True. Called with a pubsub event when a link was
        added to the graph."""
        try:
            u, v = arc.extremities
            nodeitemu = self.__nodeitems[u]
            nodeitemv = self.__nodeitems[v]
            self.__arcitems[arc] = _ArcItem(nodeitemu, nodeitemv, arc.directed)

            if draw:
                self.redraw()
        except KeyError:
            pass

    def __remove_node(self, node, draw=False):
        """Remove one node to the drawing and update it if draw is True. Called with a pubsub event when a node was
        removed from the graph."""
        try:
            del self.__nodeitems[node]

            if draw:
                self.redraw()
        except KeyError:
            pass

    def __remove_arc(self, arc, draw=False):
        """Remove one edge or arc to the drawing and update it if draw is True. Called with a pubsub event when a link
        was removed from the graph."""
        try:
            del self.__arcitems[arc]

            if draw:
                self.redraw()
        except KeyError:
            pass

    def __getitem(self, elem):
        """Return the corresponding drawing item to the element elem (a node, an edge or an arc).

        Return the corresponding drawing item to the element elem (a node, an edge or an arc). If the node, edge or arc
        does not belong to the drawn graph, an exception is raised.

        :param elem: the node, edge or arc for which the drawing item should be returned.
        :raises TypeError: if elem is neither a node, an edge nor an arc.
        :raises NodeMembershipError: if the node elem does not belong to the drawn graph.
        :raises LinkMembershipError: if the edge or arc elem does not belong to the drawn graph.

        """
        try:
            return self.__nodeitems[elem]
        except KeyError:
            try:
                return self.__arcitems[elem]
            except KeyError:
                if isinstance(elem, UndirectedNode) or isinstance(elem, DirectedNode):
                    raise NodeMembershipError(self.__graph, elem)
                elif isinstance(elem, Edge) or isinstance(elem, Arc):
                    raise LinkMembershipError(self.__graph, elem)
                else:
                    raise TypeError()

    def move_node(self, v, x, y, draw=False, doanimate=False):
        """Move the node to the coordinates (x, y), update the drawing if draw is True and animate the moving if
        doanimate is True.

        Move the node to the coordinated (x, y). If the keyword argument draw is True, the drawing is updated. Otherwise
        the node is moved but no change appears on the window.  Use the `redraw` method to do the update. This way, it
        is possible to draw more than once update at the same time. If the keyword argument 'doanimate' is True, the
        moving is animated during 1 second using a 'sinusoid in out' easing function with the function
        `gui.animations.easing_function.animate`. In that case the argument draw is ignored. The animation starts
        when the method `animate` is called. It is then possible to animate multiple nodes at the same time.

        If the node does not belong to the drawn graph, an exception is raised.

        :param v: the node of the drawn graph that should be moved.
        :param x: the abscissa where the node v should be drawn.
        :param y: the ordinate where the node v should be drawn.
        :param draw: if True, update the drawing, otherwise nothing appears, ignored if doanimate is True.
        :param doanimate: if True, animate the moving of the node when the method `animate` is called.
        :raises TypeError: if v is not a node
        :raises NodeMembershipError: if the node v does not belong to the drawn graph.
        """
        try:
            u = self.__nodeitems[v]
            if doanimate:
                item = self.__nodeitems[v]
                end = Point2(x, y)
                begin = copy(item.p)

                def move_aux(p):
                    self.move_node(v, p.x, p.y, True)

                animate_with_easing(begin, end, sininout, 1000, move_aux)
            else:
                u.p.x = x
                u.p.y = y
                if draw:
                    self.redraw()
        except KeyError:
            if isinstance(v, UndirectedNode) or isinstance(v, DirectedNode):
                raise NodeMembershipError(self.__graph, v)
            else:
                raise TypeError()

    def animate(self):
        """Start all the previously ordered animations. This method ends when the last animation end."""
        if get_nb_animating_with_easing() > 0:
            Gtk.main()

    def place_nodes(self, doanimate=False):
        """Automatically replace all the nodes using a force directed graph drawing algorithm of Kamada and Kawai.

        Automatically move all the nodes using an algorithm adapted from the force directed graph drawing algorithm of
        Kamada and Kawai given at https://cs.brown.edu/~rt/gdhandbook/chapters/force-directed.pdf. The algorithm is
        run on every connected component.

        If the algorithm reached an non-satisfying local minimum (detected if the number of iterations reaches 1000
        times the number of nodes), the positions of the nodes are randomly reset. Usually the reset is not done more
        than once for small graphs (less than 30 nodes). However, if more than 10 resets are done, the algorithm just
        give up and returns the positions of the last local minimum.

        Then each connected component is placed using the following algorithm:
        - draw a rectangle arround each connected component
        - sort every component by decreasing size
        - place the first component in the upper left corner
        - for each other component C, for each vertice (x,y) of a rectangle of any placed component, except the upper left
        vertice, try to place the upper left vertice of the rectangle of C at position (x,y). Greedely choose the
        position that minimize the maximum between height and width of the drawing and such that no two rectangles
        intersect.

        The whole graph drawing is resized so that every node is drawn inside the window.

        If the keyword argument doanimate is True, the moving is animated, otherwise the nodes are instantly moved from
        their current positions to the new ones. The animation is done using the method `move_node`. There is no need
        to call the method `animate` to start the animation as it is already done at the end of this method.

        :param doanimate: if True, animate the moving.
        """

        if len(self.__graph) == 0:
            return

        positions = self._place_nodes_kamada_kawai_algorithm()
        if doanimate:
            for u in self.__graph.nodes:
                posu = positions[u]
                self.move_node(u, posu.x, posu.y, doanimate=True)
            self.animate()
        else:
            for u in self.__graph.nodes:
                posu = positions[u]
                self.move_node(u, posu.x, posu.y)
            self.redraw()

    def _place_nodes_kamada_kawai_algorithm(self):

        MAXIMUM_ITERATIONS_PER_NODE = 100
        MAXIMUM_RESET = 10

        # Init the shortest path distances
        dists = {}
        for v in self.__graph:
            dists[v] = _breadth_first_search(self.__graph, v)

        # Init the Kamada-Kawai parameters
        l0 = NODE_RADIUS * 8
        l = l0 / max(dists[u][v] for u in self.__graph for v in self.__graph if v in dists[u])
        k = 1

        def lij(u, v):
            return l * dists[u][v]

        def kij(u, v):
            return k / dists[u][v] ** 2

        epsilon = 0.1

        # Init the positions
        positions = {}
        for u in self.__graph:
            positions[u] = copy(self.__nodeitems[u].p)

        def place_component(comp):
            """ Use the Kamada-Kawai algorithm to place the nodes of a connected component. """

            def energy_derivative_wrt_x(u):
                """ Derivative of the energy function E with respect to x(u). """
                posu = positions[u]

                def part(v):
                    posv = positions[v]
                    sqt = math.sqrt((posu.x - posv.x) ** 2 + (posu.y - posv.y) ** 2)
                    return kij(u, v) * ((posu.x - posv.x) - lij(u, v) * (posu.x - posv.x) / sqt)

                return sum(part(v) for v in comp if v != u)

            def energy_derivative_wrt_y(u):
                """ Derivative of the energy function E with respect to y(u). """
                posu = positions[u]

                def part(v):
                    posv = positions[v]
                    sqt = math.sqrt((posu.x - posv.x) ** 2 + (posu.y - posv.y) ** 2)
                    return kij(u, v) * ((posu.y - posv.y) - lij(u, v) * (posu.y - posv.y) / sqt)

                return sum(part(v) for v in comp if v != u)

            def energy_second_derivative_wrt_x2(u):
                """ Second derivative of the energy function E with respect to x(u). """
                posu = positions[u]

                def part(v):
                    posv = positions[v]
                    sqt = math.sqrt((posu.x - posv.x) ** 2 + (posu.y - posv.y) ** 2)
                    return kij(u, v) * (1 - lij(u, v) * (1 / sqt - (posu.x - posv.x)**2 * 1 / sqt**3))

                return sum(part(v) for v in comp if v != u)

            def energy_second_derivative_wrt_xy(u):
                """ Second derivative of the energy function E with respect to x(u) and y(u). """
                posu = positions[u]

                def part(v):
                    posv = positions[v]
                    sqt = math.sqrt((posu.x - posv.x) ** 2 + (posu.y - posv.y) ** 2)
                    return kij(u, v) * (lij(u, v) * (posu.x - posv.x) * (posu.y - posv.y) * 1 / sqt**3)

                return sum(part(v) for v in comp if v != u)

            def energy_second_derivative_wrt_y2(u):
                """ Second derivative of the energy function E with respect to y(u). """
                posu = positions[u]

                def part(v):
                    posv = positions[v]
                    sqt = math.sqrt((posu.x - posv.x) ** 2 + (posu.y - posv.y) ** 2)
                    return kij(u, v) * (1 - lij(u, v) * (1 / sqt - (posu.y - posv.y) ** 2 * 1 / sqt ** 3))

                return sum(part(v) for v in comp if v != u)

            def delta(u):
                """ Delta variable of the algorithm, norm of the gradient of the energy fonction with respect to
                 the position (x(u), y(u))"""
                return math.sqrt((energy_derivative_wrt_x(u)) ** 2 + (energy_derivative_wrt_y(u)) ** 2)

            def solve(u):
                """
                Solve the two variables system of the algorithm determining in which direction a single node should
                be moved to decrease the energy of the system, assuming the ot.
                """
                a11 = energy_second_derivative_wrt_x2(u)
                a21 = a12 = energy_second_derivative_wrt_xy(u)
                a22 = energy_second_derivative_wrt_y2(u)

                b1 = -1 * energy_derivative_wrt_x(u)
                b2 = -1 * energy_derivative_wrt_y(u)

                det = a11 * a22 - a21 * a12

                h11 = a22 / det
                h12 = -1 * a21 / det
                h21 = -1 * a12 / det
                h22 = a11 / det

                return h11 * b1 + h12 * b2, h21 * b1 + h22 * b2

            # Main loop of the algorithm
            # Choose a node maximizing the gradient of the energy with respect to its position
            # Move it to a position where the energy is minimum (assuming the other nodes are not moving)
            # Start again until the maximum gradient is under an epsilon constant.
            u, dlt = max(((u, delta(u)) for u in comp), key=lambda x: x[1])

            # Number of times we reset the positions of all nodes to avoid local minimum,
            # If it reaches MAXIMUM_RESET, we stop the calculations.
            reset_index = 0

            # Number of times the outer loop is done, if it reaches MAXIMUM_ITERATIONS_PER_NODE * number of nodes,
            # we reset the positions of the nodes
            outer_iteration = 0
            while dlt > epsilon:

                outer_iteration += 1

                # Number of times the inner loop is done, if it reaches MAXIMUM_ITERATIONS_PER_NODE * number of nodes,
                # we reset the positions of the nodes
                inner_iteration = 0

                while dlt > epsilon:
                    inner_iteration += 1
                    if outer_iteration > MAXIMUM_ITERATIONS_PER_NODE * len(self.__graph) \
                            or inner_iteration > MAXIMUM_ITERATIONS_PER_NODE * len(self.__graph):
                        if reset_index > MAXIMUM_RESET:  # Give up
                            return

                        for v in comp:
                            positions[v].x = random.randint(0, WIDTH)
                            positions[v].y = random.randint(0, HEIGHT)
                        outer_iteration = 0

                        reset_index += 1
                        break
                    else:
                        dx, dy = solve(u)
                        posi = positions[u]
                        posi.x += dx
                        posi.y += dy

                        dlt = delta(u)

                u, dlt = max(((u, delta(u)) for u in comp), key=lambda x: x[1])

        # Place all the connected components independantly
        components = _connected_components(self.__graph)
        for comp in components:
            place_component(comp)

        #
        # Place the components : place disjoint rectangles on the image so that each component is in one rectangle
        #

        # Sort the components by size
        components.sort(key=len)

        # Ratio between current height over width of each component
        minsx = {comp: min(positions[u].x for u in comp) for comp in components}
        maxsx = {comp: max(positions[u].x for u in comp) for comp in components}
        minsy = {comp: min(positions[u].y for u in comp) for comp in components}
        maxsy = {comp: max(positions[u].y for u in comp) for comp in components}
        ratios = {comp: max(maxsy[comp] - minsy[comp], 4 * NODE_RADIUS) / max(maxsx[comp] - minsx[comp],
                                                                              4 * NODE_RADIUS) for comp in components}
        # Rectangle of the largest component
        rm1 = ratios[components[-1]]
        rectm1 = (0, 0, WIDTH, WIDTH * rm1) if rm1 <= 1 else (0, 0, HEIGHT / rm1, HEIGHT)

        # Rectangles of each other component
        rectangles = {components[-1]: rectm1}
        # Ratio between the size of the component and the drawing area.
        area_size_ratio = rectm1[2] * rectm1[3] / len(components[-1])

        # Current size of the drawing (assuming only the largest component is drawn).
        wmax = rectm1[2]
        hmax = rectm1[3]

        # Place each other component.
        for i, comp in enumerate(reversed(components[:-1])):
            index = len(components) - 2 - i

            # The ratio between the size of the component and the drawing area should be the same for each component.
            # We can then deduce the width and the height of the rectangle of the component.
            r1 = ratios[comp]
            w1 = math.sqrt(area_size_ratio * len(comp) / r1)
            h1 = w1 * r1

            # Set of points where the upper left corner of the component can be placed.
            candidates = []
            for comp2 in components[index + 1:]:
                x2, y2, w2, h2 = rectangles[comp2]
                candidates.append((x2 + w2, y2))
                candidates.append((x2, y2 + h2))
                candidates.append((x2 + w2, y2 + h2))

            def _score(x1, y1):
                """ Score of the candidate position. Check if, by placing the rectangle at that position, there is
                an intersected rectangle among the rectangles of the already placed components. If no such overlapping
                occurs, the position is valid. In that case, the score is the maximum between width and height of the
                drawing."""
                for comp2 in components[index + 1:]:
                    r2 = rectangles[comp2]

                    if _intersect((x1, y1, w1, h1), r2):
                        return None

                return max(wmax, x1 + w1, hmax, y1 + h1)

            # Compute the score of each candidate position
            scores = list((candidate, _score(*candidate)) for candidate in candidates)

            # Return the valid position minimizing the maximum between the height and the width of the drawing.
            x1, y1 = min((scrs for scrs in scores if scrs[1] is not None), key=lambda x: x[1])[0]
            rectangles[comp] = (x1, y1, w1, h1)

        # Rescale each rectangle so that it fits with the window.

        minx = min(x for x, _, _, _ in rectangles.values())
        maxx = max(x + w for x, _, w, _ in rectangles.values())
        miny = min(y for _, y, _, _ in rectangles.values())
        maxy = max(y + h for _, y, _, h in rectangles.values())

        for comp in components:
            x, y, w, h = rectangles[comp]
            x *= WIDTH / (maxx - minx)
            w *= WIDTH / (maxx - minx)
            y *= HEIGHT / (maxy - miny)
            h *= HEIGHT / (maxy - miny)
            rectangles[comp] = (x, y, w, h)

        # Rescale and move each component in its rectangle.
        for comp in components:
            x, y, w, h = rectangles[comp]

            minx = minsx[comp]
            maxx = maxsx[comp]
            miny = minsy[comp]
            maxy = maxsy[comp]

            for u in comp:
                if maxx != minx:
                    positions[u].x = x + 2 * NODE_RADIUS + (w - 4 * NODE_RADIUS) * (positions[u].x - minx) / (
                    maxx - minx)
                else:
                    positions[u].x = x + w // 2

                if maxy != miny:
                    positions[u].y = y + 2 * NODE_RADIUS + (h - 4 * NODE_RADIUS) * (positions[u].y - miny) / (
                    maxy - miny)
                else:
                    positions[u].y = y + h // 2

        return positions

    def _place_nodes_fruchterman_reingold_algorithm(self):
        """Automatically replace all the nodes using a force directed graph drawing algorithm.

        Automatically replace all the nodes using an algorithm adapted from the force directed graph drawing algorithm
        given at https://cs.brown.edu/~rt/gdhandbook/chapters/force-directed.pdf at page number 387 (5th page of the
        pdf). The temperature starts at 50 and are multiplied by 0.99 at each iteration. The number of iterations is 500
        times the number of nodes. Those values are purely empirical.
        A repulsion force from the bounds is added :
        for each node at position (x, y), there are 4 repulsions from (x, 0), (x, HEIGHT), (0, y) and (WIDTH, y),
        this forces the nodes to stay away from the boundaries.
        """
        forces = {}
        positions = {}
        temp = 50

        for u in self.__graph.nodes:
            positions[u] = copy(self.__nodeitems[u].p)

        k = math.sqrt(WIDTH * HEIGHT / len(self.__graph))

        def attraction(mag):
            return mag ** 2 / k

        def repulsion(mag):
            return k ** 2 / mag

        for _ in range(500*len(self.__graph)):
            for u in self.__graph.nodes:
                force = Vector2(0, 0)
                posu = positions[u]
                for v in self.__graph.nodes:
                    if u == v:
                        continue
                    vu = posu - positions[v]
                    force += vu.normalized() * repulsion(vu.magnitude())
                forces[u] = force

                bounds = [Vector2(posu.x, 0), Vector2(posu.x, HEIGHT), Vector2(0, posu.y), Vector2(WIDTH, posu.y)]

                for bound in bounds:
                    boundu = posu - bound
                    force += boundu.normalized() * repulsion(boundu.magnitude())

            for a in self.__graph.links:
                u, v = a.extremities
                uv = positions[v] - positions[u]
                delta = uv.normalized() * attraction(uv.magnitude())
                forces[u] += delta
                forces[v] -= delta

            for u in self.__graph.nodes:
                posu = positions[u]
                force = forces[u]
                disp = min(force.magnitude(), temp)
                posu += force.normalized() * disp

                posu.x = min(WIDTH - 2 * NODE_RADIUS, max(0, posu.x))
                posu.y = min(HEIGHT - 2 * NODE_RADIUS, max(0, posu.y))

                force = forces[u]
                force.x = 0
                force.y = 0

            temp *= 0.99
        return positions

    def set_color(self, elem, color, draw=False):
        """Change the color of the element elem and update the drawing if draw is true.

        If elem is a node, change the external color of that node. If elem is an edge or an arc, change the color
        of the lines of that link. The color should be an RGB triple of integers between 0 and 255 (corresponding, in
        that order, to the quantity of red, green and blue in the color).

        If the keyword argument draw is True, the drawing is updated. Otherwise the color is updated but no change
        appears on the window. Use the `redraw` method to do the update. This way, it is possible to draw more than once
        update at the same time.

        If the element does not belong to the drawn graph, an exception is raised.

        :param elem: a node, an edge or an arc of the drawn graph.
        :param color: the desired color of elem, an RGB triple of integer from 0 to 255.
        :param draw: if True, update the drawing, otherwise nothing appears.
        :raises TypeError: if elem is neither a node, an edge nor an arc.
        :raises NodeMembershipError: if the node elem does not belong to the drawn graph.
        :raises LinkMembershipError: if the edge or arc elem does not belong to the drawn graph.
        """
        item = self.__getitem(elem)
        if item is None:
            return
        item.color = color
        if draw:
            self.redraw()

    def set_node_color_fill(self, v, color, draw=False):
        """Change the internal color of the node v and update the drawing if draw is true.

        Change the internal color of the node v. The color should be an RGB triple of integers between 0 and 255
        (corresponding, in that order, to the quantity of red, green and blue in the color).

        If the keyword argument draw is True, the drawing is updated. Otherwise the color is updated but no change
        appears on the window. Use the `redraw` method to do the update. This way, it is possible to draw more than once
        update at the same time.

        If v does not belong to the drawn graph, an exception is raised.

        :param v: a node of the drawn graph.
        :param color: the desired internal color of v, an RGB triple of integer from 0 to 255.
        :param draw: if True, update the drawing, otherwise nothing appears.
        :raises TypeError: if v is not a node
        :raises NodeMembershipError: if the node v does not belong to the drawn graph.
        """
        try:
            u = self.__nodeitems[v]
            u.color_fill = color
            if draw:
                self.redraw()
        except KeyError:
            if isinstance(v, UndirectedNode) or isinstance(v, DirectedNode):
                raise NodeMembershipError(self.__graph, v)
            else:
                raise TypeError()

    def set_line_width(self, elem, width, draw=False):
        """Change the width of the lines of the element elem and update the drawing if draw is true.

        If elem is a node, change the width of the external line of that node. If elem is an edge or an arc, change the
        width of the lines of that link.

        If the keyword argument draw is True, the drawing is updated. Otherwise the width is updated but no change
        appears on the window. Use the `redraw` method to do the update. This way, it is possible to draw more than once
        update at the same time.

        If elem does not belong to the drawn graph, an exception is raised.

        :param elem: a node, an edge or an arc of the drawn graph.
        :param width: the desired width of the lines of elem in pixels
        :param draw: if True, update the drawing, otherwise nothing appears.
        :raises TypeError: if elem is neither a node, an edge nor an arc.
        :raises NodeMembershipError: if the node elem does not belong to the drawn graph.
        :raises LinkMembershipError: if the edge or arc elem does not belong to the drawn graph.
        """
        item = self.__getitem(elem)
        if item is None:
            return
        item.line_width = width
        if draw:
            self.redraw()

    def set_node_radius(self, v, radius, draw=False):
        """Change the radius of the node v and update the drawing if draw is true.

        Change the radius of the node v.

        If the keyword argument draw is True, the drawing is updated. Otherwise the radius is updated but no change
        appears on the window. Use the `redraw` method to do the update. This way, it is possible to draw more than once
        update at the same time.

        If v does not belong to the drawn graph, an exception is raised.

        :param v: a node of the drawn graph.
        :param radius the desired radius of v in pixels.
        :param draw: if True, update the drawing, otherwise nothing appears.
        :raises TypeError: if v is not a node
        :raises NodeMembershipError: if the node v does not belong to the drawn graph.
        """
        try:
            u = self.__nodeitems[v]
            u.radius = radius
            if draw:
                self.redraw()
        except KeyError:
            if isinstance(v, UndirectedNode) or isinstance(v, DirectedNode):
                raise NodeMembershipError(self.__graph, v)
            else:
                raise TypeError()

    def set_label(self, elem, text, draw=False):
        """Change the text of the label of the element elem and update the drawing if draw is true.

        Change the text of the label associated with the element elem. That element is either a node, an edge or an arc
        of the drawn graph.

        If the keyword argument draw is True, the drawing is updated. Otherwise the text is updated but no change
        appears on the window. Use the `redraw` method to do the update. This way, it is possible to draw more than once
        update at the same time.

        If elem does not belong to the drawn graph, an exception is raised.

        :param elem: a node, an edge or an arc of the drawn graph.
        :param text: the desired text of the label of elem
        :param draw: if True, update the drawing, otherwise nothing appears.
        :raises TypeError: if elem is neither a node, an edge nor an arc.
        :raises NodeMembershipError: if the node elem does not belong to the drawn graph.
        :raises LinkMembershipError: if the edge or arc elem does not belong to the drawn graph.
        """
        item = self.__getitem(elem)
        if item is None:
            return
        item.label = text
        if draw:
            self.redraw()

    def set_label_color(self, elem, color, draw=False):
        """Change the color of the label of the element elem and update the drawing if draw is true.

        Change the color of the label associated with the element elem. That element is either a node, an edge or an arc
        of the drawn graph. The color should be an RGB triple of integers between 0 and 255 (corresponding, in that
        order, to the quantity of red, green and blue in the color).

        If the keyword argument draw is True, the drawing is updated. Otherwise the color is updated but no change
        appears on the window. Use the `redraw` method to do the update. This way, it is possible to draw more than once
        update at the same time.

        If elem does not belong to the drawn graph, an exception is raised.

        :param elem: a node, an edge or an arc of the drawn graph.
        :param color: the desired color of the label of elem, an RGB triple of integer from 0 to 255.
        :param draw: if True, update the drawing, otherwise nothing appears.
        :raises TypeError: if elem is neither a node, an edge nor an arc.
        :raises NodeMembershipError: if the node elem does not belong to the drawn graph.
        :raises LinkMembershipError: if the edge or arc elem does not belong to the drawn graph.
        """
        item = self.__getitem(elem)
        if item is None:
            return
        item.label_color = color
        if draw:
            self.redraw()

    def set_label_font(self, elem, font, draw=False):
        """Change the font of the label of the element elem and update the drawing if draw is true.

        Change the font of the label associated with the element elem. That element is either a node, an edge or an arc
        of the drawn graph. The font should be a triple containing, in that order, the name of the font,
        the font slant and the font weight. The last two parameters are cairo constants:
        - `cairo.FONT_SLANT_NORMAL`, `cairo.FONT_SLANT_ITALIC` and `cairo.FONT_SLANT_OBLIQUE` for the slant
        - `cairo.FONT_WEIGHT_NORMAL` and `cairo.FONT_WEIGHT_BOLD` for the weight

        If the keyword argument draw is True, the drawing is updated. Otherwise the font is updated but no change
        appears on the window. Use the `redraw` method to do the update. This way, it is possible to draw more than once
        update at the same time.

        If elem does not belong to the drawn graph, an exception is raised.

        :param elem: a node, an edge or an arc of the drawn graph.
        :param font: the desired font of the label of elem
        :param draw: if True, update the drawing, otherwise nothing appears.
        :raises TypeError: if elem is neither a node, an edge nor an arc.
        :raises NodeMembershipError: if the node elem does not belong to the drawn graph.
        :raises LinkMembershipError: if the edge or arc elem does not belong to the drawn graph.
        """
        item = self.__getitem(elem)
        if item is None:
            return
        item.label_font = font
        if draw:
            self.redraw()

    def set_label_font_size(self, elem, size, draw=False):
        """Change the font size of the label of the element elem and update the drawing if draw is true.

        Change the font size of the label associated with the element elem. That element is either a node, an edge or
        an arc of the drawn graph.

        If the keyword argument draw is True, the drawing is updated. Otherwise the size is updated but no change
        appears on the window. Use the `redraw` method to do the update. This way, it is possible to draw more than once
        update at the same time.

        If elem does not belong to the drawn graph, an exception is raised.

        :param elem: a node, an edge or an arc of the drawn graph.
        :param size: the desired font size of the label of elem
        :param draw: if True, update the drawing, otherwise nothing appears.
        :raises TypeError: if elem is neither a node, an edge nor an arc.
        :raises NodeMembershipError: if the node elem does not belong to the drawn graph.
        :raises LinkMembershipError: if the edge or arc elem does not belong to the drawn graph.
        """
        item = self.__getitem(elem)
        if item is None:
            return
        item.label_font_size = size
        if draw:
            self.redraw()

    def redraw(self):
        """Redraw the drawing area of the window. Use this method to draw all the previously updates (color, line width,
        move, ...)"""
        if self.__exited:
            return
        self.__drawingarea.queue_draw()
        self.__drawingarea.get_properties('window')[0].process_updates(True)
        while Gtk.events_pending() or not self.is_active() and Gtk.main_level() != 0:
            Gtk.main_iteration()

    def __draw_graph(self, widget, cr):
        """Called when a draw event is sent to the window. Redraw the whole area with the current value of the graph."""
        if self.__graph is None:
            return

        cr.set_source_rgb(255, 255, 255)
        cr.paint()

        for arc in self.__graph.links:
            self.__draw_arc(arc, cr)

        for node in self.__graph.nodes:
            self.__draw_node(node, cr)

    def __draw_node(self, node, cr):
        """Draw the given node on the drawing area if that node belongs to the graph."""
        self.__nodeitems[node]._draw(cr)

    def __draw_arc(self, arc, cr):
        """Draw the given edge or arc on the drawing area if that link belongs to the graph."""
        self.__arcitems[arc]._draw(cr)

    def __is_inside_node(self, v, x, y):
        """Return True if the coordinates (x, y) is inside the node v considering its current position and its
        current radius."""
        try:
            u = self.__nodeitems[v]
            return (u.p.x - x)**2 + (u.p.y - y)**2 <= u.radius**2
        except KeyError:
            if isinstance(v, UndirectedNode) or isinstance(v, DirectedNode):
                raise NodeMembershipError(self.__graph, v)
            else:
                raise TypeError()

    def pause(self):
        """Pause the execution of the code until the used click on the window.

        Pause the execution of the code until the used click on the window. That method update the drawing of the
        drawing area by calling the `redraw` method. Thus any previous change on the graph will appear if that method
        is called.
        """
        if self.__exited:
            return
        if self.__paused is None:
            self.__paused = \
                self.__add_statusbar_message('paused',
                                             'Paused! ' +
                                             'Press ESC to exit. ' +
                                             'Move the nodes by "dragNdropping" with Shift + Click. ' +
                                             'Click anywhere or press any other key to unpause.')
            self.redraw()
            Gtk.main()

    def on_button_press(self, widget, event):
        """Called when the user click on the window. Used to move nodes if the user clicks on a node. Used jointly with
        the `pause` method to pause and unpause the execution of the code if the user click anywhere else."""
        if self.__exited:
            return
        if self.__paused is not None and Gtk.main_level() != 0:
            if event.state & Gdk.ModifierType.SHIFT_MASK != 0:
                for node in self.__graph.nodes:
                    if self.__is_inside_node(node, event.x, event.y):
                        self.__dragged_node = node
                        break
            else:
                self.__statusbar.pop(self.__paused)
                self.__paused = None
                self.redraw()
                Gtk.main_quit()

    def on_mouse_move(self, widget, event):
        """Called when the used move the mouse on the window. Used to drag nodes."""
        if self.__exited:
            return
        if self.__dragged_node is None:
            return
        if event.state & Gdk.ModifierType.SHIFT_MASK == 0:
            self.__dragged_node = None
            return
        self.move_node(self.__dragged_node, event.x, event.y, draw=True)

    def on_button_release(self, widget, event):
        self.__dragged_node = None

    def on_key_press(self, widget, event):
        """Called when the user press a key. Used to exit the window with any key or jointly with the `pause` method to
        unpause the window with any key."""
        if self.__exited:
            return
        if event.keyval == Gdk.KEY_Shift_L or event.keyval == Gdk.KEY_Shift_R:
            return
        if event.keyval == Gdk.KEY_Escape:
            self.emit("delete_event", Gdk.Event())
            return
        if self.__paused is not None and Gtk.main_level() != 0:
            self.__statusbar.pop(self.__paused)
            self.__paused = None
            self.redraw()
            Gtk.main_quit()

    def __add_statusbar_message(self, context_desc, context_msg):
        """Change the message of the statusbar."""
        context_id = self.__statusbar.get_context_id(context_desc)
        self.__statusbar.push(context_id, context_msg)
        return context_id

    def press_on_exit(self, widget, event):
        """Reaction to the event of clicking on the exit button of the window."""
        self.__exited = True
        self.destroy()
        for _ in range(Gtk.main_level()):
            Gtk.main_quit()


class _NodeItem:
    """Item containing all the informations needed to draw a node of the graph."""

    def __init__(self, x, y):
        """Create a new node item at position (x,y) with default parameters."""
        self.p = Point2(x, y)

        self.color = NODE_COLOR
        self.color_fill = NODE_FILL_COLOR
        self.line_width = NODE_LINE_WIDTH
        self.radius = NODE_RADIUS
        self.label = None
        self.label_color = NODE_LABEL_COLOR
        self.label_font = NODE_LABEL_FONT
        self.label_font_size = NODE_LABEL_FONT_SIZE

    def _draw(self, cr):
        """Draw the node item using the cairo library on the drawing area of the window."""
        cr.set_source_rgb(*self.color)
        cr.set_line_width(self.line_width)
        cr.arc(self.p.x, self.p.y, self.radius, 0, 2 * math.pi)
        cr.stroke_preserve()
        cr.set_source_rgb(*self.color_fill)
        cr.fill()

        if self.label is not None:
            cr.set_source_rgb(*self.label_color)
            cr.select_font_face(*self.label_font)
            cr.set_font_size(self.label_font_size)
            (x, y, width, height, dx, dy) = cr.text_extents(self.label)
            cr.move_to(self.p.x - width / 2 - x, self.p.y - height / 2 - y)
            cr.show_text(self.label)
            cr.stroke()


class _ArcItem:
    """Item containing all the informations needed to draw an adge or an arc of the graph."""

    def __init__(self, u, v, directed):
        """Create a new edge or arc item at position (x,y) with default parameters."""
        self.u = u
        self.v = v
        self.directed = directed
        self.color = LINK_COLOR
        self.line_width = LINK_LINE_WIDTH

        self.label = None
        self.label_color = LINK_LABEL_COLOR
        self.label_font = LINK_LABEL_FONT
        self.label_font_size = LINK_LABEL_FONT_SIZE

    def _draw(self, cr):
        """Draw the edge or arc item using the cairo library on the drawing area of the window."""
        pu = self.u.p
        pv = self.v.p
        cr.set_source_rgb(*self.color)
        cr.set_line_width(self.line_width)
        uv = (pv - pu).normalized()

        pu1 = pu + uv * (self.u.radius + self.u.line_width / 2)
        pv1 = pv - uv * (self.v.radius + self.v.line_width / 2)

        cr.move_to(pu1.x, pu1.y)
        cr.line_to(pv1.x, pv1.y)
        cr.stroke()

        if self.directed:
            cr.set_source_rgb(*self.color)
            par1 = pv1 - _rotate(uv, math.pi / 4) * LINK_ARROW_LENGTH
            par2 = pv1 - _rotate(uv, -math.pi / 4) * LINK_ARROW_LENGTH

            cr.move_to(par1.x, par1.y)
            cr.line_to(pv1.x, pv1.y)
            cr.line_to(par2.x, par2.y)
            cr.stroke()

        if self.label is not None:
            nuv = _rotate(uv, math.pi / 2)
            if nuv.y > 0:
                nuv = nuv * -1

            plabel = pu + ((pv - pu) / 2) + nuv * LINK_LABEL_DISTANCE

            cr.set_source_rgb(*self.label_color)
            cr.select_font_face(*self.label_font)
            cr.set_font_size(self.label_font_size)
            (x, y, width, height, dx, dy) = cr.text_extents(self.label)
            cr.move_to(plabel.x - width / 2 - x, plabel.y - height / 2 - y)
            cr.show_text(self.label)
            cr.stroke()


def _rotate(v, alpha):
    """Return a new 2D vector equal to v rotated with the angle alpha."""
    cs = math.cos(alpha)
    sn = math.sin(alpha)
    return Vector2(v.x * cs - v.y * sn, v.x * sn + v.y * cs)


def _intersect(rect1, rect2):
    """ Return True if the two rectangles rect1 and rect2 intersect. """
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return (x1 + w1 > x2 and x2 + w2 > x1) and (y1 + h1 > y2 and y2 + h2 > y1)


def _connected_components(g):

    if len(g) == 0:
        return []

    visited = set()
    comps = []
    while len(visited) != len(g):
        for u in g:
            if u not in visited:
                break

        dists = _breadth_first_search(g, u)
        comp = [v for v in g if v in dists]
        visited.update(comp)
        comps.append(tuple(comp))
    return comps


def _breadth_first_search(g, v):
    """
    Return, for each node u, the breadth first search distance from v to u in the graph g.

    For each node u, returns the distance of a shortest path from v to u in an undirected unweighted graph using the
    breadth first search algorithm.

    :param g: an undirected graph
    :param v: a node of g
    :return: a dictionary associating for each node u the distance of a shortest path from v to u in g
    """

    to_visit = [v]
    visited = set()
    dist = {v: 0}

    while len(to_visit) != 0:
        u = to_visit.pop(0)
        visited.add(u)
        for v in u.neighbors:
            if v in visited:
                continue
            if v not in dist or dist[v] > dist[u] + 1:
                dist[v] = dist[u] + 1
            to_visit.append(v)

    return dist
