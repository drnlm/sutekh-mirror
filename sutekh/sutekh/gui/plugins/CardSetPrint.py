# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Sutekh wrapper for print plugin."""

from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.base.gui.plugins.BasePrint import BasePrint


class CardSetPrint(BasePrint, SutekhPlugin):
    """Plugin for printing the card sets."""


plugin = CardSetPrint
