import curses, vipad

with vipad.safescreen() as scr:
    keys = dict()
    for k,v in curses.__dict__.items():
        if k.startswith('KEY_'):
            keys[v] = k
    
    
    scr.scrollok(1)
    p = vipad.Panelastext(scr)
    ch = 0
    while ch != ord('q'):
        ch = scr.getch()
        given = curses.keyname(ch)
        if ch in keys:
            p.append('{0:03d} :: {1}, {2}'.format(ch, given, keys[ch]))
        else:
            p.append('{0:03d} :: {1}'.format(ch, given))