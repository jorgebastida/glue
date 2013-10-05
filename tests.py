import unittest
import glue

class TestGlue(unittest.TestCase):

    def test_add(self):
        self.assertEqual(1 + 1, 2)

    def test_version(self):
        self.assertEqual(glue.__version__, '0.9')

if __name__ == '__main__':
    unittest.main()
