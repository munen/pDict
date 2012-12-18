# -*- coding: utf-8 -*-

#########################################################################
# Alain M. Lafon, preek.aml@gmail.com (c) 2009                          #
#                                                                       #
# Main program of pDict. GUI + hooks to dictionary and thesaurus dbs.   #
#########################################################################

import wx
import string
import os
import wx.lib.delayedresult as delayedresult

import DictOnline
import DictOffline
import ThesaurusOffline
import pWordDef
import pStaticTextLink
import pShareware

class pDictGUI(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, size=(550, 400))

        # Shareware check
        self.shareware = pShareware.pShareware()
        self.trial = self.shareware.checkTrial()

        # Menu
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(4, "&About", "About")
        if self.trial:
            menu.Append(7, "&Register", "Register")
            
        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, "&Exit\tCtrl+Q", "Exit")
        menuBar.Append(menu, "&pDict")

        menu = wx.Menu()
        menu.Append(6, "&Toggle Online/Offline mode", \
                "Toggle Online/Offline mode")
        menuBar.Append(menu, "&Settings")

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.showAboutBox, id=4)
        self.Bind(wx.EVT_MENU, self.toggleNet, id=6)
        self.Bind(wx.EVT_MENU, self.showRegisterScreen, id=7)

        # Dirty hack for prefetching
        self.tmp_value = ""

        # Statusbar
        self.sb = self.CreateStatusBar()
        self.sb.SetFieldsCount(2)
        # Auto size both fields
        self.sb.SetStatusWidths([-3, -1])

        # Panel (Main window)
        panel = wx.Panel(self)
        panel.SetBackgroundColour('#d0d0d0')

        # Toggle Buttons for dictionary -> thesaurus
        self.toggle_dictionary = wx.ToggleButton(panel, 1, 'Dictionary')
        self.toggle_dictionary.SetValue(True)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.toggleDict, id=1)

        self.toggle_thesaurus_de = wx.ToggleButton(panel, 2,
                'Thesaurus German')
        self.Bind(wx.EVT_TOGGLEBUTTON, self.toggleThesaurusDE, id=2)

        self.toggle_thesaurus_en = wx.ToggleButton(panel, 5,
                'Thesaurus English')
        self.Bind(wx.EVT_TOGGLEBUTTON, self.toggleThesaurusEN, id=5)

        self.toggle_word_definition = wx.ToggleButton(panel, 8,
                'Definition')
        self.Bind(wx.EVT_TOGGLEBUTTON, self.toggleWordDefinition, id=8)

        self.search_field = wx.SearchCtrl(panel, 3, '',
                style=wx.TE_PROCESS_ENTER)
        self.search_field.SetFocus()
        self.Bind(wx.EVT_TEXT_ENTER, self.search, id=3)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.search, id=3)
        # Since not threaded, it takes a long time. Won't be on the released
        # version until done right.
        #self.Bind(wx.EVT_TEXT, self.UpdateChoices, id=3)

        # Insert the scrolled window inside the panel
        self.sw = wx.ScrolledWindow(panel, 
                style=wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL)
        self.sw.SetBackgroundColour('#ececec')

        # Stacking the controls vertically using a sizer; 10px borders for
        # controls and 0px for the ScrolledWindow to fit it into the panel
        # smoothly
        sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.toggle_dictionary, 0, wx.LEFT, 10)
        hbox.Add(self.toggle_thesaurus_de, 0, wx.LEFT, 10)
        hbox.Add(self.toggle_thesaurus_en, 0, wx.LEFT, 10)
        hbox.Add(self.toggle_word_definition, 0, wx.LEFT, 10)
        sizer.Add(hbox, 0, wx.ALL, 10)
        sizer.Add(self.search_field, 0, wx.ALL | wx.EXPAND, 10)
        
        # Display the greeter message
        font = wx.Font(18, wx.FONTFAMILY_ROMAN, wx.SLANT,
                weight=wx.FONTWEIGHT_LIGHT) 
        greet = wx.StaticText(self.sw, -1, "Type a word..",
                (25, 20)).SetFont(font)
        sizer.Add(self.sw, 10, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 0)

        # Icon
        iconFile = "pDict.ico"
        icon1 = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon1)
        

        # Center and auto-size the main window
        self.Center()
        panel.SetSizer(sizer)
        panel.Layout()

        # Initialize databases
        self.word_def = pWordDef.pWordDef()
        self.thesaurus = ThesaurusOffline.ThesaurusOffline()
        self.dictOff = DictOffline.DictOffline()
        self.dictOn = DictOnline.DictOnline()
        tmp = self.dictOn.search("test")
        if tmp != "offline":
            self.online = True
            self.sb.SetStatusText("Online mode", 1)
        else:
            self.online = False
            self.sb.SetStatusText("Offline mode", 1)

    def onQuit(self, evt):
        if self.trial:
            self.showSharewareNag()
        self.Close()

    def toggleNet(self, event):
        """Toggles from Online to Offline mode and vice versa."""
        if self.online:
            self.online = False
            self.sb.SetStatusText("Offline mode", 1)
        else:
            tmp = self.dictOn.search("test")
            if tmp != "offline":
                self.online = True
                self.sb.SetStatusText("Online mode", 1)
            else:
                self.sb.SetStatusText("Can't set mode to online", 0)

    def toggleDict(self, event):
        """Toggles the buttons and searches the dictionary."""
        self.toggle_dictionary.SetValue(True)
        self.toggle_thesaurus_de.SetValue(False)
        self.toggle_thesaurus_en.SetValue(False)
        self.toggle_word_definition.SetValue(False)
        self.search(event)

    def toggleThesaurusDE(self, event):
        """Toggles the buttons and searches the German thesaurus."""
        self.toggle_thesaurus_de.SetValue(True)
        self.toggle_dictionary.SetValue(False)
        self.toggle_thesaurus_en.SetValue(False)
        self.toggle_word_definition.SetValue(False)
        self.search(event)

    def toggleThesaurusEN(self, event):
        """Toggles the buttons and searches the English thesaurus."""
        self.toggle_thesaurus_en.SetValue(True)
        self.toggle_dictionary.SetValue(False)
        self.toggle_thesaurus_de.SetValue(False)
        self.toggle_word_definition.SetValue(False)
        self.search(event)

    def toggleWordDefinition(self, event):
        self.toggle_word_definition.SetValue(True)
        self.toggle_thesaurus_en.SetValue(False)
        self.toggle_dictionary.SetValue(False)
        self.toggle_thesaurus_de.SetValue(False)
        self.search(event)

    def clearResults(self):
        """Clears the Mainwindow by deleting all widgets inside."""
        self.sw.DestroyChildren()
        return

    def updateChoices(self, event):
        """Gets the user input and searches for potential matches."""
        value = unicode.encode(string.strip(self.search_field.GetValue()),
                "utf-8")
        if len(value) < 3:
            return
        else:
            synonyms =  self.thesaurus.search(value, "de", suggestions="on")
            self.clearResults()
            if not synonyms:
                synonyms = self.thesaurus.search(value, "en", suggestions="on")
            if synonyms:
                self.sb.SetStatusText("Suggestions for %s" % (value), 0)
                height = 20
                lines = 0
                width = 25
                for synonym in synonyms[:11]:
                    self.writeResults(synonym, height, 8, width)
                    if not synonym:
                        width = 25
                    else:
                        width = 50
                    height = height + 20
                    lines = lines + 1

    def search(self, event):
        """Gets what to fetch and starts the process."""
        self.sb.SetStatusText("Searching..", 0)
        # If UpdateChoices has set a match, then use that
        # one. If not, use the users input and reset tmp_value
        if self.tmp_value:
            self.search_field.SetValue(self.tmp_value)
            self.tmp_value = ""

        value = unicode.encode(string.strip(self.search_field.GetValue()),
            "utf-8")
        if value:
            # Dict/Thesaurus?
            if self.toggle_dictionary.GetValue():
                self.searchDict(value)
            if self.toggle_thesaurus_de.GetValue():
                self.searchThesaurus(value, 'de')
            if self.toggle_thesaurus_en.GetValue():
                self.searchThesaurus(value, 'en')
            if self.toggle_word_definition.GetValue():
                self.searchWordDef(value)
        else:
            self.sb.SetStatusText("No input", 0)

    def searchWordDef(self, value):
        """Searches WordNet via the dict protocol."""
        definition = self.word_def.search(value)
        font = wx.Font(8, wx.FONTFAMILY_MODERN, wx.NORMAL,
                weight=wx.FONTWEIGHT_NORMAL)
        if definition:
            self.clearResults()
            height = 20
            lines = 0
            width = 25
            try:
                wx.StaticText(self.sw, -1, definition, (25,
                    height)).SetFont(font)
            except Exception, msg:
                pass

            self.sb.SetStatusText("Definition for '%s'" % value) 

            self.sw.SetScrollbars(20, 20, 0, int(definition.count("\n")*0.74))
            self.sw.Layout()
            self.sw.SendSizeEvent()
        else:
            self.clearResults()
            self.sb.SetStatusText("No definition found", 0)

    def searchThesaurus(self, value, language):
        """Searches German or English thesaurus and writes the results."""
        synonyms = self.thesaurus.search(value, language)
        if synonyms:
            self.clearResults()
            height = 20
            lines = 0
            width = 25
            synonym_count = 0
            for synonym in synonyms:
                self.writeResults(synonym, height, 8, width)
                if not synonym:
                    width = 25
                else:
                    width = 50
                    synonym_count += 1
                height = height + 20
                lines = lines + 1

            # FIXME 'lines' doesn't say how many results there really are
            if len(value) == 1:
                self.sb.SetStatusText("'%s' result for '%s'" % 
                        (synonym_count, value), 0)
            else:
                self.sb.SetStatusText("'%s' results for '%s'" % 
                        (synonym_count, value), 0)

            self.sw.SetScrollbars(20, 20, 0, lines)
            self.sw.Layout()
            self.sw.SendSizeEvent()
        else:
            self.clearResults()
            self.sb.SetStatusText("No synonyms found", 0)

    def searchDict(self, value):
        """Searches online or offline dictionary and writes the results."""
        max_line_width = 0
        if self.online:
            translation = self.dictOn.search(value)
        if not self.online or translation == 'offline':
            self.online = False
            self.sb.SetStatusText("Offline mode", 1)
            translation = self.dictOff.search(value)
        if translation:
            height = 20
            self.clearResults()
            for line in range(len(translation)):
                # Original text
                self.writeResults(translation[line][0], height, 9, 25)
                height = height + 20
                if len(translation[line][0]) > max_line_width:
                    max_line_width = len(translation[line][0])
                
                # Translation
                self.writeResults(translation[line][1], height, 8, 50)
                height = height + 20
                if len(translation[line][1]) > max_line_width:
                    max_line_width = len(translation[line][0])
                wx.StaticText(self.sw, -1, " ", (25, height))#.SetFont(font)
            # If offline translation includes different groups:
            # Don't count the empty lines as results
            try:
                translation.remove(["", ""])
            except:
                pass
            if len(translation) == 1:
                self.sb.SetStatusText("'%s' result for '%s'" % \
                                     (len(translation), value), 0)
            else:
                self.sb.SetStatusText("'%s' results for '%s'" % \
                                     (len(translation), value), 0)
            # Reset scrollbar to new linecount and width
            # TODO: xPos and yPos are hardcoded to one Windows font. Better
            # solution?  
            # TODO: Refactor that all SearchMethods can use this option
            self.sw.SetScrollbars(20, 20, max_line_width/3+2, 2*line+4)
            self.sw.Layout()
            self.sw.SendSizeEvent()
        else:
            self.sb.SetStatusText("No translation found", 0)
            self.clearResults()
            self.sw.SetScrollbars(20, 20, 0, 0)

    def writeResults(self, text, height, size, position):
        """Writes each word as it belongs.
           Clickable = bold
           {} = normal
           [] = normal"""
        words = string.split(string.strip(text), ' ')
        for word in words:
            # If there are alternatives with synonyms; print a newline in
            # between. That there is a newline to be printed is expressed with
            # an empty word
            if word:
                if word[0] == '#':
                    font = wx.Font(size, wx.FONTFAMILY_MODERN, wx.NORMAL,
                            weight=wx.FONTWEIGHT_BOLD)
                    pStaticTextLink.pStaticTextLink(self.sw, -1, word[1:],
                            pos=(position, height), 
                            text=word[1:], textsize=size).SetFont(font)
                    position = position + len(word[1:])*8
                else:
                    font = wx.Font(size, wx.FONTFAMILY_MODERN, wx.NORMAL,
                            weight=wx.FONTWEIGHT_NORMAL) 
                    wx.StaticText(self.sw, -1, word, 
                            (position, height)).SetFont(font)
                    position = position + len(word)*8
            else:
                    wx.StaticText(self.sw, -1, "", (position, height))

    def showAboutBox(self, event):
        """Shows the about box."""
        description = """German <-> English\ntranslation and thesaurus."""
        licence = self.shareware.getLicenceText()
        if self.trial:
            description += "\n\nTrial Version\n"
        else:
            description += "\n\nRegistered Version\n"

        info = wx.AboutDialogInfo()
        info.SetName('pDict')
        info.SetVersion('0.9b')
        info.SetDescription(description)
        info.SetCopyright('(C) 2009 dispatched software')
        info.SetWebSite('http://dispatched.ch')
        info.SetLicence(licence)
        info.SetIcon(wx.Icon('pDict.png', wx.BITMAP_TYPE_PNG))
        wx.AboutBox(info)

    def showSharewareNag(self):
        """Shows the shareware nag screen."""
        info = wx.AboutDialogInfo()
        info.Name = "Trial version"
        info.Copyright = "(C) 2009 dispatched software"
        info.Description = "full version for 12.95eur"
        info.WebSite = ("http://dispatched.ch/pdict/", 
                "Buy now")
        info.License = self.shareware.getLicenceText()
        info.SetIcon(wx.Icon('pDict.png', wx.BITMAP_TYPE_PNG))
        wx.AboutBox(info)
    
    def showRegisterScreen(self, event):
        """Displays information on how to buy pDict."""
        self.clearResults()
        eur_symbol = u"\u20AC"
        msg = "pDict is shareware and currently not registered.\n" +\
                "The full version is 12.95%s\n" % eur_symbol
        msg += "Upon registering via mail, you will receive a key\n" +\
                "complementing your validation key."
        font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL,
                weight=wx.FONTWEIGHT_NORMAL) 
        wx.StaticText(self.sw, -1, msg, 
                (20, 20)).SetFont(font)
        buy_button = wx.Button(self.sw, -1, 'Buy now', (435, 35))
        self.Bind(wx.EVT_BUTTON, self.openBrowser, id=buy_button.GetId())
        font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL,
                weight=wx.FONTWEIGHT_BOLD) 
        wx.StaticText(self.sw, -1, "Your validation key:\n" + self.trial +\
                "\n\nYour serial:", (20, 115)).SetFont(font)
        self.serial1 = wx.TextCtrl(self.sw, -1, "", (20, 185),
                size=(38, -1))
        self.serial2 = wx.TextCtrl(self.sw, -1, "", (60, 185),
                size=(38, -1))
        self.serial3 = wx.TextCtrl(self.sw, -1, "", (100, 185),
                size=(38, -1))
        check_serial_button = wx.Button(self.sw, -1, 'Register', (155, 185))
        self.Bind(wx.EVT_BUTTON, self.getSerial, id=check_serial_button.GetId())

    def getSerial(self, event):
        """Reads the serial from the input field."""
        serial = self.serial1.GetValue() + self.serial2.GetValue() +\
                self.serial3.GetValue()
        if self.shareware.validateSerial(serial):
            self.trial = False
            wx.MessageBox('Thank you for registering.\nAfter a ' +\
                    'restart it will take effect.', 'Info')
            self.shareware.setValidation(serial)
        else:
            dial = wx.MessageDialog(None, 'Wrong serial', 'Exclamation', wx.OK | 
            wx.ICON_EXCLAMATION)
            dial.ShowModal()
            self.serial1.SetValue("")
            self.serial2.SetValue("")
            self.serial3.SetValue("")
            
        return ""

    def openBrowser(self, event):
        """Opens the browser, so that the user can buy."""
        # TODO Insert pDicts' page
        if os.name == "nt":
            os.system("start http://dispatched.ch/pdict")
        else:
            self.showSharewareNag()
        
        
class pDict(wx.App):
    def OnInit(self):
        # Shareware check
        self.shareware = pShareware.pShareware()
        self.trial = self.shareware.checkTrial()
        if self.trial:
            frame = pDictGUI(None, "pDict trial")
        else:
            frame = pDictGUI(None, "pDict")
        del self.shareware
        del self.trial
        self.SetTopWindow(frame)
        frame.Show(True)
        return True


if __name__ == '__main__':
    app = pDict(redirect=True)
    app.MainLoop()
