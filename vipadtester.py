import curses
from curses import textpad
import vipad
from basicsequence import basictester

def main():
    with vipad.cursessafescreen('xterm-256color') as scr:
        #curses.init_colors()
        curses.use_default_colors()
        maxy, maxx = scr.getmaxyx()
        ncols, nlines = maxx,maxy-8
        uly, ulx = 4, 1
        
        #scr.addstr(uly-2, ulx, "Use Ctrl-G to end editing.")
        win = curses.newwin(nlines, ncols, uly, ulx)
        colset = dict()
        for i in range(curses.COLORS):
            curses.init_pair(i, i, -1)
            curses.init_pair(256+i, -1, i)
                
        #textpad.rectangle(scr, uly-1, ulx-1, uly + nlines, ulx + ncols)
        scr.refresh()
        textbox = vipad.Panelastext(win)
        #tb = basictester()
        tb = []
        test_editbox(textbox, tb)
        
        win.refresh()
        win.getch()
        win.erase()
        for i in range(curses.COLORS):
            rgb = curses.color_content(i)
            if rgb not in colset:
                colset[rgb] = i
            win.addstr(' ', curses.color_pair(256+i))
            if i == 15 or i == 255-24:
                win.addstr('\n')
                
        win.addstr('\n')
        win.refresh()
        win.getch()
    
    for rgb, col in sorted(colset.items()):
        print col, rgb
    print len(colset)
    
    #print len(textbox)
    #print textbox[:]
    #print len(tb)
    #print tb

def test_editbox(textbox, tb):
    textbox.insert(0,'test')
    tb.insert(0,'test')
    list(tb)
    list(textbox)
    assert list(tb) == list(textbox)
    assert len(tb) == len(textbox)
    textbox.insert(1,'test 1')
    tb.insert(1,'test 1')
    assert list(tb) == list(textbox)
    assert len(tb) == len(textbox)
    textbox.insert(2, 'test 2')
    tb.insert(2, 'test 2')
    assert list(tb) == list(textbox)
    assert len(tb) == len(textbox)
    textbox[2:] = ['testtest', 'another really really long line again', 'more']
    tb[2:] = ['testtest', 'another really really long line again', 'more']
    assert list(tb) == list(textbox)
    assert len(tb) == len(textbox)
    textbox.append('a very long line that hopefully will wrap')
    tb.append('a very long line that hopefully will wrap')
    textbox.append('a very long line that hopefully will wrap')
    tb.append('a very long line that hopefully will wrap')
    assert list(tb) == list(textbox)
    assert len(tb) == len(textbox)
    vipad.log('___________')
    textbox[:] = ["0","1","2","3","4"]
    vipad.log('___________')
    tb[:] = ["0","1","2", "3","4"]
    assert tb == textbox[:]
    assert len(tb) == len(textbox)
    del textbox[1:3]
    del tb[1:3]
    assert tb == textbox[:]
    assert len(tb) == len(textbox)
    
    textbox [:] = []
    textbox.append(('123',curses.A_BOLD))
    textbox.append(('123',curses.color_pair(curses.COLOR_RED) | curses.A_BOLD))
    

if __name__ == "__main__":
    main()