import sys

from setuptools import setup, find_packages

install_requires=[
    'Pillow>=2.2.2',
    'Jinja2>=2.7,<2.8',
]

tests_require=[
    'cssutils>=0.9,<1.0',
]

# as of Python >= 2.7 argparse module is maintained within Python.
if sys.version_info >= (2, 7) or sys.version_info >= (3, 2):
    install_requires.append('argparse>=1.1')

# as of Python >= 3.3 unittest.mock module is maintained within Python.
if sys.version_info >= (3, 3):
    tests_require.append('mock>=1.0')


setup(
    name='glue',
    version='0.9.4',
    url='http://github.com/jorgebastida/glue',
    license='BSD',
    author='Jorge Bastida',
    author_email='me@jorgebastida.com',
    description='Glue is a simple command line tool to generate sprites.',
    long_description=('Glue is a simple command line tool to generate '
                      'sprites using any kind of source images like '
                      'PNG, JPEG or GIF. Glue will generate a unique PNG '
                      'file containing every source image and a map file '
                      'including the necessary information to use it.'),
    keywords = "glue sprites css cocos2d",
    packages = find_packages(),
    platforms='any',
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    entry_points = {
        'console_scripts': [
            'glue = glue.bin:main',
        ]
    },
    zip_safe = False
)
