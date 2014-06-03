import re
import os
import sys
import copy
import hashlib
import StringIO
import ConfigParser

from PIL import Image as PILImage

from glue.algorithms import algorithms
from glue.helpers import cached_property, round_up
from glue.formats import ImageFormat
from glue.exceptions import SourceImagesNotFoundError, PILUnavailableError


class ConfigurableFromFile(object):

    def _get_config_from_file(self, filename, section):
        """Return, as a dictionary, all the available configuration inside the
        sprite configuration file on this sprite path."""

        def clean(value):
            return {'true': True, 'false': False}.get(value.lower(), value)

        config = ConfigParser.RawConfigParser()
        config.read(os.path.join(self.config_path, filename))
        try:
            keys = config.options(section)
        except ConfigParser.NoSectionError:
            return {}
        return dict([[k, clean(config.get(section, k))] for k in keys])


class Image(ConfigurableFromFile):

    def __init__(self, path, config):
        self.path = path
        self.filename = os.path.basename(path)
        self.dirname = self.config_path = os.path.dirname(path)

        self.config = copy.deepcopy(config)
        self.config.update(self._get_config_from_file('sprite.conf', self.filename))

        self.x = self.y = None
        self.original_width = self.original_height = 0

        with open(self.path, "rb") as img:
            self._image_data = img.read()

        print "\t{0} added to sprite".format(self.filename)

    @cached_property
    def image(self):
        """Return a Pil representation of this image """

        if sys.version < '3':
            imageio = StringIO.StringIO(self._image_data)
        else:
            imageio = StringIO.BytesIO(self._image_data)

        try:
            source_image = PILImage.open(imageio)
            img = PILImage.new('RGBA', source_image.size, (0, 0, 0, 0))

            if source_image.mode == 'L':
                alpha = source_image.split()[0]
                transparency = source_image.info.get('transparency')
                mask = PILImage.eval(alpha, lambda a: 0 if a == transparency else 255)
                img.paste(source_image, (0, 0), mask=mask)
            else:
                img.paste(source_image, (0, 0))
        except IOError, e:
            raise PILUnavailableError(e.args[0].split()[1])
        finally:
            imageio.close()

        self.original_width, self.original_height = img.size

        # Crop the image searching for the smallest possible bounding box
        # without losing any non-transparent pixel.
        # This crop is only used if the crop flag is set in the config.
        if self.config['crop']:
            img = img.crop(img.split()[-1].getbbox())
        return img

    @property
    def width(self):
        """Return Image width"""
        return self.image.size[0]

    @property
    def height(self):
        """Return Image height"""
        return self.image.size[1]

    @property
    def padding(self):
        """Return a 4-elements list with the desired padding."""
        return self._generate_spacing_info(self.config['padding'])

    @property
    def margin(self):
        """Return a 4-elements list with the desired marging."""
        return self._generate_spacing_info(self.config['margin'])

    def _generate_spacing_info(self, data):

        data = data.split(',' if ',' in data else ' ')

        if len(data) == 4:
            data = data
        elif len(data) == 3:
            data = data + [data[1]]
        elif len(data) == 2:
            data = data * 2
        elif len(data) == 1:
            data = data * 4
        else:
            data = [0] * 4

        return map(int, data)

    @cached_property
    def horizontal_spacing(self):
        """Return the horizontal padding and margin for this image."""
        return self.padding[1] + self.padding[3] + self.margin[1] + self.margin[3]

    @cached_property
    def vertical_spacing(self):
        """Return the vertical padding and margin for this image."""
        return self.padding[0] + self.padding[2] + self.margin[0] + self.margin[2]

    @property
    def absolute_width(self):
        """Return the total width of the image taking count of the margin,
        padding and ratio."""
        return round_up(self.width + self.horizontal_spacing * max(self.config['ratios']))

    @property
    def absolute_height(self):
        """Return the total height of the image taking count of the margin,
        padding and ratio.
        """
        return round_up(self.height + self.vertical_spacing * max(self.config['ratios']))

    def __lt__(self, img):
        """Use maxside, width, hecight or area as ordering algorithm.

        :param img: Another :class:`~Image`."""
        ordering = self.config['algorithm_ordering']
        ordering = ordering[1:] if ordering.startswith('-') else ordering

        if ordering == "filename":
            return sorted([self.filename, img.filename])[0] == img.filename
        if ordering == 'width':
            return self.absolute_width <= img.absolute_width
        elif ordering == 'height':
            return self.absolute_height <= img.absolute_height
        elif ordering == 'area':
            return self.absolute_width * self.absolute_height <= img.absolute_width * img.absolute_height
        else:
            return max(self.absolute_width, self.absolute_height) <= max(img.absolute_width, img.absolute_height)


