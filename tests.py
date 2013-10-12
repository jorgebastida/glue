import os
import shutil
import unittest
import logging
from StringIO import StringIO

from PIL import Image as PILImage
import cssutils

from glue import __version__
from glue.bin import main
from glue.helpers import redirect_stdout


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

    def _exists(self, path):
        return os.path.exists(path)

    def assertExists(self, path):
        assert self._exists(path), "{0} doesn't exists".format(path)

    def assertDoesNotExists(self, path):
        assert not self._exists(path), "{0} exists".format(path)

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

    def call(self, options, capture=False):
        out = StringIO()
        with redirect_stdout(out):
            code = main(options.split())
        output = out.getvalue()
        out.close()
        if capture:
            return code, output
        return code

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

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_source(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue --source=simple output")
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

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_output(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple --output=output")
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

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_quiet(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code, out = self.call("glue simple output --quiet", capture=True)
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_recursive(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        self.create_image("simple/sub/green.png", GREEN)
        code = self.call("glue simple output --recursive")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", GREEN, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", RED, ((64, 0), (127, 63)))
        self.assertColor("output/simple.png", BLUE, ((0, 64), (63, 127)))

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 -64px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_green',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_project(self):
        self.create_image("sprites/icons/red.png", RED)
        self.create_image("sprites/icons/blue.png", BLUE)
        self.create_image("sprites/menu/green.png", GREEN)
        self.create_image("sprites/menu/yellow.png", YELLOW)
        code = self.call("glue sprites output --project")
        self.assertEqual(code, 0)

        self.assertExists("output/icons.png")
        self.assertExists("output/icons.css")
        self.assertExists("output/menu.png")
        self.assertExists("output/menu.css")

        self.assertColor("output/icons.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/icons.png", BLUE, ((64, 0), (127, 63)))
        self.assertColor("output/menu.png", YELLOW, ((0, 0), (63, 63)))
        self.assertColor("output/menu.png", GREEN, ((64, 0), (127, 63)))

        self.assertCSS(u"output/icons.css", u'.sprite_icons_red',
                       {u'background-image': u"url(icons.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/icons.css", u'.sprite_icons_blue',
                       {u'background-image': u"url(icons.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/menu.css", u'.sprite_menu_yellow',
                       {u'background-image': u"url(menu.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/menu.css", u'.sprite_menu_green',
                       {u'background-image': u"url(menu.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_algorithm_diagonal(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        self.create_image("simple/yellow.png", YELLOW)
        code = self.call("glue simple output --algorithm=diagonal")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", YELLOW, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", RED, ((64, 64), (127, 127)))
        self.assertColor("output/simple.png", BLUE, ((128, 128), (191, 191)))

        self.assertCSS(u"output/simple.css", u'.sprite_simple_yellow',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px -64px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-128px -128px',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_algorithm_horizontal(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        self.create_image("simple/yellow.png", YELLOW)
        code = self.call("glue simple output --algorithm=horizontal")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", YELLOW, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", RED, ((64, 0), (127, 63)))
        self.assertColor("output/simple.png", BLUE, ((128, 0), (129, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite_simple_yellow',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-128px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_algorithm_horizontal_bottom(self):
        self.create_image("simple/red.png", RED, (64, 64))
        self.create_image("simple/blue.png", BLUE, (32, 32))
        self.create_image("simple/yellow.png", YELLOW, (16, 16))
        code = self.call("glue simple output --algorithm=horizontal-bottom")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 32), (95, 63)))
        self.assertColor("output/simple.png", YELLOW, ((96, 48), (111, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px -32px',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_yellow',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-96px -48px',
                        u'width': u'16px',
                        u'height': u'16px'})

    def test_algorithm_vertical(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        self.create_image("simple/yellow.png", YELLOW)
        code = self.call("glue simple output --algorithm=vertical")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", YELLOW, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", RED, ((0, 64), (63, 127)))
        self.assertColor("output/simple.png", BLUE, ((0, 128), (63, 188)))

        self.assertCSS(u"output/simple.css", u'.sprite_simple_yellow',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 -64px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 -128px',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_algorithm_vertical_right(self):
        self.create_image("simple/red.png", RED, (64, 64))
        self.create_image("simple/blue.png", BLUE, (32, 32))
        self.create_image("simple/yellow.png", YELLOW, (16, 16))
        code = self.call("glue simple output --algorithm=vertical-right")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((32, 64), (63, 95)))
        self.assertColor("output/simple.png", YELLOW, ((48, 96), (63, 111)))

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px -64px',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_yellow',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-48px -96px',
                        u'width': u'16px',
                        u'height': u'16px'})

    def test_no_img(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --no-img")
        self.assertEqual(code, 0)

        self.assertDoesNotExists("output/simple.png")
        self.assertExists("output/simple.css")

        self.assertCSS(u"output/simple.css", u'.sprite_simple_red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite_simple_blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
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
