import os
import re
import hashlib
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


EXPECTED_SIMPLE_CSS = """.sprite-simple-yellow,
.sprite-simple-red,
.sprite-simple-pink,
.sprite-simple-green,
.sprite-simple-cyan,
.sprite-simple-blue{background-image:url(simple.png);background-repeat:no-repeat;}
.sprite-simple-yellow{background-position:0px 0px;width:25px;height:25px;}
.sprite-simple-red{background-position:-25px 0px;width:25px;height:25px;}
.sprite-simple-pink{background-position:-50px 0px;width:25px;height:25px;}
.sprite-simple-green{background-position:-75px 0px;width:25px;height:25px;}
.sprite-simple-cyan{background-position:-100px 0px;width:25px;height:25px;}
.sprite-simple-blue{background-position:-125px 0px;width:25px;height:25px;}
"""

EXPECTED_PROJECT_MIX_CSS = """.sprite-mix-yellow,
.sprite-mix-pink,
.sprite-mix-cyan{background-image:url(mix.png);background-repeat:no-repeat;}
.sprite-mix-yellow{background-position:0px 0px;width:25px;height:25px;}
.sprite-mix-pink{background-position:-25px 0px;width:25px;height:25px;}
.sprite-mix-cyan{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_PROJECT_RGB_CSS = """.sprite-rgb-red,
.sprite-rgb-green,
.sprite-rgb-blue{background-image:url(rgb.png);background-repeat:no-repeat;}
.sprite-rgb-red{background-position:0px 0px;width:25px;height:25px;}
.sprite-rgb-green{background-position:-25px 0px;width:25px;height:25px;}
.sprite-rgb-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_SIMPLE_CROP = """.sprite-crop-red_border,
.sprite-crop-green_border,
.sprite-crop-blue_border{background-image:url(crop.png);background-repeat:no-repeat;}
.sprite-crop-red_border{background-position:0px 0px;width:25px;height:25px;}
.sprite-crop-green_border{background-position:-25px 0px;width:25px;height:25px;}
.sprite-crop-blue_border{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_SIMPLE_PADDING = """.sprite-padding-red,
.sprite-padding-green,
.sprite-padding-blue{background-image:url(padding.png);background-repeat:no-repeat;}
.sprite-padding-red{background-position:0px 0px;width:45px;height:45px;}
.sprite-padding-green{background-position:-45px 0px;width:45px;height:35px;}
.sprite-padding-blue{background-position:0px -45px;width:31px;height:29px;}
"""

EXPECTED_VERYSIMPLE_URL = """.sprite-verysimple-red,
.sprite-verysimple-green,
.sprite-verysimple-blue{background-image:url(/static/verysimple.png);background-repeat:no-repeat;}
.sprite-verysimple-red{background-position:0px 0px;width:25px;height:25px;}
.sprite-verysimple-green{background-position:-25px 0px;width:25px;height:25px;}
.sprite-verysimple-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_NOSIZE = """
.sprite-verysimple-red,
.sprite-verysimple-green,
.sprite-verysimple-blue{background-image:url(verysimple.png);background-repeat:no-repeat;}
.sprite-verysimple-red{background-position:0px 0px;}
.sprite-verysimple-green{background-position:-25px 0px;}
.sprite-verysimple-blue{background-position:0px -25px;}
"""

EXPECTED_PADDING_NOPADDING = """.sprite-padding-red_10,
.sprite-padding-green_5-10,
.sprite-padding-blue_1-2-3-4{background-image:url(padding.png);background-repeat:no-repeat;}
.sprite-padding-red_10{background-position:0px 0px;width:25px;height:25px;}
.sprite-padding-green_5-10{background-position:-25px 0px;width:25px;height:25px;}
.sprite-padding-blue_1-2-3-4{background-position:0px -25px;width:25px;height:25px;}
"""


