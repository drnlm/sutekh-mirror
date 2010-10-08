# LocalProfileEditor.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Dialog for editing the temporary / local profile associated with
# a cardset.
# Copyright 2010 Simon Cross <hodgestar+sutekh@gmail.com>
# GPL - see COPYING for details


from sutekh.gui.SutekhDialog import SutekhDialog
from sutekh.gui.AutoScrolledWindow import AutoScrolledWindow
from sutekh.gui.PreferenceTable import PreferenceTable
from sutekh.gui.ConfigFile import FRAME
import gtk


class LocalProfileEditor(SutekhDialog):
    """Dialog which allows the user to per-deck option profiles.
       """
    # pylint: disable-msg=R0904, R0902
    # R0904 - gtk.Widget, so many public methods

    RESPONSE_CLOSE = 1
    RESPONSE_CANCEL = 2

    def __init__(self, oParent, oConfig):
        super(LocalProfileEditor, self).__init__("Edit Local Profile",
                oParent, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)

        self.__oParent = oParent
        self.__oConfig = oConfig

        aOptions = []
        for sKey in self.__oConfig.profile_options(FRAME):
            if sKey == "name":
                continue
            aOptions.append((sKey, self.__oConfig.get_option_spec(FRAME, sKey),
                True))

        self.__oOptionsTable = PreferenceTable(aOptions,
                oConfig.get_validator())
        self.vbox.pack_start(AutoScrolledWindow(self.__oOptionsTable,
            bUseViewport=True))

        self.set_default_size(600, 550)
        self.connect("response", self._button_response)
        self.add_button("Cancel", self.RESPONSE_CANCEL)
        self.add_button("Close", self.RESPONSE_CLOSE)

        self.show_all()
        self._repopulate_options()

    def _button_response(self, _oWidget, iResponse):
        """Handle dialog response"""
        if iResponse != self.RESPONSE_CLOSE:
            self.destroy()
            return

        self._store_active_profile()
        if self._check_unsaved_changes():
            self._save_unsaved_changes()
            self.destroy()
        else:
            # Evil recursion
            self.destroy()
            oDlg = LocalProfileEditor(self.__oParent, self.__oConfig)
            oDlg.run()

    def _repopulate_options(self):
        """Refresh the contents of the options box."""
        dNewValues = {}
        self.__oOptionsTable.update_values(dNewValues, {}, {})

    def _check_unsaved_changes(self):
        """Check that none of the changes make are bad.

        Return True if the changes are safe for saving, False otherwise.
        """
        # TODO: proper checks
        # TODO: proper complaints
        return True

    def _save_unsaved_changes(self):
        """Save all the unsaved changes."""
        pass
