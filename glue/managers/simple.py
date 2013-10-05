from .base import BaseManager


class SimpleManager(BaseManager):
    """Process a single folder and create one sprite. It works the
    same way as :class:`~ProjectSpriteManager`, but only for one folder.

    This is the default manager.
    """

    def __init__(self, *args, **kwargs):
        super(SimpleManager, self).__init__(*args, **kwargs)
        self.add_sprite(path=self.config['source'])
