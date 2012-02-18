Installing Glue
===============

Glue only depends on one external library, `PIL <http://www.pythonware.com/products/pil/>`_.
``PIL`` is a graphic library for python and it's used to create the sprite images.

By default some Linux distributions and OSX don't have the required codecs to manipulate ``jpeg`` images so it's necessary to install them manually.

OSX
---
If you are using OSX, the easiest way to install the jpeg decoder is using `Homebrew <http://mxcl.github.com/homebrew/>`_.
Before installing ``Homebrew`` you'll need to install Xcode, then you can follow these steps:

.. code-block:: bash

    $ sudo brew install jpeg

    $ sudo pip install glue
    # or
    $ sudo easy_install glue

Debian/Ubuntu
-------------
If you are using Debian/Ubuntu installing ``glue`` is really easy:

.. code-block:: bash

    $ apt-get install libjpeg62 libjpeg62-dev zlib1g-dev

    $ sudo pip install glue
    # or
    $ sudo easy_install glue

Windows
-------

1. Install Python, if not yet available. `Python 2.7.2 Windows installer <http://www.python.org/ftp/python/2.7.2/python-2.7.2.msi>`_.

2. Install PIL, check `this website <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_ for a matching version (`PIL-1.1.7 for Python 2.7 <http://www.lfd.uci.edu/~gohlke/pythonlibs/xn3pw759/PIL-1.1.7.win32-py2.7.exe>`_)

3. Install Python's ``easy_install`` `easy_install installer for Python 2.7 <http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11.win32-py2.7.exe>`_.

4. Add Python's Scripts dir to your Path. Add ``;C:\Python27\Scripts`` to the end of the line.

5. Start the cmd and type

.. code-block:: bash

    $ easy_install glue

6. Easy isn't?


Development version
-------------------

The source code of Glue is available on Github `https://github.com/jorgebastida/glue/ <https://github.com/jorgebastida/glue/>`_.
