Glue
====

Glue is a simple command line tool to generate CSS sprites::

    $ glue source output

* The latest documentation is available at: http://glue.readthedocs.org
* Installation instructions: http://glue.readthedocs.org/en/latest/installation.html

Features
--------
* Automatic Sprite (PNG+CSS) creation.
* Automatic multi-dpi `retina <http://glue.readthedocs.org/en/latest/ratios.html>`_ sprite creation.
* Support for multi-sprite projects.
* Create sprites from multiple folders.
* Multiple `algorithms <http://glue.readthedocs.org/en/latest/options.html#a-algorithm>`_ available.
* Automatic `crop of unnecessary transparent borders <http://glue.readthedocs.org/en/latest/quickstart.html#crop-unnecessary-transparent-spaces>`_ around source images.
* Configurable `paddings per image, sprite or project <http://glue.readthedocs.org/en/latest/paddings.html>`_.
* Watch option to keep glue running watching for file changes.
* Optional .less output format.
* Automatic sprite images post-processing using `OptiPNG <http://optipng.sourceforge.net/>`_.
* Sprite- and Project-level configuration via static config files.
* Configurable `cache busting for sprite images <http://glue.readthedocs.org/en/latest/options.html#cachebuster>`_.
* Customizable `output css templates <http://glue.readthedocs.org/en/latest/options.html#global-template>`_.
* Customizable `CSS class names <http://glue.readthedocs.org/en/latest/options.html#separator>`_.

Example
-------
Using the gorgeous `famfamfam icons <http://www.famfamfam.com/lab/icons/silk/>`_ (4.2Mb) you will get
the following ``icons.png`` (401Kb).

.. image:: https://github.com/jorgebastida/glue/raw/master/docs/img/famfamfam1.png


And also an ``icons.css`` with all the necessary CSS classes for this sprite::

    .sprite-icons-zoom_out{ background:url('icons.png'); top:0; left:0; no-repeat;}
    .sprite-icons-zoom_in{ background:url('icons.png'); top:0; left:-16; no-repeat;}
    .sprite-icons-zoom{ background:url('icons.png'); top:-16; left:0; no-repeat;}
    .sprite-icons-xhtml_valid{ background:url('icons.png'); top:-16; left:-16; no-repeat;}
    ...


Do you want to know more? Visit the quickstart guide: http://glue.readthedocs.org/en/latest/quickstart.html
