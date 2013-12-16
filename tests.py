import os
import sys
import json
import codecs
import shutil
import unittest
import logging
from StringIO import StringIO
from plistlib import readPlist

from PIL import Image as PILImage
import cssutils
from mock import patch, Mock

from glue.bin import main
from glue.core import Image
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
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        os.chdir(self.pwd)
        shutil.rmtree(self.output_path, True)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

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
                if 'min-resolution: {0}'.format(ratio) in rule.media.mediaText:
                    for media_rule in rule.cssRules:
                        if class_name in [c.selectorText for c in media_rule.selectorList]:
                            for declaration in media_rule.style.getProperties():
                                file_properties[declaration.name] = declaration.value
        self.assertEqual(file_properties, properties)

    def create_image(self, path, color=RED, size=(64, 64), margin=0):
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        image = PILImage.new('RGB', size, color)
        if margin:
            background = PILImage.new('RGBA', map(lambda x: x + margin, size))
            background.paste(image, (margin / 2, margin / 2))
            background.save(path)
        else:
            image.save(path)
        return os.path.abspath(path)

    def call(self, options, capture=False):
        out = StringIO()
        with redirect_stdout(out):
            code = main(options.split())
        output = out.getvalue()
        out.close()
        if capture:
            return code, output
        return code

    def test_simple(self):
        os.mkdir('simple')
        code = self.call("glue simple output")
        self.assertEqual(code, 4)

        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
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

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
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

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
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

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 -64px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-green',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_project(self):
        # Empty project
        os.mkdir("sprites")
        code = self.call("glue sprites output --project")
        self.assertEqual(code, 5)

        self.create_image("sprites/icons/red.png", RED)
        self.create_image("sprites/icons/blue.png", BLUE)
        self.create_image("sprites/menu/green.png", GREEN)
        self.create_image("sprites/menu/yellow.png", YELLOW)
        self.create_image("sprites/.ignore/pink.png", PINK)
        code = self.call("glue sprites output --project")
        self.assertEqual(code, 0)

        self.assertExists("output/icons.png")
        self.assertExists("output/icons.css")
        self.assertExists("output/menu.png")
        self.assertExists("output/menu.css")
        self.assertDoesNotExists("output/ignore.png")
        self.assertDoesNotExists("output/ignore.css")

        self.assertColor("output/icons.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/icons.png", BLUE, ((64, 0), (127, 63)))
        self.assertColor("output/menu.png", YELLOW, ((0, 0), (63, 63)))
        self.assertColor("output/menu.png", GREEN, ((64, 0), (127, 63)))

        self.assertCSS(u"output/icons.css", u'.sprite-icons-red',
                       {u'background-image': u"url(icons.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/icons.css", u'.sprite-icons-blue',
                       {u'background-image': u"url(icons.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/menu.css", u'.sprite-menu-yellow',
                       {u'background-image': u"url(menu.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/menu.css", u'.sprite-menu-green',
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

        self.assertCSS(u"output/simple.css", u'.sprite-simple-yellow',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px -64px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
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

        self.assertCSS(u"output/simple.css", u'.sprite-simple-yellow',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
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

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px -32px',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-yellow',
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

        self.assertCSS(u"output/simple.css", u'.sprite-simple-yellow',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 -64px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
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

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px -64px',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-yellow',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-48px -96px',
                        u'width': u'16px',
                        u'height': u'16px'})

    def test_no_img_with_img(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --no-img --img=folder")
        self.assertEqual(code, 0)

        self.assertDoesNotExists("output/simple.png")
        self.assertExists("output/simple.css")

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(../folder/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(../folder/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_ordering(self):
        settings = {'crop': False, 'padding': '0', 'margin': '0', 'ratios': [1]}
        red_path = self.create_image("simple/red.png", RED, (64, 64))
        blue_path = self.create_image("simple/blue.png", BLUE, (32, 32))

        # maxside
        settings['algorithm_ordering'] = 'maxside'
        red = Image(red_path, settings)
        blue = Image(blue_path, settings)
        assert red > blue

        # width
        settings['algorithm_ordering'] = 'width'
        red = Image(red_path, settings)
        blue = Image(blue_path, settings)
        assert red > blue

        # height
        settings['algorithm_ordering'] = 'height'
        red = Image(red_path, settings)
        blue = Image(blue_path, settings)
        assert red > blue

        # area
        settings['algorithm_ordering'] = 'area'
        red = Image(red_path, settings)
        blue = Image(blue_path, settings)
        assert red > blue

    def test_css(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --css=styles")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("styles/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"styles/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(../output/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"styles/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(../output/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_css_validation(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/sub/red.png", RED)
        code = self.call("glue simple output --recursive")
        self.assertEqual(code, 3)

    def test_less(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --less")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.less")
        self.assertDoesNotExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.less", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.less", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_scss(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --scss")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.scss")
        self.assertDoesNotExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.scss", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.scss", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_namespace(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --namespace=style")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.style-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.style-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_empty_namespace(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --namespace=")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_sprite_namespace(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --sprite-namespace=custom")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-custom-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-custom-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_sprite_namespace_with_var(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --sprite-namespace=custom-{sprite_name}")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-custom-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-custom-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_empty_sprite_namespace(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --sprite-namespace=")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_empty_namespaces(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --sprite-namespace= --namespace=")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_url(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --url=http://static.domain.com/")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(http://static.domain.com/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(http://static.domain.com/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        code = self.call("glue simple output --url=/static/")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(/static/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(/static/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        code = self.call("glue simple --url=/custom/ --css=a/b/c --img=d/e/f")
        self.assertEqual(code, 0)

        self.assertExists("d/e/f/simple.png")
        self.assertExists("a/b/c/simple.css")
        self.assertColor("d/e/f/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("d/e/f/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"a/b/c/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(/custom/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"a/b/c/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(/custom/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    @patch('glue.core.Sprite.hash')
    def test_cachebuster(self, mocked_hash):
        mocked_hash.__get__ = Mock(return_value="12345")
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --cachebuster")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png?12345)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png?12345)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    @patch('glue.core.Sprite.hash')
    def test_cachebuster_filename(self, mocked_hash):
        mocked_hash.__get__ = Mock(return_value="12345")
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --cachebuster-filename")
        self.assertEqual(code, 0)

        self.assertExists("output/simple_12345.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple_12345.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple_12345.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple_12345.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple_12345.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_separator_simple(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --separator=-")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_separator_camelcase(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --separator=camelcase")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.spriteSimpleRed',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.spriteSimpleBlue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    @patch('glue.core.Sprite.hash')
    def test_css_template(self, mocked_hash):
        mocked_hash.__get__ = Mock(return_value="12345")
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        with open('template.jinja', 'w') as f:
            f.write("custom template for {{ hash }}")

        code = self.call("glue simple output --css-template=template.jinja")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        with codecs.open('output/simple.css', 'r', 'utf-8-sig') as f:
            content = f.read()
            self.assertEqual(content, u"custom template for {0}".format(12345))

    def test_html(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --html")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertExists("output/simple.html")

    def test_json(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --json")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.json")
        with codecs.open('output/simple.json', 'r', 'utf-8-sig') as f:
            data = json.loads(f.read())
            assert isinstance(data['frames'], list)

    def test_json_hash(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --json --json-format=hash")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.json")
        with codecs.open('output/simple.json', 'r', 'utf-8-sig') as f:
            data = json.loads(f.read())
            assert isinstance(data['frames'], dict)

    def test_img(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --img=images")
        self.assertEqual(code, 0)

        self.assertExists("images/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("images/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("images/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(../images/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(../images/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_no_img(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --no-img")
        self.assertEqual(code, 0)

        self.assertDoesNotExists("output/simple.png")
        self.assertExists("output/simple.css")

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_crop(self):
        self.create_image("simple/red.png", RED, margin=4)
        self.create_image("simple/blue.png", BLUE, margin=4)
        code = self.call("glue simple output --crop")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_padding(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)

        # Simple padding
        code = self.call("glue simple output --padding=4")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((4, 4), (67, 67)))
        self.assertColor("output/simple.png", BLUE, ((76, 4), (139, 67)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'72px',
                        u'height': u'72px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-72px 0',
                        u'width': u'72px',
                        u'height': u'72px'})

        # Double padding
        code = self.call("glue simple output --padding=2,4")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")

        self.assertColor("output/simple.png", RED, ((4, 2), (67, 65)))
        self.assertColor("output/simple.png", BLUE, ((76, 2), (139, 65)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'72px',
                        u'height': u'68px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-72px 0',
                        u'width': u'72px',
                        u'height': u'68px'})

        # Triple padding
        code = self.call("glue simple output --padding=2,4,6")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")

        self.assertColor("output/simple.png", RED, ((4, 2), (67, 65)))
        self.assertColor("output/simple.png", BLUE, ((76, 2), (139, 65)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'72px',
                        u'height': u'72px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-72px 0',
                        u'width': u'72px',
                        u'height': u'72px'})

        # Full padding
        code = self.call("glue simple output --padding=2,4,6,8")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")

        self.assertColor("output/simple.png", RED, ((8, 2), (67, 65)))
        self.assertColor("output/simple.png", BLUE, ((84, 2), (147, 65)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'76px',
                        u'height': u'72px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-76px 0',
                        u'width': u'76px',
                        u'height': u'72px'})

    def test_margin(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)

        # Simple margin
        code = self.call("glue simple output --margin=4")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((4, 4), (67, 67)))
        self.assertColor("output/simple.png", BLUE, ((76, 4), (139, 67)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-4px -4px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-76px -4px',
                        u'width': u'64px',
                        u'height': u'64px'})

        # Double margin
        code = self.call("glue simple output --margin=2,4")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")

        self.assertColor("output/simple.png", RED, ((4, 2), (67, 65)))
        self.assertColor("output/simple.png", BLUE, ((76, 2), (139, 65)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-4px -2px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-76px -2px',
                        u'width': u'64px',
                        u'height': u'64px'})

        # Triple margin
        code = self.call("glue simple output --margin=2,4,6")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")

        self.assertColor("output/simple.png", RED, ((4, 2), (67, 65)))
        self.assertColor("output/simple.png", BLUE, ((76, 2), (139, 65)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-4px -2px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-76px -2px',
                        u'width': u'64px',
                        u'height': u'64px'})

        # Full margin
        code = self.call("glue simple output --margin=2,4,6,8")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")

        self.assertColor("output/simple.png", RED, ((8, 2), (67, 65)))
        self.assertColor("output/simple.png", BLUE, ((84, 2), (147, 65)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-8px -2px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-84px -2px',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_png8(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --png8")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")

        image = PILImage.open("output/simple.png")
        self.assertEqual(image.mode, 'P')
        self.assertEqual(image.getpixel((0, 0)), 0)
        self.assertEqual(image.getpixel((63, 63)), 0)
        self.assertEqual(image.getpixel((64, 0)), 1)
        self.assertEqual(image.getpixel((127, 63)), 1)

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_retina(self):

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

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px 0',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple@2x.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'background-size': u'64px 32px',
                        u'-webkit-background-size': u'64px 32px',
                        u'-moz-background-size': u'64px 32px',
                        u'width': u'32px',
                        u'height': u'32px'}, ratio=2)

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple@2x.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px 0',
                        u'background-size': u'64px 32px',
                        u'-webkit-background-size': u'64px 32px',
                        u'-moz-background-size': u'64px 32px',
                        u'width': u'32px',
                        u'height': u'32px'}, ratio=2)

    def test_retina_url(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --retina --url=http://static.domain.com/")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple@2x.png")
        self.assertExists("output/simple.css")

        self.assertColor("output/simple.png", RED, ((0, 0), (31, 31)), .1)
        self.assertColor("output/simple.png", BLUE, ((31, 0), (63, 31)), .1)
        self.assertColor("output/simple@2x.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple@2x.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(http://static.domain.com/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(http://static.domain.com/simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px 0',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(http://static.domain.com/simple@2x.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'background-size': u'64px 32px',
                        u'-webkit-background-size': u'64px 32px',
                        u'-moz-background-size': u'64px 32px',
                        u'width': u'32px',
                        u'height': u'32px'}, ratio=2)

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(http://static.domain.com/simple@2x.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px 0',
                        u'background-size': u'64px 32px',
                        u'-webkit-background-size': u'64px 32px',
                        u'-moz-background-size': u'64px 32px',
                        u'width': u'32px',
                        u'height': u'32px'}, ratio=2)

    @patch('glue.core.Sprite.hash')
    def test_retina_cachebuster(self, mocked_hash):
        mocked_hash.__get__ = Mock(return_value="12345")

        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --retina --cachebuster")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple@2x.png")
        self.assertExists("output/simple.css")

        self.assertColor("output/simple.png", RED, ((0, 0), (31, 31)), .1)
        self.assertColor("output/simple.png", BLUE, ((31, 0), (63, 31)), .1)
        self.assertColor("output/simple@2x.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple@2x.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png?12345)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png?12345)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px 0',
                        u'width': u'32px',
                        u'height': u'32px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple@2x.png?12345)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'background-size': u'64px 32px',
                        u'-webkit-background-size': u'64px 32px',
                        u'-moz-background-size': u'64px 32px',
                        u'width': u'32px',
                        u'height': u'32px'}, ratio=2)

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple@2x.png?12345)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-32px 0',
                        u'background-size': u'64px 32px',
                        u'-webkit-background-size': u'64px 32px',
                        u'-moz-background-size': u'64px 32px',
                        u'width': u'32px',
                        u'height': u'32px'}, ratio=2)

    def test_cocos2d(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --cocos2d")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.plist")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        meta = readPlist("output/simple.plist")
        self.assertEqual(meta.keys(), ['frames', 'metadata'])
        self.assertEqual(meta['frames'].keys(), ['blue.png', 'red.png'])

        code = self.call("glue simple output --cocos2d")
        self.assertEqual(code, 0)

    @patch('glue.managers.simple.SimpleManager.process')
    def test_debug(self, mock_process):
        mock_process.side_effect = Exception("Error!")
        os.mkdir('simple')
        code, output = self.call("glue simple output", capture=True)
        self.assertEqual(code, 1)

    def test_custom_paths(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple --css=output --img=output")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", RED, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", BLUE, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_sprite_config_files(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/sub/blue.png", BLUE)
        with open('simple/sprite.conf', 'w') as f:
            f.write("[sprite]\nrecursive=true\n")

        code = self.call("glue simple output")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", BLUE, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", RED, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_image_config_files(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)

        with open('simple/sprite.conf', 'w') as f:
            f.write("[blue.png]\nmargin=4\n")

        code = self.call("glue simple output")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", BLUE, ((4, 4), (67, 67)))
        self.assertColor("output/simple.png", RED, ((72, 0), (135, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-blue',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-4px -4px',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-red',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-72px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_pseudo_class(self):
        self.create_image("simple/button.png", RED)
        self.create_image("simple/button__hover.png", BLUE)
        code = self.call("glue simple output")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", BLUE, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", RED, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-button',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-button:hover',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_multiple_pseudo_class(self):
        self.create_image("simple/button.png", RED)
        self.create_image("simple/button__hover__before.png", BLUE)
        code = self.call("glue simple output")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", BLUE, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", RED, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-button',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-button:hover:before',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_custom_pseudo_class_separator(self):
        self.create_image("simple/button.png", RED)
        self.create_image("simple/button_hover.png", BLUE)
        code = self.call("glue simple output --pseudo-class-separator=_")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertExists("output/simple.css")
        self.assertColor("output/simple.png", BLUE, ((0, 0), (63, 63)))
        self.assertColor("output/simple.png", RED, ((64, 0), (127, 63)))

        self.assertCSS(u"output/simple.css", u'.sprite-simple-button',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'-64px 0',
                        u'width': u'64px',
                        u'height': u'64px'})

        self.assertCSS(u"output/simple.css", u'.sprite-simple-button:hover',
                       {u'background-image': u"url(simple.png)",
                        u'background-repeat': u'no-repeat',
                        u'background-position': u'0 0',
                        u'width': u'64px',
                        u'height': u'64px'})

    def test_no_css(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --no-css")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertDoesNotExists("output/simple.css")

    def test_no_css_with_css(self):
        self.create_image("simple/red.png", RED)
        self.create_image("simple/blue.png", BLUE)
        code = self.call("glue simple output --no-css --css=folder")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertDoesNotExists("output/folder/simple.css")

    def test_no_css_validation(self):
        """Test that CSS validations does not run if --no-css is present."""
        self.create_image("simple/red.png", RED)
        self.create_image("simple/red|.png", RED)
        code = self.call("glue simple output --no-css")
        self.assertEqual(code, 0)

        self.assertExists("output/simple.png")
        self.assertDoesNotExists("output/simple.css")

if __name__ == '__main__':
    unittest.main()
