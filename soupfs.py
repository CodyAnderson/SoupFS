import os
import re
import json
import time
import platform
from uuid import UUID,uuid4

'''def sid2uid(value):
    sidrx = re.compile('^S-1-5-\d{2}-\d+-(\d{4,10})-\d+-(\d+)$')
    m = sidrx.match(value)
    (sid,rid) = m.group(1,2)
    sidbits = ('{0:b}'.format(int(sid)))[-9:]
    uidbits = '{0:022b}'.format(int(rid))
    return int(sidbits+uidbits,2)
    
def getuid():
  print "Detecting UID..."
  print platform.system()
  if platform.system()=='Windows':
    import win32api
    import win32security
    uname=win32api.GetUserName()
    sid=str(win32security.LookupAccountName(None,uname)[0]).split(':')[1]
    uid=sid2uid(sid)
    print uname,'->',sid,'->',hex(uid)
  return uid'''

BLOCKSIZE=0x100000

def pathsplit(path):
  assert path!='/'
  sp=path.split('/')
  return '/'+'/'.join(sp[:-1]),sp[-1]
class SoupFS():
  def __init__(self,config):
    with open(config,'r') as f:
        self.config=json.load(f)
    self.dircache={}
  def loaddir(self,uuid):
    with open(os.path.join(self.config['sources'][0][1],'dirents',str(uuid)),'r') as f:
      return json.load(f)
  def savedir(self,uuid,dir):
    with open(os.path.join(self.config['sources'][0][1],'dirents',str(uuid)),'w') as f:
      return json.dump(dir,f,sort_keys=True, indent=4, separators=(',', ': '))
  def writeblock(self,uuid,block,offset,contents):
    with open(os.path.join(self.config['sources'][0][1],'blocks',"%s.%08d.block"%(str(uuid),block)),'wb') as f:
      if contents is not None:
        f.seek(offset)
        f.write(contents)
  def readblock(self,uuid,block,offset,length):
    with open(os.path.join(self.config['sources'][0][1],'blocks',"%s.%08d.block"%(str(uuid),block)),'rb') as f:
      f.seek(offset)
      return f.read(length)
  def getudir(self,uuid):
    if uuid not in self.dircache:
      self.dircache[uuid]=self.loaddir(uuid)
    return self.dircache[uuid]
  def getparentdir(self,path):
    pd=self.getudir(UUID(int=0))
    for i in path.lstrip('/').split('/')[:-1]:
      pd=self.getudir(UUID(pd['children'][i.upper()]['uuid']))
    return pd
  def getdir(self,path):
    pd=self.getudir(UUID(int=0))
    for i in path.lstrip('/').split('/'):
      pd=self.getudir(UUID(pd['children'][i.upper()]['uuid']))
    return pd
  def getattr(self,path):
    if path=='/':
      #return {k:(v if k not in ['st_gid','st_uid'] else getuid()) for k,v in self.getudir(UUID(int=0))['attrs'].items()}
      return self.getudir(UUID(int=0))['attrs']
    try:
        #return {k:(v if k not in ['st_gid','st_uid'] else getuid()) for k,v in self.getparentdir(path)['children'][pathsplit(path)[1].upper()]['attrs'].items()}
        return self.getparentdir(path)['children'][pathsplit(path)[1].upper()]['attrs']
    except:
      print "KeyError in getattr on",path
      print "    folder",pathsplit(path)[1]
      try:
          print "    parent",self.getparentdir(path)['uuid'],self.getparentdir(path)['children'].keys()
      except:
        print "Error printing parent"
      assert False
  def readdir(self,path):
    if path=='/':
      return [v['name'] for k,v in self.getudir(UUID(int=0))['children'].items()]
    return [v['name'] for k,v in self.getdir(path)['children'].items()]
  def mkdir(self,path,mode):
    pd=self.getparentdir(path)
    if pathsplit(path)[1].upper() in pd['children']:
      return
    attrs={"st_ctime": time.time(), "st_mtime": time.time(), "st_nlink": 0, "st_gid": 0, "st_size": 4096, "st_atime": time.time(), "st_uid": 0, "st_mode": 040777}
    uuid=uuid4()
    print uuid
    pd['children'][pathsplit(path)[1].upper()]={'uuid':str(uuid),'attrs':attrs,'name':pathsplit(path)[1]}
    print pd['uuid'],pd['children'].keys()
    self.savedir(UUID(pd['uuid']),pd)
    newdir={'uuid':str(uuid),'attrs':attrs,'children':{}}
    self.savedir(uuid,newdir)
  def rmdir(self,path):
    pd=self.getparentdir(path)
    del pd['children'][pathsplit(path)[1].upper()]
    self.savedir(UUID(pd['uuid']),pd)
    #we aren't actually deleting the dirent, maybe do this in fsck?
  def unlink(self,path):
    pd=self.getparentdir(path)
    del pd['children'][pathsplit(path)[1].upper()]
    self.savedir(UUID(pd['uuid']),pd)
    #we aren't actually deleting the blocks, maybe do this in fsck?
  def rename(self,old,new):
    assert pathsplit(old)[0]==pathsplit(new)[0]
    pd=self.getparentdir(old)
    pd['children'][pathsplit(new)[1].upper()]=pd['children'].pop(pathsplit(old)[1].upper())
    pd['children'][pathsplit(new)[1].upper()]['name']=pathsplit(new)[1]
    self.savedir(UUID(pd['uuid']),pd)
  def create(self,path,mode):
    pd=self.getparentdir(path)
    attrs={"st_ctime": time.time(), "st_mtime": time.time(), "st_nlink": 0, "st_gid": 0, "st_size": 0, "st_atime": time.time(), "st_uid": 0, "st_mode": 000777}
    uuid=uuid4()
    print uuid
    self.writeblock(uuid,0,0,None)
    pd['children'][pathsplit(path)[1].upper()]={'uuid':str(uuid),'attrs':attrs,'name':pathsplit(path)[1]}
    print pd['uuid'],pd['children'].keys()
    self.savedir(UUID(pd['uuid']),pd)
    return -1
  def write(self,path,buf,offset):
    pd=self.getparentdir(path)
    uuid=UUID(pd['children'][pathsplit(path)[1].upper()]['uuid'])
    #print "Writing %x bytes to offset %x"%(len(buf),offset)
    #print "Block size",hex(BLOCKSIZE)
    blkno=offset/BLOCKSIZE
    #print "Starting block",hex(blkno)
    blkoffs=offset-(blkno*BLOCKSIZE)
    #print "Starting offset",hex(blkoffs)
    bufoffs=0
    if blkoffs>0:
      pwbytes=BLOCKSIZE-blkoffs
      print "Writing partial to block %x: %x bytes"%(blkno,pwbytes)
      self.writeblock(uuid,blkno,blkoffs,buf[:pwbytes])
      blkno+=1
      bufoffs+=pwbytes
    while bufoffs<len(buf):
      print "Writing to block %x from buf[%x:%x]"%(blkno,bufoffs,bufoffs+BLOCKSIZE)
      self.writeblock(uuid,blkno,blkoffs,buf[bufoffs:bufoffs+BLOCKSIZE])
      blkno+=1
      bufoffs+=BLOCKSIZE
    if (offset+len(buf))>pd['children'][pathsplit(path)[1].upper()]['attrs']['st_size']:
      pd['children'][pathsplit(path)[1].upper()]['attrs']['st_size']=offset+len(buf)
    self.savedir(UUID(pd['uuid']),pd)
    return len(buf)
  def read(self,path,length,offset):
    pd=self.getparentdir(path)
    uuid=UUID(pd['children'][pathsplit(path)[1].upper()]['uuid'])
    #print "Reading %d bytes from offset %x"%(length,offset)
    flen=pd['children'][pathsplit(path)[1].upper()]['attrs']['st_size']
    #print "File length",flen
    length=min(length,flen-offset)
    length=max(length,0)
    #print "Corrected length:",length
    #print "Block size",hex(BLOCKSIZE)
    blkno=offset/BLOCKSIZE
    #print "Starting block",hex(blkno)
    blkoffs=offset-(blkno*BLOCKSIZE)
    #print "Starting offset",hex(blkoffs)
    bufoffs=0
    buf=""
    if blkoffs>0:
      prbytes=BLOCKSIZE-blkoffs
      prbytes=min(prbytes,length)
      print "Reading partial from block %x: %d bytes"%(blkno,prbytes)
      buf+=self.readblock(uuid,blkno,blkoffs,prbytes)
      blkno+=1
      bufoffs+=prbytes
      blkoffs=0
    while bufoffs+BLOCKSIZE<length:
      print "Reading from block %x from buf[%x:%x]"%(blkno,bufoffs,bufoffs+BLOCKSIZE)
      buf+=self.readblock(uuid,blkno,blkoffs,BLOCKSIZE)
      blkno+=1
      bufoffs+=BLOCKSIZE
    if bufoffs<length:
      prbytes=length-bufoffs
      print "Reading partial from block %x: %d bytes"%(blkno,prbytes)
      buf+=self.readblock(uuid,blkno,blkoffs,prbytes)
    return buf