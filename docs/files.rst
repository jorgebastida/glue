Configuration files
==========================

Introduction
------------
``glue`` has around 30 command line options. Remember all of them every time you need to rebuild your sprites could be really annoying. If you are using glue as part of your assets rebuild process and you want consistent executions over time, using configuration files could be a good idea.

The only thing you need to do is create a file named ``sprite.conf`` inside your sprite folder (or project folder if you want to apply this settings to your entire project) and glue will override your command line options using these settings. Project-level and sprite-level configuration files can coexist::

    sprites
        ├── actions
        │   ├── add.png
        │   ├── remove.png
        │   └── sprite.conf
        └── icons
        │   ├── comment.png
        │   ├── new.png
        │   └── rss.png
        └── sprite.conf

If for example you want to change the namespace and the default padding to all your sprites you can add this to your project-level ``sprite.conf``::

    [sprite]
    namespace=my-sprites
    padding=20


If the ``actions`` images needs to be cropped and have a different padding, you can create add the following settings to your new ``actions/sprite.conf`` file::

    [sprite]
    crop=true
    padding=10

If the ``remove.png`` image needs to have ``10px`` margin and ``0px`` padding you can append a new section to your ``actions/sprite.conf`` like the following::

    [remove.png]
    margin=10
    padding=0

This will override any previous setting about ``margin`` or ``padding`` affecting ``remove.png``.

.. note::
    project-level, sprite-level and image-level settings override any environmnet or command-line settings. More information in the `settings section <http://glue.readthedocs.org/en/latest/settings.html>`_

Available configuration
-----------------------

============================ ============== ============== ==============
Configuration File setting   Project-level  Sprite-level   Image-level
============================ ============== ============== ==============
source
output
quiet
watch
project
recursive                    X              X
follow_links                 X              X
force                        X              X
algorithm                    X              X
algorithm_ordering           X              X
css_dir                      X              X
css_format                   X              X
css_namespace                X              X
css_sprite_namespace         X              X
css_url                      X              X
css_cachebuster              X              X
css_cachebuster_filename     X              X
css_separator                X              X
css_template                 X              X
css_pseudo_class_separator   X              X
img_dir                      X              X
generate_image               X              X
png8                         X              X
ratios                       X              X
html_dir                     X              X
cocos2d_dir                  X              X
caat_dir                     X              X
json_dir                     X              X
json_format                  X              X
crop                         X              X              X
padding                      X              X              X
margin                       X              X              X
============================ ============== ============== ==============


