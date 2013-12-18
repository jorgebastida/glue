import os

from .css import CssFormat

class HtmlFormat(CssFormat):

    extension = 'html'
    template = u"""
        <html>
            <head><title>Glue Sprite Test Html</title>
            <link rel="stylesheet" type="text/css" href="{{ css_path }}"></head>
            <body>
            <style type="text/css">
                tr div:hover{ border:1px solid #ccc;}
                tr div{ border:1px solid white;}
            </style>

            <h1>CSS Classes</h1>
            <table>
            <tr>
                <th>CSS Class</th>
                <th>Result</th>
            </tr>

            {% for image in images %}
            <tr><td>.{{ image.label }}</td><td><div class="{{ image.label }}"></div></td></tr>
            {% endfor %}

            </table>
            <p><em>Generated using <a href="http://gluecss.com"/>Glue v{{ version }}</a></em></p>
            </body>
        </html>"""

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("Html format options")

        group.add_argument("--html",
                           dest="html_dir",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_HTML', False),
                           metavar='DIR',
                           help="Generate html files and optionally where")

    @classmethod
    def apply_parser_contraints(cls, parser, options):
        if 'html' in options.enabled_formats and 'css' not in options.enabled_formats:
            parser.error("You can't use --html without --css.")

    def get_context(self, *args, **kwargs):
        context = super(HtmlFormat, self).get_context(*args, **kwargs)
        context['css_path'] = os.path.relpath(os.path.join(self.sprite.config['css_dir'], '{0}.css'.format(self.sprite.name)), self.output_dir())
        return context

    def needs_rebuild(self):
        return True

    def validate(self):
        return True
