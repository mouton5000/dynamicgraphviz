# dynamicgraphviz
A dynamic graph drawer with Gtk and Cairo written with python3
by Copyright (c) 2018 Watel Dimitri

## What is this thing?

This module works with python3.4+. 

It provides two things:
- a *very simple* and *light* package to manage graphs (those graphs: https://en.wikipedia.org/wiki/Graph_theory)
- a *very simple* and *light* module to draw graphs

## What is not this thing? Should I use it?

**dynamicgraphviz** is a light and dynamic but far from complete alternative to **graphviz** (https://pypi.python.org/pypi/graphviz), to **Networkx** (https://plot.ly/python/network-graphs/) and to **graph-tool** (https://graph-tool.skewed.de/).

If you purpose is producing a tool that needs to display graphs as fast as possible: this is not for you. If you need a tool with all the minimum shortest path algorithms as optimized as possible: this is not for you. This module is not fast. I think this module can hardly be integrated in a commercial product (I should say in any product).

With this module, you can **try graph algorithms** and **see what happens in real time**. The main purpose of this project is just a tool to debug and understand in real time what a graph algorithm does with the graph. It is just an advanced substitute to `print`. In addition, the module is light and should be easy to install.

You do not see how does the Dijkstra algorithm works on a directed graph? You do not see how this dual ascent approximation algorithm build the solution of your algorithm? You like graphs (and python) and want to try anything related with graphs. Try **dynamicgraphviz**.

## Installation

To use it, you need the following open source libraries :
- **pypubsub** 4.0.0 (http://pypubsub.readthedocs.io/) (by Copyright (c) since 2006, Oliver Schoenborn)
- **pycairo** 1.15.4 (https://cairographics.org/pycairo/) (could not find the copyright if it exists)
- **euclid3** 0.0.1 (https://github.com/euclid3/euclid3) (by Copyright (c) 2006 Alex Holkner)
- **Pygobject** (Gtk for python3) 3.26.1 (http://pygobject.readthedocs.io/en/latest/index.html)

This module can simply be installed with pip, however only pypubsub, pycairo and euclid3 are automatically installed using pip. Pygobject is **not** automatically installed. Please visit http://pygobject.readthedocs.io/en/latest/getting_started.html to install PyGobject. 

Then simply run the following command:

    pip3 install dynamicgraphviz

## Getting started

The following code creates a directed graph and display it.

    from dynamicgraphviz.graph.directedgraph import DirectedGraph
    from dynamicgraphviz.gui.graphdrawer import GraphDrawer
    
    g = DirectedGraph()

    v1 = g.add_node()
    v2 = g.add_node()

    a1 = g.add_arc(v1, v2)

    gd = GraphDrawer(g)
    gd.place_nodes(doanimate=True)
    gd.pause()
    
The last line pauses the execution until the user clicks on the window.
It is possible to add and remove nodes and arcs while the window is running.

    v3.g.add_node()
    a2 = g.add_arc(v3, v1)
    
    g.remove_arc(a1)
    
    gd.pause()
    
It is possible to change some of the graphical properties of the nodes and the arcs (labels, color, width of the line, radius, ...)

    gd.set_label(a2, 10)
    gd.set_color(v1, (0, 255, 0))
    gd.set_color(a2, (10, 10, 100))
    gd.set_node_radius(v1, 35)
    gd.set_line_width(v1, 10)
    
    gd.pause()

## If I want to use this module in my own project?

If you want to use or copy, modify or distribute the code for your own purpose, feel free to do it, this project has an MIT license. Just cite at least my name somewhere, or the full copyright.
