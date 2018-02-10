'''
The utils module of the UnrealExporter package
'''

# Import statements
import pymel.core
import os

# Properly will bake an object with properly keyword arguments
# This will also do a process to make the baking faster, then resets it
def bakeThis(obj, **kwargs):

    # Maya is particular about how baking is done
    # If no object is given, just grab whatever is selected
    if obj is None:

        obj = pymel.core.selected()

    prepBake()

    pymel.core.bakeResults(obj, **kwargs)

    resetBake()

# Create locator and give it a name
def createLocator(name):

    loc = pymel.core.spaceLocator(n = name, p = (0,0,0))

    return loc

def deleteChildrenNodeType(srcNode, nodeType):

    for node in pymel.core.listRelatives(srcNode, ad = True):

        if node.type() != nodeType:

            pymel.core.delete(node)

# Euler Filters anim curves on selected objects
def eulerFilter():

    selected = pymel.core.selected()

    for item in selected:

        animCrvs = item.listConnections(type = "animCurve")

        pymel.core.filterCurve(animCrvs, filter = "euler")

# Gets the Range Slider's end time
def getEndTime():

    return pymel.core.playbackOptions(q = True, maxTime = True)

# Get the shape of the transform
def getShape(item):

    if item.type() != "transform":

        shape = item

    else:
        shape = item.getShape()

    return shape

# Gets the Range Slider's start time
def getStartTime():

    return pymel.core.playbackOptions(q = True, minTime = True)

# Loads the fbx plugin for maya
def loadFBXPlugin():

    pymel.core.loadPlugin('fbxmaya.mll', quiet = True)

# Make the baking faster
def prepBake():

    # Change evaluation mode to DG for faster baking
    pymel.core.evaluationManager(mode = "off")
    
    # Change the visibility of the viewport
    pymel.core.mel.eval("paneLayout -e -manage false $gMainPane")

# Reopen the scene post export
def reopenScene():

    scene = pymel.core.sceneName()

    pymel.core.openFile(scene, f = True)

# Resets back after bake
def resetBake():

    # Change evaluation mode back to original
    pymel.core.evaluationManager(mode = "parallel")

    # Change the visibility of the viewport back
    pymel.core.mel.eval("paneLayout -e -manage true $gMainPane")

# Set animation export options
def setAnimExportOptions():

    # Bake Complex and Shapes is needed for Blendshapes
    # Skins are needed for actual animation
    # Constraints have crashed, make sure they are false
    pymel.core.mel.FBXExportBakeComplexAnimation(v = True)
    pymel.core.mel.FBXExportShapes(v = True)
    pymel.core.mel.FBXExportSkins(v = True)
    pymel.core.mel.FBXExportConstraints(v = False)

# Set camera export options
def setCamExportOptions():

    # Bake Complex and Camera is needed for Camera
    # Constraints have crashed, make sure they are false
    pymel.core.mel.FBXExportCameras(v = True)
    pymel.core.mel.FBXExportBakeComplexAnimation(v = True)
    pymel.core.mel.FBXExportConstraints(v = False)

# Set general fbx options
def setGeneralExportOptions():

    # Get general options for exporting to Unreal
    # For less data space, export in ascii is false
    # Up Axis Z
    # Make not not just animation
    
    pymel.core.mel.FBXExportInAscii(v = False)
    pymel.core.mel.FBXExportUpAxis("z")
    pymel.core.mel.FBXExportAnimationOnly(v = False)

# Set mesh export options
def setMeshExportOptions():

    # Triangulate on Export speeds up Unreal import time
    # Smooth Mesh and Smoothing Groups for models

    pymel.core.mel.FBXExportSmoothMesh(v = True)
    pymel.core.mel.FBXExportTriangulate(v = True)
    pymel.core.mel.FBXExportTangents(v = True)
    pymel.core.mel.FBXExportSmoothingGroups(v = True)

# Set texture export options
def setTextureExportOptions():

    # Embedded the textures into the fbx file on import

    pymel.core.mel.FBXExportEmbeddedTextures(v = True)