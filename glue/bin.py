#!/usr/bin/env python
import os
import sys
import argparse

from PIL import Image as PImage

from glue.formats import formats
from glue.helpers import redirect_stdout
from glue import exceptions
from glue import managers
from glue import __version__


def main(argv=None):

    argv = (argv or sys.argv)[1:]

    parser = argparse.ArgumentParser(usage=("%(prog)s [source | --source | -s] [output | --output | -o]"))

    parser.add_argument("--source", "-s",
                        dest="source",
                        type=unicode,
                        default=os.environ.get('GLUE_SOURCE', None),
                        help="Source path")

    parser.add_argument("--output", "-o",
                        dest="output",
                        type=unicode,
                        default=os.environ.get('GLUE_OUTPUT', None),
                        help="Output path")

    parser.add_argument("-q", "--quiet",
                        dest="quiet",
                        action='store_true',
                        default=os.environ.get('GLUE_QUIET', False),
                        help="Suppress all normal output")

    parser.add_argument("-r", "--recursive",
                        dest="recursive",
                        action='store_true',
                        default=os.environ.get('GLUE_RECURSIVE', False),
                        help=("Read directories recursively and add all "
                              "the images to the same sprite."))

    parser.add_argument("--follow-links",
                        dest="follow_links",
                        action='store_true',
                        default=os.environ.get('GLUE_FOLLOW_LINKS', False),
                        help="Follow symbolic links.")

    parser.add_argument("-f", "--force",
                        dest="force",
                        action='store_true',
                        default=os.environ.get('GLUE_FORCE', False),
                        help=("Force glue to create every sprite image and "
                              "metadata file even if they already exists in "
                              "the output directory."))

    parser.add_argument("-w", "--watch",
                        dest="watch",
                        action='store_true',
                        default=os.environ.get('GLUE_WATCH', False),
                        help=("Watch the source folder for changes and rebuild "
                              "when new files appear, disappear or change."))

    parser.add_argument("--project",
                        dest="project",
                        action="store_true",
                        default=os.environ.get('GLUE_PROJECT', False),
                        help="Generate sprites for multiple folders")

    parser.add_argument("-v", "--version",
                        action="version",
                        version='%(prog)s ' + __version__,
                        help="Show program's version number and exit")

    group = parser.add_argument_group("Algorithm options")

    group.add_argument("-a", "--algorithm",
                       dest="algorithm",
                       metavar='NAME',
                       type=unicode,
                       default=os.environ.get('GLUE_ALGORITHM', 'square'),
                       choices=['square', 'vertical', 'horizontal',
                                'vertical-right', 'horizontal-bottom',
                                'diagonal'],
                       help=("Allocation algorithm: square, vertical, "
                             "horizontal, vertical-right, horizontal-bottom, "
                             "diagonal. (default: square)"))

    group.add_argument("--ordering",
                       dest="algorithm_ordering",
                       metavar='NAME',
                       type=unicode,
                       default=os.environ.get('GLUE_ORDERING', 'maxside'),
                       choices=['maxside', 'width', 'height', 'area', 'filename',
                                '-maxside', '-width', '-height', '-area', '-filename'],
                       help=("Ordering criteria: maxside, width, height, area or "
                             "filename (default: maxside)"))

    # Populate the parser with options required by other formats
    for format in formats.itervalues():
        format.populate_argument_parser(parser)

    #
    # Handle deprecated arguments
    #

    group = parser.add_argument_group("Deprecated options")
    deprecated_arguments = {}

    def add_deprecated_argument(*args, **kwargs):
        group.add_argument(*args, **kwargs)
        deprecated_arguments[kwargs['dest']] = args[0]

    add_deprecated_argument("--global-template", dest="global_template")
    add_deprecated_argument("--each-template", dest="each_template")
    add_deprecated_argument("--ratio-template", dest="ratio_template")
    add_deprecated_argument("--ignore-filename-paddings", action='store_true',
                            dest="ignore_filename_paddings")
    add_deprecated_argument("--optipng", dest="optipng", action='store_true')
    add_deprecated_argument("--optipngpath", dest="optipngpath")
    add_deprecated_argument("--debug", action='store_true', dest="debug")
    add_deprecated_argument("--imagemagick", dest="imagemagick",
                            action='store_true')
    add_deprecated_argument("--imagemagickpath", dest="imagemagickpath")

    # Parse input
    options, args = parser.parse_known_args(argv)


    # Get the list of enabled formats
    options.enabled_formats = [f for f in formats if getattr(options, '{0}_dir'.format(f), False)]

    # If there is only one enabled format (img) or if there are two (img, html)
    # this means glue is been executed without any specific main format.
    # In order to keep the legacy API we need to enable css.
    # As consequence there is no way to make glue only generate the sprite
    # image and the html file without generating the css file too.
    if set(options.enabled_formats) in (set(['img']), set(['img', 'html'])) and options.generate_css:
        options.enabled_formats.append('css')
        setattr(options, "css_dir", True)

    if not options.generate_image:
        options.enabled_formats.remove('img')

    # Fail if any of the deprecated arguments is used
    for argument in deprecated_arguments.iterkeys():
        if getattr(options, argument, None):
            parser.error(("{0} argument is deprectated "
                          "since v0.3").format(deprecated_arguments[argument]))

    extra = 0
    # Get the source from the source option or the first positional argument
    if not options.source and args:
        options.source = args[0]
        extra += 1

    # Get the output from the output option or the second positional argument
    if not options.output and args[extra:]:
        options.output = args[extra]

    # Check if source is available
    if options.source is None:
        parser.error(("You must provide the folder containing the sprites "
                      "using the first positional argument or --source."))

    # Make absolute both source and output if present
    if not os.path.isdir(options.source):
        parser.error("Directory not found: '{0}'".format(options.source))

    options.source = os.path.abspath(options.source)
    if options.output:
        options.output = os.path.abspath(options.output)

    # Check that both the source and the output are present. Output "enough"
    # information can be tricky as you can choose different outputs for each
    # of the available formats. If it is present make it absolute.
    if not options.source:
        parser.error(("Source required. Please specify a source using "
                      "--source or the first positional argument."))

    if options.output:
        for format in options.enabled_formats:
            format_option = '{0}_dir'.format(format)
            path = getattr(options, format_option)

            if isinstance(path, bool) and path:
                setattr(options, format_option, options.output)
    else:
        if options.generate_image and not options.img_dir:
            parser.error(("Output required. Please specify an output for "
                          "the sprite image using --output, the second "
                          "positional argument or --img=<DIR>"))

        for format in options.enabled_formats:
            format_option = '{0}_dir'.format(format)
            path = getattr(options, format_option)

            if isinstance(path, bool) or not path:
                parser.error(("{0} output required. Please specify an output "
                              "for {0} using --output, the second "
                              "positional argument or --{0}=<DIR>".format(format)))
            else:
                setattr(options, format_option, os.path.abspath(path))

    # If the img format is not enabled, we still need to know where the sprites
    # were generated. As img is not an enabled format img_dir would be empty
    # if --img was not userd. If this is the case we need to use whatever is
    # the output value.
    if not options.generate_image and isinstance(options.img_dir, bool):
        options.img_dir = options.output

    # Apply formats constraints
    for format in options.enabled_formats:
        formats[format].apply_parser_contraints(parser, options)

    if options.project:
        manager_cls = managers.ProjectManager
    else:
        manager_cls = managers.SimpleManager

    # Generate manager or defer the creation to a WatchManager
    if options.watch:
        manager = managers.WatchManager(manager_cls, vars(options))
    else:
        manager = manager_cls(**vars(options))

    try:
        if options.quiet:
            with redirect_stdout():
                manager.process()
        else:
            manager.process()
    except exceptions.ValidationError, e:
        sys.stderr.write(e.args[0])
        return e.error_code
    except exceptions.SourceImagesNotFoundError, e:
        sys.stderr.write("Error: No images found in %s.\n" % e.args[0])
        return e.error_code
    except exceptions.NoSpritesFoldersFoundError, e:
        sys.stderr.write("Error: No sprites folders found in %s.\n" % e.args[0])
        return e.error_code
    except exceptions.PILUnavailableError, e:
        sys.stderr.write(("Error: PIL {0} decoder is unavailable"
                          "Please read the documentation and "
                          "install it before spriting this kind of "
                          "images.\n").format(e.args[0]))
        return e.error_code
    except Exception:
        import platform
        import traceback
        sys.stderr.write("\n")
        sys.stderr.write("=" * 80)
        sys.stderr.write("\nYou've found a bug! Please, raise an issue attaching the following traceback\n")
        sys.stderr.write("https://github.com/jorgebastida/glue/issues/new\n")
        sys.stderr.write("-" * 80)
        sys.stderr.write("\n")
        sys.stderr.write("Version: {0}\n".format(__version__))
        sys.stderr.write("Python: {0}\n".format(sys.version))
        sys.stderr.write("PIL version: {0}\n".format(PImage.VERSION))
        sys.stderr.write("Platform: {0}\n".format(platform.platform()))
        sys.stderr.write("Config: {0}\n".format(vars(options)))
        sys.stderr.write("Args: {0}\n\n".format(sys.argv))
        sys.stderr.write(traceback.format_exc())
        sys.stderr.write("=" * 80)
        sys.stderr.write("\n")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
