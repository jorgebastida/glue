import os
import json
import codecs

from base import BaseTextFormat


class CAATFormat(BaseTextFormat):

    extension = 'json'
    build_per_ratio = True

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("JSON format options")

        group.add_argument("--caat",
                           dest="caat_dir",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_CAAT', False),
                           metavar='DIR',
                           help="Generate CAAT files and optionally where")

    def needs_rebuild(self):
        for ratio in self.sprite.config['ratios']:
            json_path = self.output_path(ratio)
            if os.path.exists(json_path):
                with codecs.open(json_path, 'r', 'utf-8-sig') as f:
                    try:
                        data = json.loads(f.read())
                        assert data['meta']['hash'] == self.sprite.hash
                    except Exception:
                        continue
            return True
        return False

    def get_context(self, *args, **kwargs):
        context = super(CAATFormat, self).get_context(*args, **kwargs)

        data = dict(sprites={}, meta={'version': context['version'],
                                      'hash': context['hash'],
                                      'sprite_filename': context['sprite_filename'],
                                      'width': context['width'],
                                      'height': context['height']})
        for i in context['images']:
            data['sprites'][i['filename']] = {"x" : i['abs_x'],
                                              "y" : i['abs_y'],
                                              "width" : i['width'],
                                              "height" : i['height']}
        return data

    def render(self, *args, **kwargs):
        return json.dumps(self.get_context(*args, **kwargs))