EXPECTED_VERYSIMPLE_NAMESPACE = """
.abc-verysimple-red,
.abc-verysimple-green,
.abc-verysimple-blue{background-image:url(verysimple.png);background-repeat:no-repeat;}
.abc-verysimple-red{background-position:0px 0px;width:25px;height:25px;}
.abc-verysimple-green{background-position:-25px 0px;width:25px;height:25px;}
.abc-verysimple-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_EMPTYNAMESPACE = """
.verysimple-red,
.verysimple-green,
.verysimple-blue{background-image:url(verysimple.png);background-repeat:no-repeat;}
.verysimple-red{background-position:0px 0px;width:25px;height:25px;}
.verysimple-green{background-position:-25px 0px;width:25px;height:25px;}
.verysimple-blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_ORDERING_CSS = """
.sprite-ordering-green,
.sprite-ordering-blue,
.sprite-ordering-red{background-image:url(ordering.png);background-repeat:no-repeat}
.sprite-ordering-green{background-position:0px -8px;width:25px;height:17px;}
.sprite-ordering-blue{background-position:-25px 0px;width:19px;height:25px;}
.sprite-ordering-red{background-position:-44px -23px;width:9px;height:2px;}
"""

EXPECTED_PSEUDOCLASS = """
.sprite-pseudoclass-red,
.sprite-pseudoclass-blue,
.sprite-pseudoclass-green{background-image:url(pseudoclass.png);background-repeat:no-repeat}
.sprite-pseudoclass-red:hover{background-position:0px 0px;width:31px;height:29px;}
.sprite-pseudoclass-red{background-position:-31px 0px;width:31px;height:29px;}
.sprite-pseudoclass-blue:hover{background-position:0px -29px;width:31px;height:29px;}
.sprite-pseudoclass-blue{background-position:-31px -29px;width:31px;height:29px;}
.sprite-pseudoclass-green:hover{background-position:-62px 0px;width:25px;height:25px;}
.sprite-pseudoclass-green{background-position:-62px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_SEP_ = """
.sprite_verysimple_red,
.sprite_verysimple_green,
.sprite_verysimple_blue{background-image:url(verysimple.png);background-repeat:no-repeat}
.sprite_verysimple_red{background-position:0px 0px;width:25px;height:25px;}
.sprite_verysimple_green{background-position:-25px 0px;width:25px;height:25px;}
.sprite_verysimple_blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_SEP_NAMESPACE = """
.custom_verysimple_red,
.custom_verysimple_green,
.custom_verysimple_blue{background-image:url(verysimple.png);background-repeat:no-repeat}
.custom_verysimple_red{background-position:0px 0px;width:25px;height:25px;}
.custom_verysimple_green{background-position:-25px 0px;width:25px;height:25px;}
.custom_verysimple_blue{background-position:0px -25px;width:25px;height:25px;}
"""

EXPECTED_VERYSIMPLE_CAMELCASE = """
.spriteVerysimpleRed,
.spriteVerysimpleGreen,
.spriteVerysimpleBlue{background-image:url(verysimple.png);background-repeat:no-repeat}
.spriteVerysimpleRed{background-position:0px 0px;width:25px;height:25px;}
.spriteVerysimpleGreen{background-position:-25px 0px;width:25px;height:25px;}
.spriteVerysimpleBlue{background-position:0px -25px;width:25px;height:25px;}
"""


