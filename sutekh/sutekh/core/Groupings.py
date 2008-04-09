# Groupings.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Provide classes to change the way cards are grouped in the display"""

# Base Grouping Class

class IterGrouping(object):
    """Bass class for the groupings"""
    def __init__(self, oIter, fKeys):
        """
        oIter: Iterable to group.
        fKeys: Function which maps an item from the iterable
               to a list of keys. Keys must be hashable.
        """
        self.__oIter = oIter
        self.__fKeys = fKeys

    def __iter__(self):
        dKeyItem = {}
        for oItem in self.__oIter:
            aSet = set(self.__fKeys(oItem))
            if len(aSet) == 0:
                dKeyItem.setdefault(None, []).append(oItem)
            else:
                for oKey in aSet:
                    dKeyItem.setdefault(oKey, []).append(oItem)

        aList = dKeyItem.keys()
        aList.sort()

        for oKey in aList:
            yield oKey, dKeyItem[oKey]

# Individual Groupings
#
# If you need to group PhysicalCards,
# set fGetCard to lambda x: x.abstractCard

# pylint: disable-msg=E0602
# pylint is confused by the lambda x: x construction
fDefGetCard = lambda x: x
# pylint: enable-msg=E0602

# pylint: disable-msg=C0111
# class names are pretty self-evident, so skip docstrings
class CardTypeGrouping(IterGrouping):
    def __init__(self, oIter, fGetCard=fDefGetCard):
        super(CardTypeGrouping, self).__init__(oIter,
                lambda x: [y.name for y in fGetCard(x).cardtype])

class ClanGrouping(IterGrouping):
    def __init__(self, oIter, fGetCard=fDefGetCard):
        super(ClanGrouping, self).__init__(oIter,
                lambda x: [y.name for y in fGetCard(x).clan])

class DisciplineGrouping(IterGrouping):
    def __init__(self, oIter, fGetCard=fDefGetCard):
        super(DisciplineGrouping, self).__init__(oIter,
                lambda x: [y.discipline.fullname for y in
                    fGetCard(x).discipline])

class ExpansionGrouping(IterGrouping):
    def __init__(self, oIter, fGetCard=fDefGetCard):
        super(ExpansionGrouping, self).__init__(oIter,
                lambda x: [y.expansion.name for y in fGetCard(x).rarity])

class RarityGrouping(IterGrouping):
    def __init__(self, oIter, fGetCard=fDefGetCard):
        super(RarityGrouping, self).__init__(oIter,
                lambda x: [y.rarity.name for y in fGetCard(x).rarity])

class CryptLibraryGrouping(IterGrouping):
    def __init__(self, oIter, fGetCard=fDefGetCard):
        # Vampires and Imbued have exactly one card type (we hope that WW
        # don't change that)
        super(CryptLibraryGrouping, self).__init__(oIter,
                lambda x: [fGetCard(x).cardtype[0].name in ["Vampire",
                    "Imbued"] and "Crypt" or "Library"])

class NullGrouping(IterGrouping):
    # pylint: disable-msg=W0613
    # fGetCard is required by function signature
    def __init__(self, oIter, fGetCard=fDefGetCard):
        super(NullGrouping, self).__init__(oIter, lambda x: ["All"])
