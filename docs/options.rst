Command line arguments
======================

--project
-----------
As it's explained at the :doc:`quickstart page <quickstart>` the default behaviour of ``glue`` is to handle one unique sprite folder. If you need to generate several sprites for a project, you can use the ``--project`` option to handle multiple folders with only one command.

The suggested setup is to create a new folder for every sprite, and add inside all the images you need for each one. ``glue`` will create a new sprite for every folder::

    images
    ├── actions
    │   ├── add.png
    │   └── remove.png
    ├── borders
    │   ├── top_left.png
    │   └── top_right.png
    └── icons
        ├── comment.png
        ├── new.png
        └── rss.png

.. code-block:: bash

    $ glue source output --project

.. note::
    This was the default behaviour prior to the version ``0.2``, after ``2.0`` is not.

-c --crop
---------

Usually designers add some unnecessary transparent space around the images because it is easier for them to work with a larger canvas. ``glue`` can optimize our sprite by croping all the unnecessary transparent spaces that the original images could have.

.. image:: img/crop.png

.. code-block:: bash

    $ glue source output --crop

-l --less
---------
`less <http://lesscss.org/>`_  is a dynamic stylesheet language that extends CSS with dynamic behaviors.
``glue`` can also create ``.less`` files adding the ``--less`` option.
This files contain exactly the same CSS code. This option only changes the file format.

.. code-block:: bash

    $ glue source output --less

-u --url
---------
By default ``glue`` adds to the PNG file name the relative url between the CSS and the PNG file. If for any reason you need to change this behaviour, you can use ``url=<your-static-url-to-the-png-file>`` and ``glue`` will replace its suggested one with your url.

.. code-block:: bash

    $ glue source output --url=http://static.example.com/

-q --quiet
----------
This flag will make ``glue`` suppress all console output.

.. code-block:: bash

    $ glue source output -q

-p --padding
------------
If you want to add the same padding around all images you can use the ``--padding`` option:

.. code-block:: bash

    $ glue source output --padding=10
    $ glue source output --padding=10 20
    $ glue source output --padding=10 20 30 40

--watch
------------
While you are developing a site it could be quite frustrating running ``Glue`` once and another every time you change a source image or a filename. ``--watch`` will allow you to keep ``Glue`` running in the background and it'll rebuild the sprite every time it detects changes on the source directory.

.. code-block:: bash

    $ glue source output --watch

.. note::
    New in version 0.2.5

--css --img
-----------
Usually both CSS and PNG files reside on different folders, e.g. `css` and `img`. If you want to choose an individual folder for each type of file you can use the ``--img=<dir> --css=<dir>`` options together to customize where the output files will be created.

.. code-block:: bash

    $ glue source --img=images/compiled --css=css/compiled

--html
-----------
Using the ``--html`` option, ``Glue`` will also generate a test html per sprite using all the available CSS classes. This option is only useful for testing purposes. Glue generate the ``html`` file in the same directory as the CSS file.

.. code-block:: bash

    $ glue source --html

.. note::
    New in version 0.2.5

-a --algorithm
--------------
The criteria that ``glue`` uses to order the images before adding them to the canvas can be tunned. By default the algorithm is `square`, but in some situations using another ordering like `vertical` or `horizontal` could be useful depending on the kind of images you are spriting.

* The `square` algorithm was inspired by the `Binary Tree Bin Packing Algorithm Article <http://codeincomplete.com/posts/2011/5/7/bin_packing/>`_ by Jake Gordon.
* The `vertical` one allocates the images vertically aligning them to the left of the sprite.
* The `vertical-right` one allocates the images vertically aligning them to the right of the sprite.
* The `horizontal` one allocates the images aligning them to the top of the sprite.
* The `horizontal-bottom` one allocates the images aligning them to the bottom of the sprite.
* The `diagonal` one allocates the images diagonally. It was inspired by the `Diagonal CSS Sprites Article <http://www.aaronbarker.net/2010/07/diagonal-sprites/>`_ by Aaron Barker.

.. code-block:: bash

    $ glue source output --algorithm=[square|vertical|hortizontal|diagonal|vertical-right|horizontal-bottom]


--ordering
--------------
Before processing the images using the `algorithm` glue orders the images. The default ordering is `maxside` but you can configure it using the ``--ordering`` option.

.. code-block:: bash

    $ glue source output --ordering=[maxside|width|height|area]

You can reverse how any of the available algorithms works prepending a `-`.

.. code-block:: bash

    $ glue source output --ordering=[-maxside|-width|-height|-area]

--margin
------------
If you want to spread the images around the sprite but you don't want to count this space as image width/height (as happens using `--padding``), you can use the ``--margin`` option followed by the margin you want to add:

.. code-block:: bash

    $ glue source output --margin=20

.. note::
    New in version 0.2.5

--namespace
-----------
By default ``glue`` adds the namespace ``sprite`` to all the generated CSS class names. If you want to use your own namespace you can override the default one using the ``--namespace`` option.

