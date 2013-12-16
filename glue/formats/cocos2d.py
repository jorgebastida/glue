import os
import plistlib

from base import BaseTextFormat


class Cocos2dFormat(BaseTextFormat):

    extension = 'plist'
    build_per_ratio = True

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


    def render(self, ratio):
        context = self.get_context()
        ratio_context = context['ratios'][ratio]

        data = {'frames': {},
                'metadata': {'version': context['version'],
                             'hash': context['hash'],
                             'size':'{{{width}, {height}}}'.format(**context['ratios'][ratio]),
                             'name': context['name'],
                             'format': 2,
                             'realTextureFileName': ratio_context['sprite_filename'],
                             'textureFileName': ratio_context['sprite_filename']
                }
        }
        for i in context['images']:
            image_context = i['ratios'][ratio]
            rect = '{{{{{abs_x}, {abs_y}}}, {{{width}, {height}}}}}'.format(**image_context)
            data['frames'][i['filename']] = {'frame': rect,
                                             'offset': '{0,0}',
                                             'rotated': False,
                                             'sourceColorRect': rect,
                                             'sourceSize': '{{{width}, {height}}}'.format(**image_context)}

        return plistlib.writePlistToString(data)

    def needs_rebuild(self):
        for ratio in self.sprite.config['ratios']:
            cocos2d_path = self.output_path(ratio)
            if os.path.exists(cocos2d_path):
                try:
                    data = plistlib.readPlist(cocos2d_path)
                    assert data['metadata']['hash'] == self.sprite.hash
                except Exception:
                    continue
            return True
        return False
