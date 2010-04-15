import collections
import exceptions

class BasicSequence(collections.Sequence):
    """A class that uses an abtract _get(loc) command
    to implement a __getitem__.
    
    Used as a base class, one can write a _get(loc) method, and
    slices will automatically be supported (returning lists).
    
    
    Full requirement list:
    _get(self, loc)
    __contains__(self, item)
    __len__(self)
    __iter__(self)"""
    def _get(self, loc):
        raise exceptions.NotImplementedError("_get not implemented")
    
    def __getitem__(self, key):
        if not isinstance(key, slice):
            return self._get(key)
        
        begin, end, stride = key.indices(len(self))
        
        return [self._get(i) for i in range(begin, end, stride)]

class BasicMutableSequence(collections.MutableSequence, BasicSequence):
    """A class that uses an abstract _get(loc), _set(loc, item),
    _delete(loc) to implement a MutableSequence.
    
    Used as a base class, one can write the get, set, delete, and 
    insert methods, and slices will automatically be supported 
    (accepting iterators and returning lists).
    
    Full requirement list:
    _get(self, loc)
    _set(self, loc, item)
    _delete(self, loc)
    insert(self, index, item)
    __contains__(self, item)
    __len__(self)
    __iter__(self)"""
    def _set(self, loc, item):
        raise exceptions.NotImplementedError("set not implemented")
    def _delete(self, loc):
        raise exceptions.NotImplementedError("delete not implemented")
    
    def __delitem__(self, key):
        if not isinstance(key, slice):
            return self._delete(key)
        
        begin, end, stride = key.indices(len(self))
        
        for i in reversed(range(begin, end, stride)):
            self._delete(i)
    
    def __setitem__(self, key, item):
        if not isinstance(key, slice):
            return self._set(key, item)
        
        begin, end, stride = key.indices(len(self))
        indices = range(begin, end, stride)
        
        # set those that match
        for loc, val in zip(indices, item):
            self._set(loc, val)
        
        # if indices are longer, delete items
        for loc in reversed(indices[len(item):]):
            self._delete(loc)
        
        # if item is longer, insert items
        insertloc = begin + len(indices)
        for val in item[len(indices):]:
            self.insert(insertloc, val)
            insertloc += 1

class basictester(BasicMutableSequence):
    def __init__(self, lst=[]):
        self.list = list(lst)
    def _get(self, loc):
        return self.list[int(loc)]
    def _set(self, loc, item):
        self.list[int(loc)] = item
    def _delete(self, loc):
        del self.list[int(loc)]
    def insert(self, index, item):
        self.list.insert(index, item)
    def __iter__(self):
        return iter(self.list)
    def __len__(self):
        return len(self.list)
    def __contains__(self, item):
        return item in self.list
    
    def __str__(self):
        return str(self.list)
    def __repr__(self):
        return str(self.list)
    
    @classmethod
    def runtest(cls):
        l = []
        b = cls([])
        #print l,b
        assert len(b) == len(l)
        l[:] = range(3)
        b[:] = range(3)
        #print l,b
        assert str(b) == str(l)
        l[0:0] = 'x'
        b[0:0] = 'x'
        #print l,b
        assert str(b) == str(l)
        l[2:3] = 'abcdef'
        b[2:3] = 'abcdef'
        #print l,b
        assert str(b) == str(l)
        l[3] = 'y'
        b[3] = 'y'
        #print l,b
        assert str(b) == str(l)
        l.insert(2,"something")
        b.insert(2,"something")
        #print l,b
        assert str(b) == str(l)
        l[6:] = ('abc',)
        b[6:] = ('abc',)
        #print l,b
        assert str(b) == str(l)
        l[:] = (1,2,3,4)
        b[:] = (1,2,3,4)
        #print l,b
        assert str(b) == str(l)
        l[6:4] = '123'
        b[6:4] = '123'
        #print l,b
        assert str(b) == str(l)
        l[-1:] = 'mnop'
        b[-1:] = 'mnop'
        print l
        print b
        assert str(b) == str(l)
        del l[1:3]
        del b[1:3]
        print l
        print b
        assert str(b) == str(l)

if __name__ == '__main__':
    basictester.runtest()