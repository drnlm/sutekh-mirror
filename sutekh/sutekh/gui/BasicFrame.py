# BasicFrame.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Base class for other Frames.
# Copyright 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Base class for Sutekh Frames"""

import gtk

class BasicFrame(gtk.Frame, object):
    # pylint: disable-msg=R0904
    # gtk.Widget, so lotes of public methods
    """The basic, blank frame for sutekh.

       Provides a default frame, and drag-n-drop handlind for
       sawpping the frames. Also provides gtkrc handling for
       setting the active hint.
       """
    def __init__(self, oMainWindow):
        super(BasicFrame, self).__init__()
        self._oMainWindow = oMainWindow
        self.set_name("blank frame")

        # Ensure new panes aren't completely hidden

        self._oTitle = gtk.EventBox()
        self._oTitleLabel = gtk.Label('Blank Frame')
        self._oTitleLabel.set_name('frame_title')
        self._oTitle.add(self._oTitleLabel)
        # Allows setting background colours for title easily
        self._oTitle.set_name('frame_title')
        self._oView = gtk.TextView()
        self._oView.set_editable(False)
        self._oView.set_cursor_visible(False)

        aDragTargets = [ ('STRING', 0, 0),
                         ('text/plain', 0, 0) ]

        self._oTitle.drag_source_set(
                gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON3_MASK, aDragTargets,
                gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

        self._oTitle.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                aDragTargets,
                gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

        self._oTitle.connect('drag-data-received', self.drag_drop_handler)
        self._oTitle.connect('drag-data-get', self.create_drag_data)

        self._oView.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                aDragTargets,
                gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

        self._oView.connect('drag-data-received', self.drag_drop_handler)
        self._oView.connect('drag-motion', self.drag_motion)

    # pylint: disable-msg=W0212
    # explicitly allow access to these values via thesep properties
    title = property(fget=lambda self: self._oTitleLabel.get_text(),
            doc="Frame Title")
    name = property(fget=lambda self: self._oTitleLabel.get_text(),
            doc="Frame Name")
    type = property(fget=lambda self: "Blank Frame", doc="Frame Type")
    view = property(fget=lambda self: self._oView,
            doc="Associated View Object")
    menu = property(fget=lambda self: None, doc="Frame's menu")
    # pylint: enable-msg=W0212

    def set_title(self, sTitle):
        """Set the title of the pane to sTitle"""
        self._oTitleLabel.set_text(sTitle)

    def set_focus_handler(self, oFunc):
        """Set the button press handler for the frame"""
        self.connect('button-press-event', self.call_focus, oFunc)
        # Need both, otherwise clicking on a title and the clicking on
        # the previous tree does the wrong thing
        self.view.connect('button-press-event', self.call_focus, oFunc)
        self.view.connect('focus-in-event', oFunc, self)

    def do_swap(self, aData):
        """Swap or replace this pane with the relevant pane"""
        if aData[1] != 'Card Set Pane:':
            # We swap ourself with the other pane
            oOtherFrame = self._oMainWindow.find_pane_by_name(aData[1])
            if oOtherFrame is not None:
                self._oMainWindow.swap_frames(self, oOtherFrame)
                return True
        else:
            # We replace otherselves with the card set
            if aData[2] == 'PCS:':
                self._oMainWindow.replace_with_physical_card_set(aData[3],
                        self)
                return True
            elif aData[2] == 'ACS:':
                self._oMainWindow.replace_with_abstract_card_set(aData[3],
                        self)
                return True
        return False

    def cleanup(self):
        pass

    def reload(self):
        """Reload frame contents"""
        pass

    def close_frame(self):
        """Close the frame"""
        self._oMainWindow.remove_frame(self)
        self.destroy()

    def add_parts(self):
        """Add the basic widgets (title, & placeholder) to the frame."""
        oMbox = gtk.VBox(False, 2)

        oMbox.pack_start(self._oTitle, False, False)
        # Blanks view placeholder fills everything it can
        oMbox.pack_start(self._oView, True, True)

        self.add(oMbox)
        self.show_all()

    def set_focussed_title(self):
        """Set the title to the correct style when focussed."""
        oCurStyle = self._oTitleLabel.rc_get_style()
        self._oTitleLabel.set_name('selected_title')
        # We can't have this name be a superset of the title name,
        # otherwise any style set on 'title' automatically applies
        # here, which is not what we want.

        oDefaultSutekhStyle = gtk.rc_get_style_by_paths(
                self._oTitleLabel.get_settings(), self.path() + '.',
                self.class_path(), self._oTitleLabel)
        # Bit of a hack, but get's matches to before the title specific bits
        # of the path

        oSpecificStyle = self._oTitleLabel.rc_get_style()
        if oSpecificStyle == oDefaultSutekhStyle or \
                oDefaultSutekhStyle is None:
            # No specific style which affects highlighted titles set, so create
            # one
            oMap = self._oTitleLabel.get_colormap()
            sColour = 'purple'
            if oMap.alloc_color(sColour).pixel == \
                    oCurStyle.fg[gtk.STATE_NORMAL].pixel:
                sColour = 'green'
                # Prevent collisions. If the person is using
                # purple on a green background, they deserve
                # invisible text
            sStyleInfo = """
            style "internal_sutekh_hlstyle" {
                fg[NORMAL] = "%(colour)s"
                }
            widget "%(path)s" style "internal_sutekh_hlstyle"
            """ % { 'colour' : sColour, 'path' : self._oTitleLabel.path() }
            gtk.rc_parse_string(sStyleInfo)
            # We use gtk's style machinery to do the update.
            # This seems the only way of ensuring we will actually do
            # the right thing with themes, while still allowing flexiblity
        # Here, as this forces gtk to re-asses styles of widget and children
        self._oTitle.set_name('selected_title')

    def set_unfocussed_title(self):
        """Set the title back to the default, unfocussed style."""
        self._oTitleLabel.set_name('frame_title')
        self._oTitle.set_name('frame_title')

    # pylint: disable-msg=W0613, R0913
    # function signature requires these arguments
    def close_menu_item(self, oMenuWidget):
        """Handle close requests from the menu."""
        self.close_frame()

    def call_focus(self, oWidget, oEvent, oFocusFunc):
        """Call MultiPaneWindow focus handler for button events"""
        oFocusFunc(self, oEvent, self)
        return False

    def drag_drop_handler(self, oWindow, oDragContext, iXPos, iYPos,
            oSelectionData, oInfo, oTime):
        """Handle panes being dragged onto this one.

           Allows panes to be sapped by dragging 'n dropping."""
        if not oSelectionData and oSelectionData.format != 8:
            oDragContext.finish(False, False, oTime)
        else:
            aData =  oSelectionData.data.splitlines()
            if aData[0] != 'Sutekh Pane:':
                oDragContext.finish(False, False, oTime)
            else:
                if self.do_swap(aData):
                    oDragContext.finish(True, False, oTime)
                else:
                    oDragContext.finish(False, False, oTime)

    def create_drag_data(self, oBtn, oContext, oSelectionData, oInfo, oTime):
        """Fill in the needed data for drag-n-drop code"""
        sData = 'Sutekh Pane:\n' + self.title
        oSelectionData.set(oSelectionData.target, 8, sData)

    def drag_motion(self, oWidget, oDrag_context, iXPos, iYPos, oTimestamp):
        """Show proper icon during drag-n-drop actions."""
        if 'STRING' in oDrag_context.targets:
            oDrag_context.drag_status(gtk.gdk.ACTION_COPY)
            return True
        return False
    # pylint: enable-msg=R0913, W0613
