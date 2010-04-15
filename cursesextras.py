#!/usr/bin/python
from __future__ import print_function
import curses, os
import contextlib

# Default terminal colors.
# Rather hard to find, but referenced at http://www.pixelbeat.org/docs/terminal_colours/

# note: the RGB values of the first 16 colors are not reliable, 
# as they are modifiable property of the terminal. The other colors should be.

# second note:
# the curses color_content() function should give all these values... but
# but at least on my computer, these are completely wrong (both for the first
# 16 colors and especially the other 240, which were repeats)
# an example is given in the lower main script, in which the values given
# by the curses library are printed alongside the values given here, on a 
# background of the color they represent.

# the first 16 colors

colors8 = {
        0 : (0,0,0),
        1 : (0xaa,0,0),
        2 : (0,0xaa,0),
        3 : (0xaa,0x55,0),
        4 : (0,0,0xaa),
        5 : (0xaa,0,0xaa),
        6 : (0,0xaa,0xaa),
        7 : (0xaa,0xaa,0xaa)
}

colors16 = colors8.copy()
colors16.update({
        8 : (0x55,0x55,0x55),
        9 : (0xff,0x55,0x55),
        10 : (0x55,0xff,0x55),
        11 : (0xff,0xff,0x55),
        12 : (0x55,0x55,0xff),
        13 : (0xff,0x55,0xff),
        14 : (0x55,0xff,0xff),
        15 : (0xff,0xff,0xff)
})

colors256 = colors16.copy()
# the next 216 colors are a 6x6x6 color cube
for r in range(0,6):
    for g in range(0,6):
        for b in range(0,6):
            colnum = 16 + r*36 + g*6 + b
            rgb = (r*40+55,g*40+55,b*40+55)
            colors256[colnum] = rgb

# the last 24 colors are a greyscale ramp
for grey in range(0,24):
    colnum = grey + 232
    val = grey*10+8
    colors256[colnum] = (val,val,val)

def log(*args, **kw):
    with file('/tmp/py.log','a') as f:
        kw['file'] = f
        print(*args, **kw)

@contextlib.contextmanager
def safescreen(termstr=None):
    """A context manager that acts like curses.wrapper.
    
    Example:
    with safescreen('xterm-256color') as scr:
        scr.addstr('123456')
        scr.getch()
    """
    try:
        if termstr: # modify enviornmental variables to duplicate another term
            oldterm = os.environ['TERM']
            os.environ['TERM'] = termstr # only way 
        stdscr=curses.initscr()
        log('colors:', curses.tigetnum('colors'),curses.longname())
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        
        # try to start colors, and ignore errors
        try:
            curses.start_color()
            curses.use_default_colors()
            log('colors started')
        except:
            log('safescreen:','ERROR STARTING COLORS')
            pass
        
        yield stdscr
        
    finally:
        if termstr:
            os.environ['TERM'] = oldterm
        try:
            stdscr.keypad(0)
        except:
            pass
        try:
            curses.echo()
            curses.nocbreak()
            curses.endwin()
        except:
            pass

if __name__ == '__main__':
    with safescreen('xterm-256color') as scr:
        for colnum in range(curses.COLORS):
            r,g,b = colors256[colnum]
            val = r + g + b
            if val < (16**2)*3 *.6:
                curses.init_pair(colnum, 15, colnum)
            else:
                curses.init_pair(colnum, 0, colnum)
        
        for colnum in range(0,16):
            r,g,b = colors256[colnum]
            rgbhex = "%02x%02x%02x" % (r,g,b)
            r2,g2,b2 = curses.color_content(colnum)
            r2 = r2*255 / 1000
            g2 = g2*255 / 1000
            b2 = b2*255 / 1000
            rgbhex2 = "%02x%02x%02x" % (r2,g2,b2)
            val = r + g + b
            scr.addstr(rgbhex + ' ', curses.color_pair(colnum))
            scr.addstr(rgbhex2, curses.color_pair(colnum))
            if (colnum + 1) % 4 == 0:
                scr.addstr('\n')
            
            
        for colnum in range(16,curses.COLORS):
            r,g,b = colors256[colnum]
            rgbhex = "%02x%02x%02x" % (r,g,b)
            
            scr.addstr(rgbhex, curses.color_pair(colnum))
            if colnum >= 232 and (colnum + 1) % 8 == 0:
                scr.addstr('\n')
            elif 16 <= colnum < 232 and (colnum +3) % 6 == 0:
                scr.addstr('\n')
        scr.getch()