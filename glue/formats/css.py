import re
import os
import codecs

from glue import __version__
from base import JinjaTextFormat

from ..exceptions import ValidationError


class CssFormat(JinjaTextFormat):

    extension = 'css'
    camelcase_separator = 'camelcase'
    css_pseudo_classes = set(['link', 'visited', 'active', 'hover', 'focus',
                              'first-letter', 'first-line', 'first-child',
                              'before', 'after'])

    template = u"""
        /* glue: {{ version }} hash: {{ hash }} */
        {% for image in images %}.{{ image.label }}{{ image.pseudo }}{%- if not image.last %},{{"\n"}}{%- endif %}{%- endfor %} {
            background-image: url('{{ sprite_path }}');
            background-repeat: no-repeat;
        }
        {% for image in images %}
        .{{ image.label }}{{ image.pseudo }} {
            background-position: {{ image.x ~ ('px' if image.x) }} {{ image.y ~ ('px' if image.y) }};
            width: {{ image.width }}px;
            height: {{ image.height }}px;
        }
        {% endfor %}{% for r, ratio in ratios.items() %}
        @media screen and (-webkit-min-device-pixel-ratio: {{ ratio.ratio }}), screen and (min--moz-device-pixel-ratio: {{ ratio.ratio }}), screen and (-o-min-device-pixel-ratio: {{ ratio.fraction }}), screen and (min-device-pixel-ratio: {{ ratio.ratio }}), screen and (min-resolution: {{ ratio.ratio }}dppx) {
            {% for image in images %}.{{ image.label }}{{ image.pseudo }}{% if not image.last %},{{"\n"}}    {% endif %}{% endfor %} {
                background-image: url('{{ ratio.sprite_path }}');
                -webkit-background-size: {{ width }}px {{ height }}px;
                -moz-background-size: {{ width }}px {{ height }}px;
                background-size: {{ width }}px {{ height }}px;
            }
        }
        {% endfor %}
        """

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("CSS format options")

        group.add_argument("--css",
                           dest="css_dir",
                           nargs='?',
                           const=True,
                           default=os.environ.get('GLUE_CSS', False),
                           metavar='DIR',
                           help="Generate CSS files and optionally where")

        group.add_argument("--namespace",
                           dest="css_namespace",
                           type=unicode,
                           default=os.environ.get('GLUE_CSS_NAMESPACE', 'sprite'),
                           help="Namespace for all css classes (default: sprite)")

        group.add_argument("--sprite-namespace",
                           dest="css_sprite_namespace",
                           type=unicode,
                           default=os.environ.get('GLUE_CSS_SPRITE_NAMESPACE',
                                                  '{sprite_name}'),
                           help="Namespace for all sprites (default: {sprite_name})")

        group.add_argument("-u", "--url",
                           dest="css_url",
                           type=unicode,
                           default=os.environ.get('GLUE_CSS_URL', ''),
                           help="Prepend this string to the sprites path")

        group.add_argument("--cachebuster",
                           dest="css_cachebuster",
                           default=os.environ.get('GLUE_CSS_CACHEBUSTER', False),
                           action='store_true',
                           help=("Use the sprite's sha1 first 6 characters as a "
                                 "queryarg everytime that file is referred "
                                 "from the css"))

        group.add_argument("--cachebuster-filename",
                           dest="css_cachebuster_filename",
                           default=os.environ.get('GLUE_CSS_CACHEBUSTER', False),
                           action='store_true',
                           help=("Append the sprite's sha first 6 characters "
                                 "to the output filename"))

        group.add_argument("--cachebuster-filename-only-sprites",
                           dest="css_cachebuster_only_sprites",
                           default=os.environ.get('GLUE_CSS_CACHEBUSTER_ONLY_SPRITES', False),
                           action='store_true',
                           help=("Only apply cachebuster to sprite images."))

        group.add_argument("--separator",
                           dest="css_separator",
                           type=unicode,
                           default=os.environ.get('GLUE_CSS_SEPARATOR', '-'),
                           metavar='SEPARATOR',
                           help=("Customize the separator used to join CSS class "
                                 "names. If you want to use camelCase use "
                                 "'camelcase' as separator."))

        group.add_argument("--pseudo-class-separator",
                           dest="css_pseudo_class_separator",
                           type=unicode,
                           default=os.environ.get('GLUE_CSS_PSEUDO_CLASS_SEPARATOR', '__'),
                           metavar='SEPARATOR',
                           help=("Customize the separator glue will use in order "
                                 "to determine the pseudo classes included into "
                                 "filenames."))

        group.add_argument("--css-template",
                           dest="css_template",
                           default=os.environ.get('GLUE_CSS_TEMPLATE', None),
                           metavar='DIR',
                           help="Template to use to generate the CSS output.")

        group.add_argument("--no-css",
                           dest="generate_css",
                           action="store_false",
                           default=os.environ.get('GLUE_GENERATE_CSS', True),
                           help="Don't genereate CSS files.")

    @classmethod
    def apply_parser_contraints(cls, parser, options):
        cachebusters = (options.css_cachebuster, options.css_cachebuster_filename, options.css_cachebuster_only_sprites)
        if sum(cachebusters) > 1:
            parser.error("You can't use --cachebuster, --cachebuster-filename or --cachebuster-filename-only-sprites at the same time.")

    def needs_rebuild(self):
        hash_line = '/* glue: %s hash: %s */\n' % (__version__, self.sprite.hash)
        try:
            with codecs.open(self.output_path(), 'r', 'utf-8') as existing_css:
                first_line = existing_css.readline()
                assert first_line == hash_line
        except Exception:
            return True
        return False

    def validate(self):
        class_names = [':'.join(self.generate_css_name(i.filename)) for i in self.sprite.images]
        if len(set(class_names)) != len(self.sprite.images):
            dup = [i for i in self.sprite.images if class_names.count(':'.join(self.generate_css_name(i.filename))) > 1]
            duptext = '\n'.join(['\t{0} => .{1}'.format(os.path.relpath(d.path), ':'.join(self.generate_css_name(d.filename))) for d in dup])
            raise ValidationError("Error: Some images will have the same class name:\n{0}".format(duptext))
        return True

    def output_filename(self, *args, **kwargs):
        filename = super(CssFormat, self).output_filename(*args, **kwargs)
        if self.sprite.config['css_cachebuster_filename']:
            return '{0}_{1}'.format(filename, self.sprite.hash)
        return filename

    def get_context(self, *args, **kwargs):

        context = super(CssFormat, self).get_context(*args, **kwargs)

        # Generate css labels
        for image in context['images']:
            image['label'], image['pseudo'] = self.generate_css_name(image['filename'])

        if self.sprite.config['css_url']:
            context['sprite_path'] = '{0}{1}'.format(self.sprite.config['css_url'], context['sprite_filename'])

            for r, ratio in context['ratios'].iteritems():
                ratio['sprite_path'] = '{0}{1}'.format(self.sprite.config['css_url'], ratio['sprite_filename'])

        # Add cachebuster if required
        if self.sprite.config['css_cachebuster']:

            def apply_cachebuster(path):
                return "%s?%s" % (path, self.sprite.hash)

            context['sprite_path'] = apply_cachebuster(context['sprite_path'])

            for r, ratio in context['ratios'].iteritems():
                ratio['sprite_path'] = apply_cachebuster(ratio['sprite_path'])

        return context

    def generate_css_name(self, filename):
        filename = filename.rsplit('.', 1)[0]
        separator = self.sprite.config['css_separator']
        namespace = [re.sub(r'[^\w\-_]', '', filename)]

        # Add sprite namespace if required
        if self.sprite.config['css_sprite_namespace']:
            sprite_name = re.sub(r'[^\w\-_]', '', self.sprite.name)
            sprite_namespace = self.sprite.config['css_sprite_namespace']

            # Support legacy 0.4 format
            sprite_namespace = sprite_namespace.replace("%(sprite)s", "{sprite_name}")
            namespace.insert(0, sprite_namespace.format(sprite_name=sprite_name))

        # Add global namespace if required
        if self.sprite.config['css_namespace']:
            namespace.insert(0, self.sprite.config['css_namespace'])

        # Handle CamelCase separator
        if self.sprite.config['css_separator'] == self.camelcase_separator:
            namespace = [n[:1].title() + n[1:] if i > 0 else n for i, n in enumerate(namespace)]
            separator = ''

        label = separator.join(namespace)
        pseudo = ''

        css_pseudo_class_separator = self.sprite.config['css_pseudo_class_separator']
        if css_pseudo_class_separator in filename:
            pseudo_classes = [p for p in filename.split(css_pseudo_class_separator) if p in self.css_pseudo_classes]

            # If present add this pseudo class as pseudo an remove it from the label
            if pseudo_classes:
                for p in pseudo_classes:
                    label = label.replace('{0}{1}'.format(css_pseudo_class_separator, p), "")
                pseudo = ''.join(map(lambda x: ':{0}'.format(x), pseudo_classes))

        return label, pseudo
