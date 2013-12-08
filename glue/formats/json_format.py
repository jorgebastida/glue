import os
import json
import codecs

from base import BaseTextFormat


class JSONFormat(BaseTextFormat):

    extension = 'json'

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

    def needs_rebuild(self):
        if os.path.exists(self.output_path()):
            try:
                with codecs.open('output/simple.css', 'r', 'utf-8-sig') as f:
                    data = json.loads(f.read())
                assert data['hash'] == self.sprite.hash
                return False
            except Exception:
                pass
        return True

    def render(self, *args, **kwargs):
        return json.dumps(self.get_context())
