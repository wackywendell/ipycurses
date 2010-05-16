import curses
from curses.textpad import Textbox
import textwrap

from vipad import Panelastext
#from cursesextras import log

class TextPanel(object):
    def __init__(self, win):
        self.win = win
        self.texts = []
        self.firstline = 0
        self.wrapper = textwrap.TextWrapper()
    
    def _updatewidth(self):
        self.width, self.height = self.win.getmaxyx()
    
    def _getlines(self):
        self._updatewidth()
        lines = []
        self.wrapper.width = self.width
        for t in self.texts:
            t.wrapper = self.wrapper
            lines.extend(t.wrappedlines())
        return lines
    
    def update(self):
        self._updatewidth()
        lines = self._getlines()
        start = self.firstline
        end = self.firstline + self.height
        self.win.move(0,0)
        for l in lines[start:]:
            for t, a in l:
                if a is not None:
                    self.win.addstr(t,a)
                else:
                    self.win.addstr(t)
            try:
                self.win.addstr('\n')
            except:
                break
        
    def refresh(self):
        self.update()
        self.win.refresh()
        # call

class InterpWidget(object):
    def __init__(self, win, topsize=4, botsize=4):
        self.mainwin = win
        self.maxy, self.maxx = win.getmaxyx()
        self.topwin = curses.newwin(topsize, self.maxx, 0, 0)
        self.toppad = Panelastext(self.topwin)
        
        self.mainwin.hline(topsize,0,curses.ACS_HLINE, self.maxx)
        height = self.maxy - topsize - botsize - 2 # include lines
        width = self.maxx
        locx = 0
        locy = topsize + 1
        
        self.midwin = curses.newwin(height, width,locy,locx)
        self.midpad = TextPanel(self.midwin)
        
        height = botsize
        width = self.maxx
        locx = 0
        locy = self.maxy - botsize
        
        self.mainwin.hline(locy -1,0,curses.ACS_HLINE, self.maxx)
        self.botwin = curses.newwin(height, width,locy,locx)
        self.textbox = Textbox(self.botwin)
