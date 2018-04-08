#!/usr/bin/env python

from fuse import FUSE
from soupfuse import SoupFuse
from soupfs import SoupFS
import sys

def main(mountpoint, config):
    soupfs = SoupFS(config)
    FUSE(SoupFuse(soupfs), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    if len(sys.argv)<3:
        print "Usage:"
        print "   ",sys.argv[0],"[config] [mountpoint]"
    else:
        main(sys.argv[2], sys.argv[1])