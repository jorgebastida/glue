Changelog
=========

0.2
^^^^^
* New ordering algorithms square, horizontal, vertical and diagonal.
* New command line argument ``--ordering``.
* Old algorithms maxside, width, height and area are now orderings.
* Glue now ignore folders that start with a '.'
* CSS files will now avoid using quotes around the sprite filename.
* New -v, --version option.



0.1.9
^^^^^
* New command line argument ``-z``, ``--no-size`` to avoid adding the image width and height to the sprite.
* New command line argument ``--png8`` forces the output image format to be png8 instead of png32.
* Improve CSS parsing performance removing bloat in the CSS.
* Improved documentation.
