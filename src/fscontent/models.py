'''
cms models
'''

import os

from zope.interface import implements
from repoze.bfg.interfaces import ILocation
from interfaces import IFile, IDirectory, IFilesystem

class ContentRoot(object):

    def __init__(self, content_dir):
        fs = Filesystem()
        self.root = Directory(parent=None, name='', filesystem=fs, path=content_dir)
        
    def __call__(self, request):        
        return self.root


class Filesystem(object):

    implements(IFilesystem)
            
    join = staticmethod(os.path.join)
    dirname = staticmethod(os.path.dirname)
    realpath = staticmethod(os.path.realpath)
    islink = staticmethod(os.path.islink)
    isfile = staticmethod(os.path.isfile)
    isdir = staticmethod(os.path.isdir)
    splitext = staticmethod(os.path.splitext)


class Directory(object):
    
    implements(IDirectory, ILocation)

    def __init__(self, parent, name, filesystem, path):
        self.__parent__ = parent
        self.__name__ = name
        self.filesystem = filesystem
        self.path = os.path.normpath(path)

    def __getitem__(self, name):
        nextpath = self.filesystem.join(self.path, name)
        if self.filesystem.islink(nextpath):
            realpath = self.filesystem.realpath(nextpath)
            if  (realpath.startswith(self.path) and
                  self.filesystem.isfile(realpath) ):
                realdir = self.filesystem.dirname(realpath)
                if len(self.path.split(os.sep)) == len(realdir.split(os.sep)):
                    # if this symlink to a file is in the same
                    # directory as the original file, treat it as a
                    # primitive alias; use the link target as the
                    # filename so we get the right renderer (eg. stx
                    # vs html).
                    return File(self, name, self.filesystem, realpath)
                else:
                    raise KeyError(name)
            else:
                raise KeyError(name)
        elif self.filesystem.isdir(nextpath):
            return Directory(self, name, self.filesystem, nextpath)
        elif self.filesystem.isfile(nextpath):
            return File(self, name, self.filesystem, nextpath)
        else:
            for fname in os.listdir(self.path):
                nextpath = self.filesystem.join(self.path, fname)
                base, ext = self.filesystem.splitext(fname)
                if self.filesystem.isfile(nextpath) and base == name:
                    return File(self, fname, self.filesystem, nextpath)

            raise KeyError(name)


class File(object):

    implements(IFile)
    
    def __init__(self, parent, name, filesystem, path):
        self.__parent__ = parent
        self.__name__ = name
        self.filesystem = filesystem
        self.path = path
        base, ext = self.filesystem.splitext(path)
        self.ext = ext.lstrip('.')
        
    @property
    def source(self):
        return open(self.path, 'rb').read()



    