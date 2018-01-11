# dynamicgraphviz
A dynamic graph drawer with Gtk and Cairo written with python3.

To use it, you need the following open source libraries :
- pypubsub (http://pypubsub.readthedocs.io/en/stable/about.html) (by Copyright (c) since 2006, Oliver Schoenborn)
- pycairo (https://cairographics.org/pycairo/) (could not find the copyright if it exists)
- euclid3 (https://github.com/euclid3/euclid3) (by Copyright (c) 2006 Alex Holkner)
- Pygobject (Gtk for python3) (http://pygobject.readthedocs.io/en/latest/index.html) 

## Installation

This module can simply be installed with pip, however only pypubsub, pycairo and euclid3 are automatically installed using pip. Pygobject is not automatically installed. Please visit http://pygobject.readthedocs.io/en/latest/getting_started.html to install PyGobject. 

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
    
The last line pauses the execution until the user click on the window.
It is possible to add and remove nodes and arcs while the window is running.

    v3.g.add_node()
    a2 = g.add_arc(v3, v1)
    
    g.remove_arc(a1)
    
    gd.pause()
    
It is possible to change some of the graphical properties of the nodes and the arcs.

    gd.set_label(a2, 10)
    gd.set_color(v1, (0, 255, 0))
    gd.set_color(a2, (10, 10, 100))
    gd.set_node_radius(v1, 35)
    gd.set_line_width(v1, 10)
    
    gd.pause()
