'''
The ueAsset module of the UnrealExporter package
'''

# Import statements
import pymel.core
import os

# Import utils module from UnrealExporter package
import UnrealExporter.utils

# Standard Unreal Asset class
class UnrealAsset:

    def __init__(self, node):

        # Get the initial namespace, nodeType, shape, name, and referenceFile
        self.namespace = node.namespace()
        self.objType = node.type()
        self.objShape = node.getShape()
        self.name = node.name()
        self.refFile = node.referenceFile()

    # Exports the fbx
    def export(self):

        pymel.core.mel.FBXExport(s = True,f = self.exportFilePath)

    # Imports the reference
    def importReference(self):

        # As long as there is a reference file
        if self.refFile != None:

            # Import the reference
            self.refFile.importContents()

    # Set the filename for the export
    # NOTE: needs a ".fbx" at the end
    def setFileName(self, fileName):

        self.exportFilePath = fileName

# Skeletal Mesh class, inherents from UnrealAsset
class SkeletalMesh(UnrealAsset):

    def __init__(self, node):

        # Get initial elements
        UnrealAsset.__init__(self, node)

        # Gets skinClusters, geometry, skeleton, root joint, 
        # blendshapes, blendshape targets, constraints
        self.skins = self.getSkins()
        self.geometry = self.getMeshes()
        self.skeleton = self.getSkeleton()
        self.root = self.getRoot()
        self.blendShapes = self.getBlendshapes()
        self.bsMeshes = self.getBlendshapeGeo()
        self.constraints = self.getConstraints()

    # Bakes external constraints on the rig
    # e.g. object interaction
    def bakeConstraints(self):

        # Gets start and end time
        startTime = UnrealExporter.utils.getStartTime()
        endTime = UnrealExporter.utils.getEndTime()

        # If there are constraints...
        if self.constraints:

            # Bake only the translate and rotate attributes
            attrs = ['tx',
                'ty',
                'tz',
                'rx',
                'ry',
                'rz'
                ]

            # And bake it
            UnrealExporter.utils.bakeThis(self.constraints,
                                            simulation = True, 
                                            time = (startTime, endTime), 
                                            sampleBy  = True, 
                                            disableImplicitControl = True, 
                                            preserveOutsideKeys = False,
                                            sparseAnimCurveBake = False,
                                            removeBakedAnimFromLayer = False, 
                                            bakeOnOverrideLayer = False,
                                            minimizeRotation = True, 
                                            controlPoints = False,
                                            shape = True)

    # Exports the animation for the skeletal mesh
    def exportAnimation(self):

        # Prep the export
        self.prepExport()

        # Set the export options
        UnrealExporter.utils.setGeneralExportOptions()
        UnrealExporter.utils.setAnimExportOptions()

        # Clears the selection
        pymel.core.select(clear = True)

        # Then select the skeleton, blendshapes, root, blendshape targets, and geometry
        pymel.core.select(self.skeleton, 
                    self.blendShapes, 
                    self.root, 
                    self.bsMeshes, 
                    self.geometry)

        # Then exports the file
        self.export()

    # Exports the skeleton mesh
    def exportSkeletonMesh(self):

        # Prep the export
        self.prepExport()

        # Set the export options
        UnrealExporter.utils.setGeneralExportOptions()
        UnrealExporter.utils.setMeshExportOptions()
        UnrealExporter.utils.setTextureExportOptions()
        UnrealExporter.utils.setAnimExportOptions()

        # Clear the selection
        pymel.core.select(clear = True)

        # Then select the skeleton, blendshapes, root, blendshape targets, and geometry
        pymel.core.select(self.skeleton, 
                    self.blendShapes, 
                    self.geometry, 
                    self.root, 
                    self.bsMeshes)

        # Then exports the file
        self.export()

    # Gets the blendshapes from the skeletal mesh
    def getBlendshapes(self):

        # Create an array for the blendshapes
        blendshapes = []

        # Loop through all the meshes in the skeletal mesh
        for mesh in self.geometry:

            # Grab all blendshape connections to the mesh
            meshBlends = mesh.listHistory(type = "blendShape")

            # If there are blendshapes...
            # And the blendshapes are already not recorded...
            if meshBlends and meshBlends not in blendshapes:
            
                # Add blendshape to the blendshape list
                blendshapes.extend(meshBlends)
        
        return blendshapes

    # Gets the blendshape target geometry
    def getBlendshapeGeo(self):

        # Create an array for the blendshape geo
        tgtMeshes = []

        # loop through all blendshapes
        for blendshape in self.blendShapes:

            # Add the target geo to the target mesh array
            tgtMeshes.extend(blendshape.getTarget())

        return tgtMeshes

    # Gets all external constraints
    def getConstraints(self):

        # Gets the absolute top node of the entire rig
        topNode = self.root.getParent(generations = -1)

        # Gets the topNode namespace
        topNodeNS = topNode.namespace()

        # Grab all children on the top node
        allChildren = topNode.listRelatives(ad = True)

        # Create an empty array for the constraints
        constraints = []

        # Loop through all the children
        for child in allChildren:
            
            # If the child has the same namespace as the top node....
            # Skip it
            if child.namespace() == topNodeNS:
                
                continue        
            
            # Also if the child is not a constraint
            # Skip it
            if "Constraint" not in child.type():
                
                continue
            
            # Add the constraint to the array
            constraints.append(child)
        
        return constraints

    # Get all meshes in the skeletal mesh
    def getMeshes(self):

        # Create an empty array for the skinnedMeshes
        skinnedMeshes = []

        # Grab skins
        skins = self.skins

        # Loop through skins
        for skin in skins:
            
            # Grab the geometry
            defMeshes = skin.getGeometry()

            # Loop through all geo
            for defMesh in defMeshes:

                # If the geo is not polygons
                # Skip it
                if defMesh.type() != "mesh":

                    continue

                # If the geo is not visible
                # Skip it
                elif defMesh.isVisible() != True:

                    continue

                # Add the mesh into skinMeshes
                skinnedMeshes.append(defMesh)

        return skinnedMeshes

    # Get the root joint 
    # Code from Jason Breneman - check readme for link
    def getRoot(self):
    
        rootJoint = self.skeleton[0]

        while (True):
            parent = rootJoint.listRelatives(
                                         parent=True,
                                         type='joint' )
            if not parent:
                break;

            rootJoint = parent[0]

        return rootJoint 
    
    # Get the skeleton for the skeletal mesh
    def getSkeleton(self):

        # Create an empty array for skinned joints
        skinnedJoints = []

        # Grab all joints in skeletal mesh namespace
        joints = pymel.core.ls(self.namespace + "*", type = "joint")

        # Loop through all joints
        for joint in joints:

            # See if there are any connections to skinclusters
            skins = joint.listConnections(type = "skinCluster")
            
            # If there are no skins...
            # Skip it
            if len(skins) <= 0:
                
                continue

            # Add joints to array
            skinnedJoints.append(joint)

        # If there are no joints...
        if len(skinnedJoints) <= 0:

            # Error out because um... can't have skeletal mesh w/o bones
            pymel.core.error("No Skeleton/Bones found for Skeletal Mesh Asset")

        return skinnedJoints

    # Get skin clusters
    def getSkins(self):

        # Get all skin clusters based off of namespace
        skins = pymel.core.ls(self.namespace + "*", type = "skinCluster")

        return skins

    # Prep the export
    def prepExport(self):

        # Get start and end times
        startTime = UnrealExporter.utils.getStartTime()
        endTime = UnrealExporter.utils.getEndTime()

        # Bake constraints
        self.bakeConstraints()

        # Clear the selection
        pymel.core.select(clear = True)

        # Select blendshape, skeleton, and the root
        pymel.core.select(self.blendShapes, self.skeleton, self.root)

        # Bake the selection
        UnrealExporter.utils.bakeThis(None,
                                        simulation = True, 
                                        time = (startTime, endTime), 
                                        sampleBy  = True, 
                                        disableImplicitControl = True, 
                                        preserveOutsideKeys = False,
                                        sparseAnimCurveBake = False,
                                        removeBakedAnimFromLayer = False, 
                                        bakeOnOverrideLayer = False,
                                        minimizeRotation = True, 
                                        controlPoints = False,
                                        shape = True)

        # Euler filter the selection
        UnrealExporter.utils.eulerFilter()

        # Import the reference
        self.importReference()

        # Unparent the root
        self.root.setParent(world = True)

        UnrealExporter.utils.deleteChildrenNodeType(self.root, "joint")

