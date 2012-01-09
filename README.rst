Glue
====

Glue is a simple command line tool to generate CSS sprites::

    $ glue source output

* The latest documentation is available at: http://glue.readthedocs.org
* Installation instructions: http://glue.readthedocs.org/en/latest/installation.html

Features
--------
* Automatic Sprite(PNG+CSS) creation.
* Supports multi sprite projects.
* Automatically `crop unnecessary transparent borders <http://glue.readthedocs.org/en/latest/quickstart.html#crop-unnecessary-transparent-spaces>`_ around the source images.
* Configurable `paddings per image, sprite or project <http://glue.readthedocs.org/en/latest/paddings.html>`_.
* Generate .less files.
* Automatically post-process sprite images using `OptiPNG <http://optipng.sourceforge.net/>`_.
* Read configuration from static config files.
* Configurable `cache busting for sprite images <http://glue.readthedocs.org/en/latest/options.html#cachebuster>`_.

Example
-------
For example using the gorgeous `famfamfam icons <http://www.famfamfam.com/lab/icons/silk/>`_ (4.2Mb) you will get
the following ``icons.png`` (401Kb).

.. image:: https://github.com/jorgebastida/glue/raw/master/docs/_static/famfamfam1.png


And also a ``icons.css`` with all the necessary CSS classes for this sprite::

    .sprite-icons-zoom_out{ background:url('icons.png'); top:0; left:0; no-repeat;}
    .sprite-icons-zoom_in{ background:url('icons.png'); top:0; left:-16; no-repeat;}
    .sprite-icons-zoom{ background:url('icons.png'); top:-16; left:0; no-repeat;}
    .sprite-icons-xhtml_valid{ background:url('icons.png'); top:-16; left:-16; no-repeat;}
    ...


Do you want to know more? Visit the quickstart guide: http://glue.readthedocs.org/en/latest/quickstart.html
