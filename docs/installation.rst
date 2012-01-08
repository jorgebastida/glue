Installing Glue
===============

Glue only depends on one external library, `PIL <http://www.pythonware.com/products/pil/>`_.
``PIL`` is a graphic library for python and it's used to create the sprite images.

By default some Linux distributions and OSX doesn't have the required codecs to manipulate ``jpeg`` images so it's necessary to install them manually.

Requirements
------------
OSX
^^^

Before installing ``PIL`` you'll need to install Xcode, then you can install the jpeg codecs using:

.. code-block:: bash

    $ brew install jpeg

Debian/Ubuntu
^^^^^^^^^^^^

.. code-block:: bash

    $ apt-get install libjpeg62 libjpeg62-dev zlib1g-dev

`zlib1g-dev` is required to manipulate PNG files.


Last stable version
-------------------
Just run ``easy_install`` with root rights:

.. code-block:: bash

    $ sudo easy_install glue

or even better using ``pip``:

.. code-block:: bash

    $ pip install glue

Development version
-------------------

The source code of Glue is available on Github `https://github.com/jorgebastida/glue/ <https://github.com/jorgebastida/glue/>`_.
