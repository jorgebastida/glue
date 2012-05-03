#!/usr/bin/env python

import re
import os
import sys
import copy
import hashlib
import subprocess
import ConfigParser
from optparse import OptionParser, OptionGroup

from PIL import Image as PImage

__version__ = '0.2.3'

TRANSPARENT = (255, 255, 255, 0)

CAMELCASE_SEPARATOR = 'camelcase'
CONFIG_FILENAME = 'sprite.conf'
ORDERINGS = ['maxside', 'width', 'height', 'area']
VALID_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
PSEUDO_CLASSES = set(['link', 'visited', 'active', 'hover', 'focus',
                      'first-letter', 'first-line', 'first-child',
                      'before', 'after'])

DEFAULT_SETTINGS = {'padding': '0',
                    'algorithm': 'square',
                    'ordering': 'maxside',
                    'namespace': 'sprite',
                    'crop': False,
                    'url': '',
                    'less': False,
                    'optipng': False,
                    'ignore_filename_paddings': False,
                    'png8': False,
                    'separator': '-',
                    'global_template': ('%(all_classes)s{background-image:'
                                        'url(%(sprite_url)s);'
                                        'background-repeat:no-repeat}\n'),
                    'each_template': ('%(class_name)s{'
                                      'background-position:%(x)s %(y)s;'
                                      'width:%(width)s;height:%(height)s;}\n')}


class MultipleImagesWithSameNameError(Exception):
    """Raised if two images pretend to generate the same CSS class name."""
    pass


class SourceImagesNotFoundError(Exception):
    """Raised if a folder doesn't contain any valid image."""
    pass


class NoSpritesFoldersFoundError(Exception):
    """Raised if no sprites folders could be found."""
    pass


class InvalidImageAlgorithmError(Exception):
    """Raised if the provided algorithm name is invalid."""
    pass


class InvalidImageOrderingError(Exception):
    """Raised if the provided ordering is invalid."""
    pass


