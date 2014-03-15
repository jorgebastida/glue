import os

from css import CssFormat


class ScssFormat(CssFormat):

    extension = 'scss'

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("SCSS format options")

        group.add_argument("--scss",
                           dest="scss_dir",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_SCSS', False),
                           metavar='DIR',
                           help="Generate SCSS files and optionally where")

        group.add_argument("--scss-template",
                           dest="scss_template",
                           default=os.environ.get('GLUE_SCSS_TEMPLATE', None),
                           metavar='DIR',
                           help="Template to use to generate the SCSS output.")
