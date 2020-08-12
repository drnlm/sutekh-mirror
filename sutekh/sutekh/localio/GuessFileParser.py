# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# ELDB HTML Deck Parser
# Copyright 2009 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Attempt to gues the correct format from Sutekh's available parsers."""

from sutekh.base.localio.BaseGuessFileParser import BaseGuessFileParser

from sutekh.localio.AbstractCardSetParser import AbstractCardSetParser
from sutekh.localio.PhysicalCardSetParser import PhysicalCardSetParser
from sutekh.localio.PhysicalCardParser import PhysicalCardParser
from sutekh.localio.ARDBXMLDeckParser import ARDBXMLDeckParser
from sutekh.localio.ARDBXMLInvParser import ARDBXMLInvParser
from sutekh.localio.ARDBTextParser import ARDBTextParser
from sutekh.localio.JOLDeckParser import JOLDeckParser
from sutekh.localio.ELDBInventoryParser import ELDBInventoryParser
from sutekh.localio.ELDBDeckFileParser import ELDBDeckFileParser
from sutekh.localio.ELDBHTMLParser import ELDBHTMLParser
from sutekh.localio.LackeyDeckParser import LackeyDeckParser
from sutekh.localio.SLDeckParser import SLDeckParser
from sutekh.localio.SLInventoryParser import SLInventoryParser


class GuessFileParser(BaseGuessFileParser):
    """Parser which guesses the file type"""

    PARSERS = [
        PhysicalCardSetParser,
        AbstractCardSetParser,
        PhysicalCardParser,
        ARDBXMLDeckParser,
        ARDBXMLInvParser,
        ARDBTextParser,
        ELDBInventoryParser,
        ELDBDeckFileParser,
        ELDBHTMLParser,
        SLDeckParser,
        SLInventoryParser,
        LackeyDeckParser,
        # JOL is the most permissive, so must be last
        JOLDeckParser,
    ]
