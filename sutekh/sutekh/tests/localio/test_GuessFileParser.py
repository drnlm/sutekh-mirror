# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2009 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Test guessing the file format"""

import unittest
from sutekh.tests.TestCore import SutekhTest
from sutekh.localio.GuessFileParser import GuessFileParser
from sutekh.localio.AbstractCardSetParser import AbstractCardSetParser
from sutekh.localio.PhysicalCardSetParser import PhysicalCardSetParser
from sutekh.localio.ARDBXMLDeckParser import ARDBXMLDeckParser
from sutekh.localio.ARDBXMLInvParser import ARDBXMLInvParser
from sutekh.localio.ARDBTextParser import ARDBTextParser
from sutekh.localio.JOLDeckParser import JOLDeckParser
from sutekh.localio.ELDBInventoryParser import ELDBInventoryParser
from sutekh.localio.ELDBDeckFileParser import ELDBDeckFileParser
from sutekh.localio.ELDBHTMLParser import ELDBHTMLParser
from sutekh.localio.LackeyDeckParser import LackeyDeckParser
from sutekh.tests.localio.test_JOLDeckParser import JOL_EXAMPLE_1
from sutekh.tests.localio.test_ARDBTextParser import ARDB_TEXT_EXAMPLE_1
from sutekh.tests.localio.test_ARDBXMLDeckParser import ARDB_DECK_EXAMPLE_1
from sutekh.tests.localio.test_ARDBXMLInvParser import ARDB_INV_EXAMPLE_1
from sutekh.tests.localio.test_ELDBHTMLParser import ELDB_HTML_EXAMPLE_1
from sutekh.tests.localio.test_ELDBInventoryParser import ELDB_INV_EXAMPLE_1
from sutekh.tests.localio.test_ELDBDeckFileParser import ELDB_TEXT_EXAMPLE_1
from sutekh.tests.localio.test_LackeyDeckParser import LACKEY_EXAMPLE_1
from sutekh.tests.localio.test_AbstractCardSetParser import ACS_EXAMPLE_1
from sutekh.tests.localio.test_PhysicalCardSetParser import PCS_EXAMPLE_1


class TestGuessFileParser(SutekhTest):
    """class for the guess file parser tests"""
    # pylint: disable=too-many-public-methods
    # unittest.TestCase, so many public methods

    TESTS = [
        (AbstractCardSetParser, ACS_EXAMPLE_1),
        (PhysicalCardSetParser, PCS_EXAMPLE_1),
        (ARDBXMLDeckParser, ARDB_DECK_EXAMPLE_1),
        (ARDBXMLInvParser, ARDB_INV_EXAMPLE_1),
        (ARDBTextParser, ARDB_TEXT_EXAMPLE_1),
        (JOLDeckParser, JOL_EXAMPLE_1),
        (ELDBInventoryParser, ELDB_INV_EXAMPLE_1),
        (ELDBDeckFileParser, ELDB_TEXT_EXAMPLE_1),
        (ELDBHTMLParser, ELDB_HTML_EXAMPLE_1),
        (LackeyDeckParser, LACKEY_EXAMPLE_1),
    ]

    def test_guess(self):
        """test guess against the correct parser."""
        oGuessParser = GuessFileParser()
        for cCorrectParser, sData in self.TESTS:
            oHolder1 = self._make_holder_from_string(oGuessParser, sData)
            oHolder2 = self._make_holder_from_string(cCorrectParser(),
                                                     sData)

            self.assertEqual(oHolder1.name, oHolder2.name,
                             "Holder names don't match:"
                             " %s vs %s, using %s, correct choice %s" % (
                                 oHolder1.name, oHolder2.name,
                                 oGuessParser.oChosenParser, cCorrectParser))
            self.assertEqual(oHolder1.get_cards(), oHolder2.get_cards(),
                             "Guess cards don't match:"
                             " %s vs %s, using %s, correct %s" % (
                                 oHolder1.get_cards(), oHolder2.get_cards(),
                                 oGuessParser.oChosenParser, cCorrectParser))


if __name__ == "__main__":
    unittest.main()
