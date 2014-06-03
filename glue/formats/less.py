import os

from css import CssFormat


class LessFormat(CssFormat):

    extension = 'less'
    template = u"""
        /* glue: {{ version }} hash: {{ hash }} */
        {% for image in images %}.{{ image.label }}{{ image.pseudo }}{%- if not image.last %}, {%- endif %}{%- endfor %}{
            background-image:url('{{ sprite_path }}');
            background-repeat:no-repeat;
            -webkit-background-size: {{ width }}px {{ height }}px;
            -moz-background-size: {{ width }}px {{ height }}px;
            background-size: {{ width }}px {{ height }}px;
            {% for r, ratio in ratios.items() %}
            @media screen and (-webkit-min-device-pixel-ratio: {{ ratio.ratio }}), screen and (min--moz-device-pixel-ratio: {{ ratio.ratio }}),screen and (-o-min-device-pixel-ratio: {{ ratio.fraction }}),screen and (min-device-pixel-ratio: {{ ratio.ratio }}),screen and (min-resolution: {{ ratio.ratio }}dppx){
                background-image:url('{{ ratio.sprite_path }}');
            }
            {% endfor %}
        }
        {% for image in images %}
        .{{ image.label }}{{ image.pseudo }}{
            background-position:{{ image.x ~ ('px' if image.x) }} {{ image.y ~ ('px' if image.y) }};
            width:{{ image.width }}px;
            height:{{ image.height }}px;
        }
        {% endfor %}
        """

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("CSS format options")

        group.add_argument("--less",
                           dest="less_dir",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_LESS', False),
                           metavar='DIR',
                           help="Generate LESS files and optionally where")

        group.add_argument("--less-template",
                           dest="less_template",
                           default=os.environ.get('GLUE_LESS_TEMPLATE', None),
                           metavar='DIR',
                           help="Template to use to generate the LESS output.")
