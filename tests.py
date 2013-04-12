import os
import re
import codecs
import time
import shutil
import unittest

from PIL import Image
import glue

TEST_DEFAULT_SETTINGS = glue.DEFAULT_SETTINGS
TEST_DEFAULT_SETTINGS['quiet'] = True


RED = (255, 0, 0, 255)
CYAN = (0, 255, 255, 255)
PINK = (255, 0, 255, 255)
BLUE = (0, 0, 255, 255)
GREEN = (0, 255, 0, 255)
YELLOW = (255, 255, 0, 255)
TRANSPARENT = (0, 0, 0, 0)
PURPLE = (127, 0, 255, 255)
ORANGE = (255, 127, 0, 255)


EXPECTED_SIMPLE_CSS = """.sprite-simple-yellow,
.sprite-simple-red,
.sprite-simple-pink,
.sprite-simple-green,
.sprite-simple-cyan,
.sprite-simple-blue{background-image:url('simple.png');background-repeat:no-repeat;}
.sprite-simple-yellow{background-position:0px 0px;width:25px;height:25px;}
.sprite-simple-red{background-position:-25px 0px;width:25px;height:25px;}
.sprite-simple-pink{background-position:-50px 0px;width:25px;height:25px;}
.sprite-simple-green{background-position:-75px 0px;width:25px;height:25px;}
.sprite-simple-cyan{background-position:-100px 0px;width:25px;height:25px;}
.sprite-simple-blue{background-position:-125px 0px;width:25px;height:25px;}
"""

EXPECTED_OPTIMIZED_SQUARE_CSS = """.sprite-simple-yellow,
.sprite-simple-red,
.sprite-simple-pink,
.sprite-simple-green,
.sprite-simple-cyan,
.sprite-simple-blue{background-image:url('simple.png');background-repeat:no-repeat}
.sprite-simple-yellow{background-position:0px 0px;width:25px;height:25px;}
.sprite-simple-red{background-position:-25px 0px;width:25px;height:25px;}
.sprite-simple-pink{background-position:0px -25px;width:25px;height:25px;}
.sprite-simple-green{background-position:-25px -25px;width:25px;height:25px;}
.sprite-simple-cyan{background-position:0px -50px;width:25px;height:25px;}
.sprite-simple-blue{background-position:-25px -50px;width:25px;height:25px;}
"""

EXPECTED_COMPLEXE_OPTIMIZED_SQUARE_CSS = """.sprite-complexe-green,
.sprite-complexe-purple,
.sprite-complexe-cyan,
.sprite-complexe-pink,
.sprite-complexe-blue,
.sprite-complexe-red,
.sprite-complexe-orange{background-image:url('complexe.png');background-repeat:no-repeat}
.sprite-complexe-green{background-position:0px 0px;width:125px;height:125px;}
.sprite-complexe-purple{background-position:-125px 0px;width:100px;height:100px;}
.sprite-complexe-cyan{background-position:0px -125px;width:125px;height:100px;}
.sprite-complexe-pink{background-position:-125px -100px;width:50px;height:75px;}
.sprite-complexe-blue{background-position:0px -225px;width:200px;height:75px;}
.sprite-complexe-red{background-position:-225px 0px;width:25px;height:50px;}
.sprite-complexe-orange{background-position:-125px -175px;width:125px;height:50px;}

"""

