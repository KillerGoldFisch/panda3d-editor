from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.modules.pBaseWrapper import *
from core.pModelController import modelController

DEBUG = False

class GeoMipTerrainNodeWrapper(BaseWrapper):
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    if filepath is not None:
      name = filepath.split('/')[-1]
    else:
      name = 'GeoMipTerrain'
    objectInstance = super(GeoMipTerrainNodeWrapper, self).onCreateInstance(parent, name)
    objectInstance.setTerrain(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def enableEditmode(self):
    BaseWrapper.enableEditmode(self)
    self.setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
  def disableEditmode(self):
    BaseWrapper.disableEditmode(self)
    self.setCollideMask(BitMask32.allOff())
  
  def __init__(self, parent=None, name=None):
    #name = "GeoMipTerrain-"+filepath.split('/')[-1]
    BaseWrapper.__init__(self, parent, name)
    self.terrainNode = None
    
    self.mutableParameters['factor'] = [ float,
      self.terrain.getFactor,
      self.terrain.setFactor,
      None,
      None ]
    self.mutableParameters['minlevel'] = [ int,
      self.terrain.getMinlevel,
      self.terrain.setMinlevel,
      None,
      None ]
  
  def setTerrain(self, filepath):
    if self.terrainNode is not None:
      self.terrainNode.detachNode()
    self.terrainImageFilepath = filepath
    self.terrain = GeoMipTerrain("mySimpleTerrain")
    self.terrain.setHeightfield(Filename(filepath))
    self.terrain.getRoot().reparentTo(self)
    self.terrain.getRoot().setSz(25)
    self.terrainNode = self.terrain.generate()
  
  def getSaveData(self, relativeTo):
    objectInstance = BaseWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.terrainImageFilepath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setTerrain(extRefFilename)
    BaseWrapper.loadFromData(self, eggGroup, filepath)
  
  def makeCopy(self, original):
    objectInstance = super(GeoMipTerrainNodeWrapper, self).makeCopy(original)
    objectInstance.setTerrain(original.terrainImageFilepath)
    return objectInstance
  makeCopy = classmethod(makeCopy)

