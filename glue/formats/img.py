import os

from PIL import Image as PILImage
from PIL import PngImagePlugin

from glue import __version__
from glue.helpers import round_up, cached_property
from .base import BaseFormat


class ImageFormat(BaseFormat):

    build_per_ratio = True
    extension = 'png'

    @classmethod
    def populate_argument_parser(cls, parser):
        group = parser.add_argument_group("Sprite image options")

        group.add_argument("--img",
                           dest="img_dir",
                           type=unicode,
                           default=os.environ.get('GLUE_IMG', True),
                           metavar='DIR',
                           help="Output directory for img files")

        group.add_argument("--no-img",
                           dest="generate_image",
                           action="store_false",
                           default=os.environ.get('GLUE_GENERATE_IMG', True),
                           help="Don't genereate IMG files.")

        group.add_argument("-c", "--crop",
                           dest="crop",
                           action='store_true',
                           default=os.environ.get('GLUE_CROP', False),
                           help="Crop images removing unnecessary transparent margins")

        group.add_argument("-p", "--padding",
                           dest="padding",
                           type=unicode,
                           default=os.environ.get('GLUE_PADDING', '0'),
                           help="Force this padding in all images")

        group.add_argument("--margin",
                           dest="margin",
                           type=unicode,
                           default=os.environ.get('GLUE_MARGIN', '0'),
                           help="Force this margin in all images")

        group.add_argument("--png8",
                           action="store_true",
                           dest="png8",
                           default=os.environ.get('GLUE_PNG8', False),
                           help=("The output image format will be png8 "
                                 "instead of png32"))

        group.add_argument("--ratios",
                           dest="ratios",
                           type=unicode,
                           default=os.environ.get('GLUE_RATIOS', '1'),
                           help="Create sprites based on these ratios")

        group.add_argument("--retina",
                           dest="ratios",
                           default=os.environ.get('GLUE_RETINA', False),
                           action='store_const',
                           const='2,1',
                           help="Shortcut for --ratios=2,1")

    def output_filename(self, *args, **kwargs):
        filename = super(ImageFormat, self).output_filename(*args, **kwargs)
        if self.sprite.config['css_cachebuster_filename'] or self.sprite.config['css_cachebuster_only_sprites']:
            return '{0}_{1}'.format(filename, self.sprite.hash)
        return filename

    def needs_rebuild(self):
        for ratio in self.sprite.config['ratios']:
            image_path = self.output_path(ratio)
            try:
                existing = PILImage.open(image_path)
                assert existing.info['Software'] == 'glue-%s' % __version__
                assert existing.info['Comment'] == self.sprite.hash
                continue
            except Exception:
                return True
        return False

    @cached_property
    def _raw_canvas(self):
        # Create the sprite canvas
        width, height = self.sprite.canvas_size
        canvas = PILImage.new('RGBA', (width, height), (0, 0, 0, 0))

        # Paste the images inside the canvas
        for image in self.sprite.images:
            canvas.paste(image.image,
                (round_up(image.x + (image.padding[3] + image.margin[3]) * self.sprite.max_ratio),
                 round_up(image.y + (image.padding[0] + image.margin[0]) * self.sprite.max_ratio)))

        meta = PngImagePlugin.PngInfo()
        meta.add_text('Software', 'glue-%s' % __version__)
        meta.add_text('Comment', self.sprite.hash)

        # Customize how the png is going to be saved
        kwargs = dict(optimize=False, pnginfo=meta)

        if self.sprite.config['png8']:
            # Get the alpha band
            alpha = canvas.split()[-1]
            canvas = canvas.convert('RGB'
                        ).convert('P',
                                  palette=PILImage.ADAPTIVE,
                                  colors=255)

            # Set all pixel values below 128 to 255, and the rest to 0
            mask = PILImage.eval(alpha, lambda a: 255 if a <= 128 else 0)

            # Paste the color of index 255 and use alpha as a mask
            canvas.paste(255, mask)
            kwargs.update({'transparency': 255})
        return canvas, kwargs

    def save(self, ratio):
        width, height = self.sprite.canvas_size
        canvas, kwargs = self._raw_canvas

        # Loop all over the ratios and save one image for each one
        for ratio in self.sprite.config['ratios']:

            # Create the destination directory if required
            if not os.path.exists(self.output_dir(ratio=ratio)):
                os.makedirs(self.output_dir(ratio=ratio))

            image_path = self.output_path(ratio=ratio)

            # If this canvas isn't the biggest one scale it using the ratio
            if self.sprite.max_ratio != ratio:

                reduced_canvas = canvas.resize(
                                    (round_up((width / self.sprite.max_ratio) * ratio),
                                     round_up((height / self.sprite.max_ratio) * ratio)),
                                     PILImage.ANTIALIAS)
                reduced_canvas.save(image_path, **kwargs)
                # TODO: Use Imagemagick if it's available
            else:
                canvas.save(image_path, **kwargs)
