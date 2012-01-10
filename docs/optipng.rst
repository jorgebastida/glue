OptiPNG
=======

OptiPNG is not a ``glue`` requirement but is hardly recommended to optimize the output PNG files to make them as small as possible. OptiPNG is a PNG optimizer that recompresses image files to a smaller size, without losing any information.

OSX
---
You can install optipng form source or using `Homebrew <http://mxcl.github.com/homebrew/>`_:

.. code-block:: bash

    $ brew install optipng


Debian/Ubuntu
-------------
You can install optipng form source or using apt:

.. code-block:: bash

    $ apt-get install optipng

Windows
-------
OptiPNG distributes an executable version for Windows, so you can download it from the `optipng sourceforge page <http://sourceforge.net/projects/optipng/files/OptiPNG/optipng-0.6.5/>`_.

From source
-----------
To install optipng from source, `download the last available version <http://sourceforge.net/projects/optipng/files/OptiPNG/optipng-0.6.5/>`_ and then you can install it doing:

.. code-block:: bash

    $ tar zvxf optipng-0.6.5.tar.gz
    $ cd optipng-0.6.5
    $ ./configure
    $ make
    $ sudo make install
