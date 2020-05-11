"""Framework for Intelligent Agents Development - PADE

The MIT License (MIT)

Copyright (c) 2019 Lucas S Melo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE."""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pade',
      version='2.2.3',
      description='Framework for multiagent systems development in Python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Lucas S Melo',
      author_email='lucassmelo@dee.ufc.br',
      package_data={'': ['*.html', '*.js', '*.css', '*.sqlite', '*.png']},
      include_package_data=True,
      install_requires=['twisted',
                        'requests',
                        'pagan',
                        'alchimia',
                        'click',
                        'Flask-Bootstrap',
                        'Flask-Login',
                        'Flask-WTF',
                        'Flask-SQLAlchemy',
                        'Flask-Migrate',
                        'Flask-Script',
                        'Flask',
                        'terminaltables'],
      license='MIT',
      keywords='multiagent distributed systems',
      url='http://pade.readthedocs.org',
      packages=find_packages(),
      entry_points='''
            [console_scripts]
            pade=pade.cli.pade_cmd:cmd
      ''',
      classifiers=[  
              'Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'Topic :: Software Development :: Build Tools',
              'License :: OSI Approved :: MIT License',
              'Operating System :: OS Independent',
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.7',
      ],)
