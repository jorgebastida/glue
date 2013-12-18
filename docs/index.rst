Glue
================================

Glue is a simple command line tool to generate sprites::

    $ glue source output

* Automatic Sprite (Image + Metadata) creation including:

  - css (less, scss)
  - cocos2d
  - json (array, hash)
  - CAAT

* Automatic multi-dpi `retina <http://glue.readthedocs.org/en/latest/ratios.html>`_ sprite creation.
* Support for multi-sprite projects.
* Create sprites from multiple folders (recursively).
* Multiple `algorithms <http://glue.readthedocs.org/en/latest/options.html#a-algorithm>`_ available.
* Automatic `crop of unnecessary transparent borders <http://glue.readthedocs.org/en/latest/quickstart.html#crop-unnecessary-transparent-spaces>`_ around source images.
* Configurable paddings and margin per image, sprite or project.
* Watch option to keep glue running watching for file changes.
* Project-, Sprite- and Image-level configuration via static config files.
* Customizable `output <http://glue.readthedocs.org/en/latest/templates.html>`_ using jinja templates.
* CSS: Optional .less/.scss output format.
* CSS: Configurable `cache busting for sprite images <http://glue.readthedocs.org/en/latest/options.html#cachebuster>`_.
* CSS: Customizable `class names <http://glue.readthedocs.org/en/latest/options.html#separator>`_.

Documentation
-------------
.. toctree::
   :maxdepth: 2

   installation
   quickstart
   pseudoclasses
   ratios
   files
   templates
   options
   settings
   faq
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

