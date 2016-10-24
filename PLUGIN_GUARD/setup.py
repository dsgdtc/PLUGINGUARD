#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""Pluginguard setup"""

from os.path import abspath, normpath, dirname, join as pjoin
import sys

from setuptools import setup, find_packages

if sys.version_info[:2] < (2, 6):
    sys.exit("Required Python 2.6 or later, found %s!" % sys.version)

#SRC = 'src'
PKG = 'pluginguard'
HERE = normpath(abspath(dirname(__file__)))

META = {}
LINES = [i.strip() for i in open(pjoin(HERE, PKG, '__init__.py'), 'rb')
         if i.startswith('__')]
for i in LINES:
    k, v = i.split('=', 1)
    META[k.strip()] = v.strip(" '\"")

LONG_DESCRIPTION = open(pjoin(HERE, 'README'), 'r').read()

DESCRIPTION = LONG_DESCRIPTION.splitlines()[0].strip()

STATUS_MAP = {
    'Planning': 1,
    'Pre-Alpha': 2,
    'Alpha': 3,
    'Beta': 4,
    'Production/Stable': 5,
    'Mature': 6,
    'Inactive': 7
}

# Get classifiers from http://pypi.python.org/pypi?:action=list_classifiers
CLASSIFIERS = [
    'Development Status :: %d - %s' % (STATUS_MAP[META['__status__']], META['__status__']),
    'Environment :: Web Environment',
    'Environment :: No Input/Output (Daemon)',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: Proprietary',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries',
]

INSTALL_REQUIRES = [
    'setuptools >= 0.6',
    'configobj >= 4.6.0',
]

if __name__ == """__main__""":
    setup(
        name='pluginguard',
        version=str(META['__version__']),
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=META['__author__'],
        author_email=META['__email__'],
        maintainer=META['__maintainer__'],
        maintainer_email=META['__email__'],
        classifiers=CLASSIFIERS,
        license=META['__license__'],
        platforms=['Linux'],
        packages = [ 'pluginguard' ],
        data_files = [('/etc/pluginguard/', ['etc/pluginguard/plugin_guard.cfg']),
                      ('/var/log/plugin_guard/', ['var/log/plugin_guard/plugin_guard.log']),
                    ],
        entry_points={
            'console_scripts': [
                'pluginguard = pluginguard.pluginguard:main',
                'pluginguard_start = pluginguard.pluginguard:start',
                'pluginguard_stop = pluginguard.pluginguard:stop',
                'pluginguard_status = pluginguard.pluginguard:status',
            ]
        },
        zip_safe=True
    )
