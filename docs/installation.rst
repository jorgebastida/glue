Installing Glue
===============

Glue only depends on one external library, `PIL <http://www.pythonware.com/products/pil/>`_.
``PIL`` is a graphic library for python and it's used to create the sprite images.

By default some Linux distributions and OSX doesn't have the required codecs to manipulate ``jpeg`` images so it's necessary to install them manually.

OSX
---
If you are using OSX The easiest way to install ``PIL`` is using `Homebrew <http://mxcl.github.com/homebrew/>`_.
Before installing ``Homebrew`` you'll need to install Xcode, then you can follow this steps:

Snow Leopard
^^^^^^^^^^^^
.. code-block:: bash

    $ brew install pil
    $ sudo brew link pil
    $ sudo ln -s /usr/local/Cellar/pil/1.1.7/lib/python2.6/site-packages/PIL/ /Library/Python/2.6/site-packages/PIL

    $ sudo pip install glue --no-deps
    # or
    $ sudo easy_install glue --no-deps

Snow Leopard
^^^^^^^^^^^^
.. code-block:: bash

    $ brew install pil
    $ sudo brew link pil
    $ sudo ln -s /usr/local/Cellar/pil/1.1.7/lib/python2.7/site-packages/PIL/ /Library/Python/2.7/site-packages/PIL

    $ sudo pip install glue --no-deps
    # or
    $ sudo easy_install glue --no-deps

Debian/Ubuntu
-------------
If you are using Debian/Ubuntu installing ``glue`` is really easy:

.. code-block:: bash

    $ apt-get install libjpeg62 libjpeg62-dev zlib1g-dev

    $ sudo pip install glue
    # or
    $ sudo easy_install glue


Development version
-------------------

The source code of Glue is available on Github `https://github.com/jorgebastida/glue/ <https://github.com/jorgebastida/glue/>`_.
