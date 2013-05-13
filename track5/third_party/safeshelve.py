import shelve, os, fcntl, new
import __builtin__
from fcntl import LOCK_SH, LOCK_EX, LOCK_UN, LOCK_NB

class SafeShelf(shelve.Shelf):
    def close(self):
        #print 'closing shelf'
        if not self._closed:
            shelve.Shelf.close(self)
            fcntl.flock(self._lckfile.fileno(), LOCK_UN)
            self._lckfile.close()
            self._closed = True
    
    @staticmethod    
    def convertFromShelf(shelf, lckfile):
        shelf._lckfile = lckfile
        shelf._closed = False
        shelf.__class__ = SafeShelf
        return shelf
        
    #def __setitem__(self, key, val):
    #    print key
    #    shelve.Shelf.__setitem__(self, key, val)

def open(filename, flag='c', protocol=None, writeback=False, block=True):
    #print 'opening shelf with flag %s and fn: %s' % (flag,filename)
    """Open the shelve file, creating a lockfile at '.filename.lck'.  If 
    block is False then a IOError will be raised if the lock cannot
    be acquired."""
    lckfilename = os.path.dirname(filename) + os.sep + '.' + os.path.basename(filename) + '.lck'
#   print filename, lckfilename
    old_umask = os.umask(000)
    lckfile = __builtin__.open(lckfilename, 'w')
    os.umask(old_umask)

    # Accquire the lock
    if flag == 'r':
        lockflags = LOCK_SH
    else:
        lockflags = LOCK_EX
    if not block:
        lockflags |= LOCK_NB
    fcntl.flock(lckfile.fileno(), lockflags)

    # Open the shelf
    shelf = shelve.open(filename, flag, protocol, writeback)
    
    # And return a SafeShelf version of it
    return SafeShelf.convertFromShelf(shelf, lckfile)
