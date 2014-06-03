import os

from glue.exceptions import NoSpritesFoldersFoundError
from .base import BaseManager
from glue.core import ConfigurableFromFile


class ProjectManager(BaseManager, ConfigurableFromFile):
    """Process a path searching for folders that contain images.
       Every folder will be a new sprite with all the images inside.
       This is not the default manager. It is only used if you use
       the ``--project`` argument."""

    def __init__(self, *args, **kwargs):
        super(ProjectManager, self).__init__(*args, **kwargs)
        self.config_path = self.config['source']
        self.config.update(self._get_config_from_file('sprite.conf', 'sprite'))

    def find_sprites(self):

        for filename in sorted(os.listdir(self.config['source'])):

            # Only process folders
            path = os.path.join(self.config['source'], filename)

            # Ignore filenames starting with '.'
            if filename.startswith('.'):
                continue

            # Ignore symlinks if necessary.
            if not os.path.isdir(path) and not (os.path.islink(path) and self.config['follow_links']):
                continue

            self.add_sprite(path=path)

        if not self.sprites:
            raise NoSpritesFoldersFoundError(self.config['source'])
