"""Provides a pygments formatter for use with urwid."""

from pygments.formatter import Formatter
import curses, exceptions
from pygments.token import Token
from cursesextras import *

class CursesFormatter(Formatter):
    """Formatter that returns [(text,attr), ...],
    where text is a string, and attr is a simple curses attribute.
    
    Note: curses must be started and initialized before the formatter
    can return any valid """
    def __init__(self, **options):
        """Extra arguments:
        
        usebold: if false, bold will be ignored and always off
                default: True
        usebg: if false, background color will always be 'default'
                default: True
        defaultfg: the default color to use for the foreground, used
            if the style does not specify.
            This is in curses format, e.g. curses.COLOR_BLACK.
            Use -1 for the terminal default, -2 for the pygments style default.
            default: -1 (terminal default)
        defaultbg: the default color to use for the background, used in blank
            space, and behind normal text when usebg = False or when
            the style does not specify a foreground color.
            This is in curses format, e.g. curses.COLOR_BLACK.
            Use -1 for the terminal default, -2 for the pygments style default.
            default: -1 (terminal default)
        colors: number of colors to use (-1 for auto, 16, 88, or 256)
                default: -1 (automatic)"""
        Formatter.__init__(self, **options)
        self.usebold = options.get('usebold',True)
        self.usebg = options.get('usebg', True)
        self.defaultbg = options.get('defaultbg', -1)
        self.defaultfg = options.get('defaultfg', -1)
        self.colors = options.get('colors', -1)
        self.style_attrs = {}
        self._tokentocolorpair = {}
        self._setup = False
    
    def __setattr__(self, name, val):
        # if something important has changed, indicate style setup needs to 
        # be run again
        if name in ['usebold','usebg','style','colors']:
            self._setup = False
        object.__setattr__(self, name, val)
    
    @staticmethod
    def _distance(col1, col2):
        r1, g1, b1 = col1
        r2, g2, b2 = col2
        
        rd = r1 - r2
        gd = g1 - g2
        bd = b1 - b2
        
        return rd*rd + gd*gd + bd*bd
    
    @staticmethod
    def hextorgb(hexstr):
        if hexstr[0] == '#':
            hexstr = hexstr[1:]
        rgb = int(hexstr, 16)
        r = (rgb >> 16) & 0xff
        g = (rgb >> 8) & 0xff
        b = rgb & 0xff
        return r,g,b
    
    def findclosest(self, rgb):
        """Takes an rgb tuple and finds the nearest color to it in the given
        colordict, where colordict[colornum] = (r,g,b)"""
        
        dist = 257 * 257 * 3
        bestcol = None
        
        for col,colrgb in self.getcolordict().items():
            curdist = self._distance(rgb, colrgb)
            if curdist < dist:
                dist = curdist
                bestcol = col
        
        return bestcol
    
    def _regrouppairs(self):
        """Goes through all the color pairs currently defined, and if two
        tokens have the same color, they are reassigned to the same color pair.
        
        When you change colors... they won't be exactly right, but it frees up 
        pairs."""
        madepairs = {}
        for (token, colpair) in list(self._tokentocolorpair.items()):
            fg,bg = curses.pair_content(colpair)
            if (fg,bg) in madepairs:
                self._tokentocolorpair[token] = madepairs[(fg,bg)]
            else:
                madepairs[(fg,bg)] = colpair
    
    def _makeattr(self, token, fgcol, bgcol, otherattr):
        """Used by _make_all_colors and _setup_styles to fill a spot in
        self.style_attrs."""
        
        # first get the right color pair for the token.
        # if the style has been changed, we want to reuse the same color pairs
        # as often as possible
        if str(token) in self._tokentocolorpair:
            colpair = self._tokentocolorpair[str(token)]
        else:
            usedcolpairs = list(self._tokentocolorpair.values())
            # unused pairs start from 2; 0 is the 'default' white on black,
            # and 1 is for the standard background.
            colpair = -1
            for pair in xrange(2,curses.COLOR_PAIRS):
                if pair not in usedcolpairs:
                    colpair = pair
                    break
            if colpair == -1:
                # reuse old tokens if they're not in this style
                styletokens = [str(token) for (token, ndef) in self.style]
                for t in self._tokentocolorpair:
                    if t not in styletokens:
                        nextcol = self._tokentocolorpair[t]
                        break
            if colpair == -1:
                # if we've used all available color pairs... its time 
                # to reconsolidate and retry
                self._regrouppairs()
                
                # this assumes the reconsolidation will do something.
                # its conceivable it won't... but unlikely.
                # if there are no more color pairs left even after 
                # reconsolidation, we should get a recursion error here.
                return self._makeattr(token, fgcol, bgcol, otherattr)
                
            self._tokentocolorpair[str(token)] = colpair
        
        #log(colpair,fgcol,bgcol)
        try:
            curses.init_pair(colpair, fgcol, bgcol)
        except:
            log(colpair, fgcol, bgcol)
            raise
        self.style_attrs[str(token)] = curses.color_pair(colpair) | otherattr
    
    def _makecolor(self, colnum, rgb):
        """Initializes a color and color pair in curses, as well as storing the
        relevant data in self._tokentocolorpair.
        
        Assumes rgb is an (r,g,b) tuple, where r,g,b are in the range 0-255"""
        r,g,b = rgb
        r = r*1000/255
        g = g*1000/255
        b = b*1000/255
        
        curses.init_color(colnum, r,g,b)
    
    def getstylefg(self):
        # get foreground from style
        # this is slightly complicated - pygments doesn't really give a way.
        # so we try Token.Text or Token.Generic.Output; if they don't work,
        # we just use black.
        given = None # the hex string from the style
        try:
            given = self.style.style_for_token(Token.Text)['color']
        except KeyError:
            # sometimes there are errors. We ignore them.
            pass
        try:
            given = given or self.style.style_for_token(Token.Generic.Output)['color']
        except KeyError:
            pass
        if not given:
            given = '000000'
        log('given:', given)
        rgb = self.hextorgb(given)
        if self.canchange():
            self._makecolor(16, rgb) # we reserve color 16 for this purpose
            return 16
        return self.findclosest(rgb)
    
    def getstylebg(self):
        """Returns a background color equal or close to that specified by the
        current style.
        
        Returns in curses format (e.g. curses.COLOR_WHITE).
        If possible, the color will be made and then returned.
        """
        rgb = self.hextorgb(self.style.background_color)
        if self.canchange():
            self._makecolor(17, rgb) # we reserve color 17 for this purpose
            return 17
        col = self.findclosest(rgb)
        return col % max(1,curses.COLORS)
    
    def makebackground(self, win):
        """Sets the background of the given window to be as close to that 
        specified by the style as possible.
        
        WARNING: This will also set the colors/attributes of most written 
        characters on the screen. The recommended way of using this is to
        call it shortly after the creation of the window, and call
        'formatter.updatewindow()' on every style change.
        """
        col = self.getstylebg()
        curses.init_pair(1,-1, col)
        win.bkgd(' ', curses.color_pair(1))
        
    def updatewindow(self, win):
        col = self.getstylebg()
        curses.init_pair(1,-1, col)
        win.redrawwin()
        
    def canchange(self):
        canchange = (curses.can_change_color() and
                    (self.colors == -1 or self.colors >= 256) and
                    curses.COLORS > 16)
        if not canchange:
            return False
        try:
            self._makecolor(curses.COLORS-1,(0,0,0))
            return True
            log('CHANGE SUCCESSFUL!', curses.COLORS-1)
        except:
            log('CANCHANGE FALSE!')
            return False
            
    
    def getcolordict(self):
        colors = self.colors
        if colors == -1:
            colors = curses.COLORS
        
        if colors >= 256:
            #log('256')
            return colors256
        elif 8 <= colors <= 16:
            #log('16')
            return colors16
        
        
        # otherwise... black and white.
        #log('bw')
        return {-1:(0,0,0)}
    
    def setup_styles(self, force = False):
        """Creates color pairs and fills the self.style_attrs dict."""
        
        # if its already been setup, don't do it twice...
        if self._setup and not force:
            return
        self._setup = True
        
        log('SETTING UP STYLES...')
        
        # if we already have a style setup that has more definitions than the 
        # new one, clear those out...
        if self.style_attrs:
            tokens = [token for (token, ndef) in self.style]
            for k in list(self.style_attrs.keys()):
                if k not in tokens:
                    del self.style_attrs[k]
        
        # if we can make our own colors, great!
        canchange = self.canchange()
        
        # if we don't have colors or color pairs
        if curses.COLORS <= 1 or curses.COLOR_PAIRS <= 8:
            for ttype, ndef in self.style:
                self.style_attrs[str(ttype)] = 0
                if ndef['bold'] and self.usebold:
                    self.style_attrs[str(ttype)] |= curses.A_BOLD
            return
        
        colors = self.colors
        
        # otherwise, we use the given colors, and find the closest matches.
        if colors == -1:
            colors = curses.COLORS
        
        colordict = self.getcolordict()
        
        defaultfg = self.defaultfg
        defaultbg = self.defaultbg
        if defaultfg == -2:
            defaultfg = self.getstylefg()
        if defaultbg == -2:
            defaultbg = self.getstylebg()
        
        lastcolor = 17 # used for making colors - next color made will be 18.
                       # We don't touch colors 0-17:
                       # 0-15 are the standard first 16 colors,
                       # and 16,17 are for default foreground,background.
        for ttype, ndef in self.style:
            fgcol = defaultfg
            bgcol = defaultbg
            attr = 0
            if ndef['color']:
                colstr = ndef['color']
                rgb = self.hextorgb(colstr)
                if canchange:
                    lastcolor = fgcol = lastcolor + 1
                    self._makecolor(lastcolor, rgb)
                else:
                    fgcol = self.findclosest(rgb)
            if self.usebg and ndef['bgcolor']:
                colstr = ndef['bgcolor']
                rgb = self.hextorgb(colstr)
                if canchange:
                    lastcolor = bgcol = lastcolor + 1
                    self._makecolor(lastcolor, rgb)
                else:
                    bgcol = self.findclosest(rgb)
            if self.usebold and ndef['bold']:
                attr |= curses.A_BOLD
            # if we only have 8 colors, fake 16 by using bold
            if colors == 8 and fgcol >= 8:
                fgcol %= 8
                attr |= curses.A_BOLD
            if colors <= 8 and bgcol >= 8:
                bgcol %= colors
            
            self._makeattr(ttype, fgcol, bgcol, attr)
        
    def formatgenerator(self, tokensource):
        """Takes a token source, and generates (tokenstring, cursesattr) pairs.
        
        Curses MUST ALREADY BE STARTED in order for 
        setup to complete accurately.
        """
        
        self.setup_styles()
        
        for (ttype, tstring) in tokensource:
            while str(ttype) not in self.style_attrs:
                if str(ttype) == '':
                    yield tstring, 0
                    
                ttype = ttype[:-1]

            attr = self.style_attrs[str(ttype)]
            yield tstring, attr
    
    def format(self, tokensource, outfile):
        for (tstring, attr) in self.formatgenerator(tokensource):
            outfile.write(tstring, attr)
