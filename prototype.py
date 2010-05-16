#!/usr/bin/env python 
import curses
from optparse import OptionParser

import pygments.lexers, pygments.styles

from cursesextras import safescreen, log
from cursespygments import CursesFormatter
from interpreterwidget import InterpWidget
import markup

if __name__ == '__main__':
    parser=OptionParser()
    
    # try to force 256-color by treating the terminal as xterm-256color
    parser.add_option('-c', '--color', dest='color',action='store_true')
    # use a different terminal settings
    parser.add_option('-t', '--term', dest='term')
    #use a different style
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
                break
    
    formatter = CursesFormatter(style=style,usebg=True,defaultbg=-2)
    lexer = pygments.lexers.get_lexer_by_name('python')
    
    with safescreen(termname) as scr:
        interp = InterpWidget(scr)
        scr.refresh()
        interp.topwin.addstr("This is where completions would be.\n")
        interp.topwin.scrollok(1)
        interp.topwin.refresh()
        formatter.makebackground(interp.midwin)
        interp.midwin.refresh()
        allcode = []
        
        #interp.midpad.texts.append(markup.Text('123'))
        #interp.midpad.refresh()
        while True:
            code = interp.textbox.edit().rstrip()
            if not code:
                break
            allcode.append(code)
            tokensource = lexer.get_tokens(code)
            
            textobj = markup.Text(formatter.formatgenerator(tokensource))
            #wrapped = (textobj)
            #interp.topwin.addstr(repr(wrapped) + '\n')
            #interp.topwin.refresh()
            
            interp.midpad.texts.append(textobj)
            #log(interp.midpad.texts)
            interp.midpad.refresh()
            interp.botwin.clear()
    
    for code in allcode:
        print code.rstrip()