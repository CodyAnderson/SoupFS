import os
import sys
import errno
from fuse import FuseOSError, Operations

class SoupFuse(Operations):
    def __init__(self, soup):
        self.soup = soup

    # Helpers
    # =======

    '''def _full_path(self, partial):
        partial = partial.lstrip("/")
        path = os.path.join(self.root, partial)
        return path'''

    # Filesystem methods
    # ==================

    '''def access(self, path, mode):
        full_path = self._full_path(path)
        print "Accessing",path,mode
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        print "Chmod",path,mode
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        print "Chown",path,uid,gid
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    '''
    def getattr(self, path, fh=None):
        #print "Getattr",path
        try:
            return self.soup.getattr(path)
        except AssertionError:
            raise FuseOSError(errno.ENOENT)
        #full_path = self._full_path(path)
        #st = os.lstat(full_path)
        #return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
        #             'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
    
    def readdir(self, path, fh):
        print "Readdir",path
        return ['.','..']+self.soup.readdir(path)
        #full_path = self._full_path(path)

        #dirents = ['.', '..']
        #if os.path.isdir(full_path):
        #    dirents.extend(os.listdir(full_path))
        #for r in dirents:
        #    yield r
    '''
    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    '''
    def rmdir(self, path):
        print "Rmdir",path
        return self.soup.rmdir(path)
        #full_path = self._full_path(path)
        #return os.rmdir(full_path)

    
    def mkdir(self, path, mode):
        print "Mkdir",path
        return self.soup.mkdir(path,mode)
        #return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        print "Statfs",path
        stats={'f_blocks':2**38,'f_bfree':2**38,'f_bavail':2**38,'f_bsize':2**12,'f_frsize':2**12}
        return stats

        '''uint64_t f_bsize;
    uint64_t f_frsize;
    fuse_fsblkcnt_t f_blocks;
    fuse_fsblkcnt_t f_bfree;
    fuse_fsblkcnt_t f_bavail;
    fuse_fsfilcnt_t f_files;
    fuse_fsfilcnt_t f_ffree;
    fuse_fsfilcnt_t f_favail;
    uint64_t f_fsid;
    uint64_t f_flag;
    uint64_t f_namemax;'''
        #full_path = self._full_path(path)
        #stv = os.statfs(full_path)
        #return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
        #    'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
        #    'f_frsize', 'f_namemax'))

    def unlink(self, path):
        print "Unlink",path
        return self.soup.unlink(path)
        #return os.unlink(self._full_path(path))
    '''
    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))

    '''
    def rename(self, old, new):
        print "rename",old,new
        return self.soup.rename(old,new)
        #return os.rename(self._full_path(old), self._full_path(new))
    '''

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)'''

    # File methods
    # ============

    def open(self, path, flags):
        print "Open",path,flags
        return 0
        #full_path = self._full_path(path)
        #return os.open(full_path, flags)
    
    def create(self, path, mode, fi=None):
        print "Create",path,mode
        self.soup.create(path,mode)
        return 0
        #full_path = self._full_path(path)
        #return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)
    
    def read(self, path, length, offset, fh):
        print "Read",path,length,offset,fh
        return self.soup.read(path,length,offset)
        #os.lseek(fh, offset, os.SEEK_SET)
        #return os.read(fh, length)
    
    def write(self, path, buf, offset, fh):
        print "Write",path,'[%x] %x'%(len(buf),offset)
        return self.soup.write(path,buf,offset)
        #os.lseek(fh, offset, os.SEEK_SET)
        #return os.write(fh, buf)
    '''
    def truncate(self, path, length, fh=None):
        print "Trunc",path,length
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        print "Flush",path
        return os.fsync(fh)

    def release(self, path, fh):
        print "Release",path
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        print "Fsync",path
        return self.flush(path, fh)'''