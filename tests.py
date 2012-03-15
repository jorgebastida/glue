import os
import unittest
import shutil

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


EXPECTED_SIMPLE_CSS = """
.sprite-simple-yellow,
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
.sprite-simple-blue{background-position:-125px 0px;width:25px;height:25px;}"""


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


class GlueTestCase(unittest.TestCase):

    def assertEqualCSS(self, css_text1, css_text2):
        css1 = SimpleCssCompiler(css_text1)
        css2 = SimpleCssCompiler(css_text2)
        assert css1 == css2


class TestManagers(GlueTestCase):

    def setUp(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.base_path, 'test_tmp/')
        shutil.rmtree(self.output_path, True)

    def generate_manager(self, manager_cls, path, config=None):
        config = config or {}
        config = glue.ConfigManager(config, defaults=TEST_DEFAULT_SETTINGS)
        simple_path = os.path.join(self.base_path, 'tests_resources/%s' % path)
        output_path = os.path.join(self.base_path, 'test_tmp/')

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

        # Test diagonal algorith
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
