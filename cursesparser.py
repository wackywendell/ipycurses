from pygments.lexers import PythonLexer
import pygments.token as pygtoken
import curses

standardcols = {
    pygtoken.Number: (curses.COLOR_CYAN, curses.A_BOLD),
    pygtoken.Operator: (curses.COLOR_YELLOW, curses.A_BOLD),
    pygtoken.String: (curses.COLOR_BLUE, curses.A_BOLD),
    pygtoken.Comment: (curses.COLOR_RED, curses.A_BOLD),
    pygtoken.Name: (curses.COLOR_WHITE, curses.A_BOLD),
    pygtoken.Error: (curses.COLOR_RED, curses.A_NORMAL),
    pygtoken.Keyword:(curses.COLOR_GREEN, curses.A_BOLD),
    pygtoken.Text: (curses.COLOR_YELLOW, curses.A_BOLD),
    pygtoken.Token: (None, None) # other
}

class CursesParser:
    def __init__(self, makecolors = True, style = standardcols):
        if makecolors:
            self.makecolorpairs()
        if style is None:
            style = standardcols
        self.style = style
        self.lexer = PythonLexer()
    
    @classmethod
    def makecolorpairs(cls):
        """Initializes curses for colors, makes a color pair of 
        (color, defaultbg) for every color, and initializes self.colorpairs as
        a dictionary with a color -> colorpair mapping"""
        if hasattr(cls, 'colorpairs'):
            return cls.colorpairs
        curses.start_color()
        curses.use_default_colors()
        maxcolors = curses.COLORS
        maxpairs = curses.COLOR_PAIRS
        totalmax = min(maxcolors+1, maxpairs)
        cls.colorpairs = {}
        for colpr in range(1,totalmax):
            if colpr >= maxpairs:
                break
            col = colpr % maxcolors
            curses.init_pair(colpr, col, -1)
            cls.colorpairs[col] = curses.color_pair(colpr)
        return cls.colorpairs
    
    def get_colors(self, raw):
        """Uses pygments to parse the text, and yields (text, color, attr)
        tuples"""
        for tkn, txt in self.lexer.get_tokens(raw):
            notyielded = True
            while notyielded:
                if tkn is None:
                    yield (txt, None, None)
                    notyielded = False
                elif tkn in self.style:
                    col, attr = self.style[tkn]
                    yield (txt, col, attr)
                    notyielded = False
                else:
                    tkn = tkn.parent
    
    def parsetoscr(self, scr, raw):
        """Parses text, and uses scr.addstr to print the text directly."""
        self.makecolorpairs()
        for (txt, col, attr) in self.get_colors(raw):
            fullattr = attr
            if attr is None:
                fullattr = curses.A_NORMAL
            if col is not None: # and col in self.colorpairs:
                fullattr |= self.colorpairs[col]
            scr.addstr(txt, fullattr)