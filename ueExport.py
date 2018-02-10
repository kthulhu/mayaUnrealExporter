'''
The ueExport module for Maya UI useage
'''

# Import statements
import pymel.core
import os

# Import utils and ueAsset modules from UnrealExport package
import UnrealExporter.utils, UnrealExporter.ueAsset

# UI variables
global WINDOW_NAME

WINDOW_NAME = "UnrealExportWin"

'''
UI Code start
'''

# Browse the directory path
def browseDirFilePath():

    # Grab the filepath
    filepath = pymel.core.fileDialog2(ds = 1, cap = "Select Folder for export", fm = 3)
    
    # Check if the filepath is none
    if filepath != None:

        # Replace for FBX file handling
        filepath = filepath[0].replace("\\", "/")
        
        # Add to the textfield for UI
        pymel.core.textField("ExportDirTF", e = True, tx = filepath)
    
    # If file was not chosen, error out    
    else:
        
        pymel.core.error("No Folder chosen, please select a directory")

# Creates the file for FBX
def createExportFile():

    # Query the directory UI textfield
    fileDir = pymel.core.textField("ExportDirTF", q = True, tx = True)

    # if the directory in UI is empty
    if not fileDir:

        pymel.core.error("Must select a directory to export to")

    # Query the file name UI textfield
    fileName = pymel.core.textField("ExportFileTF", q = True, tx = True)

    # If the filename in UI is empty
    if not fileName:

        pymel.core.error("Must give FBX a name for export")

    # If user did not put ".fbx" in the ui
    if ".fbx" not in fileName:

        # Add it back in
        fileName = fileName + ".fbx"

    # Create the entire path for export
    exportFile = os.path.join(fileDir, fileName).replace("\\", "/")

    # Return it
    return exportFile

def deleteDisplay():

    global WINDOW_NAME

    if pymel.core.window(WINDOW_NAME, ex = True):
        
        pymel.core.deleteUI(WINDOW_NAME)

def displayUI():

    global WINDOW_NAME
    
    deleteDisplay()
    
    pymel.core.window(WINDOW_NAME, t = "Export FBX for Unreal", h = 60, w = 150, sizeable = False, mxb = False, mnb = True)

    pymel.core.columnLayout(adj = True)

    pymel.core.separator(h = 5, st = "none")
    
    pymel.core.rowLayout(cat = (1, "both", 7.5))
    
    pymel.core.text("Select an Object (Ctrl, Mesh, Camera) to Export for Unreal")
    
    pymel.core.setParent('..')
    
    pymel.core.separator(h = 5, st = "none")
    
    pymel.core.rowLayout(nc = 3,cw3 = (65, 170, 30), cat = [(1, "both", 2), (2, "both", 2), (3, "both", 5)])

    pymel.core.text("Export Dir:")

    pymel.core.textField("ExportDirTF", w = 175)

    pymel.core.button(l = "Browse", w = 50, c = "ueExport.browseDirFilePath()")

    pymel.core.setParent('..')

    pymel.core.separator(h = 10, st = "none")
    
    pymel.core.setParent('..')
    
    pymel.core.rowLayout(nc = 2,cw2 = (68, 170), cat = [(1, "both", 2), (2, "both", 2)])

    pymel.core.text("Export FBX:")

    pymel.core.textField("ExportFileTF", w = 235)

    pymel.core.setParent('..')

    pymel.core.separator(h = 10, st = "none")

    pymel.core.rowLayout(nc = 2, cat = [(1, "both", 2), (2, "both", 2)])

    pymel.core.button(l = "Cancel", w = 150, c = "ueExport.deleteDisplay()")

    pymel.core.button(l = "Export", w = 150, c = "ueExport.runProcess()")
    
    pymel.core.setParent('..')
    
    pymel.core.separator(h = 5, st = "none")

    pymel.core.showWindow()

'''
UI Code end
'''

# Checks if there's any animation in the asset
def checkAnimation(asset):

    print asset.namespace

    # Variable to check if animation is fasle
    isAnimated = False

    # Grab all transforms in the asset's namespace
    transforms = pymel.core.ls(asset.namespace + "*", type = "transform")

    # Loop through all transforms
    for transform in transforms:

        # If the value for isAnimated has changed, break the loop
        if isAnimated:

            break

        # Try to see if transform has a shape
        try:

            # If not, then skip
            if transform.getShape().type() == None:

                continue

        # If errors out, continue
        except:

            continue

        # Grab the shape type
        shapeType = transform.getShape().type()

        # If the shape type is a nurbsCurve
        if shapeType == "nurbsCurve":
            
            # Grab all connections
            connections = transform.listConnections()
            
            # Loop through all connections
            for connection in connections:
                
                # If the connection type is an animation curve
                if connection.type() == "animCurveTL":
                    
                    # Set isAnimated to True
                    isAnimated = True

                    # Break the loop
                    break

    return isAnimated

# Exports animation for skeltal mesh and camera
def exportAnimAsset(asset):

    # Exports the animation
    asset.exportAnimation()

# Exports meshes for static mesh
def exportMeshAsset(asset):

    # Exports the mesh
    asset.exportMesh()

# Exports meshes, skins, blendshapes, and skeleton for skeletal mesh
def exportSkelAsset(asset):

    # Exports the skeltal mesh
    asset.exportSkeletonMesh()

# Run process for UI
def runProcess():

    # Grabs the first selected item
    selectedItem = pymel.core.selected()[0]

    # Grabs the shape node of selection
    shape = UnrealExporter.utils.getShape(selectedItem)

    # Check if it's a skeletal mesh, then creates an ueAsset of it
    asset = setUnrealAssetObject(shape, selectedItem)

    # Grab export name from UI
    ueFbx = createExportFile()

    # Sets the file export name
    asset.setFileName(ueFbx)

    # Grab the class name
    assetType = asset.__class__.__name__

    # If its a skeletal mesh
    if assetType == "SkeletalMesh":

        # Check the animation
        if checkAnimation(asset):

            # Export animation
            exportAnimAsset(asset)

        # Else export the skeletal mesh
        else:

            exportSkelAsset(asset)

    # Else if its a camera
    elif assetType == "Camera":

        # Export the animation
        exportAnimAsset(asset)

    # Else, it's a static mesh
    else:

        # Export the mesh
        exportMeshAsset(asset)

    deleteDisplay()

# Checks the asset to determine the ueAsset
def setUnrealAssetObject(shape, item):

    asset = None

    # If the asset is a camera
    if shape.type() == "camera":

        # Create a camera object
        asset = UnrealExporter.ueAsset.Camera(item)

    # If the asset is a nurbsCurve or a joint
    elif shape.type() == "nurbsCurve" or shape.type() == "joint":

        # Create a skeletal mesh object
        asset = UnrealExporter.ueAsset.SkeletalMesh(item)

    # If the asset is a mesh
    elif shape.type() == "mesh":

        # Create a static mesh object
        asset = UnrealExporter.ueAsset.StaticMesh(item)

    # If it has none of those
    else:

        # Error out
        pymel.core.error("Asset could not be exported ")

    # Return the asset
    return asset
