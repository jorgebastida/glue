import os
import shutil
import contextlib
import unittest
import logging

from PIL import Image as PILImage
import cssutils

from glue.bin import main


RED = (255, 0, 0, 255)
CYAN = (0, 255, 255, 255)
PINK = (255, 0, 255, 255)
BLUE = (0, 0, 255, 255)
GREEN = (0, 255, 0, 255)
YELLOW = (255, 255, 0, 255)
TRANSPARENT = (0, 0, 0, 0)

COLORS = {RED: 'RED',
          CYAN: 'CYAN',
          PINK: 'PINK',
          BLUE: 'BLUE',
          GREEN: 'GREEN',
          YELLOW: 'YELLOW',
          TRANSPARENT: 'TRANSPARENT'}

@contextlib.contextmanager
def chdir(dirname=None):
    pwd = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(pwd)


class TestGlue(unittest.TestCase):

    TEST_PATH = 'tests_tmp/'

    def setUp(self):
        cssutils.log.setLevel(logging.ERROR)
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.base_path, self.TEST_PATH)
        shutil.rmtree(self.output_path, True)
        os.makedirs(self.output_path)
        self.pwd = os.getcwd()
        os.chdir(self.output_path)

    def tearDown(self):
        os.chdir(self.pwd)
        shutil.rmtree(self.output_path, True)

    def assertExists(self, path):
        assert os.path.exists(path), "{0} doesn't exists".format(path)

    def assertColor(self, path, color, points, tolerance=0):
        image = PILImage.open(path)
        for point in points:
            image_color = image.getpixel(point)
            if tolerance:
                diffs = [abs(x - y) for x, y in zip(color, image_color)]
                match = max(diffs) < 255 / tolerance
            else:
                match = image_color == color

            if not match:
                assert False, "{0} {1} should be {2} but is {3}".format(path, point, COLORS.get(color, color), COLORS.get(image_color, image_color))

    def assertCSS(self, path, class_name, properties, ratio=None):
        stylesheet = cssutils.parseFile(path, validate=False)

        file_properties = {}
        for rule in stylesheet.cssRules:
            if isinstance(rule, cssutils.css.CSSStyleRule):
                if class_name in [c.selectorText for c in rule.selectorList]:
                    for declaration in rule.style.getProperties():
                        file_properties[declaration.name] = declaration.value
            elif isinstance(rule, cssutils.css.CSSMediaRule) and ratio:
                if 'min-device-pixel-ratio: {0}'.format(ratio) in rule.media.mediaText:
                    for media_rule in rule.cssRules:
                        if class_name in [c.selectorText for c in media_rule.selectorList]:
                            for declaration in media_rule.style.getProperties():
                                file_properties[declaration.name] = declaration.value

        self.assertEqual(file_properties, properties)

    def create_image(self, path, color=RED, size=(64, 64)):
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        image = PILImage.new('RGB', size, color)
        image.save(path)

    def call(self, options):
        return main(options.split())

    def test_simple_css(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_simple_css_retina(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --retina")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple@2x.png")
        self.assertExists("output/simple.css")

        self.assertColor("output/simple.png", RED, ((0, 0), (31, 31)), .1)
        self.assertColor("output/simple.png", BLUE, ((31, 0), (63, 31)), .1)
        self.assertColor("output/simple@2x.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple@2x.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px 0',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple@2x.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'background-size': u'64px 32px',
                        u'-webkit-background-size': u'64px 32px',
                        u'-moz-background-size': u'64px 32px',
                        u'width': u'32px',
                        u'height': u'32px'}, ratio=2)

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple@2x.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px 0',
                        u'background-size': u'64px 32px',
                        u'-webkit-background-size': u'64px 32px',
                        u'-moz-background-size': u'64px 32px',
                        u'width': u'32px',
                        u'height': u'32px'}, ratio=2)

if __name__ == '__main__':
    unittest.main()
