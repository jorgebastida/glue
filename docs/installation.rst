Installation
============

Glue only depends on one external library, `PIL <http://www.pythonware.com/products/pil/>`_.
``PIL`` is a graphic library for python and it's used to create the sprite images.

You will also need ``Python 2.5`` or higher to get started, so be sure to have an up to date ``Python 2.x`` installation.

System Wide Installation
------------------------
Just run ``easy_install`` with root rights::

    $ sudo easy_install glue

or even better using ``pip``::

    $ pip install glue


.. note::
    On Windows Run it in an Admin shell on Windows systems and without sudo

.. note::
    On OSX you'll need to install Xcode in order to compile ``PIL``.

Development version
-------------------

The source code of Glue is available on Github `https://github.com/jorgebastida/glue/ <https://github.com/jorgebastida/glue/>`_.

Installing OptiPNG
------------------

OptiPNG is not a glue requirement but is hardly recomended to optimize the output PNG files to make them as small as possible.

OptiPNG is a PNG optimizer that recompresses image files to a smaller size, without losing any information. This program also converts external formats (BMP, GIF, PNM and TIFF) to optimized PNG, and performs PNG integrity checks and corrections.

OSX
^^^
You can install optipng form source or using `Homebrew <http://mxcl.github.com/homebrew/>`_::

    $ brew install optipng


Debian/Ubuntu
^^^^^^^^^^^^^
You can install optipng form source or using apt::

    $ apt-get install optipng

From source
^^^^^^^^^^^
To install optipng from source, `download the last available version <http://sourceforge.net/projects/optipng/files/OptiPNG/optipng-0.6.5/>`_ and then you can install it doing::

    $ tar zvxf optipng-0.6.5.tar.gz
    $ cd optipng-0.6.5
    $ ./configure
    $ make
    $ sudo make install
