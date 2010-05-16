# -*- coding: utf-8 -*-
"""A module for handling text with attributes, such as color, bold/italic, etc.
The attributes can be anything, as long as each is associated with 1 or more
characters; this module treats each 'attr' as a black box: it could be a string,
an object, a list, etc.

The most useful thing here is the Text object. It can be instantiated with a
plain string, with a '(str, attr) pair, or a list of (str, attr) pairs.
"""

from textwrap import TextWrapper

# The default TextWrapper object; used as a default by Text objects if no other
# is given
wrapper = TextWrapper()

def fullmarkup(obj):
    """Accepts strings, (string, attr) tuples, or lists of tuples and yields
    (string, attr) pairs. Allows users to give varied forms of markup, and
    allows objects to receive a uniform set."""
    if isinstance(obj, (basestring, tuple)):
        obj = [obj]
    
    for item in obj:
        if isinstance(item, basestring):
            yield item, None
        else:
            yield item

def decompose(markup):
        """Decomposes parsed markup into separate text and attribute objects.
        
        Returns (txt, attrs), where:
        txt is a string
        attrs is a list of (attr, len) pairs, where (len) is the number
        of characters to which the attr is to be applied."""
        loc = 0
        fulltxt = ''
        attrs = []
        for txt, attr in markup:
            fulltxt += txt
            attrs.append((attr, len(txt)))
        
        return fulltxt, attrs

def recompose(text, attrlist):
    """Recomposes text, attrlist objects into a parsed markup format."""
    markup = []
    for (attr, length) in attrlist:
        curtext, text = text[:length], text[length:]
        markup.append((curtext, attr))
    return markup

class Text(object):
    """Provides an object for interacting with markup.
    
    Text.aslines() returns a list of [line, line, line...] where each line is
    markup; str(Text) returns it as plain text, without attributes; and
    Text.wrappedlines() uses the TextWrapper instance to wrap the text, while
    maintaining the attributes in the correct place."""
    def __init__(self, markup = None, textwrapper = wrapper):
        """Parameters:
        'markup' is another Text object, a string, a (str, attr) pair, or a list
         of (str, attr) pairs.
        'wrapper' is a TextWrapper instance for later use by wrappedlines. It 
        can be shared.
        """
        if isinstance(markup, Text):
            self.wrapper = markup.wrapper
            self.markup = markup.markup
        else:
            if markup == None:
                markup = []
            self.markup = markup
            self.wrapper = textwrapper
    
    @property
    def markup(self):
        "A list representing the markup of this object."
        return self._markup
    
    @markup.setter
    def markup(self, newmarkup):
        self._markup = list(fullmarkup(newmarkup))
        self._lines = None
    
    def aslines(self, removelastnewline = True):
        """Takes parsed markup and splits it into lines.
        
        parameters:
        removelastnewline: does not count a trailing newline as a new, blank line
        
        returns markup:
        markup: [line, line, ...]
        where line is in [(txt, attr), ...] format"""
        
        if self._lines is None:
            lines = []
            curline = []
            
            for txt, attr in self._markup:
                if '\n' in txt:
                    splittxt = txt.split('\n')
                    
                    txt = splittxt.pop(-1)
                    # now txt is a line beginning, and splittxt is a list of
                    # line endings
                    
                    for lineend in splittxt:
                        if len(lineend) > 0:
                            curline.append((lineend, attr))
                        lines.append(curline)
                        curline = []
                
                if len(txt) > 0:
                    curline.append((txt, attr))
            
            lines.append(curline)
            
            self._lines = lines
        
        lines = self._lines
        
        if removelastnewline and len(lines)>0 and not lines[-1]:
            return lines[:-1]
        
        return lines
    
    def __str__(self):
        return ''.join(t for t,a in self.markup)
    
    def __repr__(self):
        return 'Text(' + repr(list(self.markup)) + ')'
    
    def wrappedlines(self):
        """Uses self.wrapper to wrap the text.
        
        NOTE: The attributes of self.wrapper below will be set to the values 
        below. This is necessary to ensure that the attributes are lined up 
        correctly:
        
        self.wrapper.drop_whitespace = False
        self.wrapper.initial_indent = ''
        self.wrapper.expand_tabs = False
        self.wrapper.replace_whitespace = False
        self.wrapper.fix_sentence_endings = False
        
        Some of these (such as initial indent and expand_tabs) could be worked
        around, but I just haven't gotten there yet.
        """
        self.wrapper.drop_whitespace = False
        self.wrapper.initial_indent = ''
        self.wrapper.expand_tabs = False
        self.wrapper.replace_whitespace = False
        self.wrapper.fix_sentence_endings = False
        finallines = []
        # this will be filled and reset for every new wrapped line
        lineattrlist = []
        lencovered = 0
        
        for unwrappedline in self.aslines():
            unwrappedtext, attrlist = decompose(unwrappedline)
            
            if not unwrappedtext:
                finallines.append(('',[]))
                continue
            
            lines = self.wrapper.wrap(unwrappedtext)
            
            curattr, curattrlen = attrlist.pop(0)
            curcovered = 0
            for l in lines:
                linelen = len(l)
                if linelen == 0:
                    finallines.append((l,[]))
                while curcovered + curattrlen < linelen:
                    if curattrlen > 0:
                        lineattrlist.append((curattr, curattrlen))
                    curcovered += curattrlen
                    curattr, curattrlen = attrlist.pop(0)
                if curcovered + curattrlen == linelen:
                    if curattrlen > 0:
                        lineattrlist.append((curattr, curattrlen))
                    curattrlen = 0
                    curcovered = 0
                else:
                    thislinecovered = linelen - curcovered
                    fornextline = curattrlen - thislinecovered
                    if thislinecovered > 0:
                        lineattrlist.append((curattr, thislinecovered))
                    curattrlen = fornextline
                    curcovered = 0
                finallines.append((l,lineattrlist))
                lineattrlist = []
        
        #return finallines
        recomposed = [recompose(t, a) for t, a in finallines]
        return recomposed
    
    def __add__(self, other):
        newmarkup = self.markup + Text(other).markup
        return Text(newmarkup)
    
    def __radd__(self, other):
        return self.__add__(other)


def markuptest(markup):
    parsed = list(fullmarkup(markup))
    print('markup:', markup)
    print('parsed:', parsed)
    txt, attrs = decomposed = decompose(parsed)
    print('decomposed:', decomposed)
    recomposed = recompose(txt, attrs)
    print( 'recomposed:', recomposed)
    
    assert parsed == recomposed
    

def test():
    l = []
    #l.append(('123\n', 'blue'))
    #l.append('\n')
    #l.append(('456\n', 'red'))
    l.extend(['a very long line that should exceed the limit and need to be wrapped, with some ', ('bold', 'bold'), ' text. '] * 3)
    l.append('\n')
    l.append('A last line, for good measure.\n')
    
    #l = ['A long line with a single ', ('bold', 'bold'), ' word in the middle.']
    
    t=Text(l, TextWrapper(width=30))
    #print t.markup
    
    #print str(t)
    #print repr(t)
    
    #for l in t.aslines():
        #print 'LINE::',l
    for l in t.wrappedlines():
        print 'WRAPPED::',l
        print str(Text(l))
    #print t.wrappedlines()
     

if __name__ == '__main__':
    #markuptest('123')
    #markuptest([('123', 'red'), ('456', 'green')])
    #markuptest([('123', 'red'), '456', 'green'])
    test()