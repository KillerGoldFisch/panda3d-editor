import posixpath

from pandac.PandaModules import *

from core.pTexturePainter import texturePainter, PNMBrush_BrushEffect_Enum

from core.pTreeNode import *
from core.pConfigDefs import *

# uniform float4 texpix_x contains the same as i manually input using k_heightmapSize
# thuogh k_heightmapSize adds another value, the color scaling
# color is on tex0
# height is on tex1
SHADER = """//Cg

void vshader(in  varying float4 vtx_position : POSITION,
             in  varying float2 vtx_texcoord0 : TEXCOORD0,
             in  varying float3 vtx_normal,
             in  uniform sampler2D k_heightmap,
             in  uniform float4x4 mat_modelproj,
             in  uniform float4x4 mat_projection,
             out varying float4 l_position : POSITION,
             out varying float4 l_bright)
{
  // vertex height
  float a = tex2D(k_heightmap, vtx_texcoord0).r;
  vtx_position.z = a;
  l_position=mul(mat_modelproj, vtx_position);
  // color
  float b = tex2D(k_heightmap, vtx_texcoord0+float2(1./128,0)).r;
  float c = tex2D(k_heightmap, vtx_texcoord0+float2(0,1./128)).r;
  float multiplier = float(8.0);
  l_bright = float4(0.5+multiplier*(a-b), .5+multiplier*(a-b)+4*(a-c), .5+multiplier*(a-c), 1);
}

void fshader(in float4 l_bright,
             in float4 l_position : POSITION,
             out float4 o_color:COLOR)
{
  o_color = l_bright;
} """

COMPILED_SHADER = Shader.make(SHADER)

BACKGROUND_SHADER = """//Cg

void vshader(in  varying float4 vtx_position : POSITION,
             in  varying float2 vtx_texcoord0 : TEXCOORD0,
             in  varying float3 vtx_normal,
             in  uniform sampler2D k_heightmap,
             in  uniform sampler2D tex_0,
             in  uniform float4x4 mat_modelproj,
             in  uniform float4x4 mat_projection,
             out varying float4 l_position : POSITION,
             out varying float4 l_bright)
{
  // vertex height
  float a = tex2D(k_heightmap, vtx_texcoord0);
  vtx_position.z = a;
  l_position=mul(mat_modelproj, vtx_position);
  // coloring
  l_bright = tex2D(tex_0, vtx_texcoord0);
}

void fshader(in float4 l_bright,
             in float4 l_position : POSITION,
             out float4 o_color:COLOR)
{
  o_color = l_bright;
} """
COMPILED_BACKGROUND_SHADER = Shader.make(BACKGROUND_SHADER)

class GeoMipTerrainHeightfield(TreeNode):
  ''' this node handles the height texture of the geomipterrain
  '''
  className = 'Heightfield'
  def __init__(self, parent=None, geoMipTerrain=None, name='heightfield'):
    self.geoMipTerrain = geoMipTerrain
    self.heightfield = ''
    TreeNode.__init__(self, name)
    TreeNode.reparentTo(self, parent)
    
    self.mutableParameters['heightfield'] = [ Filepath,
      self.getHeightfield,
      self.setHeightfield,
      None,
      None ]
    self.renderMode = 1
    self.mutableParameters['paint mode (shader)'] = [ int,
      self.getRenderMode,
      self.setRenderMode,
      None,
      None]
    
    self.possibleChildren = []
    self.possibleFunctions = ['save']
  
  def startEdit(self):
    if not TreeNode.isEditmodeStarted(self):
      TreeNode.startEdit(self)
      
      # disable the 3d window object selection
      messenger.send(EVENT_SCENEPICKER_MODELSELECTION_DISABLE)
      
      if self.renderMode == 0:
        # update terrain height using geoMip.generate
        texturePainter.enableEditor(self.geoMipTerrain.terrain.getRoot(), self.geoMipTerrain.terrain.heightfield())
        texturePainter.startEdit()
      if self.renderMode == 1:
        # --- rendering using a shader ---
        # backup bruteforce state
        self.bruteforceState =self.geoMipTerrain.terrain.getBruteforce()
        self.geoMipTerrain.terrain.setBruteforce(True)
        self.geoMipTerrain.terrain.update()
        self.paintImage = self.geoMipTerrain.terrain.heightfield()
        self.paintTexture = Texture()
        self.paintTexture.load(self.paintImage)
        texturePainter.enableEditor(self.geoMipTerrain.terrain.getRoot(), self.paintImage)
        texturePainter.startEdit()
        self.geoMipTerrain.terrain.getRoot().setShaderInput("heightmap", self.paintTexture)
        self.geoMipTerrain.terrain.getRoot().setShader(COMPILED_SHADER)
        # also apply the shader on the paint-model, hmm how to keep the texture?
        texturePainter.paintModel.setShaderInput("heightmap", self.paintTexture)
        texturePainter.paintModel.setShader(COMPILED_BACKGROUND_SHADER)
      
      self.lastUpdateTime = 0
      taskMgr.add(self.updateTask, 'geoMipUpdateTask')
  
  def updateTask(self, task):
    # update 5 times a second
    if task.time > self.lastUpdateTime + 0.5:
      self.lastUpdateTime = task.time
      if self.renderMode == 0:
          print "I: GeoMipTerrainHeightfield.updateTask: updating terrain", task.time
          self.geoMipTerrain.terrain.update()
      elif self.renderMode == 1:
        texturePainter.paintModel.setShader(COMPILED_BACKGROUND_SHADER)
        texturePainter.paintModel.setShaderInput("heightmap", self.paintTexture)
    if self.renderMode == 1:
      self.paintTexture.load(self.geoMipTerrain.terrain.heightfield())
    return task.cont
  
  def stopEdit(self):
    if TreeNode.isEditmodeStarted(self):
      taskMgr.remove('geoMipUpdateTask')
      
      # enable the 3d window object selection
      messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
      
      # stop the shader and regenerate the terrain
      if self.renderMode == 0:
        pass
      elif self.renderMode == 1:
        # restore bruteforce state
        self.geoMipTerrain.terrain.setBruteforce(self.bruteforceState)
        self.geoMipTerrain.terrain.getRoot().clearShader()
        self.geoMipTerrain.terrain.update()
      
      # stop painting
      texturePainter.stopEdit()
      texturePainter.disableEditor()
      
      TreeNode.stopEdit(self)
  
  def save(self):
    # saving the texture
    print "saving the heightfield to", self.heightfield
    self.geoMipTerrain.terrain.heightfield().write(Filename(self.heightfield))
  
  def getHeightfield(self):
    return self.heightfield
  
  def setHeightfield(self, heightfield):
    # backup editing
    editStarted = TreeNode.isEditmodeStarted(self)
    if editStarted:  self.stopEdit()
    # change stuff
    self.heightfield = heightfield
    self.geoMipTerrain.update()
    # restore editing
    if editStarted:  self.startEdit()
  
  def getRenderMode(self):
    return self.renderMode
  
  def setRenderMode(self, renderMode):
    # backup editing
    editStarted = TreeNode.isEditmodeStarted(self)
    if editStarted:  self.stopEdit()
    # change stuff
    if not (renderMode == 0 or renderMode == 1):
      renderMode = 1
    self.renderMode = renderMode
    # restore editing
    if editStarted:  self.startEdit()