class SquareAlgorithmNode(object):

    def __init__(self, x=0, y=0, width=0, height=0, used=False,
                 down=None, right=None):
        """Node constructor.

        :param x: X coordinate.
        :param y: Y coordinate.
        :param width: Image width.
        :param height: Image height.
        :param used: Flag to determine if the node is used.
        :param down: Down :class:`~Node`.
        :param right Right :class:`~Node`.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.used = used
        self.right = right
        self.down = down

    def find(self, node, width, height):
        """Find a node to allocate this image size (width, height).

        :param node: Node to search in.
        :param width: Pixels to grow down (width).
        :param height: Pixels to grow down (height).
        """
        if node.used:
            return self.find(node.right, width, height) or \
                   self.find(node.down, width, height)
        elif node.width >= width and node.height >= height:
            return node
        return None

    def grow(self, width, height):
        """ Grow the canvas to the most appropriate direction.

        :param width: Pixels to grow down (width).
        :param height: Pixels to grow down (height).
        """
        can_grow_d = width <= self.width
        can_grow_r = height <= self.height

        should_grow_r = can_grow_r and self.height >= (self.width + width)
        should_grow_d = can_grow_d and self.width >= (self.height + height)

        if should_grow_r:
            return self.grow_right(width, height)
        elif should_grow_d:
            return self.grow_down(width, height)
        elif can_grow_r:
            return self.grow_right(width, height)
        elif can_grow_d:
            return self.grow_down(width, height)

        return None

    def grow_right(self, width, height):
        """Grow the canvas to the right.

        :param width: Pixels to grow down (width).
        :param height: Pixels to grow down (height).
        """
        old_self = copy.copy(self)
        self.used = True
        self.x = self.y = 0
        self.width += width
        self.down = old_self
        self.right = SquareAlgorithmNode(x=old_self.width,
                                         y=0,
                                         width=width,
                                         height=self.height)

        node = self.find(self, width, height)
        if node:
            return self.split(node, width, height)
        return None

    def grow_down(self, width, height):
        """Grow the canvas down.

        :param width: Pixels to grow down (width).
        :param height: Pixels to grow down (height).
        """
        old_self = copy.copy(self)
        self.used = True
        self.x = self.y = 0
        self.height += height
        self.right = old_self
        self.down = SquareAlgorithmNode(x=0,
                                        y=old_self.height,
                                        width=self.width,
                                        height=height)

        node = self.find(self, width, height)
        if node:
            return self.split(node, width, height)
        return None

    def split(self, node, width, height):
        """Split the node to allocate a new one of this size.

        :param node: Node to be splitted.
        :param width: New node width.
        :param height: New node height.
        """
        node.used = True
        node.down = SquareAlgorithmNode(x=node.x,
                                        y=node.y + height,
                                        width=node.width,
                                        height=node.height - height)
        node.right = SquareAlgorithmNode(x=node.x + width,
                                         y=node.y,
                                         width=node.width - width,
                                         height=height)
        return node


class SquareAlgorithm(object):

    def process(self, sprite):

        root = SquareAlgorithmNode(width=sprite.images[0].absolute_width,
                    height=sprite.images[0].absolute_height)

        # Loot all over the images creating a binary tree
        for image in sprite.images:
            node = root.find(root, image.absolute_width, image.absolute_height)
            if node:  # Use this node
                node = root.split(node, image.absolute_width,
                                        image.absolute_height)
            else:  # Grow the canvas
                node = root.grow(image.absolute_width, image.absolute_height)

            image.x = node.x
            image.y = node.y


class VerticalAlgorithm(object):

    def process(self, sprite):
        y = 0
        for image in sprite.images:
            image.x = 0
            image.y = y
            y += image.absolute_height


class VerticalRightAlgorithm(object):

    def process(self, sprite):
        max_width = max([i.width for i in sprite.images])
        y = 0
        for image in sprite.images:
            image.x = max_width - image.width
            image.y = y
            y += image.absolute_height


class HorizontalAlgorithm(object):

    def process(self, sprite):
        x = 0
        for image in sprite.images:
            image.y = 0
            image.x = x
            x += image.absolute_width


class HorizontalBottomAlgorithm(object):

    def process(self, sprite):
        max_height = max([i.height for i in sprite.images])
        x = 0
        for image in sprite.images:
            image.y = max_height - image.height
            image.x = x
            x += image.absolute_width


class DiagonalAlgorithm(object):

    def process(self, sprite):
        x = y = 0
        for image in sprite.images:
            image.x = x
            image.y = y
            x += image.absolute_width
            y += image.absolute_height


ALGORITHMS = {'square': SquareAlgorithm,
              'vertical': VerticalAlgorithm,
              'vertical-right': VerticalRightAlgorithm,
              'horizontal': HorizontalAlgorithm,
              'horizontal-bottom': HorizontalBottomAlgorithm,
              'diagonal': DiagonalAlgorithm}


class Image(object):

    def __init__(self, name, sprite):
        """Image constructor

        :param name: Image name.
        :param sprite: :class:`~Sprite` instance for this image."""
        self.x = None
        self.y = None
        self.name = name
        self.sprite = sprite
        self.filename, self.format = name.rsplit('.', 1)

        pseudo = set(self.filename.split('_')).intersection(PSEUDO_CLASSES)
        self.pseudo = ':%s' % list(pseudo)[-1] if pseudo else ''

        image_path = os.path.join(sprite.path, name)
        image_file = open(image_path, "rb")

        try:
            source_image = PImage.open(image_file)
            source_image.load()
            self.image = PImage.new('RGBA', source_image.size, (0, 0, 0, 0))

            if source_image.mode == 'L':
                alpha = source_image.split()[0]
                mask = PImage.eval(alpha, lambda a: 0 if a == source_image.info.get('transparency', 0) else 255)
                self.image.paste(source_image, (0, 0), mask=mask)
            else:
                self.image.paste(source_image, (0, 0))

        except IOError, e:
            sys.stderr.write(("ERROR: PIL %s decoder is unavailable. "
                              "Please read the documentation and "
                              "install it before spriting this kind of "
                              "images.\n" % e.args[0].split()[1]))
            sys.exit(1)

        image_file.close()

        if self.sprite.config.crop:
            self._crop_image()

        self.width, self.height = self.image.size
        self.absolute_width = self.width + self.padding[1] + self.padding[3]
        self.absolute_height = self.height + self.padding[0] + self.padding[2]

    def _crop_image(self):
        """Crop the image searching for the smallest possible bounding box
        without losing any non-transparent pixel.

        This crop is only used if the crop flag is set in the config.
        """
        width, height = self.image.size
        maxx = maxy = 0
        minx = miny = sys.maxint

        for x in xrange(width):
            for y in xrange(height):
                if y > miny and y < maxy and maxx == x:
                    continue
                if self.image.getpixel((x, y)) != TRANSPARENT:
                    if x < minx:
                        minx = x
                    if x > maxx:
                        maxx = x
                    if y < miny:
                        miny = y
                    if y > maxy:
                        maxy = y
        self.image = self.image.crop((minx, miny, maxx + 1, maxy + 1))

    def _generate_padding(self, padding):
        """Return a 4-elements list with the desired padding.

        :param padding: Padding as a list or a raw string representing
                        the padding for this image."""

        if type(padding) == str:
            padding = padding.replace('px', '').split()

        if len(padding) == 4:
            padding = padding
        elif len(padding) == 3:
            padding = padding + [padding[1]]
        elif len(padding) == 2:
            padding = padding * 2
        elif len(padding) == 1:
            padding = padding * 4
        else:
            padding = [DEFAULT_SETTINGS['padding']] * 4
        return map(int, padding)

    @property
    def class_name(self):
        """Return the CSS class name for this file.

        This CSS class name will have the following format:

        ``.[namespace]-[sprite_name]-[image_name]{ ... }``

        The image_name will only contain alphanumeric characters,
        ``-`` and ``_``. The default namespace is ``sprite``, but it could
        be overridden using the ``--namespace`` optional argument.


        * ``animals/cat.png`` will be ``.sprite-animals-cat``
        * ``animals/cow_20.png`` will be ``.sprite-animals-cow``
        * ``animals/cat_hover.png`` will be ``.sprite-animals-cat:hover``
        * ``animals/cow_20_hover.png`` will be ``.sprite-animals-cow:hover``

        The separator used is also configurable using the ``--separator``
        option. For a camelCase representation of the CSS class name use
        ``camelcase`` as separator.
        """
        name = self.filename

        # Remove padding information
        if not self.sprite.manager.config.ignore_filename_paddings:
            padding_info_name = '-'.join(self._padding_info)
            if padding_info_name:
                padding_info_name = '_%s' % padding_info_name
            name = name.replace(padding_info_name, '')

        # Remove pseudo-class information
        if self.pseudo:
            name = name.replace('_%s' % self.pseudo[1:], '')

        # Clean filename
        name = re.sub(r'[^\w\-_]', '', name)

        # Customize the name if necessary
        separator = self.sprite.manager.config.separator
        if separator == CAMELCASE_SEPARATOR:
            separator = ''
            if self.sprite.namespace:
                name = name[:1].capitalize() + name[1:]

        # Add pseudo-class information
        name = '%s%s' % (name, self.pseudo)

        return separator.join([self.sprite.namespace, name])

    @property
    def _padding_info(self):
        """Return the padding information from the filename."""
        for block in self.filename.split('_')[::-1]:
            if re.match(r"^(\d+-?){,3}\d+$", block):
                return block.split('-')
        return []

    @property
    def padding(self):
        """Return the padding for this image based on the filename and
        the sprite settings file.

        * ``filename.png`` will have the default padding ``10px``.
        * ``filename_20.png`` -> ``20px`` all around the image.
        * ``filename_1-2-3.png`` -> ``1px 2px 3px 2px`` around the image.
        * ``filename_1-2-3-4.png`` -> ``1px 2px 3px 4px`` around the image.

        """
        padding = self._padding_info
        if len(padding) == 0 or \
           self.sprite.manager.config.ignore_filename_paddings:
            padding = self.sprite.config.padding
        return self._generate_padding(padding)

    def __lt__(self, img):
        """Use maxside, width, height or area as ordering algorithm.

        :param img: Another :class:`~Image`."""
        ordering = self.sprite.config.ordering
        ordering = ordering[1:] if ordering.startswith('-') else ordering

        if ordering not in ORDERINGS:
            raise InvalidImageOrderingError(ordering)

        if ordering == 'width':
            return self.absolute_width <= img.absolute_width
        elif ordering == 'height':
            return self.absolute_height <= img.absolute_height
        elif ordering == 'area':
            return self.absolute_width * self.absolute_height <= \
                   img.absolute_width * img.absolute_height
        else:
            return max(self.absolute_width, self.absolute_height) <= \
                   max(img.absolute_width, img.absolute_height)


class Sprite(object):

    def __init__(self, name, path, manager):
        """Sprite constructor.

        :param name: Sprite name.
        :param path: Sprite path
        :param manager: Sprite manager. :class:`~ProjectSpriteManager` or
                        :class:`SimpleSpriteManager`"""
        self.name = name
        self.manager = manager
        self.images = []
        self.path = path
        self.cachebuster_hash = ''

        self.config = manager.config.extend(get_file_config(self.path))
        self.process()

    def process(self):
        """Process a sprite path searching for all the images and then
        allocate all of them in the most appropriate position.
        """

        algorithm = ALGORITHMS.get(self.config.algorithm)

        if not algorithm:
            raise InvalidImageAlgorithmError(self.config.algorithm)

        self.algorithm = algorithm()
        self.images = self._locate_images()

        self.algorithm.process(self)

    def _locate_images(self):
        """Return all valid images within a folder.

        All files with a extension not included i
        (png, jpg, jpeg and gif) or beginning with '.' will be ignored.

        If the folder doesn't contain any valid image it will raise
        :class:`~MultipleImagesWithSameNameError`

        The list of images will be ordered using the desired ordering
        algorithm. The default is 'maxside'.
        """
        extensions = '|'.join(VALID_IMAGE_EXTENSIONS)
        extension_re = re.compile('.+\.(%s)$' % extensions, re.IGNORECASE)

        images = [Image(n, sprite=self) for n in os.listdir(self.path) if \
                                    not n.startswith('.') and \
                                    extension_re.match(n)]

        if not len(images):
            raise SourceImagesNotFoundError()

        # Check if there are duplicate class names
        class_names = [i.class_name for i in images]
        if len(set(class_names)) != len(images):
            dup = [i for i in images if class_names.count(i.class_name) > 1]
            raise MultipleImagesWithSameNameError(dup)

        for image in images:
            self.manager.log("\t %s => .%s" % (image.name, image.class_name))

        return sorted(images, reverse=self.config.ordering[0] != '-')

    def save_image(self):
        """Create the image file for this sprite."""
        self.manager.log("Creating '%s' image file..." % self.name)

        sprite_output_path = self.manager.output_path('img')

        # Search for the max x and y (Necessary to generate the canvas).
        width = height = 0

        for image in self.images:
            x = image.x + image.absolute_width
            y = image.y + image.absolute_height
            if width < x:
                width = x
            if height < y:
                height = y

        # Create the sprite canvas
        canvas = PImage.new('RGBA', (width, height), (0, 0, 0, 0))

        # Paste the images inside the canvas
        for image in self.images:
            canvas.paste(image.image, (image.x + image.padding[3],
                                       image.y + image.padding[0]))

        if self.config.cachebuster or self.config.cachebuster_filename:
            self.cachebuster_hash = hashlib.sha1(canvas.tostring()
                                                ).hexdigest()[:6]

        # Save png
        sprite_filename = '%s.png' % self.filename
        sprite_image_path = os.path.join(sprite_output_path, sprite_filename)

        args, kwargs = [sprite_image_path], dict(optimize=True)

        if self.config.png8:
            # Get the alpha band
            alpha = canvas.split()[-1]
            canvas = canvas.convert('RGB'
                        ).convert('P', palette=PImage.ADAPTIVE, colors=255)

            # Set all pixel values below 128 to 255, and the rest to 0
            mask = PImage.eval(alpha, lambda a: 255 if a <= 128 else 0)

            # Paste the color of index 255 and use alpha as a mask
            canvas.paste(255, mask)
            kwargs.update({'transparency': 255})

        save = lambda: canvas.save(*args, **kwargs)
        save()

        if self.config.optipng:
            command = ["%s %s" % (self.config.optipngpath,
                                  sprite_image_path)]

            error = subprocess.call(command, shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
            if error:
                self.manager.log("Error: optipng has failed, reverting to "
                                 "the original file.")
                save()

    def save_css(self):
        """Create the CSS or LESS file for this sprite."""
        format = 'less' if self.config.less else 'css'
        self.manager.log("Creating '%s' %s file..." % (self.name, format))

        output_path = self.manager.output_path('css')
        filename = '%s.%s' % (self.filename, format)
        css_filename = os.path.join(output_path, filename)

        # Fix css urls on Windows
        css_filename = '/'.join(css_filename.split('\\'))

        css_file = open(css_filename, 'w')

        # get all the class names and join them
        class_names = ',\n'.join(['.%s' % i.class_name for i in self.images \
                                                  if ':' not in i.class_name])

        # add the global style for all the sprites for less bloat
        template = self.config.global_template.decode('unicode-escape')
        css_file.write(template % {'all_classes': class_names,
                                   'sprite_url': self.image_url})

        # compile one template for each file
        for image in self.images:

            x = '%spx' % (image.x * -1 if image.x else 0)
            y = '%spx' % (image.y * -1 if image.y else 0)
            height = '%spx' % image.absolute_height
            width = '%spx' % image.absolute_width

            template = self.config.each_template.decode('unicode-escape')
            css_file.write(template % {'class_name': '.%s' % image.class_name,
                                       'sprite_url': self.image_url,
                                       'height': height,
                                       'width': width,
                                       'y': y,
                                       'x': x})
        css_file.close()

    @property
    def namespace(self):
        """Return the namespace for this sprite."""

        namespace = [self.name]
        separator = self.config.separator

        if self.config.namespace:
            namespace.insert(0, self.config.namespace)

        if separator == CAMELCASE_SEPARATOR:
            namespace = [n.lower().capitalize() if i > 0 else n.lower() \
                                            for i, n in  enumerate(namespace)]
            separator = ''
        return separator.join(namespace)

    @property
    def filename(self):
        """Return the desired filename for files generated by this sprite."""
        if self.config.cachebuster_filename:
            return '%s_%s' % (self.name, self.cachebuster_hash)
        return self.name

    @property
    def image_path(self):
        """Return the output path for the image file."""
        return os.path.join(self.manager.output_path('img'),
                            '%s.png' % self.filename)

    @property
    def image_url(self):
        """Return the sprite image url."""
        url = os.path.relpath(self.image_path, self.manager.output_path('css'))

        if self.config.url:
            url = os.path.join(self.config.url, '%s.png' % self.filename)

        if self.config.cachebuster:
            url = "%s?%s" % (url, self.cachebuster_hash)

        return url


class ConfigManager(object):
    """Manage all the available configuration.

    If no config is available, return the default one."""

    def __init__(self, *args, **kwargs):
        """ConfigManager constructor.

        :param *args: List of config dictionaries. The order of this list is
                      important because as soon as a config property
                      is available it will be returned.
        :param defaults: Dictionary with the default configuration.
        :param priority: Dictionary with the command line configuration. This
                         configuration will override any other from any source.
        """
        self.defaults = kwargs.get('defaults', {})
        self.priority = kwargs.get('priority', {})
        self.sources = list(args)

    def extend(self, config):
        """Return a new :class:`~ConfigManager` instance with this new config
                         inside the sources list.

        :param config: Dictionary with the new config.
        """
        return self.__class__(config, *self.sources, priority=self.priority,
                              defaults=self.defaults)

    def __getattr__(self, name):
        """Return the first available configuration value for this key. This
        method always prioritizes the command line configuration. If this key
        is not available within any configuration dictionary, it returns the
        default value

        :param name: Configuration property name.
        """
        sources = [self.priority] + self.sources
        for source in sources:
            value = source.get(name)
            if value is not None:
                return value
        return self.defaults.get(name)


class BaseManager(object):

    def __init__(self, path, config, output=None):
        """BaseManager constructor.

        :param path: Sprite path.
        :param config: :class:`~ConfigManager` instance with all the
                       configuration for this sprite.
        :param output: output dir.
        """
        self.path = path
        self.config = config
        self.output = output
        self.sprites = []

    def process_sprite(self, path, name):
        """Create a new Sprite using this path and name and append it to the
        sprites list.

        :param path: Sprite path.
        :param name: Sprite name.
        """
        self.log("Processing '%s':" % name)
        sprite = Sprite(name=name, path=path, manager=self)
        self.sprites.append(sprite)

    def save(self):
        """Save all the sprites inside this manager."""
        for sprite in self.sprites:
            sprite.save_image()
            sprite.save_css()

    def output_path(self, format):
        """Return the path where all the generated files will be saved.

        :param format: File format.
        """
        if format == 'css' and self.config.css_dir:
            sprite_output_path = self.config.css_dir
        elif format == 'img' and self.config.img_dir:
            sprite_output_path = self.config.img_dir
        else:
            sprite_output_path = self.output
        if not os.path.exists(sprite_output_path):
            os.makedirs(sprite_output_path)
        return sprite_output_path

    def log(self, message):
        """Print the message if necessary."""
        if not self.config.quiet:
            print(message)

    def process(self):
        raise NotImplementedError()


class ProjectSpriteManager(BaseManager):

    def process(self):
        """Process a path searching for folders that contain images.
        Every folder will be a new sprite with all the images inside.

        The filename of the image can also contain information about the
        padding needed around the image.

        * ``filename.png`` will have the default padding (10px).
        * ``filename_20.png`` will have 20px all around the image.
        * ``filename_1-2-3.png`` will have 1px 2px 3px 2px around the image.
        * ``filename_1-2-3-4.png`` will have 1px 2px 3px 4px around the image.

        The generated CSS file will have a CSS class for every image found
        inside the sprites folder. These CSS class names will have the
        following format:

        ``.[namespace]-[sprite_name]-[image_name]{ ... }``

        The image_name will only contain alphanumeric characters,
        ``-`` and ``_``. The default namespace is ``sprite``, but it could be
        overridden using the ``--namespace`` optional argument.


        * ``animals/cat.png`` CSS class will be ``.sprite-animals-cat``
        * ``animals/cow_20.png`` CSS class will be ``.sprite-animals-cow``

        If two images have the same name,
        :class:`~MultipleImagesWithSameNameError` will be raised.

        This is not the default manager. It is only used if you use
        the ``--project`` argument.
        """
        for sprite_name in os.listdir(self.path):
            # Only process folders
            path = os.path.join(self.path, sprite_name)
            if os.path.isdir(path) and not sprite_name.startswith('.'):
                self.process_sprite(path=path, name=sprite_name)

        if not len(self.sprites):
            raise NoSpritesFoldersFoundError()

        self.save()


class SimpleSpriteManager(BaseManager):

    def process(self):
        """Process a single folder and create one sprite. It works the
        same way as :class:`~ProjectSpriteManager`, but only for one folder.

        This is the default manager.
        """
        self.process_sprite(path=self.path, name=os.path.basename(self.path))
        self.save()


def get_file_config(path, section='sprite'):
    """Return, as a dictionary, all the available configuration inside the
    sprite configuration file on this path.

    :param path: Path where the configuration file is.
    :param section: The configuration file section that needs to be read.
    """
    def clean(value):
        return {'true': True, 'false': False}.get(value.lower(), value)

    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(path, CONFIG_FILENAME))
    try:
        keys = config.options(section)
    except ConfigParser.NoSectionError:
        return {}
    return dict([[k, clean(config.get(section, k))] for k in keys])


def command_exists(command):
    """Check if a command exists by running it.

    :param command: command name.
    """
    try:
        subprocess.check_call([command], shell=True, stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return False
    return True


#########################################################################
# PIL currently doesn't support full alpha for PNG8 so it's necessary to
# monkey patch PIL to support them.
# http://mail.python.org/pipermail/image-sig/2010-October/006533.html
#########################################################################
from PIL import ImageFile, PngImagePlugin


def patched_chunk_tRNS(self, pos, len):
    i16 = PngImagePlugin.i16
    s = ImageFile._safe_read(self.fp, len)
    if self.im_mode == "P":
        self.im_info["transparency"] = map(ord, s)
    elif self.im_mode == "L":
        self.im_info["transparency"] = i16(s)
    elif self.im_mode == "RGB":
        self.im_info["transparency"] = i16(s), i16(s[2:]), i16(s[4:])
    return s
PngImagePlugin.PngStream.chunk_tRNS = patched_chunk_tRNS


def patched_load(self):
    if self.im and self.palette and self.palette.dirty:
        apply(self.im.putpalette, self.palette.getdata())
        self.palette.dirty = 0
        self.palette.rawmode = None
        try:
            trans = self.info["transparency"]
        except KeyError:
            self.palette.mode = "RGB"
        else:
            try:
                for i, a in enumerate(trans):
                    self.im.putpalettealpha(i, a)
            except TypeError:
                self.im.putpalettealpha(trans, 0)
            self.palette.mode = "RGBA"
    if self.im:
        return self.im.pixel_access(self.readonly)
PImage.Image.load = patched_load
#########################################################################


def main():
    parser = OptionParser(usage=("usage: %prog [options] source_dir [<output> "
                                 "| --css=<dir> --img=<dir>]"))
    parser.add_option("--project", action="store_true",
                  dest="project", help="generate sprites for multiple folders")
    parser.add_option("-c", "--crop", dest="crop", action='store_true',
                help="crop images removing unnecessary transparent margins")
    parser.add_option("-l", "--less", dest="less", action='store_true',
                help="generate output stylesheets as .less instead of .css")
    parser.add_option("-u", "--url", dest="url", default=None,
                      help="prepend this url to the sprites filename")
    parser.add_option("-q", "--quiet", dest="quiet", action='store_true',
                      help="suppress all normal output")
    parser.add_option("-p", "--padding", dest="padding", default=None,
                      help="force this padding in all images")
    parser.add_option("-v", "--version", action="store_true", dest="version",
                      help="show program's version number and exit")

    group = OptionGroup(parser, "Output Options")
    group.add_option("--css", dest="css_dir", default='',
                    help="output directory for css files", metavar='DIR')
    group.add_option("--img", dest="img_dir", default='', metavar='DIR',
                    help="output directory for img files")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Advanced Options")
    group.add_option("-a", "--algorithm", dest="algorithm", default=None,
                    help=("allocation algorithm: square, vertical, horizontal "
                          "(default: square)"), metavar='NAME')
    group.add_option("--ordering", dest="ordering", default=None,
                    help=("ordering criteria: maxside, width, height or "
                          "area (default: maxside)"), metavar='NAME')
    group.add_option("--namespace", dest="namespace",  default=None,
                      help="namespace for all css classes (default: sprite)")
    group.add_option("--png8", action="store_true", dest="png8",
                      help=("the output image format will be png8 "
                            "instead of png32"))
    group.add_option("--ignore-filename-paddings",
                      dest="ignore_filename_paddings", action='store_true',
                      help="ignore filename paddings")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Output CSS Template Options")
    group.add_option("--separator", dest="separator",
                    help=("Customize the separator used to join CSS class "
                          "names. If you want to use camelCase use "
                          "'camelcase' as separator."),
                    metavar='SEPARATOR')
    group.add_option("--global-template", dest="global_template",
                    help=("Customize the global section of the output CSS."
                          "This section will be added only once for each "
                          "sprite."),
                    metavar='TEMPLATE')

    group.add_option("--each-template", dest="each_template",
                    help=("Customize each image output CSS."
                          "This section will be added once for each "
                          "image inside the sprite."),
                    metavar='TEMPLATE')
    parser.add_option_group(group)

    group = OptionGroup(parser, "Optipng Options",
                      "You need to install optipng before using these options")
    group.add_option("--optipng", dest="optipng", action='store_true',
                help="postprocess images using optipng")
    group.add_option("--optipngpath", dest="optipngpath", default='optipng',
                    help="path to optipng (default: optipng)", metavar='PATH')
    parser.add_option_group(group)

    group = OptionGroup(parser, "Browser Cache Invalidation Options")
    group.add_option("--cachebuster", dest="cachebuster",
                    action='store_true',
                    help=("use the sprite's sha1 first 6 characters as a "
                          "queryarg everytime that file is referred from "
                          "the css"))
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

    if options.optipng and not command_exists(options.optipngpath):
        parser.error("'optipng' seems to be unavailable. You need to "
                     "install it before using --optipng, or "
                     "provide a path using --optipngpath.")

    source = os.path.abspath(args[0])
    output = os.path.abspath(args[1]) if len(args) == 2 else None

    if not os.path.isdir(source):
        parser.error("Directory not found: '%s'" % source)

    if options.project:
        manager_cls = ProjectSpriteManager
    else:
        manager_cls = SimpleSpriteManager

    # Get configuration from file
    config = get_file_config(source)

    # Convert options to dict
    options = options.__dict__

    config = ConfigManager(config, priority=options, defaults=DEFAULT_SETTINGS)
    manager = manager_cls(path=source, output=output, config=config)

    try:
        manager.process()
    except MultipleImagesWithSameNameError, e:
        sys.stderr.write("Error: Some images will have the same class name:\n")
        for image in e.args[0]:
            sys.stderr.write('\t %s => .%s\n' % (image.name, image.class_name))
    except SourceImagesNotFoundError:
        sys.stderr.write("Error: No images found.\n")
    except NoSpritesFoldersFoundError:
        sys.stderr.write("Error: No sprites folders found.\n")
    except InvalidImageOrderingError, e:
        sys.stderr.write("Error: Invalid image ordering %s.\n" % e.args[0])
    except InvalidImageAlgorithmError, e:
        sys.stderr.write("Error: Invalid image algorithm %s.\n" % e.args[0])


if __name__ == "__main__":
    main()
