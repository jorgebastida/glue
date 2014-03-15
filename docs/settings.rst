Settings
========

Settings Priority
------------------

Remember that environment variables would override glue's defaults but their priority is lower than
command line options.

From higher priority to lower priority:

1. Image settings (from configuration file)
2. Sprite settings (from configuration file)
3. Command line settings
4. Environment variables
5. Default settings

Every command-line option available in glue is configurable using environment variables.

.. note::
    New in version 0.9

Settings Map
------------

============================ =================================== ===============================
Command-line arg             Environment Variable                Configuration File setting
============================ =================================== ===============================
--source                     GLUE_SOURCE                         source
--output                     GLUE_OUTPUT                         output
-q --quiet                   GLUE_QUIET                          quiet
-r --recursive               GLUE_RECURSIVE                      recursive
--follow-links               GLUE_FOLLOW_LINKS                   follow_links
-f --force                   GLUE_FORCE                          force
-w --watch                   GLUE_WATCH                          watch
--project                    GLUE_PROJECT                        project
-a --algorithm               GLUE_ALGORITHM                      algorithm
--ordering                   GLUE_ORDERING                       algorithm_ordering
--css                        GLUE_CSS                            css_dir
--less                       GLUE_LESS                           less_dir
--less-template              GLUE_LESS_TEMPLATE                  less_template
--scss                       GLUE_SCSS                           scss_format
--scss-template              GLUE_SCSS_TEMPLATE                  scss_template
--namespace                  GLUE_CSS_NAMESPACE                  css_namespace
--sprite-namespace           GLUE_CSS_SPRITE_NAMESPACE           css_sprite_namespace
-u --url                     GLUE_CSS_URL                        css_url
--cachebuster                GLUE_CSS_CACHEBUSTER                css_cachebuster
--cachebuster-filename       GLUE_CSS_CACHEBUSTER                css_cachebuster_filename
--separator                  GLUE_CSS_SEPARATOR                  css_separator
--css-template               GLUE_CSS_TEMPLATE                   css_template
--pseudo-class-separator     GLUE_CSS_PSEUDO_CLASS_SEPARATOR     css_pseudo_class_separator
--img                        GLUE_IMG                            img_dir
--no-img                     GLUE_GENERATE_IMG                   generate_image
--no-css                     GLUE_GENERATE_CSS                   generate_css
-c --crop                    GLUE_CROP                           crop
-p --padding                 GLUE_PADDING                        padding
--margin                     GLUE_MARGIN                         margin
--png8                       GLUE_PNG8                           png8
--ratios                     GLUE_RATIOS                         ratios
--retina                     GLUE_RETINA                         ratios
--html                       GLUE_HTML                           html_dir
--cocos2d                    GLUE_COCOS2D                        cocos2d_dir
--json                       GLUE_JSON                           json_dir
--json-format                GLUE_JSON_FORMAT                    json_format
--caat                       GLUE_CAAT                           caat_dir
============================ =================================== ===============================
