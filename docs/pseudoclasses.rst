Pseudo Classes
===========================

Using the filename
------------------
Using the filename of the source images you can customize the pseudo class related to the images, so if you simply append ``_hover`` to the filename ``glue`` will add ``:hover`` to the CSS class name::

    buttons
    ├── pay.png
    └── pay_hover.png

Using this simple convention you can create for example create button sprites like:

.. image:: img/buttons.png

And generate automatically the following css:

.. code-block:: css

    .sprite-buttons-pay{background-image:url(buttons.png);background-repeat:no-repeat}
    .sprite-buttons-pay:hover{background-position:0px 0px;width:174px;height:62px;}
    .sprite-buttons-pay{background-position:0px -62px;width:174px;height:62px;}

Available pseudo classes
------------------------

Glue will only detect the following pseudo-classes: ``link``, ``visited``, ``active``, ``hover``, ``focus``, ``first-letter``, ``first-line``, ``first-child``, ``before`` and ``after``.


Can I also use the filename to customize the padding?
-----------------------------------------------------

Yes! of course you can! For example the following sprite will be completely valid::

    buttons
    ├── pay_10-30.png
    └── pay_10-30_hover.png


You can add the padding or pseudo-class preferences **in any order**.
