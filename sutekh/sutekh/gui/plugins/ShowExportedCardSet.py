# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2011 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Plugin for displaying the exported version of a card set in a gtk.TextView.
   Intended to make cutting and pasting easier."""

from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.base.gui.plugins.BaseShowExported import BaseShowExported
from sutekh.localio.WriteJOL import WriteJOL
from sutekh.localio.WriteLackeyCCG import WriteLackeyCCG
from sutekh.localio.WriteELDBDeckFile import WriteELDBDeckFile
from sutekh.localio.WriteArdbText import WriteArdbText
from sutekh.localio.WritePmwiki import WritePmwiki
from sutekh.localio.WriteVEKNForum import WriteVEKNForum
from sutekh.localio.WriteSLDeck import WriteSLDeck


class ShowExported(SutekhPlugin, BaseShowExported):
    """Display the various exported versions of a card set."""

    EXPORTERS = BaseShowExported.EXPORTERS.copy()
    EXPORTERS.update({
        'Export to JOL format': WriteJOL,
        'Export to Lackey CCG format': WriteLackeyCCG,
        'Export to ARDB Text': WriteArdbText,
        'BBcode output for the V:EKN Forums': WriteVEKNForum,
        'Export to ELDB ELD Deck File': WriteELDBDeckFile,
        'Export to pmwiki': WritePmwiki,
        'Export for SL import form': WriteSLDeck,
    })


plugin = ShowExported
