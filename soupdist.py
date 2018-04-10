import os
import json

class SoupDist():
  def __init__(self,config):
    self.config=config
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