# Static Mesh class, inherents from UnrealAsset
class StaticMesh(UnrealAsset):

    def __init__(self, node):

        # Get initial elements
        UnrealAsset.__init__(self, node)

        # Get the geometry and the transform root
        self.geometry = self.getMeshes()
        self.root = self.getRoot()

    # Create root
    def createRoot(self):

        # Create the reference locator name
        refLocName = self.name + "_srt"

        # Create the locator
        root = UnrealExporter.utils.createLocator(refLocName)

        return root

    # Exports the mesh
    def exportMesh(self):

        # Clears the selection
        pymel.core.select(clear = True)

        # Selects the root and the geometry
        pymel.core.select(self.root, self.geometry)

        # Imports the reference
        self.importReference()

        # Set the export options
        UnrealExporter.utils.setGeneralExportOptions()
        UnrealExporter.utils.setMeshExportOptions()

        # Exports the mesh
        self.export()

    # Get the meshes
    def getMeshes(self):

        # If there isnt a namespace...
        if self.namespace == "":

            # Return an array of the object's shape
            return [self.objShape]

        # Return all meshes in namespace
        return pymel.core.ls(self.namespace + "*", type = "mesh")

    # Gets the root
    def getRoot(self):

        # If there isnt a namespace...
        if self.namespace == "":

            # Return their root
            return self.setRoot()

        # Get all locators in namespace
        locs = pymel.core.ls(self.namespace + "*", type = "locator")

        # If locators exist
        if locs:

            # Get the parent of the shape of the first locator
            return locs[0].getParent()

        else:

            # Return their root
            return self.setRoot()

    # Set Root
    def setRoot(self):

        # Create root
        rootLoc = self.createRoot()

        # Loop through meshes
        for mesh in self.geometry:

            # Get the parent of the shape
            meshSRT = mesh.getParent()

            # Set the parent of the root locator
            meshSRT.setParent(rootLoc)

        return rootLoc

