import os

from base import BaseJSONFormat


class PhaserFormat(BaseJSONFormat):

    extension = 'json'
    build_per_ratio = True

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("JSON format options")

        group.add_argument("--phaser",
                           dest="phaser_dir",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_PHASER', False),
                           metavar='DIR',
                           help="Generate phaser compatible files and optionally where")

    def get_context(self, *args, **kwargs):
        context = super(PhaserFormat, self).get_context(*args, **kwargs)
        if kwargs['ratio']:
            use_context = context['ratios'][kwargs['ratio']]
            width = use_context['width']
            height = use_context['height']
        else:
            width = context['width']
            height = context['height']

        data = dict(frames={}, meta={
            'app': 'https://github.com/jorgebastida/glue/',
            'version': context['version'],
            'format': 'RGBA8888',
            'image': context['sprite_filename'],
            'size': {
                'w': width,
                'h': height
                },
            'scale': 1
        })


        for i in context['images']:
            if 'ratio' in kwargs:
                image_dict = i['ratios'][kwargs['ratio']]
            else:
                image_dict = i

            data['frames'][i['filename']] = {
                'frame': {
                    'x' : image_dict['abs_x'],
                    'y' : image_dict['abs_y'],
                    'w' : image_dict['width'],
                    'h' : image_dict['height']
                }
            }

        return data
