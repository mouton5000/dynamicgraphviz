from setuptools import setup

import dynamicgraphviz

setup(
    name='dynamicgraphviz',
    version=dynamicgraphviz.__version__,
    packages=['dynamicgraphviz.graph', 'dynamicgraphviz.gui', 'dynamicgraphviz.gui.animations',
              'dynamicgraphviz.helpers', 'dynamicgraphviz.exceptions'],
    url='https://github.com/mouton5000/dynamicgraphviz',
    license='MIT',
    author=dynamicgraphviz.__author__,
    author_email=dynamicgraphviz.__email__,
    description='A dynamic graph drawer with Gtk and Cairo',
    require=['euclid3', 'pypubsub', 'pycairo', 'pygtk']
)
