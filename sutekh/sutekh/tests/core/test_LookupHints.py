# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Test cases for the CardSetUtilities functions"""

from sutekh.tests.TestCore import SutekhTest
from sutekh.base.core.BaseAdapters import IAbstractCard


class LookupTests(SutekhTest):
    """class for various lookup tests"""
    # pylint: disable=R0904
    # R0904 - unittest.TestCase, so many public methods

    def test_basic(self):
        """Test behaviour"""
        oCard = IAbstractCard("Pier 13, Port of Baltimore")
        self.assertEqual(oCard, IAbstractCard("Pier 13"))

        oCard = IAbstractCard("Anastasz di Zagreb")
        self.assertEqual(oCard, IAbstractCard("Anastaszdi Zagreb"))

        oCard = IAbstractCard("The Path of Blood")
        # Article shifting
        self.assertEqual(oCard, IAbstractCard("Path of Blood, The"))

        # Odd cases
        self.assertEqual(oCard, IAbstractCard("THE PATH OF bLOOD"))
        self.assertEqual(oCard, IAbstractCard("the paTH oF bLOOD"))
