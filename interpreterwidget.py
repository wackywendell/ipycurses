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

if __name__ == '__main__':
    parser=OptionParser()
    parser.add_option('-c', '--color', dest='color',action='store_true')
    parser.add_option('-t', '--term', dest='term')
    parser.add_option('-s', '--style', dest='style')
    opts, args = parser.parse_args()
    termname = opts.term
    style = opts.style
    if opts.color and not opts.term:
        termname = 'xterm-256color'
    if not style:
        allstyles = list(pygments.styles.get_all_styles())
        style = 'default'
        for s in ('monokai', 'native'):
            if s in allstyles:
                style = s
        self.formatter = UrwidFormatter(style=s)
    
    formatter = CursesFormatter(style=style,usebg=True,defaultbg=-2)
    lexer = pygments.lexers.get_lexer_by_name('python')
    
    with safescreen(termname) as scr:
        interp = InterpWidget(scr)
        scr.refresh()
        interp.topwin.addstr(str(curses.COLORS))
        interp.topwin.refresh()
        formatter.makebackground(interp.midwin)
        interp.midwin.refresh()
        allcode = []
        while True:
            code = interp.textbox.edit()
            if not code:
                break
            allcode.append(code)
            tokensource = lexer.get_tokens(code)
            for (plaintext, attr) in \
                    formatter.formatgenerator(tokensource):
                interp.midwin.addstr(plaintext, attr)
            interp.midwin.refresh()
            interp.botwin.clear()
    
    for code in allcode:
        print code.rstrip()