#!/usr/bin/python3
# ~/dev/py/wireops/setup.py

""" Set up wireops package. """

import re
from distutils.core import setup
__version__ = re.search(r"__version__\s*=\s*'(.*)'",
                        open('wireops/__init__.py').read()).group(1)

# see http://docs.python.org/distutils/setupscript.html

setup(name='wireops',
      version=__version__,
      author='Jim Dixon',
      author_email='jddixon@gmail.com',
      #
      # wherever we have a .py file that will be imported, we
      # list it here, without the extension but SQuoted
      py_modules=[],
      #
      # a package has its own directory with an __init__.py in it
      packages=['wireops', ],
      #
      # scripts should have a globally unique name; they might be in a
      #   scripts/ subdir; SQuote the script name
      scripts=[],
      description='python3 protocol for compressed data transfer',
      url='https://jddixon.github.io/wireops',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],)
