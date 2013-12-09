import os
import plistlib

from base import BaseTextFormat


class Cocos2dFormat(BaseTextFormat):

    extension = 'plist'

    def render(self, *args, **kwargs):
        context = self.get_context()
        data = {'frames': {},
                'metadata': {'version': context['version'],
                             'hash': context['hash'],
                             'size':'{{{width}, {height}}}'.format(**context),
                             'name': context['name'],
                             'format': 2,
                             'realTextureFileName': context['sprite_filename'],
                             'textureFileName': context['sprite_filename']
                }
        }
        for i in context['images']:
            rect = '{{{{{abs_x}, {abs_y}}}, {{{width}, {height}}}}}'.format(**i)
            data['frames'][i['filename']] = {'frame': rect,
                                             'offset': '{0,0}',
                                             'rotated': False,
                                             'sourceColorRect': rect,
                                             'sourceSize': '{{{width}, {height}}}'.format(**i)}

        return plistlib.writePlistToString(data)

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("Cocos2d format options")

        group.add_argument("--cocos2d",
                           dest="cocos2d_dir",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_COCOS2D', False),
                           metavar='DIR',
                           help="Generate Cocos2d files and optionally where")

    def needs_rebuild(self):
        if os.path.exists(self.output_path()):
            try:
                data = plistlib.readPlist(self.output_path())
                assert data['metadata']['hash'] == self.sprite.hash
                return False
            except Exception:
                pass
        return True
