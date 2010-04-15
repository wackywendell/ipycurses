from cursesextras import *
from myspath import path
import cursespygments
import pygments, pygments.lexers, pygments.styles
from optparse import OptionParser

def gettermcapabilities():
    def termnamegen():
        base = path('/lib/terminfo')
        for dr in base.getdirs():
            for f in dr.getfiles():
                #print str(f[-1])
                yield str(f[-1])

    f=file('testeroutput.py','w')

    output = []
    for t in termnamegen():
        #output.append('-------')
        #output.append(t)
        
        curses.setupterm(t)
        canchange = curses.tigetflag('ccc') # curses.can_change_color()
        colors = curses.tigetnum('colors') # curses.COLORS
        pairs = curses.tigetnum('pairs') # curses.COLOR_PAIRS
        output.append('-------')
        output.append(t)
        output.append('can_change_colors: ' + str(canchange))
        output.append('colors, pairs: ' + str((colors, pairs)))

    curses.setupterm()

    for o in output:
        print>>f, o

def testformatter():
    parser=OptionParser()
    parser.add_option('-c', '--color', dest='color',action='store_true')
    parser.add_option('-t', '--term', dest='term')
    opts, args = parser.parse_args()
    termname = opts.term
    if opts.color and not opts.term:
        termname = 'xterm-256color'
    #print termname
    bgcol = 15
    fgcol = curses.COLOR_BLACK
    formatter = cursespygments.CursesFormatter(usebg=True, defaultbg=-2,
                    defaultfg = -2)
    lexer = pygments.lexers.get_lexer_by_name('python')
    
    def texttoscreen(scr, txt):
        for text, attr in formatter.formatgenerator(lexer.get_tokens(txt)):
            scr.addstr(text, attr)
        #scr.addstr('\n')
    
    with safescreen(termname) as scr:
        formatter.makebackground(scr)
        for s in list(pygments.styles.get_all_styles()):
            formatter.style = pygments.styles.get_style_by_name(s)
            #formatter.setup_styles()
            texttoscreen(scr, s)
            texttoscreen(scr, 'def g(x=3+4, y = "abcd"): pass')
            formatter.updatewindow(scr)
            if scr.getch() == ord('q'):
                break

testformatter()