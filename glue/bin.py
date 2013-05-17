#!/usr/bin/env python
import os
import sys
from optparse import OptionParser, OptionGroup

from PIL import Image as PImage

from glue import core, exceptions, __version__


def main():

    parser = OptionParser(usage=("usage: %prog [options] source_dir [<output> "
                                 "| --css=<dir> --img=<dir>]"))
    parser.add_option("--project", action="store_true", dest="project",
            help="generate sprites for multiple folders")
    parser.add_option("-r", "--recursive", dest="recursive", action='store_true',
            help=("Read directories recursively and add all the "
                  "images to the same sprite."))
    parser.add_option("--follow-links", dest="follow_links", action='store_true',
            help="Follow symbolic links.")
    parser.add_option("-c", "--crop", dest="crop", action='store_true',
            help="crop images removing unnecessary transparent margins")
    parser.add_option("-l", "--less", dest="less", action='store_true',
            help="generate output stylesheets as .less instead of .css")
    parser.add_option("-u", "--url", dest="url",
            help="prepend this url to the sprites filename")
    parser.add_option("-q", "--quiet", dest="quiet", action='store_true',
            help="suppress all normal output")
    parser.add_option("-p", "--padding", dest="padding",
            help="force this padding in all images")
    parser.add_option("--ratios", dest="ratios",
            help="Create sprites based on these ratios")
    parser.add_option("--retina", dest="retina", action='store_true',
            help="Shortcut for --ratios=2,1")
    parser.add_option("-f", "--force", dest="force", action='store_true',
            help=("force glue to create every sprite and CSS file even if "
                  "they already exists in the output directory."))
    parser.add_option("-w", "--watch", dest="watch", default=False,
            action='store_true',
            help=("Watch the source folder for changes and rebuild "
                  "when new files appear, disappear or change."))
    parser.add_option("-v", "--version", action="store_true", dest="version",
            help="show program's version number and exit")

    group = OptionGroup(parser, "Output Options")
    group.add_option("--css", dest="css_dir", default='', metavar='DIR',
            help="output directory for css files")
    group.add_option("--img", dest="img_dir", default='', metavar='DIR',
            help="output directory for img files")
    group.add_option("--html", dest="html", action="store_true",
            help="generate test html file using the sprite image and CSS.")
    group.add_option("--no-css", dest="no_css", action="store_true",
            help="don't genereate CSS files.")
    group.add_option("--no-img", dest="no_img", action="store_true",
            help="don't genereate IMG files.")

    parser.add_option_group(group)

    group = OptionGroup(parser, "Advanced Options")
    group.add_option("-a", "--algorithm", dest="algorithm", metavar='NAME',
            help=("allocation algorithm: square, vertical, horizontal, "
                  "vertical-right, horizontal-bottom, diagonal. "
                  "(default: square)"))
    group.add_option("--ordering", dest="ordering", metavar='NAME',
            help=("ordering criteria: maxside, width, height or "
                  "area (default: maxside)"))
    group.add_option("--margin", dest="margin", type=int,
            help="force this margin in all images")
    group.add_option("--namespace", dest="namespace",
            help="namespace for all css classes (default: sprite)")
    group.add_option("--sprite-namespace", dest="sprite_namespace",
            help="namespace for all sprites (default: sprite name)")
    group.add_option("--png8", action="store_true", dest="png8",
            help="the output image format will be png8 instead of png32")
    group.add_option("--ignore-filename-paddings", action='store_true',
            dest="ignore_filename_paddings", help="ignore filename paddings")
    group.add_option("--debug", dest="debug", action='store_true',
            help="don't catch unexpected errors and let glue fail hardly")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Output CSS Template Options")
    group.add_option("--separator", dest="separator", metavar='SEPARATOR',
            help=("Customize the separator used to join CSS class "
                  "names. If you want to use camelCase use "
                  "'camelcase' as separator."))
    group.add_option("--global-template", dest="global_template",
            metavar='TEMPLATE',
            help=("Customize the global section of the output CSS."
                  "This section will be added only once for each "
                  "sprite."))
    group.add_option("--each-template", dest="each_template",
            metavar='TEMPLATE',
            help=("Customize each image output CSS."
                  "This section will be added once for each "
                  "image inside the sprite."))
    group.add_option("--ratio-template", dest="ratio_template",
            metavar='TEMPLATE',
            help=("Customize ratios CSS media queries template."
                  "This section will be added once for each "
                  "ratio different than 1."))
    parser.add_option_group(group)

    group = OptionGroup(parser, "Optipng Options",
                "You need to install optipng before using these options")
    group.add_option("--optipng", dest="optipng", action='store_true',
            help="postprocess images using optipng")
    group.add_option("--optipngpath", dest="optipngpath",
            help="path to optipng (default: optipng)", metavar='PATH')
    parser.add_option_group(group)

    group = OptionGroup(parser, "ImageMagick Options",
                "You need to install ImageMagick before using these options")
    group.add_option("--imagemagick", dest="imagemagick", action='store_true',
            help="Use ImageMagick to scale down retina sprites instead of Pillow.")
    group.add_option("--imagemagickpath", dest="imagemagickpath",
            help="path to imagemagick (default: convert)", metavar='PATH')
    parser.add_option_group(group)

    group = OptionGroup(parser, "Browser Cache Invalidation Options")
    group.add_option("--cachebuster", dest="cachebuster", action='store_true',
            help=("use the sprite's sha1 first 6 characters as a "
                  "queryarg everytime that file is referred from the css"))
    group.add_option("--cachebuster-filename", dest="cachebuster_filename",
            action='store_true',
            help=("append the sprite's sha first 6 characters "
                  "to the otput filename"))
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    if options.version:
        sys.stdout.write("%s\n" % __version__)
        sys.exit(0)

    if options.cachebuster and options.cachebuster_filename:
        parser.error("You can't use --cachebuster and "
                     "--cachebuster-filename at the same time.")

    if not len(args):
        parser.error("You must provide the folder containing the sprites.")

    if len(args) == 1 and not (options.css_dir and options.img_dir):
        parser.error(("You must choose the output folder using either the "
                      "output argument or both --img and --css."))

    if len(args) == 2 and (options.css_dir or options.img_dir):
        parser.error(("You must choose between using an unique output dir, or "
                      "using --css and --img."))

    source = os.path.abspath(args[0])
    output = os.path.abspath(args[1]) if len(args) == 2 else None

    if not os.path.isdir(source):
        parser.error("Directory not found: '%s'" % source)

    if options.project:
        manager_cls = core.ProjectSpriteManager
    else:
        manager_cls = core.SimpleSpriteManager

    # Get configuration from file
    config = core.get_file_config(source)

    # Convert options to dict
    options = options.__dict__

    config = core.ConfigManager(config, priority=options, defaults=core.DEFAULT_SETTINGS)

    manager = manager_cls(path=source, output=output, config=config)

    if config.optipng and not core.command_exists(config.optipngpath):
        parser.error("'optipng' seems to be unavailable. You need to "
                     "install it before using --optipng, or "
                     "provide a path using --optipngpath.")

    if manager.config.watch:
        core.WatchManager(path=source, action=manager.process).run()
        sys.exit(0)

    try:
        manager.process()
    except exceptions.MultipleImagesWithSameNameError, e:
        sys.stderr.write("Error: Some images will have the same class name:\n")
        for image in e.args[0]:
            rel_path = os.path.relpath(image.path)
            sys.stderr.write('\t%s => .%s\n' % (rel_path, image.class_name))
        sys.exit(e.error_code)
    except exceptions.SourceImagesNotFoundError, e:
        sys.stderr.write("Error: No images found in %s.\n" % e.args[0])
        sys.exit(e.error_code)
    except exceptions.NoSpritesFoldersFoundError, e:
        sys.stderr.write("Error: No sprites folders found in %s.\n" % e.args[0])
        sys.exit(e.error_code)
    except exceptions.InvalidImageOrderingError, e:
        sys.stderr.write("Error: Invalid image ordering %s.\n" % e.args[0])
        sys.exit(e.error_code)
    except exceptions.InvalidImageAlgorithmError, e:
        sys.stderr.write("Error: Invalid image algorithm %s.\n" % e.args[0])
        sys.exit(e.error_code)
    except exceptions.PILUnavailableError, e:
        sys.stderr.write(("Error: PIL %s decoder is unavailable"
                          "Please read the documentation and "
                          "install it before spriting this kind of "
                          "images.\n") % e.args[0])
        sys.exit(e.error_code)
    except Exception:
        if config.debug:
            import platform
            sys.stderr.write("Glue version: %s\n" % __version__)
            sys.stderr.write("PIL version: %s\n" % PImage.VERSION)
            sys.stderr.write("Platform: %s\n" % platform.platform())
            sys.stderr.write("Config: %s\n" % config.sources)
            sys.stderr.write("Args: %s\n" % sys.argv)
            sys.stderr.write("\n")

        sys.stderr.write("Error: Unknown Error.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
