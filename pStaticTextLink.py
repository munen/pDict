# -*- coding: utf-8 -*-

#########################################################################
# Alain M. Lafon, preek.aml@gmail.com (c) 2009                          #
#                                                                       #
# Ressource for creating clickable labels in the GUI.                   #
#########################################################################

import wx
from wx.lib.stattext import GenStaticText

class pStaticTextLink(GenStaticText):
    def __init__(self, parent, id=-1, label='', pos=(-1, -1),
        size=(-1, -1), style=0, name='Link', text='', textsize=9):

        self.parent = parent
        self.text = text

        GenStaticText.__init__(self, parent, id, label, pos, size, style, name)

        self.font1 = wx.Font(textsize, wx.SWISS, wx.NORMAL, wx.BOLD, True,
                'Verdana')
        self.font2 = wx.Font(textsize, wx.FONTFAMILY_MODERN, wx.NORMAL,
                weight=wx.FONTWEIGHT_BOLD)

        self.SetFont(self.font2)

        self.Bind(wx.EVT_LEFT_UP, self.onMouseEventUp)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEventMoving)


    def onMouseEventMoving(self, event):
        if event.Moving():
            self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            self.SetForegroundColour('grey')
            self.SetFont(self.font1)
        else:
            self.SetForegroundColour('black')
            self.SetCursor(wx.NullCursor)
            self.SetFont(self.font2)
        event.Skip()


    def onMouseEventUp(self, event):
        if event.LeftUp():
            # parent = ScrolledWindow -> Parent -> Frame
            # Dirty hack for prefetching. Send the GUI the clicked
            # value and start a search.
            self.parent.GetParent().GetParent().tmp_value = self.text
            self.parent.GetParent().GetParent().search(event)
            # Old code before prefetching.
            #self.parent.GetParent().GetParent().search_field.SetValue(self.text)
            #self.parent.GetParent().GetParent().Search(wx.EVT_SEARCHCTRL_SEARCH_BTN)
