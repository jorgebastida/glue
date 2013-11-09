Templates
=========

Introduction
------------

``glue`` formats based on templates can be customized with your own templates from the command line. By convention every format (i.e ``css``) will define an optional  ``--css-template`` with wich you can override the template the format will use.

These templates are simple `Jinja2 templates <http://jinja.pocoo.org/docs/>`_ you can customize a far as you want using the following context variables.

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

CSS Template Example
--------------------

.. code-block:: jinja

    /* glue: {{ version }} hash: {{ hash }} */
    {% for image in images %}.{{ image.label }}{{ image.pseudo }}{%- if not image.last %}, {%- endif %}{%- endfor %}{
        background-image:url('{{ sprite_path }}');
        background-repeat:no-repeat;
    }
    {% for image in images %}
    .{{ image.label }}{{ image.pseudo }}{
        background-position:{{ image.x ~ ('px' if image.x) }} {{ image.y ~ ('px' if image.y) }};
        width:{{ image.width }}px;
        height:{{ image.height }}px;
    }
    {% endfor %}
    {% for ratio in ratios %}
    @media screen and (-webkit-min-device-pixel-ratio: {{ ratio.ratio }}), screen and (min--moz-device-pixel-ratio: {{ ratio.ratio }}),screen and (-o-min-device-piratio: {{ ratio.fraction }}),screen and (min-device-pixel-ratio: {{ ratio.ratio }}){
        {% for image in images %}.{{ image.label }}{{ image.pseudo }}{% if not image.last %}, {% endif %}
        {% endfor %}{
            background-image:url('{{ ratio.sprite_path }}');
            -webkit-background-size: {{ width }}px {{ height }}px;
            -moz-background-size: {{ width }}px {{ height }}px;
            background-size: {{ width }}px {{ height }}px;
        }
    }
    {% endfor %}
