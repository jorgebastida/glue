Changelog
=========

0.2.2
^^^^^^
* Added support for 8bit bg images.
* Fixed newline characters support on ``--global-template`` and ``--each-template``.

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
