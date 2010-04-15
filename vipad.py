#!/usr/bin/env python
from __future__ import print_function
from cursesextras import *
from curses.textpad import Textbox as orig_Textbox
# /usr/lib/python2.5/curses/textpad.py
from exceptions import EOFError, KeyboardInterrupt
from basicsequence import BasicMutableSequence

def parsemarkup(obj):
    """Accepts strings, (string, attr) tuples, or lists of tuples.
    
    Yields (string, attr) pairs."""
    if isinstance(obj, (basestring, tuple)):
        obj = [obj]
    
    for item in obj:
        if isinstance(item, basestring):
            yield item, None
        else:
            yield item

class Panelastext(BasicMutableSequence):
    def __init__(self, win):
        """A window is required to instantiate the textbox."""
        self.win = win
        self._maxyx = win.getmaxyx()
        self._curpos = (0,0) # relative to buffer, not to actual window
        self._winpos = 0 # where the window is relative to buffer
        self._wrappedlines = set() # lines that are a continuation of the line above
        self._lowerline = -1 # don't go beyond this (pad coord, not line coord)
    
    def _tophyscoord(self, linenum):
        """Returns (begin, end) representing the lines in the pad that 
        correspond to line linenum"""
        linenum = int(linenum)
        begin = end = linenum
        for i in sorted(self._wrappedlines):
            if i <= begin:
                begin += 1
                end += 1
            elif i <= end + 1:
                end += 1
            else:
                break
        return (begin, end)
    
    def _tolinecoord(self, linenum):
        """Given a physical coordinate, returns the corresponding line number in
        the text"""
        linenum = int(linenum)
        for i in reversed(sorted(self._wrappedlines)):
            if i <= linenum:
                linenum -= 1
        return linenum
    
    def _delete(self, linenum):
        """Removes the specified line."""
        log(str(type(self)) + "._delete(%d) %d" % (linenum, len(self)))
        begin, end = self._tophyscoord(linenum)
        self.win.move(begin,0)
        lines = 0
        for i in range(begin, end+1):
            self.win.deleteln()
            if i in self._wrappedlines:
                self._wrappedlines.remove(i)
            lines += 1
        self._lowerline -= lines
        for i in sorted(self._wrappedlines):
            if i > end:
                self._wrappedlines.remove(i)
                self._wrappedlines.add(i-lines)
        
        log(self[:])
    
    def __iter__(self):
        return iter(self[:])
    
    def insert(self, index, line):
        """Inserts the given line after the specified point."""
        log(str(type(self)) + ".insert(%d,%r)" % (index, line))
        begin, end = self._tophyscoord(index)
        self.win.move(begin,0)
        self.win.insertln()
        self._lowerline += 1
        for i in sorted(self._wrappedlines):
            if i >= begin:
                self._wrappedlines.remove(i)
                self._wrappedlines.add(i+1)
        if line:
            self._set(index, line)
    
    def _get(self, loc):
        "Returns the line as a str."
        begin, end = self._tophyscoord(loc)
        
        line = ''
        for linenum in range(begin,end+1):
            line += self.win.instr(linenum,0)
        
        return line.rstrip()
    
    def _set(self, loc, newline):
        log(str(type(self)) + "._set(%d,%r) %d" % (loc, newline, len(self)))
        maxy, maxx = self._maxyx
        begin, end = self._tophyscoord(loc)
        numoldlines = end - begin + 1
        numnewlines = max(((len(newline)-1) / maxx) + 1,1)
        self.win.move(begin,0)
        # add or delete the right number of physical lines to replace 
        # what we have
        for i in range(numoldlines - numnewlines):
            self.win.deleteln()
        for i in range(numnewlines - numoldlines):
            self.win.insertln()
        for i in range(numnewlines):
            self.win.move(begin+i,0)
            line, newline = newline[:maxx], newline[maxx:]
            self.win.clrtoeol()
            for obj, attr in reversed(list(parsemarkup(line))):
                if attr == None:
                    attr = 0
                self.win.addstr(obj, attr)
        
        log('wrapped:', sorted(self._wrappedlines))
        # update wrapped lines - we've changed things
        if numnewlines != numoldlines:
            newend = begin + numnewlines - 1
            for i in range(newend+1, end+1):
                self._wrappedlines.remove(i)
            for i in range(end+1,newend+1):
                self._wrappedlines.add(i)
            for i in sorted(self._wrappedlines):
                if i > newend:
                    self._wrappedlines.remove(i)
                    self._wrappedlines.add(i + numnewlines - numoldlines)
        log('new wrapped:', sorted(self._wrappedlines))
        # update how many lines there are
        # we may have inserted / deleted a line in the middle,
        # or possibly (through `x[-1:] = lines`, for example) put lines
        # at the end
        self._lowerline = max(self._lowerline + numnewlines - numoldlines, end)
        log(self[:])
    
    
    def __len__(self):
        return (self._lowerline + 1) - len(self._wrappedlines)
    
    

class ExtendedTextbox(Panelastext):
    """a class based theoretically on the standard curses.textpad, but 
    implementing several advanced features:
    - scrolling (TODO)
    - completion requests (TODO)
    - prompt for entry (TODO)
    - color management (TODO)
    - auto indentation (TODO)"""
    def __init__(self, win):
        """A window is required to instantiate the textbox."""
        Panelastext.__init__(self, win)
        win.keypad(1)
    
    def do_command(self, ch):
        """Process a single editing command.
        
        Returns a boolean, where 'True' indicates editing has finished."""
        cury, curx = self._curpos
        #(maxy, maxx) = self._getlim()
        if ch == ord('q'):
            return True
        if curses.ascii.isprint(ch):
            self.win.insch(cury, curx, ch)
            curx += 1
            self.win.move(cury,curx)
            self.refresh()
            return False
    

    def gather(self):
        "Collect and return the contents of the window."
        result = self[:]
        #for y in range(self._lowerline+1):
            #result.append(self._getline(y))
        return '\n'.join(result)
    
    def refresh(self):
        self.win.refresh()
        
    def edit(self):
        "Edit in the widget window and collect the results."
        log(self._maxyx, self._lowerline)
        while 1:
            ch = self.win.getch()
            if not ch:
                continue
            finished = self.do_command(ch)
            if finished:
                break
        return self.gather()