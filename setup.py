#!/usr/bin/env python
from setuptools import setup
from io import open
import re

def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()

with open('pyCryptomusAPI/version.py', 'r', encoding='utf-8') as f:  # Credits: LonamiWebs
    version = re.search(r"^__version__\s*=\s*'(.*)'.*$",
                        f.read(), flags=re.MULTILINE).group(1)

setup(name='pyCryptomusAPI',
      version=version,
      description='Python implementation of Cryptomus (https://cryptomus.com) and Heleket (https://heleket.com) pubilc API',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      author='Badiboy',
      url='https://github.com/Badiboy/pyCryptomusAPI',
      packages=['pyCryptomusAPI'],
      install_requires=['requests'],
      license='MIT license',
      keywords="Crypto Pay API Cryptomus Heleket",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3',
#          'License :: OSI Approved :: MIT License',
      ],
)
