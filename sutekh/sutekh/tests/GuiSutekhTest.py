# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2009 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Base for Sutekh test cases that use gtk windows"""

from sutekh.base.tests.TestUtils import GuiBaseTest
from sutekh.tests.TestCore import SutekhTest
import tempfile
import os
import gc
from sutekh.gui.SutekhMainWindow import SutekhMainWindow
from sutekh.gui.ConfigFile import ConfigFile


class ConfigSutekhTest(SutekhTest):
    """Base class for Sutekh tests that need a config file.

       Defines common startUp and tearDown routines."""
    # pylint: disable=C0103, R0904
    # C0103 - setUp + tearDown names are needed by unittest,
    #         so use their convention
    # R0904 - unittest.TestCase, so many public methods

    def setUp(self):
        """Setup config file for the tests"""
        super(ConfigSutekhTest, self).setUp()
        # Carry on with the test
        sConfigFile = self._create_tmp_file()
        self.oConfig = ConfigFile(sConfigFile)
        # basic validation
        self.oConfig.add_plugin_specs('CardImagePlugin', {})
        self.oConfig.add_plugin_specs('StarterInfoPlugin', {})
        self.oConfig.add_plugin_specs('TWDAInfoPlugin', {})
        self.oConfig.add_plugin_specs('RulebookPlugin', {})
        self.oConfig.validate()
        # Don't try and create a path in the user's home dir
        self.sPluginDir = tempfile.mkdtemp(suffix='dir', prefix='sutekhtests')
        # For new icon check
        os.makedirs(os.path.join(self.sPluginDir, 'clans'))
        self.oConfig.set_plugin_key('CardImagePlugin', 'card image path',
                                    self.sPluginDir)
        self.oConfig.set_plugin_key('CardImagePlugin', 'download images',
                                    False)
        self.oConfig.set_plugin_key('RulebookPlugin', 'rulebook path',
                                    self.sPluginDir)
        # Touch index file for rulebook plugin
        open(os.path.join(self.sPluginDir, 'index.txt'), 'w').close()
        self.oConfig.set_plugin_key('StarterInfoPlugin', 'show starters', 'No')
        self.oConfig.set_plugin_key('TWDAInfoPlugin', 'twda configured', 'No')
        self.oConfig.set_icon_path(self.sPluginDir)
        # Needed so validate doesn't remove our settings later
        self.oConfig.check_writeable()  # Make sure we do write the config file
        self.oConfig.write()

    def tearDown(self):
        """Tear down config file stuff after test run"""
        os.remove(os.path.join(self.sPluginDir, 'index.txt'))
        os.rmdir(os.path.join(self.sPluginDir, 'clans'))
        os.rmdir(self.sPluginDir)
        super(ConfigSutekhTest, self).tearDown()
        # FIXME: This helps the test suite, but I'm not sure why
        # This warrants further investigation at some point
        gc.collect()


class GuiSutekhTest(ConfigSutekhTest, GuiBaseTest):
    """Base class for Sutekh tests that use the main window.

       Define common setup and teardown routines common to gui test cases.
       """
    # pylint: disable=C0103, R0904
    # C0103 - setUp + tearDown names are needed by unittest,
    #         so use their convention
    # R0904 - unittest.TestCase, so many public methods

    def setUp(self):
        """Setup gtk window for the tests"""
        super(GuiSutekhTest, self).setUp()
        # Carry on with the test
        self.oWin = SutekhMainWindow()

    def tearDown(self):
        """Tear down gtk framework after test run"""
        self.oWin.destroy()
        super(GuiSutekhTest, self).tearDown()