.. code-block:: bash

    $ glue source output --namespace=my-namespace

--png8
------
By using the flag ``png8`` the output image format will be png8 instead of png32.

.. code-block:: bash

    $ glue source output --png8

.. note::
    New in version 0.1.9

--ignore-filename-paddings
--------------------------
``glue`` by default uses the end of each filename to discover if you want to add some padding to that image. If for any reason you want to disable this behavior (e.g. legacy purposes), you can use the ``--ignore-filename-paddings`` option to disable it.

.. code-block:: bash

    $ glue source output --ignore-filename-paddings

--separator
--------------------------
``glue`` by default uses ``-`` as separator for the CSS class names. If you want to customize this behaviour you can use ``--separator`` to specify your own
one:

.. code-block:: bash

    $ glue source output --separator=_

If you want to use `camelCase <http://en.wikipedia.org/wiki/CamelCase>`_ instead of a separator, choose ``camelcase`` as separator.

.. code-block:: bash

    $ glue source output --separator=camelcase

--global-template
------------------
If you want to customize the output CSS you can use this option to tune the global section of the output CSS. This template is going to be only added **once per sprite**. Usually you'll not need to change this template.

.. code-block:: bash

    $ glue source output --global-template=<template>


For example if you want to add quotes around the sprite image:

.. code-block:: bash

    $ glue source output --global-template="%(all_classes)s{background-image:url('%(sprite_url)s');background-repeat:no-repeat}"

.. note::
    New in version 0.2.1

--each-template
------------------
If you want to customize the output CSS, you can use this option to tune the output CSS generated for each image. This template is going to be added **once per image** present in the sprite. Usually you'll change this template if you want to remove the block size from the output CSS or make any other fine tune.

.. code-block:: bash

    $ glue source output --each-template=<template>


For example if you want to remove the block size from the output CSS (old ``--no-size`` option):

.. code-block:: bash

    $ glue source output --each-template="%(class_name)s{background-position:%(x)s %(y)s;}"

.. note::
    New in version 0.2.1

--optipng
---------

OptiPNG is a PNG optimizer that recompresses image files to a smaller size, without losing any information.

OptiPNG is not a glue requirement but is hardly recommended to optimize the output PNG files to make them as small as possible.

If you have ``optipng`` installed on your computer you can use the  ``--optipng`` option to automatically optimize all the sprites that ``glue`` generates. If you don't know how to install it, read the :doc:`optipng page <optipng>`.

.. code-block:: bash

    $ glue source output --optipng


--optipngpath
-------------
If ``optipng`` is not in your computer ``PATH``, you can choose the optipng path using this option.

.. code-block:: bash

    $ glue source output --optipng --optipngpath=<dir>

--cachebuster
-------------
If you decide to add an expires header to your static resources (and if you haven't already you really should), you need to worry about cache busting these resources every time you change one of them.

Cache busting is a technique that prevents a browser from reusing a resource that was already downloaded and cached. Cache in general is good, but in some situations could be annoying if it's duration is too long and we want to update a resource **now**.

This technique adds a flag to every url that links an external resource (PNG in this case). This flag usually is the last modified time or the ``hash`` of the file.

``glue`` can use this technique to automatically add the ``hash`` of the PNG file to the CSS url, so as soon as the file change (add/remove an image) the ``hash`` will be different and the browser will re-download the image.


.. code-block:: bash

    $ glue source output --cachebuster

Original css:

.. code-block:: css

    .sprite-icons-zoom{ background:url('sprites/icons/icons.png'); top:0; left:0; no-repeat;}
    .sprite-icons-wrench_orange{ background:url('sprites/icons/icons.png'); top:0; left:-16; no-repeat;}
    ...

After --cachebuster:

.. code-block:: css

    .sprite-icons-zoom{ background:url('sprites/icons/icons.png=p3c54d'); top:0; left:0; no-repeat;}
    .sprite-icons-wrench_orange{ background:url('sprites/icons/icons.png?p3c54d'); top:0; left:-16; no-repeat;}
    ...

--cachebuster-filename
-----------------------
This option has the same purpose than ``--cachebuster`` but insted of using the hash of the PNG as a queryarg it uses it as part of the filename.


.. code-block:: bash

    $ glue source output --cachebuster-filename

Original css:

.. code-block:: css

    .sprite-icons-zoom{ background:url('sprites/icons/icons.png'); top:0; left:0; no-repeat;}
    .sprite-icons-wrench_orange{ background:url('sprites/icons/icons.png'); top:0; left:-16; no-repeat;}
    ...

After --cachebuster:

.. code-block:: css

    .sprite-icons-zoom{ background:url('sprites/icons/icons_p3c54d.png'); top:0; left:0; no-repeat;}
    .sprite-icons-wrench_orange{ background:url('sprites/icons/icons_p3c54d.png'); top:0; left:-16; no-repeat;}
    ...
