#!/usr/bin/env python
import re
import os
import copy
import ConfigParser
from optparse import OptionParser


from PIL import Image as PImage


class MultipleImagesWithSameNameError(Exception):
    """ Raised if two images are going to have the same css class name """
    pass


class SourceImagesNotFoundError(Exception):
    pass


class NoSpritesFoldersFoundError(Exception):
    pass


class InvalidImageOrderingAlgorithmError(Exception):
    pass


class Node(object):

    def __init__(self, x=0, y=0, width=0, height=0, used=False,
                 down=None, right=None):
        """ Node constructor """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.used = used
        self.right = right
        self.down = down

    def find(self, node, width, height):
        """ Find a node to allocate this image size """
        if node.used:
            return self.find(node.right, width, height) or \
                   self.find(node.down, width, height)
        elif node.width >= width and node.height >= height:
            return node
        return None

    def grow(self, width, height):
        """ Grow the canvas to the more appropriate direction """
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
        """ Grow the canvas to the right """
        old_self = copy.copy(self)
        self.used = True
        self.x = self.y = 0
        self.width += width
        self.down = old_self
        self.right = Node(x=old_self.width,
                          y=0,
                          width=width,
                          height=self.height)

        node = self.find(self, width, height)
        if node:
            return self.split(node, width, height)
        return None

    def grow_down(self, width, height):
        """ Grow the canvas down """
        old_self = copy.copy(self)
        self.used = True
        self.x = self.y = 0
        self.height += height
        self.right = old_self
        self.down = Node(x=0,
                         y=old_self.height,
                         width=self.width,
                         height=height)

        node = self.find(self, width, height)
        if node:
            return self.split(node, width, height)
        return None

    def split(self, node, width, height):
        """ Split the node. """
        node.used = True
        node.down = Node(x=node.x,
                               y=node.y + height,
                               width=node.width,
                               height=node.height - height)
        node.right = Node(x=node.x + width,
                                y=node.y,
                                width=node.width - width,
                                height=height)
        return node


class Image(object):

    ORDERINGS = ['maxside', 'width', 'height', 'area']

    def __init__(self, name, sprite):
        """ Image constructor """
        self.name = name
        self.sprite = sprite
        self.filename, self.format = name.rsplit('.', 1)
        image_path = os.path.join(sprite.path, name)

        image_file = open(image_path, "rb")
        self.image = PImage.open(image_file)
        self.image.load()
        image_file.close()

        self.width, self.height = self.image.size

        self.width += self.padding[1] + self.padding[3]
        self.height += self.padding[0] + self.padding[2]
        self.node = None

    def _generate_padding(self, padding):
        if type(padding) == str:
            padding = padding.split()

        if len(padding) == 3:
            padding = padding + [padding[1]]
        elif len(padding) == 2:
            padding = padding * 2
        elif len(padding) == 1:
            padding = padding * 4
        elif len(padding) == 0:
            padding = [self.DEFAULT_PADDING] * 4
        return map(int, padding)

    @property
    def stylesheet_data(self):
        return {'namespace': self.sprite.namespace,
                'sprite_url': self.sprite.image_url,
                'image_class_name': self.class_name,
                'top': self.node.y * -1 if self.node.y else 0,
                'left': self.node.x * -1 if self.node.x else 0}

    @property
    def class_name(self):
        """CSS class name for this file.

        The class name will only contain the alphanumeric characters,
        '-' and '_'. This css class name will have the following format:

        i.e:
            animals/cat.png css class will be .sprite-animals-cat
            animals/cow-20.png css class will be .sprite-animals-cow"""

        padding_info_name = '-'.join(self._padding_info)
        if padding_info_name:
            padding_info_name = '_%s' % padding_info_name
        name = self.filename[:len(padding_info_name) * -1 or None]
        name = re.sub(r'[^\w\-\_]', '', name)
        return '%s-%s' % (self.sprite.namespace, name)

    @property
    def _padding_info(self):
        """
        Extract the padding information from the filename
        """
        padding_info = self.filename.rsplit('_', 1)[-1]
        if re.match(r"^(\d+-?){,4}\d+$", padding_info):
            return padding_info.split('-')
        return []

    @property
    def padding(self):
        """
        Return the padding for this image based on the filename.

        i.e:
            filename.png wil have the default padding (10px).
            filename-20-.png will have 20px all arround the image.
            filename-1-2-3.png will have 1px 2px 3px 2px arround the image.
            filename-1-2-3-4.png will have 1px 2px 3px 4px arround the image.
        """
        padding = self._padding_info
        if len(padding) == 0:
            padding = self.sprite.config.get('defaults', 'padding')
        return self._generate_padding(padding)

    @property
    def x(self):
        return self.node.x + self.padding[3]

    @property
    def y(self):
        return self.node.y + self.padding[0]

    def __lt__(self, img):
        """Use the maxside, width, height or area as ordering algorithm."""
        algorithm = self.sprite.get_conf('algorithm')
        if algorithm == 'width':
            return self.width <= img.width
        elif algorithm == 'height':
            return self.height <= img.height
        elif algorithm == 'area':
            return self.width * self.height <= img.width * img.height
        else:
            return max(self.width, self.height) <= max(img.width, img.height)


