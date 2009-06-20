# test_WriteCSV.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Test Writing a card set to an CSV file"""

from sutekh.tests.TestCore import SutekhTest
from sutekh.tests.core.test_PhysicalCardSet import CARD_SET_NAMES, \
        get_phys_cards
from sutekh.core.SutekhObjects import PhysicalCardSet
from sutekh.io.WriteCSV import  WriteCSV
import unittest

EXPECTED_1 = """"Card Name", "Expansion", "Number"
".44 Magnum", "Jyhad", 1
".44 Magnum", "Unknown Expansion", 3
"AK-47", "Lords of the Night", 1
"AK-47", "Unknown Expansion", 1
"Abbot", "Third Edition", 1
"Abbot", "Unknown Expansion", 1
"Abebe", "Unknown Expansion", 1
"Abombwe", "Legacy of Blood", 1
"Abombwe", "Unknown Expansion", 1
"Alan Sovereign (Advanced)", "Promo-20051001", 1
"The Path of Blood", "Lords of the Night", 1
"""

EXPECTED_2 = """".44 Magnum", "Jyhad", 1
".44 Magnum", "Unknown Expansion", 3
"AK-47", "Lords of the Night", 1
"AK-47", "Unknown Expansion", 1
"Abbot", "Third Edition", 1
"Abbot", "Unknown Expansion", 1
"Abebe", "Unknown Expansion", 1
"Abombwe", "Legacy of Blood", 1
"Abombwe", "Unknown Expansion", 1
"Alan Sovereign (Advanced)", "Promo-20051001", 1
"The Path of Blood", "Lords of the Night", 1
"""


EXPECTED_3 = """"Card Name", "Number"
".44 Magnum", 4
"AK-47", 2
"Abbot", 2
"Abebe", 1
"Abombwe", 2
"Alan Sovereign (Advanced)", 1
"The Path of Blood", 1
"""

EXPECTED_4 = """".44 Magnum", 4
"AK-47", 2
"Abbot", 2
"Abebe", 1
"Abombwe", 2
"Alan Sovereign (Advanced)", 1
"The Path of Blood", 1
"""


class CSVWriterTests(SutekhTest):
    """class for the CSV deck writer tests"""

    def test_deck_writer(self):
        """Test HTML deck writing"""
        # pylint: disable-msg=E1101, R0915, R0914
        # E1101: SQLObject + PyProtocols magic confuses pylint
        # R0915, R0914: Want a long, sequential test case to minimise
        # repeated setups, so it has lots of lines + variables
        aAddedPhysCards = get_phys_cards()
        # We have a physical card list, so create some physical card sets
        oPhysCardSet1 = PhysicalCardSet(name=CARD_SET_NAMES[0])
        oPhysCardSet1.comment = 'A test comment'
        oPhysCardSet1.author = 'A test author'

        for oCard in aAddedPhysCards:
            oPhysCardSet1.addPhysicalCard(oCard.id)
            oPhysCardSet1.syncUpdate()
        oPhysCardSet1.addPhysicalCard(aAddedPhysCards[0])
        oPhysCardSet1.addPhysicalCard(aAddedPhysCards[0])
        oPhysCardSet1.syncUpdate()

        # Check output

        oWriter = WriteCSV(True, True)
        sData = self._round_trip_obj(oWriter, oPhysCardSet1)

        self.assertEqual(sData, EXPECTED_1)

        oWriter = WriteCSV(False, True)
        sData = self._round_trip_obj(oWriter, oPhysCardSet1)

        self.assertEqual(sData, EXPECTED_2)

        oWriter = WriteCSV(True, False)
        sData = self._round_trip_obj(oWriter, oPhysCardSet1)

        self.assertEqual(sData, EXPECTED_3)

        oWriter = WriteCSV(False, False)
        sData = self._round_trip_obj(oWriter, oPhysCardSet1)

        self.assertEqual(sData, EXPECTED_4)


if __name__ == "__main__":
    unittest.main()
