Installing Glue
===============

Glue only depends on one external library, `PIL <http://www.pythonware.com/products/pil/>`_.
``PIL`` is a graphic library for python and it's used to create the sprite images.

By default some Linux distributions and OSX doesn't have the required codecs to manipulate ``jpeg`` images so it's necessary to install them manually.

OSX
---
If you are using OSX The easiest way to install the jpeg decoder is using `Homebrew <http://mxcl.github.com/homebrew/>`_.
Before installing ``Homebrew`` you'll need to install Xcode, then you can follow this steps:

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


Development version
-------------------

The source code of Glue is available on Github `https://github.com/jorgebastida/glue/ <https://github.com/jorgebastida/glue/>`_.