class Sprite(object):

    DEFAULT_SETTINGS = {'padding': '10',
                        'algorithm': 'maxside',
                        'name': '',
                        'namespace': '',
                        'less': False,
                        'css': True,
                        'url': ''}

    def __init__(self, name, path, manager):
        self.name = name
        self.manager = manager
        self.images = []
        self.path = path

        algorithm = self.get_conf('algorithm')
        if algorithm not in Image.ORDERINGS:
            raise InvalidImageOrderingAlgorithmError(algorithm)

        self.process()

    def process(self):
        """
        Process a path searching for all the available images and
        generate an apropiate image sprite and css file.

        both as css and sprite image will be created inside the output_path
        inside a subdirectory corresponding to the sprite name.
        """
        self.images = self._locate_images()
        width = self.images[0].width
        height = self.images[0].height
        root = Node(width=width, height=height)

        # Loot all over the images creating a binary tree
        for image in self.images:
            print "\t %s => .%s" % (image.name, image.class_name)
            node = root.find(root, image.width, image.height)
            if node:  # Use this node
                image.node = root.split(node, image.width, image.height)
            else:  # Grow the canvas
                image.node = root.grow(image.width, image.height)

    def _locate_images(self):
        """
        Find all the images within a folder

        All the files with an extension not included in VALID_IMAGE_EXTENSIONS
        or begging with a '.' will be ignored.
        """
        extensions = '|'.join(self.manager.VALID_IMAGE_EXTENSIONS)
        extension_re = re.compile('.+\.(%s)$' % extensions, re.IGNORECASE)

        images = [Image(name, sprite=self) for name in os.listdir(self.path) if \
                                    not name.startswith('.') and \
                                    extension_re.match(name)]

        if len(images) == 0:
            raise SourceImagesNotFoundError()

        # Check if there are duplicate class names
        class_names = [i.class_name for i in images]
        if len(set(class_names)) != len(images):
            dup = [i for i in images if class_names.count(i.class_name) > 1]
            raise MultipleImagesWithSameNameError(dup)

        return sorted(images, reverse=True)

    def save_image(self):
        print "Generating '%s' image file..." % self.name
        sprite_output_path = self.manager.output_path(self.name)
        # Search for the max x and y neccesary to generate the canvas.
        width = height = 0

        for image in self.images:
            padding = image.padding
            x = image.node.x + image.width + padding[1] + padding[3]
            y = image.node.y + image.height + padding[0] + padding[2]
            if width < x:
                width = x
            if height < y:
                height = y

        # Create the sprite canvas
        canvas = PImage.new('RGBA', (width, height), (0, 0, 0, 0))

        # Paste the images inside the canvas
        for image in self.images:
            canvas.paste(image.image, (image.x, image.y))

        # Save png
        sprite_filename = '%s.png' % self.filename
        sprite_image_path = os.path.join(sprite_output_path, sprite_filename)
        canvas.save(sprite_image_path)

    def save_css(self):
        print "Generating '%s' css file..." % self.name

        # Generate css files
        css_filename = os.path.join(self.output_path, '%s.css' % self.filename)
        css_file = open(css_filename, 'w')

        # Create all the necessary class names
        for image in self.images:
            css_file.write((".%(image_class_name)s{ "
                            "background:url('%(sprite_url)s');"
                            " top:%(top)i; left:%(left)i;"
                            " no-repeat;}\n") % image.stylesheet_data)
        css_file.close()

    def save_less(self):
        print "Generating '%s' less file..." % self.name

        # Generate less files
        less_filename = os.path.join(self.output_path, '%s.less' % self.filename)
        less_file = open(less_filename, 'w')

        less_file.write('@%s-base-url: "%s";\n' % (self.namespace,
                                                   self.image_url))

        # Create all the necessary class names
        for image in self.images:
            less_file.write(('.%(image_class_name)s{ '
                             'background:url("@{%(namespace)s-base-url}");'
                             ' top:%(top)i; left:%(left)i;'
                             ' no-repeat;}\n') % image.stylesheet_data)
        less_file.close()

    @property
    def namespace(self):
        if self.get_conf('namespace'):
            return self.get_conf('namespace')
        return 'sprite-%s' % self.name

    @property
    def filename(self):
        output_name = self.get_conf('name')
        if not output_name:
            output_name = self.name
        return output_name

    @property
    def image_path(self):
        return os.path.join(self.output_path, '%s.png' % self.filename)

    @property
    def output_path(self):
        return self.manager.output_path(self.name)

    @property
    def image_url(self):
        return os.path.join(self.get_conf('url'), self.image_path)

    @property
    def config(self):
        if not getattr(self, '_config', None):
            self._config = ConfigParser.RawConfigParser(self.DEFAULT_SETTINGS)
            self._config.read(os.path.join(self.path, 'sprite.conf'))
        return self._config

    def get_conf(self, name):
        try:
            value = getattr(self.manager.options, name, None) or \
               self.config.get('defaults', name)
        except ConfigParser.NoSectionError:
            value = self.DEFAULT_SETTINGS.get(name)

        if name in ['css', 'less']:
            return {'true': True, 'false': False}.get(value.lower())
        return value


