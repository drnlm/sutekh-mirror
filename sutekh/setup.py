# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

# Be sure that the import will grab the correct version
# of SutekhInfo when building packages.

"""Setuptools setup.py file for Sutekh."""

#from setuptools import setup, find_packages

# avoid importing all of Sutkeh and its dependencies
import importlib
import os
import sys

from setuptools import find_packages
from cx_Freeze import setup, Executable

sys.path.append('sutekh')
SutekhInfo = importlib.import_module("SutekhInfo").SutekhInfo

build_exe_options = {
    'includes': ['sqlobject.boundattributes', 'sqlobject.declarative',
                 'packaging.specifiers', 'packaging.requirements', 'packaging.version'],
    # We need to exclude DateTime to avoid sqlobject trying (and failing) to import it
    # in col.py
    # We exclude some other unneeded packages to reduce bloat
    'excludes': ['DateTime', 'tkinter', 'test'],
    'include_files': [
        # We should reduce the number of icons we copy
         (os.path.join(sys.prefix, 'share', 'icons', 'Adwaita'),
             os.path.join('share', 'icons', 'Adwaita')),
         (os.path.join(sys.prefix, 'lib', 'gtk-3.0'),
             os.path.join('lib', 'gtk-3.0')),
         (os.path.join(sys.prefix, 'lib', 'gdk-pixbuf-2.0'),
             os.path.join('lib', 'gdk-pixbuf-2.0')),
         # We don't import plugins directly, so we include them now
         (os.path.join('sutekh', 'base', 'gui', 'plugins'),
             os.path.join('sutekh', 'base', 'gui', 'plugins')),
         (os.path.join('sutekh', 'gui', 'plugins'),
             os.path.join('sutekh', 'gui', 'plugins')),
         # Include docs
         (os.path.join('sutekh', 'docs', 'html_docs'),
             os.path.join('sutekh', 'docs', 'html_docs')),
         # icons
         ('artwork', 'artwork'),
    ],
    'packages': ['gi', 'cairo'],
}


guibase = None
if sys.platform == "win32":
    guibase = "Win32GUI"
    # Copy in ssl certs from msys2 installation
    import ssl
    ssl_paths = ssl.get_default_verify_paths()
    build_exe_options['include_files'].append(
            (ssl_paths.openssl_cafile, os.path.join('etc', 'ssl', 'cert.pem')))
    build_exe_options['include_files'].append(
            (ssl_paths.openssl_capath, os.path.join('etc', 'ssl', 'certs')))
    build_exe_options['include_files'].append(
            (os.path.join('lib', 'librsvg-2.a'), os.path.join('lib', 'librsvg-2.a')))
    build_exe_options['include_files'].append(
            (os.path.join('lib', 'librsvg-2.dll.a'), os.path.join('lib', 'librsvg-2.dll.a')))


setup   (   # Metadata
            name = SutekhInfo.NAME,
            version = SutekhInfo.VERSION_STR,
            description = SutekhInfo.DESCRIPTION,
            long_description = open('README', 'r').read(),

            author = SutekhInfo.AUTHOR_NAME,
            author_email = SutekhInfo.AUTHOR_EMAIL,

            maintainer = SutekhInfo.MAINTAINER_NAME,
            maintainer_email = SutekhInfo.MAINTAINER_EMAIL,

            url = SutekhInfo.SOURCEFORGE_URL,
            download_url = SutekhInfo.PYPI_URL,

            license = SutekhInfo.LICENSE,

            classifiers = SutekhInfo.CLASSIFIERS,

            platforms = SutekhInfo.PLATFORMS,

            # Dependencies
            install_requires = SutekhInfo.INSTALL_REQUIRES,
            python_requires = '>=3',

            # Files
            packages = find_packages(exclude=['sutekh.tests.*',
                'sutekh.tests', 'sutekh.base.tests']),
            package_data = {
                #   catch-all empty package ''.
                # Include SVG and INI files from sutekh.gui package
                'sutekh.gui': ['*.svg', '*.ini'],
                # need baseconfigspec.ini from sutekh.base.gui
                'sutekh.base.gui': ['*.ini'],
                # Include LICENSE information for sutekh package
                # Include everything under the docs directory
                'sutekh': ['COPYING'],
                'sutekh.docs.html_docs': ['*'],
            },
            entry_points = {
                'console_scripts' : ['sutekh-cli = sutekh.SutekhCli:main'],
                'gui_scripts' : ['sutekh = sutekh.SutekhGui:main'],
            },
            options = {
                "build_exe": build_exe_options,
            },
            executables = [Executable("sutekh/SutekhGui.py", icon="artwork/sutekh-icon-inkscape.ico",
                                      base=guibase),
                           Executable("sutekh/SutekhCli.py", base=None)],
            data_files = [
                ('share/doc/python-sutekh', [
                    'COPYRIGHT',
                    'sutekh/COPYING',
                ]),
            ],
        )
