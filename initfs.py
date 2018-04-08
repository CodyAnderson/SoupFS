import os
import sys
import time
import json
from uuid import UUID
if __name__ == '__main__':
    if len(sys.argv)<2:
        print "Usage:"
        print "   ",sys.argv[0],"[directory]"
    else:
        try:
          os.mkdir(os.path.join(sys.argv[1],'dirents'))
        except:
          pass
        try:
          os.mkdir(os.path.join(sys.argv[1],'blocks'))
        except:
          pass
        with open(os.path.join(sys.argv[1],'dirents',str(UUID(int=0))),'w') as f:
          rootdir={}
          attrs={}
          attrs['st_ctime']=time.time()
          attrs['st_atime']=time.time()
          attrs['st_mtime']=time.time()
          attrs['st_gid']=0
          attrs['st_uid']=0
          attrs['st_size']=4096
          attrs['st_nlink']=0
          attrs['st_mode']=040777
          rootdir['attrs']=attrs
          rootdir['uuid']=str(UUID(int=0))
          rootdir['children']={}
          json.dump(rootdir,f,sort_keys=True, indent=4, separators=(',', ': '))