# Camera class, inherents from UnrealAsset
class Camera(UnrealAsset):

    def __init__(self, node):

        # Get inital elements
        UnrealAsset.__init__(self, node)

        # Set camera transform to selection
        self.camTransform = node

    # Exports the animation for the camera
    def exportAnimation(self):

        # Set the export
        self.prepExport()

        # Set the export options
        UnrealExporter.utils.setGeneralExportOptions()
        UnrealExporter.utils.setCamExportOptions()

        # Export
        self.export()

    # Move keyframes to zero
    def moveKeysToFrameZero(self):

        # Moves the keyframes of any object to frame 0
        object = self.camExport

        # Get keyframes from object
        keyFrames = pymel.core.keyframe(object, q = True)

        # Get the first key
        firstKey = keyFrames[0]

        # Move first key (which will move everything else) to frame 0
        pymel.core.keyframe(object, edit = True, relative = True, tc = (-1*firstKey))

    # Process through for export
    def prepExport(self):

        dupCam = pymel.core.camera()[0]

        dupCamPC = pymel.core.parentConstraint(self.camTransform, dupCam, weight = 1, mo = 0)

        # Get start and end times
        startTime = UnrealExporter.utils.getStartTime()
        endTime = UnrealExporter.utils.getEndTime()

        dupCam.select(r = True)

        # Bake the camera animation
        UnrealExporter.utils.bakeThis(None,
                                        simulation = True, 
                                        time = (startTime, endTime), 
                                        sampleBy  = True, 
                                        disableImplicitControl = True, 
                                        preserveOutsideKeys = False,
                                        sparseAnimCurveBake = False,
                                        removeBakedAnimFromLayer = False, 
                                        bakeOnOverrideLayer = False,
                                        minimizeRotation = True, 
                                        controlPoints = False,
                                        shape = True)

        # Reset the baking
        UnrealExporter.utils.resetBake()

        # Duplicate the camera
        ueCam = pymel.core.duplicate(dupCam, returnRootsOnly = True, inputConnections = True)[0]

        # Rename it
        ueCam.rename("UE_" + self.name)

        # Set camera for export to duplicated camera
        self.camExport = ueCam

        # Group camera
        camGrp = pymel.core.group(empty = True)

        # Set the parent of camera to group
        self.camTransform.setParent(camGrp)

        # Parent constrain camera to new camera
        ueCamPC = pymel.core.parentConstraint(self.camTransform, ueCam, weight = 1)

        # Offset the rotation for export
        ueCamPC.setAttr("target[0].targetOffsetRotateY", 90)

        # Select the camera for baking
        ueCam.select()

        # Bake the camera animation
        UnrealExporter.utils.bakeThis(None,
                                        simulation = True, 
                                        time = (startTime, endTime), 
                                        sampleBy  = True, 
                                        disableImplicitControl = True, 
                                        preserveOutsideKeys = False,
                                        sparseAnimCurveBake = False,
                                        removeBakedAnimFromLayer = False, 
                                        bakeOnOverrideLayer = False,
                                        minimizeRotation = True, 
                                        controlPoints = False,
                                        shape = True)

        # Euler Filter the animation curves
        UnrealExporter.utils.eulerFilter()

        # Reset the baking
        UnrealExporter.utils.resetBake()

        # Delete the group
        pymel.core.delete(camGrp)

        # Delete the duplicate camera
        pymel.core.delete(dupCam)

        # Move the keyframes to frame 0 for export
        self.moveKeysToFrameZero()