#!/usr/bin/env python
"""Gtk+ Shell for IPython notebooks
-----------------------------------

IPython notebook embedded in a Gtk+ Application.
"""

from distutils.core import setup
import setuptools

setup (name             = 'notizblock',
       version          = '0.1.0',
       author           = 'Christian Kellner',
       author_email     = 'kellner@biologie.uni-muenchen.de',
       url              = 'https://github.com/gicmo/Notizblock',
       description      = __doc__.split("\n")[0],
       long_description = "\n".join(__doc__.split("\n")[2:]),
       packages         = ['IPNotizblock'],
       scripts          = ['notizblock'],
       data_files       = [('share/applications'), ['notizblock.desktop']]
       )