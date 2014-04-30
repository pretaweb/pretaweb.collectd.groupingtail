from setuptools import setup, find_packages
import os

version = '1.0a1dev2'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='pretaweb.collectd.groupingtail',
      version=version,
      description="Log tail parser-collectd plugin",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Adam Terrey (PretaWeb)',
      author_email='software@pretaweb.com',
      url='http://www.pretaweb.com',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['pretaweb', 'pretaweb.collectd'],
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'test': [
            'mock',
          ],
      },
      install_requires=[
          'setuptools',
          'collectd',
          'pygtail==0.2.1.1', # our special branch because the main branch is broken for now
          # -*- Extra requirements: -*-
          # temp restrict to our branch till we get it merged
          'pygtail >=0.2.1.1dev',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
