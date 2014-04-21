Glue
====

.. image:: https://badge.fury.io/py/glue.png
    :target: http://badge.fury.io/py/glue

.. image:: https://travis-ci.org/jorgebastida/glue.png?branch=master
    :target: https://travis-ci.org/jorgebastida/glue

.. image:: https://coveralls.io/repos/jorgebastida/glue/badge.png?branch=master
    :target: https://coveralls.io/r/jorgebastida/glue?branch=master

.. image:: https://pypip.in/d/glue/badge.png
    :target: https://crate.io/packages/glue/


Glue is a simple command line tool to generate sprites::

    $ glue source output

* The latest documentation is available at: http://glue.readthedocs.org
* Installation instructions: http://glue.readthedocs.org/en/latest/installation.html
* Glue-users mailing list: https://groups.google.com/forum/#!forum/glue-users

Features
--------
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
* Configurable `paddings and margin per image, sprite or project <http://glue.readthedocs.org/en/latest/paddings.html>`_.
* Watch option to keep glue running watching for file changes.
* Project-, Sprite- and Image-level configuration via static config files.
* Customizable `output <http://glue.readthedocs.org/en/latest/options.html#global-template>`_ using jinja templates.
* CSS: Optional .less/.scss output format.
* CSS: Configurable `cache busting for sprite images <http://glue.readthedocs.org/en/latest/options.html#cachebuster>`_.
* CSS: Customizable `class names <http://glue.readthedocs.org/en/latest/options.html#separator>`_.
* Python ``2.6``, ``2.7`` and ``3.3+`` supported.
* Really `well tested <https://coveralls.io/r/jorgebastida/glue?branch=master>`_.

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

Contribute
-----------

* Fork the repository on GitHub to start making your changes to the master branch (or branch off of it).
* Write a test which shows that the bug was fixed or that the feature works as expected.

  - Use ``python setup.py test``

* Send a pull request and bug the maintainer until it gets merged and published. :) Make sure to add yourself to AUTHORS.


Is your company using glue?
---------------------------
We are creating a list of companies using glue in production. If your company use ``glue``, please send `me <mailto:me@jorgebastida.com>`_ an email or send me a message to `@jorgebastida <https://twitter.com/jorgebastida>`_ . I would really appreciate it.


We need your help
------------------

There are several features that ``glue`` users would love to have... but they require a substancial amount of work and dedication, so we are looking for feature-sponsors! If you want to lead the development/testing of any of the following features, please contact `Jorge Bastida <mailto:me@jorgebastida.com>`_.

Here you have some examples:

* Windows support (I'm not a Windows user, ``glue`` needs somebody who care about how ``glue`` works on Windows and write down some installation instructions).
* Cocos2d Format (Already exists, but we need somebody to give it some love).
* New Formats (After 0.9, ``glue`` is ready to accept new output formats - If you want to create a new format, contact me).
* Binary packaging for OSX and Windows (For some users it would be really cool if they were able to download an already packaged binary version).
