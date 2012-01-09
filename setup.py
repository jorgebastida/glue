"""
Glue
-----

Glue is a simple command line tool to generate CSS sprites.

"""


try:
    from setuptools import setup
    kw = {'entry_points':
          """[console_scripts]\nglue = glue:main\n""",
          'zip_safe': False}
except ImportError:
    from distutils.core import setup
    kw = {'scripts': ['glue.py']}

setup(
    name='glue',
    version='0.1.9',
    url='http://github.com/jorgebastida/glue',
    license='BSD',
    author='Jorge Bastida',
    author_email='me@jorgebastida.com',
    description='Glue is a simple command line tool to generate CSS sprites.',
    long_description=('Glue is a simple command line tool to generate CSS '
                      'sprites.'),
    py_modules=['glue'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'PIL>=1.1.6'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    **kw
)
