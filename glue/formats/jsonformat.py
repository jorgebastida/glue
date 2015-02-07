from collections import OrderedDict
import os
import json
import codecs

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
                           choices=['array', 'hash'],
                           help=("JSON structure format (array, hash)"))

        group.add_argument("--output_abs_xy",
                           dest="output_abs_xy",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_JSON', False),
                           metavar='DIR',
                           help="Output x,y as positive values")

    def get_context(self, *args, **kwargs):
        context = super(JSONFormat, self).get_context(*args, **kwargs)

        output_abs_xy = self.sprite.config.get('output_abs_xy')
        frames = OrderedDict([[i['filename'], {'filename': i['filename'],
                                        'frame': {'x': i['abs_x'] if output_abs_xy else i['x'],
                                                  'y': i['abs_y'] if output_abs_xy else i['y'],
                                                  'w': i['width'],
                                                  'h': i['height']},
                                        'rotated': False,
                                        'trimmed': False,
                                        'spriteSourceSize': {'x': i['abs_x'] if output_abs_xy else i['x'],
                                                             'y': i['abs_y'] if output_abs_xy else i['y'],
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
                                       'height': context['height']})

        if self.sprite.config['json_format'] == 'array':
            data['frames'] = frames.values()
        else:
            data['frames'] = frames

        return data