class BaseManager(object):

    VALID_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

    def __init__(self, path, options):
        """ SpriteManager constructor """
        self.path = path
        self.options = options
        self.sprites = []

    def process_sprite(self, path, name):
        print "Processing '%s':" % name
        sprite = Sprite(name=name, path=path, manager=self)
        self.sprites.append(sprite)

    def save(self):
        for sprite in self.sprites:
            sprite.save_image()
            if sprite.get_conf('css'):
                sprite.save_css()
            if sprite.get_conf('less'):
                sprite.save_less()

    def output_path(self, name):
        # Generate output dir
        sprite_output_path = os.path.join(self.options.dir, name)
        if not os.path.exists(sprite_output_path):
            os.makedirs(sprite_output_path)
        return sprite_output_path


class MultipleSpriteManager(BaseManager):

    def process(self):
        """
        Process a path searching for folders that contains images
        Every folder will be used as one sprite, and will contain all the
        images inside the folder.

        The filename of the images also can contain information about the
        padding needed arround the image.

        i.e:
            filename.png wil have the default padding (10px).
            filename-20.png will have 20px all arround the image.
            filename-1-2-3.png will have 1px 2px 3px 2px arround the image.
            filename-1-2-3-4.png will have 1px 2px 3px 4px arround the image.

        The generated css file will contain a css class for every image found
        inside the sprite folder. The class name will only contain the
        alphanumeric characters, '-' and '_' .This css class name will have the
        following format:

        i.e:
            animals/cat.png css class will be .sprite-animals-cat
            animals/cow-20.png css class will be .sprite-animals-cow

        If two images has the same name, an error will be raised.
        """
        for sprite_name in os.listdir(self.path):
            # Only process folders
            path = os.path.join(self.path, sprite_name)
            if os.path.isdir(path):
                self.process_sprite(path=path, name=sprite_name)

        if len(self.sprites) == 0:
            raise NoSpritesFoldersFoundError()

        self.save()


class SimpleSpriteManager(BaseManager):

    def process(self):
        self.process_sprite(path=self.path, name=os.path.basename(self.path))
        self.save()


def main():
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="dir", default='sprites',
                    help="Output directory for the sprites, css and less files")
    parser.add_option("-l", "--less", action="store_true", dest="less",
                      help="Generate .less files", default=None)
    parser.add_option("-u", "--url", dest="url", default=None,
                      help="Prepend this url to the sprites urls")
    parser.add_option("-n", "--nocss", action="store_false", dest="css",
                      default=None, help="Don't create css files")
    parser.add_option("-s", "--simple", action="store_true", dest="simple",
                      help="Only generate sprites for one folder")
    parser.add_option("--namespace", dest="namespace",  default=None,
                      help="Namespace for the css and less styles")
    parser.add_option("-f", "--name", dest="name", default=None,
                      help="Force sprite, css and less file names")
    parser.add_option("-a", "--algorithm", dest="algorithm", default=None,
                    help="Ordering algorithm: maxside, width, height or area")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("You must choose the folder that contains the sprites.")

    if options.simple:
        manager_cls = SimpleSpriteManager
    else:
        manager_cls = MultipleSpriteManager

    manager = manager_cls(path=os.path.abspath(args[0]), options=options)

    try:
        manager.process()
    except MultipleImagesWithSameNameError, e:
        print "Conflict: Two or more images will have the same class name:"
        for image in e.args[0]:
            print '\t %s => %s' % (image.name, image.class_name)
    except SourceImagesNotFoundError, e:
        print "Error: No images found."
    except NoSpritesFoldersFoundError, e:
        print "Error: No sprite folders found."


if __name__ == "__main__":
    main()