EXPECTED_PROJECT_MIX_CSS = """.sprite-mix-yellow,
.sprite-mix-pink,
.sprite-mix-cyan{background-image:url('mix.png');background-repeat:no-repeat;}
.sprite-mix-yellow{background-position:0px 0px;width:25px;height:25px;}
.sprite-mix-pink{background-position:-25px 0px;width:25px;height:25px;}
.sprite-mix-cyan{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_PROJECT_RGB_CSS = """.sprite-rgb-red,
.sprite-rgb-green,
.sprite-rgb-blue{background-image:url('rgb.png');background-repeat:no-repeat;}
.sprite-rgb-red{background-position:0px 0px;width:25px;height:25px;}
.sprite-rgb-green{background-position:-25px 0px;width:25px;height:25px;}
.sprite-rgb-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_SIMPLE_CROP = """.sprite-crop-red_border,
.sprite-crop-green_border,
.sprite-crop-blue_border{background-image:url('crop.png');background-repeat:no-repeat;}
.sprite-crop-red_border{background-position:0px 0px;width:25px;height:25px;}
.sprite-crop-green_border{background-position:-25px 0px;width:25px;height:25px;}
.sprite-crop-blue_border{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_SIMPLE_PADDING = """.sprite-padding-red,
.sprite-padding-green,
.sprite-padding-blue,
.sprite-padding-500{background-image:url('padding.png');background-repeat:no-repeat}
.sprite-padding-red{background-position:0px 0px;width:45px;height:45px;}
.sprite-padding-green{background-position:-45px 0px;width:45px;height:35px;}
.sprite-padding-blue{background-position:0px -45px;width:31px;height:29px;}
.sprite-padding-500{background-position:-31px -45px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_URL = """.sprite-verysimple-red,
.sprite-verysimple-green,
.sprite-verysimple-blue{background-image:url('/static/verysimple.png');background-repeat:no-repeat;}
.sprite-verysimple-red{background-position:0px 0px;width:25px;height:25px;}
.sprite-verysimple-green{background-position:-25px 0px;width:25px;height:25px;}
.sprite-verysimple-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_NOSIZE = """.sprite-verysimple-red,
.sprite-verysimple-green,
.sprite-verysimple-blue{background-image:url('verysimple.png');background-repeat:no-repeat;}
.sprite-verysimple-red{background-position:0px 0px;}
.sprite-verysimple-green{background-position:-25px 0px;}
.sprite-verysimple-blue{background-position:0px -25px;}
"""

EXPECTED_PADDING_NOPADDING = """.sprite-padding-red_10,
.sprite-padding-green_5-10,
.sprite-padding-blue_1-2-3-4,
.sprite-padding-500{background-image:url('padding.png');background-repeat:no-repeat}
.sprite-padding-red_10{background-position:0px 0px;width:25px;height:25px;}
.sprite-padding-green_5-10{background-position:-25px 0px;width:25px;height:25px;}
.sprite-padding-blue_1-2-3-4{background-position:0px -25px;width:25px;height:25px;}
.sprite-padding-500{background-position:-25px -25px;width:25px;height:25px;}
"""


EXPECTED_VERYSIMPLE_NAMESPACE = """.abc-verysimple-red,
.abc-verysimple-green,
.abc-verysimple-blue{background-image:url('verysimple.png');background-repeat:no-repeat;}
.abc-verysimple-red{background-position:0px 0px;width:25px;height:25px;}
.abc-verysimple-green{background-position:-25px 0px;width:25px;height:25px;}
.abc-verysimple-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_EMPTYNAMESPACE = """.verysimple-red,
.verysimple-green,
.verysimple-blue{background-image:url('verysimple.png');background-repeat:no-repeat;}
.verysimple-red{background-position:0px 0px;width:25px;height:25px;}
.verysimple-green{background-position:-25px 0px;width:25px;height:25px;}
.verysimple-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_SPRITE_NAMESPACE =""".sprite-foo-red,
.sprite-foo-green,
.sprite-foo-blue{background-image:url('verysimple.png');background-repeat:no-repeat}
.sprite-foo-red{background-position:0px 0px;width:25px;height:25px;}
.sprite-foo-green{background-position:-25px 0px;width:25px;height:25px;}
.sprite-foo-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_NO_NAMESPACE =""".red,
.green,
.blue{background-image:url('verysimple.png');background-repeat:no-repeat}
.red{background-position:0px 0px;width:25px;height:25px;}
.green{background-position:-25px 0px;width:25px;height:25px;}
.blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_SPRITE_NAMESPACE_EMPTY =""".sprite-red,
.sprite-green,
.sprite-blue{background-image:url('verysimple.png');background-repeat:no-repeat}
.sprite-red{background-position:0px 0px;width:25px;height:25px;}
.sprite-green{background-position:-25px 0px;width:25px;height:25px;}
.sprite-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_ORDERING_CSS = """.sprite-ordering-green,
.sprite-ordering-blue,
.sprite-ordering-red{background-image:url('ordering.png');background-repeat:no-repeat}
.sprite-ordering-green{background-position:0px -8px;width:25px;height:17px;}
.sprite-ordering-blue{background-position:-25px 0px;width:19px;height:25px;}
.sprite-ordering-red{background-position:-44px -23px;width:9px;height:2px;}
"""

EXPECTED_PSEUDOCLASS = """.sprite-pseudoclass-red,
.sprite-pseudoclass-blue,
.sprite-pseudoclass-green{background-image:url('pseudoclass.png');background-repeat:no-repeat}
.sprite-pseudoclass-red:hover{background-position:0px 0px;width:31px;height:29px;}
.sprite-pseudoclass-red{background-position:-31px 0px;width:31px;height:29px;}
.sprite-pseudoclass-blue:hover{background-position:0px -29px;width:31px;height:29px;}
.sprite-pseudoclass-blue{background-position:-31px -29px;width:31px;height:29px;}
.sprite-pseudoclass-green:hover{background-position:-62px 0px;width:25px;height:25px;}
.sprite-pseudoclass-green{background-position:-62px -25px;width:25px;height:25px;}
"""

EXPECTED_PSEUDOCLASSONLY = """.sprite-pseudoclassonly-red:hover,
.sprite-pseudoclassonly-blue{background-image:url('pseudoclassonly.png');background-repeat:no-repeat}
.sprite-pseudoclassonly-red:hover{background-position:0px 0px;width:25px;height:25px;}
.sprite-pseudoclassonly-blue:hover{background-position:-25px 0px;width:25px;height:25px;}
.sprite-pseudoclassonly-blue{background-position:0px -25px;width:25px;height:25px;}"""

EXPECTED_PSEUDOCLASSNAMES = """.sprite-pseudoclassnames-link,
.sprite-pseudoclassnames-hover{background-image:url('pseudoclassnames.png');background-repeat:no-repeat}
.sprite-pseudoclassnames-link{background-position:0px 0px;width:25px;height:25px;}
.sprite-pseudoclassnames-hover:hover{background-position:-25px 0px;width:25px;height:25px;}
.sprite-pseudoclassnames-hover{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_SEP_ = """.sprite_verysimple_red,
.sprite_verysimple_green,
.sprite_verysimple_blue{background-image:url('verysimple.png');background-repeat:no-repeat}
.sprite_verysimple_red{background-position:0px 0px;width:25px;height:25px;}
.sprite_verysimple_green{background-position:-25px 0px;width:25px;height:25px;}
.sprite_verysimple_blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_SEP_NAMESPACE = """.custom_verysimple_red,
.custom_verysimple_green,
.custom_verysimple_blue{background-image:url('verysimple.png');background-repeat:no-repeat}
.custom_verysimple_red{background-position:0px 0px;width:25px;height:25px;}
.custom_verysimple_green{background-position:-25px 0px;width:25px;height:25px;}
.custom_verysimple_blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_CAMELCASE = """.spriteVerysimpleRed,
.spriteVerysimpleGreen,
.spriteVerysimpleBlue{background-image:url('verysimple.png');background-repeat:no-repeat}
.spriteVerysimpleRed{background-position:0px 0px;width:25px;height:25px;}
.spriteVerysimpleGreen{background-position:-25px 0px;width:25px;height:25px;}
.spriteVerysimpleBlue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_CAMELCASE = """.spriteCamelcaseBoxredSmall,
.spriteCamelcaseBoxBlueSmall,
.spriteCamelcaseBoxGreenSmall{background-image:url('camelcase.png');background-repeat:no-repeat}
.spriteCamelcaseBoxredSmall{background-position:0px 0px;width:25px;height:25px;}
.spriteCamelcaseBoxBlueSmall{background-position:-25px 0px;width:25px;height:25px;}
.spriteCamelcaseBoxGreenSmall{background-position:0px -25px;width:25px;height:25px;}"""


EXPECTED_VERYSIMPLE_RATIOS = """.sprite-verysimple-red,
.sprite-verysimple-green,
.sprite-verysimple-blue{background-image:url('verysimple.png');background-repeat:no-repeat}
.sprite-verysimple-red{background-position:-5px -5px;width:13px;height:13px;}
.sprite-verysimple-green{background-position:-26px -5px;width:13px;height:13px;}
.sprite-verysimple-blue{background-position:-5px -26px;width:13px;height:13px;}
@media only screen and (-webkit-min-device-pixel-ratio: 1.5), only screen and (min--moz-device-pixel-ratio: 1.5), only screen and (-o-min-device-pixel-ratio: 150/100), only screen and (min-device-pixel-ratio: 1.5) {.sprite-verysimple-red,
.sprite-verysimple-green,
.sprite-verysimple-blue{background-image:url('verysimple@1.5x.png');-webkit-background-size: 45px 45px;-moz-background-size: 45px 45px;background-size: 45px 45px;}}
@media only screen and (-webkit-min-device-pixel-ratio: 2.0), only screen and (min--moz-device-pixel-ratio: 2.0), only screen and (-o-min-device-pixel-ratio: 200/100), only screen and (min-device-pixel-ratio: 2.0) {.sprite-verysimple-red,
.sprite-verysimple-green,
.sprite-verysimple-blue{background-image:url('verysimple@2x.png');-webkit-background-size: 45px 45px;-moz-background-size: 45px 45px;background-size: 45px 45px;}}
"""

EXPECTED_RECURSIVE = """.sprite-recursive-red,
.sprite-recursive-green,
.sprite-recursive-blue{background-image:url('recursive.png');background-repeat:no-repeat}
.sprite-recursive-red{background-position:0px 0px;width:25px;height:25px;}
.sprite-recursive-green{background-position:-25px 0px;width:25px;height:25px;}
.sprite-recursive-blue{background-position:0px -25px;width:25px;height:25px;}
"""


class SimpleCssCompiler(object):

    def __init__(self, css_text, ignore=['background-position']):
        self._rules = {}

        # Remove glue comment
        css_text = re.sub(r'(\/\* glue\: [\d\.]* hash\: \w+ \*\/\n)', '', css_text)

        rules = ['%s}' % r for r in css_text.split('}') if r.strip()]

        for rule in rules:
            selectors, styles = rule.split('{', 1)
            selectors = selectors.split(',')
            styles = [s.split(':') for s in styles.replace('}', '').split(';') if s]

            for selector in selectors:
                for key, value in styles:
                    if key not in ignore:
                        self._rules.setdefault(selector, {})[key] = value

    def __eq__(self, other):
        return self._rules == other._rules


class TestGlue(unittest.TestCase):

    def assertEqualCSSFileContent(self, path, content):

        with codecs.open(path, 'r', glue.UTF8) as css:
            filecss = SimpleCssCompiler(css.read())
            contentcss = SimpleCssCompiler(content)
            assert filecss == contentcss

    def assertCSSFileContains(self, path, content):

        with codecs.open(path, 'r', glue.UTF8) as css:
            assert content in css.read()

    def assertAreaColor(self, area, color):
        colors = area.getcolors(area.size[0] * area.size[1])
        colors = filter(lambda c: c[1][3] in [255, 0], colors)
        colors = sorted(colors, key=lambda c: c[0], reverse=True)

        assert len(colors) == 1, "More than one color"
        assert colors[0][1] == color, "Invalid predominant color"

    def setUp(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.base_path, 'tests_tmp/')
        shutil.rmtree(self.output_path, True)

    def generate_manager(self, manager_cls, path, config=None):
        config = config or {}
        config = glue.ConfigManager(config, defaults=TEST_DEFAULT_SETTINGS)
        simple_path = os.path.join(self.base_path, 'tests_resources/%s' % path)
        output_path = os.path.join(self.base_path, 'tests_tmp/')

        return manager_cls(path=simple_path,
                           config=config,
                           output=output_path)

    def test_simple_manager(self):
        manager = self.generate_manager(glue.SimpleSpriteManager, 'simple')
        manager.process()

        # Test default algorith
        img_path = os.path.join(self.output_path, 'simple.png')
        css_path = os.path.join(self.output_path, 'simple.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((25, 0)), RED)
        self.assertEqual(image.getpixel((50, 0)), CYAN)
        self.assertEqual(image.getpixel((0, 25)), PINK)
        self.assertEqual(image.getpixel((25, 25)), GREEN)
        self.assertEqual(image.getpixel((50, 25)), BLUE)

        self.assertEqualCSSFileContent(css_path, EXPECTED_SIMPLE_CSS)

        # Test optimized square algorith
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'simple',
                                        {'ordering': 'height',
                                        'algorithm': 'optimized-square'})
        manager.process()

        img_path = os.path.join(self.output_path, 'simple.png')
        css_path = os.path.join(self.output_path, 'simple.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((25, 0)), RED)
        self.assertEqual(image.getpixel((0, 25)), PINK)
        self.assertEqual(image.getpixel((25, 25)), GREEN)
        self.assertEqual(image.getpixel((0, 50)), CYAN)
        self.assertEqual(image.getpixel((25, 50)), BLUE)

        self.assertEqualCSSFileContent(css_path, EXPECTED_OPTIMIZED_SQUARE_CSS)

        # Test optimized square algorith
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'complexe',
                                        {'ordering': 'height',
                                        'algorithm': 'optimized-square'})
        manager.process()

        img_path = os.path.join(self.output_path, 'complexe.png')
        css_path = os.path.join(self.output_path, 'complexe.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), GREEN)
        self.assertEqual(image.getpixel((125, 0)), PURPLE)
        self.assertEqual(image.getpixel((225, 0)), RED)
        self.assertEqual(image.getpixel((0, 125)), CYAN)
        self.assertEqual(image.getpixel((125, 100)), PINK)
        self.assertEqual(image.getpixel((125, 175)), ORANGE)
        self.assertEqual(image.getpixel((0, 225)), BLUE)

        self.assertEqualCSSFileContent(css_path, EXPECTED_COMPLEXE_OPTIMIZED_SQUARE_CSS)

        # Test vertical algorith
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'simple',
                                        {'algorithm': 'vertical'})
        manager.process()

        img_path = os.path.join(self.output_path, 'simple.png')
        css_path = os.path.join(self.output_path, 'simple.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((0, 25)), RED)
        self.assertEqual(image.getpixel((0, 50)), PINK)
        self.assertEqual(image.getpixel((0, 75)), GREEN)
        self.assertEqual(image.getpixel((0, 100)), CYAN)
        self.assertEqual(image.getpixel((0, 125)), BLUE)

        self.assertEqualCSSFileContent(css_path, EXPECTED_SIMPLE_CSS)

        # Test horizontal algorith
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'simple',
                                        {'algorithm': 'horizontal'})
        manager.process()

        img_path = os.path.join(self.output_path, 'simple.png')
        css_path = os.path.join(self.output_path, 'simple.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((25, 0)), RED)
        self.assertEqual(image.getpixel((50, 0)), PINK)
        self.assertEqual(image.getpixel((75, 0)), GREEN)
        self.assertEqual(image.getpixel((100, 0)), CYAN)
        self.assertEqual(image.getpixel((125, 0)), BLUE)

        self.assertEqualCSSFileContent(css_path, EXPECTED_SIMPLE_CSS)

        # Test diagonal algorithm
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'simple',
                                        {'algorithm': 'diagonal'})
        manager.process()

        img_path = os.path.join(self.output_path, 'simple.png')
        css_path = os.path.join(self.output_path, 'simple.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((25, 25)), RED)
        self.assertEqual(image.getpixel((50, 50)), PINK)
        self.assertEqual(image.getpixel((75, 75)), GREEN)
        self.assertEqual(image.getpixel((100, 100)), CYAN)
        self.assertEqual(image.getpixel((125, 125)), BLUE)

        self.assertEqualCSSFileContent(css_path, EXPECTED_SIMPLE_CSS)

        # Test horizontal-bottom algorith
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'ordering',
                                        {'algorithm': 'horizontal-bottom'})
        manager.process()

        img_path = os.path.join(self.output_path, 'ordering.png')
        css_path = os.path.join(self.output_path, 'ordering.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 8)), GREEN)
        self.assertEqual(image.getpixel((25, 0)), BLUE)
        self.assertEqual(image.getpixel((44, 23)), RED)

        self.assertEqualCSSFileContent(css_path, EXPECTED_ORDERING_CSS)

        # Test vertical-right algorith
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'ordering',
                                        {'algorithm': 'vertical-right'})
        manager.process()

        img_path = os.path.join(self.output_path, 'ordering.png')
        css_path = os.path.join(self.output_path, 'ordering.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), GREEN)
        self.assertEqual(image.getpixel((6, 17)), BLUE)
        self.assertEqual(image.getpixel((16, 42)), RED)

        self.assertEqualCSSFileContent(css_path, EXPECTED_ORDERING_CSS)

    def test_project_manager(self):
        manager = self.generate_manager(glue.ProjectSpriteManager, 'multiple')
        manager.process()

        rgb_img_path = os.path.join(self.output_path, 'rgb.png')
        rgb_css_path = os.path.join(self.output_path, 'rgb.css')
        mix_img_path = os.path.join(self.output_path, 'mix.png')
        mix_css_path = os.path.join(self.output_path, 'mix.css')
        self.assertTrue(os.path.isfile(rgb_img_path))
        self.assertTrue(os.path.isfile(rgb_css_path))
        self.assertTrue(os.path.isfile(mix_img_path))
        self.assertTrue(os.path.isfile(mix_css_path))

        image = Image.open(rgb_img_path)

        self.assertEqual(image.getpixel((0, 0)), RED)
        self.assertEqual(image.getpixel((25, 0)), GREEN)
        self.assertEqual(image.getpixel((0, 25)), BLUE)
        self.assertEqual(image.getpixel((25, 25)), TRANSPARENT)

        self.assertEqualCSSFileContent(rgb_css_path, EXPECTED_PROJECT_RGB_CSS)

        image = Image.open(mix_img_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((25, 0)), PINK)
        self.assertEqual(image.getpixel((0, 25)), CYAN)
        self.assertEqual(image.getpixel((25, 25)), TRANSPARENT)

        self.assertEqualCSSFileContent(mix_css_path, EXPECTED_PROJECT_MIX_CSS)

    def test_crop(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'crop',
                                        {'crop': True})
        manager.process()

        img_path = os.path.join(self.output_path, 'crop.png')
        css_path = os.path.join(self.output_path, 'crop.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), RED)
        self.assertEqual(image.getpixel((25, 0)), GREEN)
        self.assertEqual(image.getpixel((0, 25)), BLUE)
        self.assertEqual(image.getpixel((25, 25)), TRANSPARENT)
        self.assertEqualCSSFileContent(css_path, EXPECTED_SIMPLE_CROP)

    def test_padding(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'padding')
        manager.process()

        img_path = os.path.join(self.output_path, 'padding.png')
        css_path = os.path.join(self.output_path, 'padding.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), TRANSPARENT)
        self.assertEqual(image.getpixel((10, 10)), RED)
        self.assertEqual(image.getpixel((34, 34)), RED)
        self.assertEqual(image.getpixel((55, 5)), GREEN)
        self.assertEqual(image.getpixel((79, 29)), GREEN)
        self.assertEqual(image.getpixel((5, 46)), BLUE)
        self.assertEqual(image.getpixel((28, 70)), BLUE)
        self.assertEqual(image.getpixel((31, 45)), YELLOW)
        self.assertEqual(image.getpixel((54, 69)), YELLOW)
        self.assertEqual(image.getpixel((89, 73)), TRANSPARENT)

        self.assertEqualCSSFileContent(css_path, EXPECTED_SIMPLE_PADDING)

    def test_margin(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'simple',
                                        {'margin': 10})
        manager.process()

        img_path = os.path.join(self.output_path, 'simple.png')
        css_path = os.path.join(self.output_path, 'simple.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), TRANSPARENT)
        self.assertEqual(image.getpixel((10, 10)), YELLOW)
        self.assertEqual(image.getpixel((34, 34)), YELLOW)
        self.assertEqual(image.getpixel((55, 10)), RED)
        self.assertEqual(image.getpixel((79, 34)), RED)
        self.assertEqual(image.getpixel((100, 10)), CYAN)
        self.assertEqual(image.getpixel((124, 34)), CYAN)

        self.assertEqual(image.getpixel((10, 55)), PINK)
        self.assertEqual(image.getpixel((34, 79)), PINK)
        self.assertEqual(image.getpixel((55, 55)), GREEN)
        self.assertEqual(image.getpixel((79, 79)), GREEN)
        self.assertEqual(image.getpixel((100, 55)), BLUE)
        self.assertEqual(image.getpixel((124, 79)), BLUE)

        self.assertEqualCSSFileContent(css_path, EXPECTED_SIMPLE_CSS)

    def test_pseudoclass(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'pseudoclass')
        manager.process()

        img_path = os.path.join(self.output_path, 'pseudoclass.png')
        css_path = os.path.join(self.output_path, 'pseudoclass.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((4, 1)), RED)
        self.assertEqual(image.getpixel((28, 25)), RED)
        self.assertEqual(image.getpixel((35, 1)), RED)
        self.assertEqual(image.getpixel((59, 25)), RED)
        self.assertEqual(image.getpixel((62, 0)), GREEN)
        self.assertEqual(image.getpixel((86, 24)), GREEN)
        self.assertEqual(image.getpixel((4, 30)), BLUE)
        self.assertEqual(image.getpixel((28, 54)), BLUE)
        self.assertEqual(image.getpixel((35, 30)), BLUE)
        self.assertEqual(image.getpixel((59, 54)), BLUE)
        self.assertEqual(image.getpixel((62, 25)), GREEN)
        self.assertEqual(image.getpixel((86, 49)), GREEN)

        self.assertEqualCSSFileContent(css_path, EXPECTED_PSEUDOCLASS)

    def test_pseudoclassonly(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'pseudoclassonly')
        manager.process()

        img_path = os.path.join(self.output_path, 'pseudoclassonly.png')
        css_path = os.path.join(self.output_path, 'pseudoclassonly.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_PSEUDOCLASSONLY)

    def test_pseudoclassnames(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'pseudoclassnames')
        manager.process()

        img_path = os.path.join(self.output_path, 'pseudoclassnames.png')
        css_path = os.path.join(self.output_path, 'pseudoclassnames.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_PSEUDOCLASSNAMES)

    def test_ignore_filename_padding(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'padding',
                                        {'ignore_filename_paddings': True})
        manager.process()

        img_path = os.path.join(self.output_path, 'padding.png')
        css_path = os.path.join(self.output_path, 'padding.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), RED)
        self.assertEqual(image.getpixel((25, 0)), GREEN)
        self.assertEqual(image.getpixel((0, 25)), BLUE)
        self.assertEqual(image.getpixel((25, 25)), YELLOW)

        self.assertEqualCSSFileContent(css_path, EXPECTED_PADDING_NOPADDING)

    def test_less(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'less': True})
        manager.process()

        less_path = os.path.join(self.output_path, 'verysimple.less')
        self.assertTrue(os.path.isfile(less_path))

    def test_url(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'url': '/static/'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_URL)

    def test_ordering(self):
        # Test maxside ordering
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'ordering',
                                        {'ordering': 'maxside',
                                         'algorithm': 'horizontal'})
        manager.process()

        img_path = os.path.join(self.output_path, 'ordering.png')
        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), GREEN)
        self.assertEqual(image.getpixel((25, 0)), BLUE)
        self.assertEqual(image.getpixel((44, 0)), RED)

        # Test maxside ordering
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'ordering',
                                        {'ordering': 'width',
                                         'algorithm': 'horizontal'})
        manager.process()

        img_path = os.path.join(self.output_path, 'ordering.png')
        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), GREEN)
        self.assertEqual(image.getpixel((25, 0)), BLUE)
        self.assertEqual(image.getpixel((44, 0)), RED)

        # Test maxside ordering
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'ordering',
                                        {'ordering': 'height',
                                         'algorithm': 'horizontal'})
        manager.process()

        img_path = os.path.join(self.output_path, 'ordering.png')
        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), BLUE)
        self.assertEqual(image.getpixel((19, 0)), GREEN)
        self.assertEqual(image.getpixel((44, 0)), RED)

        # Test area ordering
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'ordering',
                                        {'ordering': 'area',
                                         'algorithm': 'horizontal'})
        manager.process()

        img_path = os.path.join(self.output_path, 'ordering.png')
        image = Image.open(img_path)

        self.assertEqual(image.getpixel((0, 0)), BLUE)
        self.assertEqual(image.getpixel((19, 0)), GREEN)
        self.assertEqual(image.getpixel((44, 0)), RED)

    def test_namespace(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'namespace': 'abc'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_NAMESPACE)

        # Empty namespace
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'namespace': ''})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_EMPTYNAMESPACE)

    def test_sprite_namespace(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'sprite_namespace': 'foo'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_SPRITE_NAMESPACE)

        # Empty namespace
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'sprite_namespace': ''})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_SPRITE_NAMESPACE_EMPTY)

    def test_remove_all_namespaces(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'sprite_namespace': '',
                                         'namespace': ''})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_NO_NAMESPACE)

    def test_separator(self):
        # Custom separator
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'separator': '_'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_SEP_)

        # separator and namespace
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'separator': '_',
                                         'namespace': 'custom'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_SEP_NAMESPACE)

        # camelcase separator
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'separator': 'camelcase'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_CAMELCASE)

    def test_camelcase(self):
        # camelcase separator
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'camelcase',
                                        {'separator': 'camelcase'})
        manager.process()

        css_path = os.path.join(self.output_path, 'camelcase.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_CAMELCASE)

    def test_cachebuster(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'cachebuster': True})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        img_hash = manager.sprites[0].hash[:6]
        self.assertCSSFileContains(css_path, 'verysimple.png?%s' % img_hash)

    def test_cachebuster_filename(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'cachebuster_filename': True})
        manager.process()

        wrong_css_path = os.path.join(self.output_path, 'verysimple.css')
        wrong_img_path = os.path.join(self.output_path, 'verysimple.png')
        self.assertFalse(os.path.isfile(wrong_css_path))
        self.assertFalse(os.path.isfile(wrong_img_path))

        # Discover the css file
        css_filename = [f for f in os.listdir(self.output_path) if f.endswith('.css')][0]
        css_path = os.path.join(self.output_path, css_filename)

        img_hash = manager.sprites[0].hash[:6]
        img_path = os.path.join(self.output_path, 'verysimple_%s.png' % img_hash)
        self.assertTrue(os.path.isfile(img_path))

    def test_png8(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'png8': True})
        manager.process()

        img_path = os.path.join(self.output_path, 'verysimple.png')
        self.assertTrue(os.path.isfile(img_path))

        image = Image.open(img_path)
        self.assertEqual(image.mode, 'P')

        transparency = image.info.get('transparency')

        self.assertTrue(all([t == 255 for t in transparency[:-1]]))
        self.assertEqual(transparency[-1], 0)

    def test_templates(self):
        # Test empty templates
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'global_template': '',
                                         'each_template': ''})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, '')

        # Test no-size template
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'each_template': ('%(class_name)s{background-position:%(x)s %(y)s;}\n')})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_NOSIZE)

    def test_ratios(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'ratios': '2,1.5,1',
                                         'margin': '5'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        img_path = os.path.join(self.output_path, 'verysimple.png')
        img_path_15x = os.path.join(self.output_path, 'verysimple@1.5x.png')
        img_path_2x = os.path.join(self.output_path, 'verysimple@2x.png')

        self.assertTrue(os.path.isfile(css_path))
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(img_path_2x))
        self.assertTrue(os.path.isfile(img_path_15x))

        img = Image.open(img_path)

        self.assertAreaColor(img.crop((5, 5, 18, 18)), RED)
        self.assertAreaColor(img.crop((27, 5, 40, 18)), GREEN)
        self.assertAreaColor(img.crop((5, 27, 18, 40)), BLUE)

        img_15x = Image.open(img_path_15x)
        self.assertAreaColor(img_15x.crop((8, 8, 25, 25)), RED)
        self.assertAreaColor(img_15x.crop((41, 8, 59, 25)), GREEN)
        self.assertAreaColor(img_15x.crop((8, 42, 25, 59)), BLUE)

        img_2x = Image.open(img_path_2x)

        self.assertEqual(img_2x.getpixel((10, 10)), RED)
        self.assertEqual(img_2x.getpixel((34, 34)), RED)
        self.assertEqual(img_2x.getpixel((55, 10)), GREEN)
        self.assertEqual(img_2x.getpixel((79, 34)), GREEN)
        self.assertEqual(img_2x.getpixel((10, 55)), BLUE)
        self.assertEqual(img_2x.getpixel((34, 79)), BLUE)

        self.assertEqualCSSFileContent(css_path, EXPECTED_VERYSIMPLE_RATIOS)

    def test_recursive(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'recursive',
                                        {'recursive': True})
        manager.process()

        css_path = os.path.join(self.output_path, 'recursive.css')
        self.assertTrue(os.path.isfile(css_path))

        self.assertEqualCSSFileContent(css_path, EXPECTED_RECURSIVE)

    def test_metadata(self):
        manager = self.generate_manager(glue.SimpleSpriteManager, 'verysimple')
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')

        # Comment format: /* glue: 0.2.8 hash: 2973af2c6c */
        with codecs.open(css_path, 'r', glue.UTF8) as css:
            _, version, _, css_sprite_hash = css.read().split('\n', 1)[0][3:-3].split()
            self.assertEqual(version, glue.__version__)
            self.assertTrue(css_sprite_hash.isalnum())
            self.assertEqual(len(css_sprite_hash), 10)

        img_path = os.path.join(self.output_path, 'verysimple.png')
        img = Image.open(img_path)
        self.assertEqual(img.info['Software'], 'glue-%s' % glue.__version__)
        self.assertEqual(img.info['Comment'], css_sprite_hash)

        run_1_css_mtime = os.path.getmtime(css_path)
        run_1_img_mtime = os.path.getmtime(img_path)

        # Check if running the command again doesn't override the files.
        # We need to stop 1s in order to get a different mtime
        time.sleep(1)

        manager = self.generate_manager(glue.SimpleSpriteManager, 'verysimple')
        manager.process()

        run_2_css_mtime = os.path.getmtime(css_path)
        run_2_img_mtime = os.path.getmtime(img_path)

        self.assertEqual(run_1_css_mtime, run_2_css_mtime)
        self.assertEqual(run_1_img_mtime, run_2_img_mtime)

        # Check if changing preferences.
        # We need to stop 1s in order to get a different mtime
        time.sleep(1)

        manager = self.generate_manager(glue.SimpleSpriteManager,
                                       'verysimple',
                                       {'padding': '5'})
        manager.process()

        run_3_css_mtime = os.path.getmtime(css_path)
        run_3_img_mtime = os.path.getmtime(img_path)

        self.assertNotEqual(run_1_css_mtime, run_3_css_mtime)
        self.assertNotEqual(run_1_img_mtime, run_3_img_mtime)

        # Check --force option
        # We need to stop 1s in order to get a different mtime
        time.sleep(1)

        manager = self.generate_manager(glue.SimpleSpriteManager,
                                       'verysimple',
                                       {'padding': '5',
                                        'force': True})
        manager.process()

        run_4_css_mtime = os.path.getmtime(css_path)
        run_4_img_mtime = os.path.getmtime(img_path)

        self.assertNotEqual(run_3_css_mtime, run_4_css_mtime)
        self.assertNotEqual(run_3_img_mtime, run_4_img_mtime)

    def test_no_css(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'no_css': True})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        img_path = os.path.join(self.output_path, 'verysimple.png')

        self.assertTrue(os.path.isfile(img_path))
        self.assertFalse(os.path.isfile(css_path))

    def test_no_img(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'no_img': True})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        img_path = os.path.join(self.output_path, 'verysimple.png')

        self.assertFalse(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

    def test_no_img_no_css(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'no_img': True,
                                         'no_css': True})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        img_path = os.path.join(self.output_path, 'verysimple.png')

        self.assertFalse(os.path.isfile(img_path))
        self.assertFalse(os.path.isfile(css_path))


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.conf_a = {'a': 'a'}
        self.conf_b = {'b': 'b'}
        self.conf_c = {'c': 'c'}
        self.conf_d = {'d': 'd'}

    def test_constructor(self):
        cm = glue.ConfigManager(self.conf_a, self.conf_b,
                                defaults=self.conf_c,
                                priority=self.conf_d)
        self.assertEqual(cm.sources, [self.conf_a, self.conf_b])
        self.assertEqual(cm.defaults, self.conf_c)
        self.assertEqual(cm.priority, self.conf_d)

    def test_extend(self):
        cm = glue.ConfigManager(self.conf_a, self.conf_b)
        cm2 = cm.extend(self.conf_c)
        self.assertEqual(cm2.sources[0], self.conf_c)
        self.assertEqual(cm2.sources[1:], cm.sources)
        self.assertEqual(cm2.defaults, cm.defaults)
        self.assertEqual(cm2.priority, cm.priority)

    def test___getattr__(self):
        cm = glue.ConfigManager(self.conf_a, self.conf_b,
                                defaults=self.conf_c,
                                priority=self.conf_d)
        self.assertEqual(cm.a, 'a')
        self.assertEqual(cm.b, 'b')
        self.assertEqual(cm.c, 'c')
        self.assertEqual(cm.d, 'd')

        cm = glue.ConfigManager(self.conf_a, {'a': 'aa'},
                                defaults={'a': 'aaa'},
                                priority={'a': 'aaaa'})
        self.assertEqual(cm.a, 'aaaa')

        cm = glue.ConfigManager(self.conf_a, {'a': 'aa'},
                                defaults={'a': 'aaa'})
        self.assertEqual(cm.a, 'a')

        cm = glue.ConfigManager(self.conf_b, defaults={'a': 'aaa'})
        self.assertEqual(cm.a, 'aaa')

    def test_get_file_config(self):
        expected = {'algorithm': 'horizontal',
                    'cachebuster': True,
                    'cachebuster-filename': True,
                    'crop': True,
                    'each_template': 'each_template',
                    'global_template': 'global_template',
                    'html': True,
                    'ignore_filename_paddings': True,
                    'less': True,
                    'margin': '2',
                    'namespace': 'test',
                    'optipng': True,
                    'optipngpath': '/foo/bar/optipng',
                    'ordering': 'width',
                    'padding': '1',
                    'png8': True,
                    'project': True,
                    'quiet': True,
                    'ratio_template': 'ratio_template',
                    'ratios': '1,2,3',
                    'retina': True,
                    'separator': '_-_',
                    'url': 'http://test.com',
                    'random': False}
        config = glue.get_file_config('tests_resources/config/')
        self.assertEqual(config, expected)

if __name__ == '__main__':
    unittest.main()
