__all__=['CodeNodeWrapper']

import imp, os, traceback

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pConfigDefs import *

DEBUG = False

class CodeNodeWrapper(VirtualNodeWrapper):
  className = 'Code'
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    name='CodeNode'
    objectInstance = super(CodeNodeWrapper, self).onCreateInstance(parent, name)
    objectInstance.setScript(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__(self, parent, name='CodeNode'):
    self.objectInstance = None
    VirtualNodeWrapper.__init__(self, parent, name, CODE_WRAPPER_DUMMYOBJECT) 
  
  def setScript(self, filepath):
    if filepath != ' ':
      if self.objectInstance is not None:
        self.objectInstance.destroy()
        del self.objectInstance
        self.objectInstance = None
      
      filename=os.path.basename(filepath)
      dirname=os.path.dirname(filepath)
      filebase, fileext = os.path.splitext(filename)
      dirname = Filename(dirname).toOsSpecific()
      if fileext == '.py':
        try:
          fp, filename, description=imp.find_module(filebase, [dirname])
          module = imp.load_module(filebase, fp, filename, description)
          try:
            objectClass = getattr(module, filebase[0].upper()+filebase[1:])
            objectInstance = objectClass(self)
            self.objectInstance = objectInstance
          except:
            print "W: CodeNodeWrapper.setScript: creating code instance failed"
            traceback.print_exc()
        except:
          print "W: CodeNodeWrapper.setScript: finding module failed"
          traceback.print_exc()
      self.scriptFilepath = filepath
      self.setFilepath(self.scriptFilepath)
  
  def destroy(self):
    VirtualNodeWrapper.destroy(self)
    if self.objectInstance is not None:
      self.objectInstance.destroy()
      del self.objectInstance
      self.objectInstance = None
  
  def getSaveData(self, relativeTo):
    objectInstance = VirtualNodeWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.scriptFilepath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setScript(extRefFilename)
    VirtualNodeWrapper.loadFromData(self, eggGroup, filepath)
  
  def duplicate(self, original):
    objectInstance = super(CodeNodeWrapper, self).duplicate(original)
    objectInstance.setScript(original.scriptFilepath)
    return objectInstance
  duplicate = classmethod(duplicate)
