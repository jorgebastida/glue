"""
Glue
-----

Glue is a command line tool to generate css sprites.

123 glue!
````````````````

::

    $ glue images

Easy to Setup
`````````````````

::

    $ easy_install glue
    or
    $ pip install glue

Links
`````

* `website <http://glue.github.com/>`_
* `documentation <http://glue.github.com/docs/>`_

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
    name='Glue',
    version='0.1',
    url='http://glue.github.com/',
    license='BSD',
    author='Jorge Bastida',
    author_email='me@jorgebastida.com',
    description='A command line tool to generate css sprites.',
    long_description=__doc__,
    py_modules=['glue'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'PIL>=1.1.7'
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
