import os

from base import BasePlistFormat


class Cocos2dFormat(BasePlistFormat):

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

    def get_context(self, ratio, *args, **kwargs):
        context = super(Cocos2dFormat, self).get_context(ratio, *args, **kwargs)
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
        return data