class Sprite(ConfigurableFromFile):

    config_filename = 'sprite.conf'
    config_section = 'sprite'
    valid_extensions = ['png', 'jpg', 'jpeg', 'gif']

    def __init__(self, path, config, name=None):
        self.path = self.config_path = path
        self.config = copy.deepcopy(config)
        self.config.update(self._get_config_from_file('sprite.conf', 'sprite'))
        self.name = name or self.config.get('name', os.path.basename(path))

        # Setup ratios
        ratios = self.config['ratios'].split(',')
        ratios = set([float(r.strip()) for r in ratios if r.strip()])

        # Always add 1.0 as a required ratio
        ratios.add(1.0)

        # Create a sorted list of ratios
        self.ratios = sorted(ratios)
        self.max_ratio = max(self.ratios)
        self.config['ratios'] = self.ratios

        # Discover images inside this sprite
        self.images = self._locate_images()

        img_format = ImageFormat(sprite=self)
        for ratio in ratios:
            ratio_output_key = 'ratio_{0}_output'.format(ratio)
            if ratio_output_key not in self.config:
                self.config[ratio_output_key] = img_format.output_path(ratio)

        print "Processing '{0}':".format(self.name)

        # Generate sprite map
        self.process()

    def process(self):
        algorithm_cls = algorithms[self.config['algorithm']]
        algorithm = algorithm_cls()
        algorithm.process(self)

    def validate(self):
        pass

    @cached_property
    def hash(self):
        """ Return a hash of this sprite. In order to detect any change on
        the source images  it use the data, order and path of each image.
        In the same way it use this sprite settings as part of the hash.
        """
        hash_list = []
        for image in self.images:
            hash_list.append(os.path.relpath(image.path))
            hash_list.append(image._image_data)

        for key, value in self.config.iteritems():
            hash_list.append(key)
            hash_list.append(value)

        if sys.version < '3':
            return hashlib.sha1(''.join(map(str, hash_list))).hexdigest()[:10]
        return hashlib.sha1(''.join(map(str, hash_list)).encode('utf-8')).hexdigest()[:10]

    @cached_property
    def canvas_size(self):
        """Return the width and height for this sprite canvas"""
        width = height = 0
        for image in self.images:
            x = image.x + image.absolute_width
            y = image.y + image.absolute_height
            if width < x:
                width = x
            if height < y:
                height = y
        return round_up(width), round_up(height)

    def sprite_path(self, ratio=1.0):
        return self.config['ratio_{0}_output'.format(ratio)]

    def _locate_images(self):
        """Return all valid images within a folder.

        All files with a extension not included in
        (png, jpg, jpeg and gif) or beginning with '.' will be ignored.

        If the folder doesn't contain any valid image it will raise
        :class:`~SourceImagesNotFoundError`

        The list of images will be ordered using the desired ordering
        algorithm. The default is 'maxside'.
        """
        extensions = '|'.join(self.valid_extensions)
        extension_re = re.compile('.+\.(%s)$' % extensions, re.IGNORECASE)
        files = sorted(os.listdir(self.path))

        images = []
        for root, dirs, files in os.walk(self.path, followlinks=self.config['follow_links']):
            for filename in sorted(files):
                if not filename.startswith('.') and extension_re.match(filename):
                    images.append(Image(path=os.path.join(root, filename), config=self.config))
            if not self.config['recursive']:
                break

        if not images:
            raise SourceImagesNotFoundError(self.path)

        images = sorted(images, reverse=self.config['algorithm_ordering'][0] != '-')

        return images
