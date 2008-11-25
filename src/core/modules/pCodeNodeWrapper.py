import os, imp, traceback

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pCommonPath import *
from core.pConfigDefs import *

class CodeNodeWrapper(VirtualNodeWrapper):
  def onCreateInstance(self, parent, filepath):
    print "I: pCodeNodeWrapper.onCreateInstance:"
    print "  - parent", parent
    print "  - script", filepath
    if filepath != ' ':
      filename=os.path.basename(filepath)
      dirname=os.path.dirname(filepath)
      filebase, fileext = os.path.splitext(filename)
      if fileext == '.py':
        fp, filename, description=imp.find_module(filebase, [dirname])
        print "  - find_module", fp, filename, description
        try:
          module = imp.load_module(filebase, fp, filename, description)
          print "  - load_module", module, dir(module)
        except:
          print "find_module failed"
          traceback.print_exc()
        try:
          objectClass = getattr(module, filebase[0].upper()+filebase[1:])
          objectInstance = objectClass(filepath, parent)
        except:
          print "W: CodeNodeWrapper.onCreateInstance: error creating code instance"
          traceback.print_exc()
        try:
          #
          objectInstance.enableEditmode()
          # set as active object be the editor
          modelController.selectModel( objectInstance )
          #
          messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
          return objectInstance
        except:
          print "W: CodeNodeWrapper.onCreateInstance: error enabling the editor on code instance"
          traceback.print_exc()
    return None
  onCreateInstance=classmethod(onCreateInstance)
  
  def loadFromEggGroup( self, eggGroup, parent, filepath ):
    print "I: CodeNodeWrapper.loadFromEggGroup:"
    eggExternalReference = eggGroup.getChildren()[0]
    referencedFilename = eggExternalReference.getFilename()
    filepath = os.path.join(filepath,str(referencedFilename))
    objectInstance = self.onCreateInstance(parent, filepath)
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)
  
  def __init__(self, name=None, parent=None):
    self.scriptFilepath = name
    VirtualNodeWrapper.__init__(self, CODE_WRAPPER_DUMMYOBJECT, name, parent) 
  
  def getSaveData( self, relativeTo ):
    ''' link the egg-file into the egg we save
    '''
    # convert the matrix, very ugly right now
    om = self.getMat()
    nm = Mat4D()
    for x in xrange(4):
        for y in xrange(4):
            nm.setCell( x, y, om.getCell(x,y) )
    # the matrix we define must be applied to the nodes in "local space"
    nodeName = self.getName()
    instance = EggGroup( nodeName+"-Group" )
    instance.setGroupType(EggGroup.GTInstance)
    instance.setTransform3d( nm )
    # userdata is not written to the eggFile
    #instance.setUserData( self.wrapperTypeTag )
    className = 'CodeNodeWrapper' #self.__class__.__name__ -> yields the wrong classname
    instance.setTag( MODEL_WRAPPER_TYPE_TAG, className )
    # convert to a relative path
    scriptFilepath = relpath( relativeTo, os.path.abspath(self.scriptFilepath) )
    #print "I: CodeNodeWrapper.getSaveData: scriptFilepath:", scriptFilepath, self.scriptFilepath, relativeTo
    # add the reference to the egg-file
    ext = EggExternalReference( className+"-EggExternalReference", scriptFilepath )
    instance.addChild(ext)
    return instance
