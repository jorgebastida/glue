Add Paddings to your images
===========================

Using the filename
------------------
In some situations it's really useful to add some padding to an image. ``glue`` will use the filename to determine the padding, so if you simply append ``_10`` to the filename it'll add a ``10px`` padding all around the image::

    $ mv rainbow.png rainbow_10.png
    $ glue icons sprites

This small change means that the ``rainbow.png`` image needs a ``10px`` padding all around the image.

.. image:: img/famfamfam3.png

If you don't need the same padding all around the image, you can use ``_10-20`` for a ``10px 20px 10px 20px`` padding or
``_10-20-30-40`` for a ``10px 20px 30px 40px`` padding as this table shows:

=================== =========================
filename            padding
=================== =========================
cat.png             0px 0px 0px 0px
cat_20.png          20px 20px 20px 20px
cat_20-30.png       20px 30px 20px 30px
cat_20-30-40.png    20px 30px 40px 30px
cat_20-30-40-50.png 20px 30px 40px 30px
=================== =========================


This padding information will not be used as part of the css class name, so you can change the padding safely.

.. code-block:: css

    .sprite-icons-rainbow{ background:url('sprites/icons/icons.png'); top:0; left:0; no-repeat;}
    ...

.. note::
    If you use the ``--crop`` option, the padding is applied after cropping the image, so you can crop all the unnecessary space around the images and then add the same padding to all of them uniformly.

Using static files or the command line
--------------------------------------

You can use both static configuration files or the command line to add padding to your images:

* :doc:`Command line arguments page <options>`.
* :doc:`Configuration files <files>`.

