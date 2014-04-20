Templates
=========

Introduction
------------

``glue`` formats based on templates can be customized usign your own templates. By convention, every format (i.e ``css``) will define an optional  ``--css-template`` with wich you can override the default template.

These templates are simple `Jinja2 templates <http://jinja.pocoo.org/docs/>`_, so you can customize a far as you want using the following context variables.

.. note::
    By default glue will use it's own internal templates, so you don't need to provide a template unless you want to super-customize glue's output.

.. note::
    If you don't know if you need a custom template, you **don't** need a custom template.


BaseTextFormat
--------------

Global
^^^^^^^

============================ ======================================================
Variable                     Value
============================ ======================================================
version                      Glue version
hash                         Hash of the sprite
name                         Name of the sprite
sprite_path                  Sprite path
sprite_filename              Sprite filename
width                        Sprite width
height                       Sprite height
images                       List of ``Images`` inside the sprite
ratios                       List of the ``Ratios`` inside
============================ ======================================================

Image
^^^^^^

============================ ======================================================
Variable                     Value
============================ ======================================================
filename                     Image original filename
last                         Last Image in the sprite
x                            X position within the sprite
y                            Y position within the sprite
width                        Image width
height                       Image height
============================ ======================================================

Ratio
^^^^^^

============================ ======================================================
Variable                     Value
============================ ======================================================
ratio                        Ratio value
fraction                     Nearest fraction for this ratio
sprite_path                  Sprite Image path for this ratio
============================ ======================================================

CssFormat
---------

Image
^^^^^^

============================ ======================================================
Variable                     Value
============================ ======================================================
label                        CSS label for this image
pseudo                       CSS pseudo class (if any)
============================ ======================================================

HtmlFormat
----------

Global
^^^^^^

============================ ======================================================
Variable                     Value
============================ ======================================================
css_path                     Path where the css file is
============================ ======================================================


Templates Examples
--------------------

If you are going to create a new template from scratch or if you want to do some changes to an existing output, a good starting point would be to read some of the existing templates in the ``formats`` `folder <https://github.com/jorgebastida/glue/tree/master/glue/formats>`_.
