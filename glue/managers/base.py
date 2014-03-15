from glue.core import Sprite
from glue.formats import formats


class BaseManager(object):

    def __init__(self, *args, **kwargs):
        self.config = kwargs
        self.sprites = []

    def process(self):
        self.find_sprites()
        self.validate()
        self.save()

    def add_sprite(self, path):
        """Create a new Sprite using this path and name and append it to the
        sprites list.

        :param path: Sprite path.
        :param name: Sprite name.
        """
        sprite = Sprite(path=path, config=self.config)
        self.sprites.append(sprite)

    def find_sprites(self):
        raise NotImplementedError

    def validate(self):
        """Validate all sprites inside this manager."""

        for sprite in self.sprites:
            sprite.validate()

    def save(self):
        """Save all sprites inside this manager."""

        for format_name in self.config['enabled_formats']:
            format_cls = formats[format_name]
            for sprite in self.sprites:
                format = format_cls(sprite=sprite)
                format.validate()
                if format.needs_rebuild() or sprite.config['force']:
                    print "Format '{0}' for sprite '{1}' needs rebuild...".format(format_name, sprite.name)
                    format.build()
                else:
                    print "Format '{0}'' for sprite '{1}' already exists...".format(format_name, sprite.name)
