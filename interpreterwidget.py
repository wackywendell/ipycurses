import curses
from cursesextras import safescreen
from vipad import Panelastext
from curses.textpad import Textbox
import pygments.lexers, pygments.styles
from cursespygments import CursesFormatter
from optparse import OptionParser

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
        self.midpad = Panelastext(self.midwin)
        
        height = botsize
        width = self.maxx
        locx = 0
        locy = self.maxy - botsize
        
        self.mainwin.hline(locy -1,0,curses.ACS_HLINE, self.maxx)
        self.botwin = curses.newwin(height, width,locy,locx)
        self.textbox = Textbox(self.botwin)
