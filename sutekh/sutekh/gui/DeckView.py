import gtk, gobject, pango
from CardListView import CardListView
from CellRendererSutekhButton import CellRendererSutekhButton
from SutekhObjects import *
from DeleteDeckDialog import DeleteDeckDialog

class DeckView(CardListView):
    def __init__(self,oWindow,oController,Name):
        super(DeckView,self).__init__(oController)
        self.deckName=Name
        self.__oWin=oWindow
        
        oCell1 = gtk.CellRendererText()
        oCell1.set_property('style', pango.STYLE_ITALIC)
        oCell2 = gtk.CellRendererText()
        oCell2.set_property('style', pango.STYLE_ITALIC)
        oCell3 = CellRendererSutekhButton()
        oCell4 = CellRendererSutekhButton()
        oCell3.load_icon(gtk.STOCK_GO_UP,self)
        oCell4.load_icon(gtk.STOCK_GO_DOWN,self)
        
        oColumn1 = gtk.TreeViewColumn("#",oCell1,text=1)
        self.append_column(oColumn1)
        oColumn1.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        oColumn1.set_fixed_width(40)
        oColumn2 = gtk.TreeViewColumn("Cards", oCell2, text=0)
        oColumn2.set_expand(True)
        self.append_column(oColumn2)
        oColumn3 = gtk.TreeViewColumn("",oCell3)
        oColumn3.set_fixed_width(20)
        oColumn3.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.append_column(oColumn3)
        oColumn4 = gtk.TreeViewColumn("",oCell4)
        oColumn4.set_fixed_width(20)
        oColumn4.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.append_column(oColumn4) 

        self.set_expander_column(oColumn2)
     
        oCell3.connect('clicked',self.incCard)
        oCell4.connect('clicked',self.decCard)

        aTargets = [ ('STRING', 0, 0), # second 0 means TARGET_STRING
                     ('text/plain', 0, 0) ] # and here

        self.drag_source_set(gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON3_MASK,
                  aTargets, gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.drag_dest_set(gtk.DEST_DEFAULT_ALL, aTargets, gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

        self.connect('drag_data_get',self.dragCard)
        self.connect('drag_data_delete',self.dragDelete)
        self.connect('drag_data_received',self.cardDrop)
        self.connect('button_press_event',self.pressButton)

        self.load()
               
    def incCard(self,oCell,oPath):
        oIter = self._oModel.get_iter(oPath)
        sCardName = self._oModel.get_value(oIter,0)
        self._oC.incCard(sCardName)
    
    def decCard(self,oCell,oPath):
        oIter = self._oModel.get_iter(oPath)
        sCardName = self._oModel.get_value(oIter,0)
        self._oC.decCard(sCardName)
    
    def dragCard(self, btn, context, selection_data, info, time):
        oModel, oIter = self._oSelection.get_selected()
        if not oIter:
            return
        sCardName = oModel.get_value(oIter,0)
        number = str(oModel.get_value(oIter,1))
        selection_data.set(selection_data.target, 8, \
              "Deck:" + self.deckName + "_" + number + "_" + sCardName)

    def dragDelete(self, btn, context, data):
        pass

    def cardDrop(self, w, context, x, y, data, info, time):
        if data and data.format == 8 and data.data[:5] == "Phys:":
            # Card is from the Physical card view, so we only get one
            print data.data[5:]
            self._oC.addCard(data.data[5:])
            context.finish(True, False, time)
        else:
            if data and data.format == 8 and data.data[:5] == "Deck:":
                # Card is from a deck, so extract deckname
                [sourceDeckName,number,card] = data.data[5:].split("_")
                if sourceDeckName != self.deckName:
                    # different deck, so try and add number cards
                    # We rely on addCard to prevent stuff becoming 
                    # inconsistent
                    for j in range(int(number)):
                        self._oC.addCard(card)
            else:
                context.finish(False, False, time)

    def deleteDeck(self):
        # Check if deck is empty
        oPCS = PhysicalCardSet.byName(self.deckName)
        if len(oPCS.cards)>0:
            # Not empty
            Dialog=DeleteDeckDialog(self.__oWin,self.deckName)
            Dialog.run()
            if not Dialog.getResult():
                return False # not deleting 
        # Either deck empty, or user agreed to delete
        deck=PhysicalCardSet.byName(self.deckName)
        PhysicalCardSet.delete(deck.id)
        # Tell Window to clean up
        return True 
    
    def load(self):
        self._oModel.clear()
        # oIter = self._oModel.append(None)
        # This feels a bit clumsy, but does work - NM
        cardDict = {}
        
        oPCS = PhysicalCardSet.byName(self.deckName)
        for oCard in oPCS.cards:
            # Check if Card is already in dictionary
            if oCard.abstractCardID in cardDict:
                cardDict[oCard.abstractCardID][1] += 1
            else:
                cardDict[oCard.abstractCardID] = [oCard.abstractCard.name,1]
         
        aCards = list(cardDict.iteritems())
        aCards.sort(lambda x,y: cmp(x[1],y[1]))
 
        for iD, aItems in aCards:
            sName, iCnt = aItems
            self._oModel.set(self._oModel.append(None),
                0, sName,
                1, iCnt
            )   

        self.expand_all()

    def pressButton(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo != None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor( path, col, False)
                popupMenu=PopupMenu(self,path)
                print gobject.list_properties(col)
                print path, cellx, celly
                popupMenu.popup( None, None, None, event.button, time)
                return True # Don't propogate to buttons
        return False
