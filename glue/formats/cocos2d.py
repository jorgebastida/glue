import os

from base import JinjaTextFormat
from plistlib import readPlist


class Cocos2dFormat(JinjaTextFormat):

    extension = 'plist'
    template = u"""
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>

        <key>frames</key>
        <dict>
            {% for image in images %}
            <key>{{ image.filename }}</key>
            <dict>
                <key>aliases</key>
                <array></array>
                <key>spriteColorRect</key>
                <string>{{ '{{' }}0, 0{{ '}' }}, {{ '{' }}{{ image.width }}, {{ image.height }}{{ '}}' }}</string>
                <key>spriteOffset</key>
                <string>{0, -0}</string>
                <key>spriteSize</key>
                <string>{{ '{' }}{{ image.width }}, {{ image.height }}{{ '}' }}</string>
                <key>spriteSourceSize</key>
                <string>{{ '{' }}{{ image.width }}, {{ image.height }}{{ '}' }}</string>
                <key>spriteTrimmed</key>
                <true/>
                <key>textureRect</key>
                <string>{{ '{{' }}{{ image.x }}, {{ image.y }}{{ '}' }}, {{ '{' }}{{ image.width }}, {{ image.height }}{{ '}}' }}</string>
                <key>textureRotated</key>
                <false/>
            </dict>
            {% endfor %}
        </dict>
        <key>metadata</key>
        <dict>
            <key>version</key>
            <string>{{ version }}</string>
            <key>hash</key>
            <string>{{ hash }}</string>
            <key>size</key>
            <string>{{ '{' }}{{ width }}, {{ height }}{{ '}' }}</string>
            <key>name</key>
            <string>{{ name }}</string>
            <key>textureFileName</key>
            <string>{{ sprite_filename }}</string>
            <key>premultipliedAlpha</key>
            <false/>
        </dict>
        </dict>
        </plist>"""

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
                data = readPlist(self.output_path())
                assert data['metadata']['hash'] == self.sprite.hash
                return False
            except Exception:
                pass
        return True
