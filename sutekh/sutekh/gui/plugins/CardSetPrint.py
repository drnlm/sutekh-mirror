# CardSetPrint.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Plugin for simple, direct printing of the card set."""

import gtk
import pango
from sutekh.core.SutekhObjects import PhysicalCardSet, AbstractCardSet, \
        IAbstractCard, ICardType
from sutekh.gui.PluginManager import CardListPlugin
from sutekh.gui.SutekhDialog import do_complaint_error

try:
    # pylint: disable-msg=W0104
    # This is an existance check, so it does do nothing
    gtk.PrintOperation
except AttributeError:
    raise ImportError("GTK version does not contain PrintOperation."
            " Try PyGTK >= 2.10.")

class CardSetPrint(CardListPlugin):
    """Plugin for printing the card sets.

       Use gtk's Printing support to print out a simple list of the cards
       in the card set. This has less formatting than exporting via
       HTML, for instance, but does print directly.
       """
    dTableVersions = { AbstractCardSet: [2, 3],
                       PhysicalCardSet: [2, 3, 4]}
    aModelsSupported = [AbstractCardSet, PhysicalCardSet]

    # pylint: disable-msg=W0201
    # We don't care that we define _oSettings here, due to how plugin is called
    def get_menu_item(self):
        """Register on the 'Actions' Menu"""
        if not self.check_versions() or not self.check_model_type():
            return None

        # Keep print settings
        self._oSettings = None

        # internal state for printing
        self._aPageBreaks = None
        self._oPangoLayout = None

        oPrint = gtk.MenuItem("Print Card Set")
        oPrint.connect("activate", self.activate)
        return ('Actions', oPrint)

    # pylint: enable-msg=W0201

    # pylint: disable-msg=W0613
    # oWidget part of function signature
    def activate(self, oWidget):
        """In response to the menu choice, do the actual print operation."""
        oPrintOp = gtk.PrintOperation()

        if not self._oSettings is None:
            oPrintOp.set_print_settings(self._oSettings)

        oPrintOp.connect("begin-print", self.begin_print)
        oPrintOp.connect("end-print", self.end_print)
        oPrintOp.connect("draw-page", self.draw_page)

        oRes = oPrintOp.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG,
                self.parent)

        if oRes == gtk.PRINT_OPERATION_RESULT_ERROR:
            do_complaint_error("Error printing card set:\n")
        elif oRes == gtk.PRINT_OPERATION_RESULT_APPLY:
            self._oSettings = oPrintOp.get_print_settings()

    # pylint: enable-msg=W0613

    def begin_print(self, oPrintOp, oContext):
        """Set up printing context.

           This includes determining pagination and the number of pages.
           """
        oPrintOp.set_use_full_page(False)
        oPrintOp.set_unit(gtk.UNIT_MM)
        oPrintOp.set_n_pages(1) # safety net in case error occur later on

        fWidth, fHeight = oContext.get_width(), oContext.get_height()

        oLayout = oContext.create_pango_layout()
        oLayout.set_font_description(pango.FontDescription("sans 12"))
        oLayout.set_width(int(fWidth * pango.SCALE))

        oLayout.set_markup(self.cardlist_markup())

        iLineCount = oLayout.get_line_count()

        fPageHeight = 0
        aPageBreaks = []

        for iThisLine in range(iLineCount):
            oLine = oLayout.get_line(iThisLine)
            # pylint: disable-msg=W0612
            # not interested in oInkRect
            oInkRect, oLogicalRect = oLine.get_extents()

            # line height / SCALE
            fLineHeight = float(oLogicalRect[3]) / pango.SCALE

            if fPageHeight + fLineHeight > fHeight:
                aPageBreaks.append(iThisLine)
                fPageHeight = 0

            fPageHeight += fLineHeight

        oPrintOp.set_n_pages(len(aPageBreaks)+1)
        self._aPageBreaks = aPageBreaks
        self._oPangoLayout = oLayout

    # pylint: disable-msg=W0613
    # oPrintOp, oContext part of function signature
    def end_print(self, oPrintOp, oContext):
        """Clean up resources allocated in begin_print.
           """
        self._aPageBreaks = None
        self._oPangoLayout = None

    def draw_page(self, oPrintOp, oContext, iPageNum):
        """Page drawing callback.
           """
        # pylint: disable-msg=R0914
        # We use lots of variables for clarity
        iStartPageLine, iEndPageLine = 0, 0
        aPageBreaks = self._aPageBreaks
        oLayout = self._oPangoLayout

        if iPageNum > 0:
            iStartPageLine = aPageBreaks[iPageNum-1]

        if iPageNum < len(aPageBreaks):
            iEndPageLine = aPageBreaks[iPageNum]
        else:
            iEndPageLine = oLayout.get_line_count()

        oContext = oContext.get_cairo_context()
        oContext.set_source_rgb(0, 0, 0)
        oContext.set_line_width(0.1)

        oIter = oLayout.get_iter()

        fStartPos = 0.0
        iLine = 0

        while True:
            if iLine >= iStartPageLine:
                oLine = oIter.get_line()
                # pylint: disable-msg=W0612
                # not interested in oInkRect
                oInkRect, oLogicalRect = oLine.get_extents()

                fBaseLine = float(oIter.get_baseline()) / pango.SCALE

                if iLine == iStartPageLine:
                    fStartPos = fBaseLine

                # line x co-ordinate / SCALE
                fXPos = float(oLogicalRect[0]) / pango.SCALE
                # baseline - start pos - line y-co-ordinate / SCALE
                fYPos = fBaseLine - fStartPos - float(oLogicalRect[1]) / \
                        pango.SCALE

                oContext.move_to(fXPos, fYPos)
                oContext.layout_line_path(oLine)
                oContext.stroke_preserve()
                oContext.fill()

            iLine += 1
            if not (iLine < iEndPageLine and oIter.next_line()):
                break

    # pylint: enable-msg=W0613

    def cardlist_markup(self):
        """Format the card set nicely for printing."""
        def escape(sInput):
            """Escape strings so that markup and special characters
               don't break things."""
            from gobject import markup_escape_text
            if sInput:
                return markup_escape_text(sInput)
            else:
                return sInput # pass None straigh through

        oCS = self.get_card_set()
        aCrypt, aLibrary = self.get_cards(oCS)


        aMarkup = []
        aMarkup.append("<u>%s</u>" % escape(oCS.name))
        aMarkup.append("  Author: %s" % escape(oCS.author))
        aMarkup.append("  Comment: %s" % escape(oCS.comment))
        aMarkup.append("  Annotations: %s" % escape(oCS.annotations))
        aMarkup.append("")

        aMarkup.append("<u>Crypt:</u>")
        for oCard, iCnt in aCrypt:
            aMarkup.append("  %ix %s" % (iCnt, escape(oCard.name)))
        aMarkup.append("")

        aMarkup.append("<u>Library:</u>")
        for oCard, iCnt in aLibrary:
            aMarkup.append("  %ix %s" % (iCnt, escape(oCard.name)))

        return "\n".join(aMarkup)

    def get_cards(self, oCardSet):
        """Extract the cards from the card set, seperating them into
           crypt and library cards."""
        dCrypt = {}
        dLibrary = {}
        # pylint: disable-msg=E1101
        # PyProtocols + SQLObject confuses pylitn here
        aCryptTypes = set([ICardType("Vampire"), ICardType("Imbued")])

        for oCard in oCardSet.cards:
            oACard = IAbstractCard(oCard)
            if set(oACard.cardtype).intersection(aCryptTypes):
                dCrypt.setdefault(oACard.id, [oACard, 0])
                dCrypt[oACard.id][1] += 1
            else:
                dLibrary.setdefault(oACard.id, [oACard, 0])
                dLibrary[oACard.id][1] += 1

        # pylint: disable-msg=W0612
        # oId is a loop ariable and not of interest to us
        aCrypt = [(oCard, iCnt) for oId, (oCard, iCnt) in dCrypt.iteritems()]
        aCrypt.sort(key = lambda x: x[0].name)

        aLibrary = [(oCard, iCnt) for oId, (oCard, iCnt) in
                dLibrary.iteritems()]
        aLibrary.sort(key = lambda x: x[0].name)

        return aCrypt, aLibrary

# pylint: disable-msg=C0103
# accept plugin name
plugin = CardSetPrint
