#!/usr/bin/env python
import __builtin__
raw_input_original = raw_input

def newrawinput(prompt=None):
    print "rawinputcalled! prompt: %r" % prompt
    return raw_input_original(prompt)

__builtin__.raw_input = newrawinput
from IPython.Shell import IPShell

IPShell().mainloop()