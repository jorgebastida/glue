.. glue documentation master file, created by
   sphinx-quickstart on Sun Jan  1 19:36:52 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Glue
================================

Glue is a simple command line tool to generate CSS sprites::

    $ glue source output

* Automatic Sprite (PNG+CSS) creation.
* Automatic multi-dpi (retina) sprite creation.
* Support for multi-sprite projects.
* Multiple algorithms available.
* Automatic crop of unnecessary transparent borders around source images.
* Configurable paddings per image, sprite or project.
* Configurable output CSS file extension (.less, .scss, etc).
* Automatic sprite images post-processing using OptiPNG.
* Sprite- and Project-level configuration via static config files.
* Configurable cache busting for sprite images.
* Customizable output css templates.
* Customizable CSS class names.

Documentation
-------------
.. toctree::
   :maxdepth: 2

   installation
   quickstart
   paddings
   pseudoclasses
   ratios
   files
   options
   optipng
   faq
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

