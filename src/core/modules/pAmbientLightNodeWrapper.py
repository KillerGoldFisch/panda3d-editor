import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class AmbientLightNodeWrapper( LightNodeWrapper ):
  def __init__(self, parent=None, name='AmbientLight'):
    # define the name of this object
    LightNodeWrapper.__init__(self, parent, name, AMBIENTLIGHT_WRAPPER_DUMMYOBJECT, AmbientLight)
