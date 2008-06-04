# GuiCardLookup.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""
Lookup AbstractCards for a list of card names, presenting the user with a GUI
to pick unknown cards from.
"""

import re
import gtk
import pango
import gobject
from sqlobject import SQLObjectNotFound
from sutekh.core.SutekhObjects import AbstractCard, PhysicalCard, IExpansion, \
        Expansion, IPhysicalCard
from sutekh.core.CardLookup import AbstractCardLookup, PhysicalCardLookup, \
        ExpansionLookup, LookupFailed
from sutekh.core.Filters import CardNameFilter
from sutekh.gui.SutekhDialog import SutekhDialog, do_complaint_error
from sutekh.gui.CellRendererSutekhButton import CellRendererSutekhButton
from sutekh.gui.PhysicalCardView import PhysicalCardView
from sutekh.gui.AutoScrolledWindow import AutoScrolledWindow

class DummyController(object):
    """Dummy controller class, so we can use the card views directly"""
    def __init__(self, sFilterType):
        self.sFilterType = sFilterType

    filtertype = property(fget=lambda self: self.sFilterType)

    def set_card_text(self, sCardName):
        """Ignore card text updates."""
        pass

class ACLLookupView(PhysicalCardView):
    """Specialised version for the Card Lookup."""
    # pylint: disable-msg=R0904
    # gtk.Widget, so many public methods.

    def __init__(self, oDialogWindow, oConfig):
        oController = DummyController('PhysicalCard')
        super(ACLLookupView, self).__init__(oController, oDialogWindow,
                oConfig)
        self.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self._oModel.bExpansions = False

    def get_selected_card(self):
        """Return the selected card with a dummy expansion of ''."""
        sNewName = 'No Card'
        oModel, aSelection = self.get_selection().get_selected_rows()
        for oPath in aSelection:
            # pylint: disable-msg=W0612
            # only interested in sNewName and sExpansion
            sNewName, sExpansion, iCount, iDepth = \
                oModel.get_all_from_path(oPath)
        return sNewName, ''

class PCLLookupView(PhysicalCardView):
    """Also show current allocation of cards in the physical card view."""
    # pylint: disable-msg=R0904
    # gtk.Widget, so many public methods.

    def __init__(self, oDialogWindow, oConfig):
        oController = DummyController('PhysicalCard')
        super(PCLLookupView, self).__init__(oController, oDialogWindow,
                oConfig)
        self.get_selection().set_mode(gtk.SELECTION_SINGLE)

    def get_selected_card(self):
        """Return the selected card and expansion."""
        sNewName = 'No Card'
        sExpansion = '  Unpecified Expansion'
        oModel, aSelection = self.get_selection().get_selected_rows()
        for oPath in aSelection:
            # pylint: disable-msg=W0612
            # only interested in sNewName and sExpansion
            sNewName, sExpansion, iCount, iDepth = \
                oModel.get_all_from_path(oPath)
        if sExpansion is None:
            sExpansion = ''
        return sNewName, sExpansion

class ReplacementTreeView(gtk.TreeView):
    """A TreeView which tracks the current set of replacement cards."""
    # pylint: disable-msg=R0904
    # gtk.Widget, so many public methods.

    def __init__(self, oCardListView, oFilterToggleButton):
        """Construct a gtk.TreeView object showing the current
           card replacements.

           For abstract cards, the card names are stored as is.
           For physical cards, the card names have " [<expansion>]"
           appended.
           """
        # ListStore: count, missing card, replacement
        oModel = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING,
                               gobject.TYPE_STRING)

        super(ReplacementTreeView, self).__init__(oModel)
        self.oCardListView = oCardListView
        self.oModel = oModel
        self.oFilterToggleButton = oFilterToggleButton

        self._create_text_column('Missing Card', 1)
        self._create_text_column('Replace Card', 2)

        self._create_button_column(gtk.STOCK_OK, 'Set',
                'Use the selected card',
                self._set_to_selection) # use selected card
        self._create_button_column(gtk.STOCK_REMOVE, 'Ignore',
                'Ignore the current card',
                self._set_ignore) # ignore current card
        self._create_button_column(gtk.STOCK_FIND, 'Filter',
                'Filter on best guess',
                self._set_filter) # filter out best guesses

    # utility methods to simplify column creation
    def _create_button_column(self, oIcon, sLabel, sToolTip, fClicked):
        """Create a column with a button, usin oIcon and the function
           fClicked."""
        oCell = CellRendererSutekhButton(bShowIcon=True)
        oCell.load_icon(oIcon, self)
        oLabel = gtk.Label(sLabel)
        if hasattr(oLabel,'set_tooltip_text'):
            # GTK < 2.12 doesn't have the new tooltip API
            oLabel.set_tooltip_text(sToolTip)
        oColumn = gtk.TreeViewColumn("", oCell)
        oColumn.set_widget(oLabel)
        oColumn.set_fixed_width(22)
        oColumn.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.append_column(oColumn)
        oCell.connect('clicked', fClicked)

    def _create_text_column(self, sLabel, iColumn):
        """Create a text column, using iColumn from the model"""
        oCell = gtk.CellRendererText()
        oCell.set_property('style', pango.STYLE_ITALIC)
        oColumn = gtk.TreeViewColumn(sLabel, oCell, text=iColumn)
        oColumn.set_expand(True)
        oColumn.set_sort_column_id(iColumn)
        self.append_column(oColumn)

    # pylint: disable-msg=W0613
    # argument lists determined by callback signature

    def _set_to_selection(self, oCell, oPath):
        """Set the replacement card to the selected entry"""

        # We handle PhysicalCards on a like-for-like matching case.
        # For cases where the user selects an expansion with too few
        # cards, but where there are enough phyiscal cards, we do the
        # best we can

        oIter = self.oModel.get_iter(oPath)

        sNewName, sExpansion = self.oCardListView.get_selected_card()
        if sNewName == 'No Card':
            do_complaint_error("Please select a card")
            return

        if sExpansion != '':
            sReplaceWith = sNewName + " [%s]" % (sExpansion,)
        else:
            sReplaceWith = sNewName

        self.oModel.set_value(oIter, 2, sReplaceWith)

    def _set_ignore(self, oCell, oPath):
        """Mark the card as not having a replacement."""
        oIter = self.oModel.get_iter(oPath)
        self.oModel.set_value(oIter, 2, "No Card")

    def _set_filter(self, oCell, oPath):
        """Set the card list filter to the best guess filter for this card."""
        oIter = self.oModel.get_iter(oPath)
        sFullName = self.oModel.get_value(oIter, 1)
        # pylint: disable-msg=W0612
        # we ignore sExp here
        sName, sExp = self.parse_card_name(sFullName)

        oFilter = self.best_guess_filter(sName)
        self.oCardListView.get_model().selectfilter = oFilter

        if not self.oFilterToggleButton.get_active():
            self.oFilterToggleButton.set_active(True)
        else:
            self.oCardListView.load()

    def run_filter_dialog(self, oButton):
        """Display the filter dialog and apply results."""
        self.oCardListView.get_filter(None)
        self.oFilterToggleButton.set_active(
            self.oCardListView.get_model().applyfilter)

    def toggle_apply_filter(self, oButton):
        """Toggle whether the filter is applied."""
        self.oCardListView.get_model().applyfilter = \
            self.oFilterToggleButton.get_active()
        self.oCardListView.load()

    # pylint: enable-msg=W0613

    NAME_RE = re.compile(r"^(?P<name>.*?)( \[(?P<exp>[^]]+)\])?$")

    @classmethod
    def parse_card_name(cls, sName):
        """Parser the card name and expansion out of the string."""
        oMatch = cls.NAME_RE.match(sName)
        assert oMatch is not None
        return oMatch.group('name'), oMatch.group('exp')

    @staticmethod
    def best_guess_filter(sName):
        """Create a filter for selecting close matches to a card name."""
        # Set the filter on the Card List to one the does a
        # Best guess search
        sFilterString = ' ' + sName.lower() + ' '
        # Kill the's in the string
        sFilterString = sFilterString.replace(' the ', '')
        # Kill commas, as possible issues
        sFilterString = sFilterString.replace(',', '')
        # Wildcard spaces
        sFilterString = sFilterString.replace(' ', '%').lower()
        # Stolen semi-concept from soundex - replace vowels with wildcards
        # Should these be %'s ??
        # (Should at least handle the Rotscheck variation as it stands)
        sFilterString = sFilterString.replace('a', '_')
        sFilterString = sFilterString.replace('e', '_')
        sFilterString = sFilterString.replace('i', '_')
        sFilterString = sFilterString.replace('o', '_')
        sFilterString = sFilterString.replace('u', '_')
        return CardNameFilter(sFilterString)


class GuiLookup(AbstractCardLookup, PhysicalCardLookup, ExpansionLookup):
    """Lookup AbstractCards. Use the user as the AI if a simple lookup fails.
    """

    def __init__(self, oConfig):
        super(GuiLookup, self).__init__()
        self._oConfig = oConfig

    def lookup(self, aNames, sInfo):
        """Lookup missing abstract cards.

           Provides an implementation for AbstractCardLookup.
        """
        dCards = {}
        dUnknownCards = {}

        for sName in aNames:
            if not sName:
                # None here is an explicit ignore from the lookup cache
                dCards[sName] = None
            else:
                try:
                    # pylint: disable-msg=E1101
                    # SQLObject methods confuse pylint
                    oAbs = AbstractCard.byCanonicalName(
                                sName.encode('utf8').lower())
                    # pylint: enable-msg=E1101
                    dCards[sName] = oAbs
                except SQLObjectNotFound:
                    dUnknownCards[sName] = None

        if dUnknownCards:
            if not self._handle_unknown_abstract_cards(dUnknownCards, sInfo):
                raise LookupFailed("Lookup of missing cards aborted by the" \
                                   " user.")

        for sName, sNewName in dUnknownCards.items():
            if sNewName is None:
                continue
            try:
                # pylint: disable-msg=E1101
                # SQLObject methods confuse pylint
                oAbs = AbstractCard.byCanonicalName(
                                        sNewName.encode('utf8').lower())
                # pylint: enable-msg=E1101
                dUnknownCards[sName] = oAbs
            except SQLObjectNotFound:
                raise RuntimeError("Unexpectedly encountered missing" \
                                   " abstract card '%s'." % sNewName)

        def new_card(sName):
            """emulate python 2.5's a = x if C else y"""
            if sName in dCards:
                return dCards[sName]
            else:
                return dUnknownCards[sName]

        return [new_card(sName) for sName in aNames]

    def physical_lookup(self, dCardExpansions, dNameCards, dNameExps, sInfo):
        """Lookup missing physical cards.

           Provides an implementation for PhysicalCardLookup.
        """
        aCards = []
        dUnknownCards = {}

        for sName in dCardExpansions:
            oAbs = dNameCards[sName]
            if oAbs is None:
                continue
            try:
                for sExpansionName in dCardExpansions[sName]:
                    iCnt = dCardExpansions[sName][sExpansionName]
                    oExpansion = dNameExps[sExpansionName]
                    aCards.extend([IPhysicalCard((oAbs, oExpansion))]*iCnt)
            except SQLObjectNotFound:
                for sExpansionName in dCardExpansions[sName]:
                    iCnt = dCardExpansions[sName][sExpansionName]
                    if iCnt > 0:
                        dUnknownCards[(oAbs.name, sExpansionName)] = iCnt

        if dUnknownCards:
            # We need to lookup cards in the physical card view
            if not self._handle_unknown_physical_cards(dUnknownCards,
                                                       aCards, sInfo):
                raise LookupFailed("Lookup of missing cards aborted by the" \
                                   " user.")

        return aCards

    def expansion_lookup(self, aExpansionNames, sInfo):
        """Lookup missing expansions.

           Provides an implementation for ExpansionLookup.
        """
        dExps = {}
        dUnknownExps = {}

        for sExp in aExpansionNames:
            if not sExp:
                dExps[sExp] = None
            else:
                try:
                    oExp = IExpansion(sExp)
                    dExps[sExp] = oExp
                except KeyError:
                    dUnknownExps[sExp] = None

        if dUnknownExps:
            if not self._handle_unknown_expansions(dUnknownExps, sInfo):
                raise LookupFailed("Lookup of missing expansions aborted by" \
                                   " the user.")

        for sName, sNewName in dUnknownExps.items():
            if sNewName is None:
                continue
            try:
                oExp = IExpansion(sNewName)
                dUnknownExps[sName] = oExp
            except KeyError:
                raise RuntimeError("Unexpectedly encountered" \
                                   " missing expansion '%s'." % sNewName)

        def new_exp(sName):
            """emulate python 2.5's a = x if C else y"""
            if sName in dExps:
                return dExps[sName]
            else:
                return dUnknownExps[sName]

        return [new_exp(sName) for sName in aExpansionNames]

    def _handle_unknown_physical_cards(self, dUnknownCards, aPhysCards, sInfo):
        """Handle unknwon physical cards

           We allow the user to select the correct replacements from the
           Physical Card List
        """

        oUnknownDialog = SutekhDialog( \
                "Unknown Physical cards found importing %s" % sInfo, None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_OK,
                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        sMsg1 = "While importing %s\n" \
          "The following cards could not be found in the Physical Card List:" \
          "\nChoose how to handle these cards?\n" % sInfo

        sMsg2 = "OK creates the card set, " \
          "Cancel aborts the creation of the card set"

        # pylint: disable-msg=E1101
        # vbox confuses pylint

        oMesgLabel1 = gtk.Label()
        oMesgLabel1.set_text(sMsg1)
        oUnknownDialog.vbox.pack_start(oMesgLabel1, False, False)

        oHBox = gtk.HBox()
        oUnknownDialog.vbox.pack_start(oHBox, True, True)

        oMesgLabel2 = gtk.Label()
        oMesgLabel2.set_text(sMsg2)
        oUnknownDialog.vbox.pack_start(oMesgLabel2)

        oPhysCardView = PCLLookupView(oUnknownDialog, self._oConfig)
        oViewWin = AutoScrolledWindow(oPhysCardView)
        oViewWin.set_size_request(200, 600)
        oHBox.pack_start(oViewWin, True, True)

        oVBox = gtk.VBox()
        oHBox.pack_start(oVBox)

        oFilterDialogButton = gtk.Button("Specify Filter")
        oFilterApplyButton = gtk.CheckButton("Apply Filter to view")

        oReplacementView = ReplacementTreeView(oPhysCardView,
                                               oFilterApplyButton)
        oModel = oReplacementView.get_model()

        oReplacementWin = AutoScrolledWindow(oReplacementView)
        oReplacementWin.set_size_request(400, 600)
        oVBox.pack_start(oReplacementWin, True, True)

        oFilterButtons = gtk.HBox()
        oVBox.pack_start(gtk.HSeparator())
        oVBox.pack_start(oFilterButtons)

        oFilterButtons.pack_start(oFilterDialogButton)
        oFilterButtons.pack_start(oFilterApplyButton)

        oFilterDialogButton.connect("clicked",
            oReplacementView.run_filter_dialog)
        oFilterApplyButton.connect("toggled",
            oReplacementView.toggle_apply_filter)

        # Populate the model with the card names and best guesses
        for (sName, sExpName), iCnt in dUnknownCards.items():
            sBestGuess = "No Card"
            sFullName = "%s [%s]" % (sName, sExpName)

            oIter = oModel.append(None)
            oModel.set(oIter, 0, iCnt, 1, sFullName, 2, sBestGuess)

        oUnknownDialog.vbox.show_all()
        oPhysCardView.load()

        iResponse = oUnknownDialog.run()
        oUnknownDialog.destroy()

        if iResponse == gtk.RESPONSE_OK:
            # For cards marked as replaced, add them to the list of
            # Physical Cards
            oIter = oModel.get_iter_root()
            while not oIter is None:
                sFullName, sNewFullName = oModel.get(oIter, 1, 2)
                sName, sExpName = oReplacementView.parse_card_name(sFullName)

                sNewName, sNewExpName = \
                    oReplacementView.parse_card_name(sNewFullName)

                if sNewExpName is not None:
                    try:
                        iExpID = IExpansion(sNewExpName).id
                    except SQLObjectNotFound:
                        iExpID = None
                    except KeyError:
                        iExpID = None
                else:
                    iExpID = None

                iCnt = dUnknownCards[(sName, sExpName)]

                if sNewName != "No Card":
                    # Find First physical card that matches this name
                    # that's not in aPhysCards
                    oAbs = AbstractCard.byCanonicalName(
                                sNewName.encode('utf8').lower())
                    oPhys = PhysicalCard.selectBy(abstractCardID=oAbs.id,
                                expansionID=iExpID).getOne()
                    aPhysCards.extend([oPhys]*iCnt)

                oIter = oModel.iter_next(oIter)
            return True
        else:
            return False

    def _handle_unknown_abstract_cards(self, dUnknownCards, sInfo):
        """Handle the list of unknown abstract cards.

           We allow the user to select the correct replacements from the
           Abstract Card List.
           """
        oUnknownDialog = SutekhDialog( \
                "Unknown cards found importing %s" % sInfo, None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_OK,
                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        sMsg1 = "While importing %s\n" \
                "The following card names could not be found:\n" \
                "Choose how to handle these cards?\n" % (sInfo)

        sMsg2 = "OK creates the card set, " \
                "Cancel aborts the creation of the card set"

        # pylint: disable-msg=E1101
        # vbox confuses pylint

        oMesgLabel1 = gtk.Label()
        oMesgLabel1.set_text(sMsg1)
        oUnknownDialog.vbox.pack_start(oMesgLabel1, False, False)

        oHBox = gtk.HBox()
        oUnknownDialog.vbox.pack_start(oHBox, True, True)

        oMesgLabel2 = gtk.Label()
        oMesgLabel2.set_text(sMsg2)
        oUnknownDialog.vbox.pack_start(oMesgLabel2)

        oAbsCardView = ACLLookupView(oUnknownDialog, self._oConfig)
        oViewWin = AutoScrolledWindow(oAbsCardView)
        oViewWin.set_size_request(200, 600)
        oHBox.pack_start(oViewWin, True, True)

        oVBox = gtk.VBox()
        oHBox.pack_start(oVBox)

        oFilterDialogButton = gtk.Button("Specify Filter")
        oFilterApplyButton = gtk.CheckButton("Apply Filter to view")

        oReplacementView = ReplacementTreeView(oAbsCardView,
            oFilterApplyButton)
        oModel = oReplacementView.get_model()

        oReplacementWin = AutoScrolledWindow(oReplacementView)
        oReplacementWin.set_size_request(400, 600)
        oVBox.pack_start(oReplacementWin, True, True)

        oFilterButtons = gtk.HBox()
        oVBox.pack_start(gtk.HSeparator())
        oVBox.pack_start(oFilterButtons)

        oFilterButtons.pack_start(oFilterDialogButton)
        oFilterButtons.pack_start(oFilterApplyButton)

        oFilterDialogButton.connect("clicked",
            oReplacementView.run_filter_dialog)
        oFilterApplyButton.connect("toggled",
            oReplacementView.toggle_apply_filter)

        # Populate the model with the card names and best guesses
        for sName in dUnknownCards:
            oBestGuessFilter = oReplacementView.best_guess_filter(sName)
            aCards = list(oBestGuessFilter.select(PhysicalCard).distinct())
            if len(aCards) == 1:
                sBestGuess = aCards[0].name
            else:
                sBestGuess = "No Card"

            oIter = oModel.append(None)
            # second 1 is the dummy card count
            oModel.set(oIter, 0, 1, 1, sName, 2, sBestGuess)

        oUnknownDialog.vbox.show_all()
        oAbsCardView.load()

        iResponse = oUnknownDialog.run()
        oUnknownDialog.destroy()

        if iResponse == gtk.RESPONSE_OK:
            # For cards marked as replaced, add them to the Holder
            oIter = oModel.get_iter_root()
            while not oIter is None:
                sName, sNewName = oModel.get(oIter, 1, 2)
                if sNewName != "No Card":
                    dUnknownCards[sName] = sNewName
                oIter = oModel.iter_next(oIter)
            return True
        else:
            return False

    @staticmethod
    def _handle_unknown_expansions(dUnknownExps, sInfo):
        """Handle the list of unknown expansions.

           We allow the user to select the correct replacements from the
           expansions listed in the database.
           """
        oUnknownDialog = SutekhDialog(
            "Unknown expansions found importing %s" % sInfo, None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_OK, gtk.RESPONSE_OK,
             gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        aKnownExpansions = list(Expansion.select())

        oMesgLabel1 = gtk.Label()
        oMesgLabel2 = gtk.Label()

        sMsg1 = "While importing %s\n" \
                "The following expansions could not be found:\n" \
                "Choose how to handle these expansions?\n" % (sInfo)
        sMsg2 = "OK continues the card set creation process, " \
                "Cancel aborts the creation of the card set"

        # pylint: disable-msg=E1101
        # vbox confuses pylint

        oMesgLabel1.set_text(sMsg1)
        oUnknownDialog.vbox.pack_start(oMesgLabel1, False, False)

        oButtonBox = gtk.VBox()

        # Fill in the Expansions and options
        dReplacement = {}
        for sName in dUnknownExps:
            oBox = gtk.HBox()
            oLabel = gtk.Label("%s is Unknown: Replace with " % sName)
            oBox.pack_start(oLabel)

            oSelector = gtk.combo_box_new_text()
            oSelector.append_text("No Expansion")
            for oExp in aKnownExpansions:
                oSelector.append_text(oExp.name)

            dReplacement[sName] = oSelector

            oBox.pack_start(dReplacement[sName])
            oButtonBox.pack_start(oBox)

        oUnknownDialog.vbox.pack_start(oButtonBox, True, True)

        oMesgLabel2.set_text(sMsg2)

        oUnknownDialog.vbox.pack_start(oMesgLabel2)
        oUnknownDialog.vbox.show_all()

        iResponse = oUnknownDialog.run()

        oUnknownDialog.destroy()

        if iResponse == gtk.RESPONSE_OK:
            # For cards marked as replaced, add them to the Holder
            for sName in dUnknownExps:
                sNewName = dReplacement[sName].get_active_text()
                if sNewName != "No Expansion":
                    dUnknownExps[sName] = sNewName
            return True
        else:
            return False
