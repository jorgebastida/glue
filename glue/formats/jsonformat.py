import os
import json

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from base import BaseJSONFormat


class JSONFormat(BaseJSONFormat):

    extension = 'json'
    build_per_ratio = True

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("JSON format options")

        group.add_argument("--json",
                           dest="json_dir",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_JSON', False),
                           metavar='DIR',
                           help="Generate JSON files and optionally where")

        group.add_argument("--json-format",
                           dest="json_format",
                           metavar='NAME',
                           type=unicode,
                           default=os.environ.get('GLUE_JSON_FORMAT', 'array'),
                           choices=['array', 'hash','txtpkr'],
                           help=("JSON structure format (array, hash, txtpkr)"))

    def get_context(self, *args, **kwargs):
        context = super(JSONFormat, self).get_context(*args, **kwargs)

        frames = OrderedDict([[i['filename'], {'filename': i['filename'],
                                        'frame': {'x': i['x'],
                                                  'y': i['y'],
                                                  'w': i['width'],
                                                  'h': i['height']},
                                        'rotated': False,
                                        'trimmed': False,
                                        'spriteSourceSize': {'x': i['x'],
                                                             'y': i['y'],
                                                             'w': i['width'],
                                                             'h': i['height']},
                                        'sourceSize': {'w': i['original_width'],
                                                       'h': i['original_height']}}] for i in context['images']])

        data = OrderedDict(frames=None, meta={'version': context['version'],
                                       'hash': context['hash'],
                                       'name': context['name'],
                                       'sprite_path': context['sprite_path'],
                                       'sprite_filename': context['sprite_filename'],
                                       'width': context['width'],
                                       'height': context['height'],
                                       'image': context['sprite_filename']})

        if self.sprite.config['json_format'] == 'array':
            data['frames'] = frames.values()
        else:
            data['frames'] = frames
            if self.sprite.config['json_format'] == 'txtpkr':
                for d in data['frames']:
                    x = d['frame']['x']
                    y = d['frame']['y']
                    # Make the x,y coordinates grow in positive numbers
                    d['frame']['x'] = x*-1
                    d['frame']['y'] = y*-1
                    d['spriteSourceSize']['x'] = x*-1
                    d['spriteSourceSize']['y'] = y*-1

        return data