class SimpleCssCompiler(object):

    def __init__(self, css_text, ignore=['background-position']):
        self._rules = {}

        css_text = css_text.replace('\n', '')
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

    def assertEqualCSS(self, css_text1, css_text2):
        css1 = SimpleCssCompiler(css_text1)
        css2 = SimpleCssCompiler(css_text2)
        assert css1 == css2

    def setUp(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.base_path, 'tests_tmp/')
        self.clean_output_path()

    def clean_output_path(self):
        for root, dirs, files in os.walk(self.output_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def tearDown(self):
        self.clean_output_path()

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
        css = open(css_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((25, 0)), RED)
        self.assertEqual(image.getpixel((50, 0)), CYAN)
        self.assertEqual(image.getpixel((0, 25)), PINK)
        self.assertEqual(image.getpixel((25, 25)), GREEN)
        self.assertEqual(image.getpixel((50, 25)), BLUE)

        self.assertEqualCSS(css.read(), EXPECTED_SIMPLE_CSS)
        css.close()

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
        css = open(css_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((0, 25)), RED)
        self.assertEqual(image.getpixel((0, 50)), PINK)
        self.assertEqual(image.getpixel((0, 75)), GREEN)
        self.assertEqual(image.getpixel((0, 100)), CYAN)
        self.assertEqual(image.getpixel((0, 125)), BLUE)

        self.assertEqualCSS(css.read(), EXPECTED_SIMPLE_CSS)
        css.close()

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
        css = open(css_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((25, 0)), RED)
        self.assertEqual(image.getpixel((50, 0)), PINK)
        self.assertEqual(image.getpixel((75, 0)), GREEN)
        self.assertEqual(image.getpixel((100, 0)), CYAN)
        self.assertEqual(image.getpixel((125, 0)), BLUE)

        self.assertEqualCSS(css.read(), EXPECTED_SIMPLE_CSS)
        css.close()

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
        css = open(css_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((25, 25)), RED)
        self.assertEqual(image.getpixel((50, 50)), PINK)
        self.assertEqual(image.getpixel((75, 75)), GREEN)
        self.assertEqual(image.getpixel((100, 100)), CYAN)
        self.assertEqual(image.getpixel((125, 125)), BLUE)

        self.assertEqualCSS(css.read(), EXPECTED_SIMPLE_CSS)
        css.close()

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
        css = open(css_path)

        self.assertEqual(image.getpixel((0, 8)), GREEN)
        self.assertEqual(image.getpixel((25, 0)), BLUE)
        self.assertEqual(image.getpixel((44, 23)), RED)

        self.assertEqualCSS(css.read(), EXPECTED_ORDERING_CSS)
        css.close()

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
        css = open(css_path)

        self.assertEqual(image.getpixel((0, 0)), GREEN)
        self.assertEqual(image.getpixel((6, 17)), BLUE)
        self.assertEqual(image.getpixel((16, 42)), RED)

        self.assertEqualCSS(css.read(), EXPECTED_ORDERING_CSS)
        css.close()

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
        css = open(rgb_css_path)

        self.assertEqual(image.getpixel((0, 0)), RED)
        self.assertEqual(image.getpixel((25, 0)), GREEN)
        self.assertEqual(image.getpixel((0, 25)), BLUE)
        self.assertEqual(image.getpixel((25, 25)), TRANSPARENT)

        self.assertEqualCSS(css.read(), EXPECTED_PROJECT_RGB_CSS)
        css.close()

        image = Image.open(mix_img_path)
        css = open(mix_css_path)

        self.assertEqual(image.getpixel((0, 0)), YELLOW)
        self.assertEqual(image.getpixel((25, 0)), PINK)
        self.assertEqual(image.getpixel((0, 25)), CYAN)
        self.assertEqual(image.getpixel((25, 25)), TRANSPARENT)

        self.assertEqualCSS(css.read(), EXPECTED_PROJECT_MIX_CSS)
        css.close()

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
        css = open(css_path)

        self.assertEqual(image.getpixel((0, 0)), RED)
        self.assertEqual(image.getpixel((25, 0)), GREEN)
        self.assertEqual(image.getpixel((0, 25)), BLUE)
        self.assertEqual(image.getpixel((25, 25)), TRANSPARENT)
        self.assertEqualCSS(css.read(), EXPECTED_SIMPLE_CROP)
        css.close()

    def test_padding(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'padding')
        manager.process()

        img_path = os.path.join(self.output_path, 'padding.png')
        css_path = os.path.join(self.output_path, 'padding.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)
        css = open(css_path)

        self.assertEqual(image.getpixel((0, 0)), TRANSPARENT)
        self.assertEqual(image.getpixel((10, 10)), RED)
        self.assertEqual(image.getpixel((34, 34)), RED)
        self.assertEqual(image.getpixel((55, 5)), GREEN)
        self.assertEqual(image.getpixel((79, 29)), GREEN)
        self.assertEqual(image.getpixel((5, 46)), BLUE)
        self.assertEqual(image.getpixel((28, 70)), BLUE)
        self.assertEqual(image.getpixel((89, 73)), TRANSPARENT)

        self.assertEqualCSS(css.read(), EXPECTED_SIMPLE_PADDING)
        css.close()

    def test_pseudoclass(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'pseudoclass')
        manager.process()

        img_path = os.path.join(self.output_path, 'pseudoclass.png')
        css_path = os.path.join(self.output_path, 'pseudoclass.css')
        self.assertTrue(os.path.isfile(img_path))
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)
        css = open(css_path)

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

        self.assertEqualCSS(css.read(), EXPECTED_PSEUDOCLASS)
        css.close()

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
        css = open(css_path)

        self.assertEqual(image.getpixel((0, 0)), RED)
        self.assertEqual(image.getpixel((25, 0)), GREEN)
        self.assertEqual(image.getpixel((0, 25)), BLUE)
        self.assertEqual(image.getpixel((25, 25)), TRANSPARENT)

        self.assertEqualCSS(css.read(), EXPECTED_PADDING_NOPADDING)
        css.close()

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

        css = open(css_path)
        self.assertEqualCSS(css.read(), EXPECTED_VERYSIMPLE_URL)
        css.close()

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

        css = open(css_path)
        self.assertEqualCSS(css.read(), EXPECTED_VERYSIMPLE_NAMESPACE)
        css.close()

        # Empty namespace
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'namespace': ''})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        css = open(css_path)
        self.assertEqualCSS(css.read(), EXPECTED_VERYSIMPLE_EMPTYNAMESPACE)
        css.close()

    def test_separator(self):
        # Custom separator
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'separator': '_'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        css = open(css_path)
        self.assertEqualCSS(css.read(), EXPECTED_VERYSIMPLE_SEP_)
        css.close()

        # separator and namespace
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'separator': '_',
                                         'namespace': 'custom'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        css = open(css_path)
        self.assertEqualCSS(css.read(), EXPECTED_VERYSIMPLE_SEP_NAMESPACE)
        css.close()

        # camelcase separator
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'separator': 'camelcase'})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        css = open(css_path)
        self.assertEqualCSS(css.read(), EXPECTED_VERYSIMPLE_CAMELCASE)
        css.close()

    def test_cachebuster(self):
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'cachebuster': True})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        img_path = os.path.join(self.output_path, 'verysimple.png')
        self.assertTrue(os.path.isfile(css_path))

        image = Image.open(img_path)
        css = open(css_path)

        img_hash = hashlib.sha1(image.tostring()).hexdigest()[:6]
        self.assertTrue('verysimple.png?%s' % img_hash in css.read())

        css.close()

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

        css = open(css_path)
        css_text = css.read()
        css.close()

        img_hash = re.findall(r'verysimple_(\w+).png', css_text)[0]

        img_path = os.path.join(self.output_path, 'verysimple_%s.png' % img_hash)
        self.assertTrue(os.path.isfile(img_path))

        image = Image.open(img_path)
        real_img_hash = hashlib.sha1(image.tostring()).hexdigest()[:6]

        self.assertTrue(real_img_hash == img_hash)

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

        css = open(css_path)
        self.assertEqualCSS(css.read(), '')
        css.close()

        # Test no-size template
        manager = self.generate_manager(glue.SimpleSpriteManager,
                                        'verysimple',
                                        {'each_template': ('%(class_name)s{background-position:%(x)s %(y)s;}\n')})
        manager.process()

        css_path = os.path.join(self.output_path, 'verysimple.css')
        self.assertTrue(os.path.isfile(css_path))

        css = open(css_path)
        self.assertEqualCSS(css.read(), EXPECTED_VERYSIMPLE_NOSIZE)
        css.close()


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


if __name__ == '__main__':
    unittest.main()
