Pseudo Classes
===========================

Using the filename
------------------
Using the filename of the source images you can customize the pseudo class related to the images, so if you simply append ``__hover`` to the filename ``glue`` will add ``:hover`` to the CSS class name::

    buttons
    ├── pay.png
    └── pay__hover.png

Using this simple convention you can create for example create button sprites like:

.. image:: img/buttons.png

And generate automatically the following css:

.. code-block:: css

    .sprite-buttons-pay{background-image:url(buttons.png);background-repeat:no-repeat}
    .sprite-buttons-pay:hover{background-position:0px 0px;width:174px;height:62px;}
    .sprite-buttons-pay{background-position:0px -62px;width:174px;height:62px;}

.. note::
    You can use multiple pseudo-classes at the same time ``__hover__before.png``

.. note::
    pseudo-class separator use to be ``_``. Since ``glue 0.9`` it is ``__``. If you don't want / you can'e rename all your files, you can use ``--pseudo-class-separator=_`` in order to make ``glue`` work in legacy mode.


Available pseudo classes
------------------------

Glue will only detect the following pseudo-classes: ``link``, ``visited``, ``active``, ``hover``, ``focus``, ``first-letter``, ``first-line``, ``first-child``, ``before`` and ``after``.
