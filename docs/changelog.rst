Changelog
=========

0.2.5
^^^^^^
* New ``--watch`` option to keep glue running in the background watching file changes.
* New option ``--html`` that generates a html using all the available css classes.
* New option ``--margin`` that adds margins around the sprited images. This margin doesn't count as image size.
* Add MANIFEST.in and tune the setup.py preparing the Debian/Ubuntu package.
* Fix _locate_images to be deterministic.
* Add support to Travis CI.
* Fix 8bit B/W images bug.

0.2.4
^^^^^^
* Better error handling: Glue will now return non zero return codes if something goes wrong.

0.2.3
^^^^^^
* Fix ``--version``
* Fix the camelcase ``--separator`` to not lowercase the filename before the capitalization.

0.2.2
^^^^^^
* New feature: Per-file pseudo-class customization.
* Added support for 8bit bg images.
* Added support for digit-only images.
* Fix newline characters support on ``--global-template`` and ``--each-template``.
* New algoritms ``vertical-right`` and ``horizontal-bottom``.
* New option ``--separator``: Customizable CSS class name separator.

0.2.1
^^^^^^
* New command line argument ``--global-template``.
* New command line argument ``--each-template``.
* ``-z`` and ``--no-size`` arguments are now deprecated.

0.2
^^^^^
* The default behaviour of glue is now the old ``--simple`` one.
* The old default behaviour (multiple-sprites) is now accesible using --project
* ``--simple`` argument is now deprecated
* New ordering algorithms square, horizontal, vertical and diagonal.
* New command line argument ``--ordering``.
* New command line argument ``--cachebuster-filename``.
* Old algorithms maxside, width, height and area are now orderings.
* Glue now ignore folders that start with a '.'
* CSS files will now avoid using quotes around the sprite filename.
* New ``-v``, ``--version`` option.
* Fix bugs.
* New test suite.



0.1.9
^^^^^
* New command line argument ``-z``, ``--no-size`` to avoid adding the image width and height to the sprite.
* New command line argument ``--png8`` forces the output image format to be png8 instead of png32.
* Improve CSS parsing performance removing bloat in the CSS.
* Improved documentation.
