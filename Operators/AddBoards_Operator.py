import bpy
import os
import time

# Addon Imports :

# Global variables :

# Popup message box function :
def ShowMessageBox(message="", title="INFO", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


#######################################################################################
########################### Model Operations : Operators ##############################

#######################################################################################
# Add meshes of boards with markers
class JawTracker_OT_AddBoards(bpy.types.Operator):
    """ Add Boards """

    bl_idname = "jawtracker.addboards"
    bl_label = "Add Boards with Markers"

    def execute(self, context):
        JawTrackerProps = bpy.context.scene.JawTrackerProps
        start = time.perf_counter()
        
        #set scene units 
        Units = bpy.context.scene.unit_settings
        Units.system = 'METRIC'
        Units.scale_length = 0.001
        Units.length_unit = 'MILLIMETERS'

        
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(addon_dir, "Resources\\boards.blend")


        filepathUp = os.path.join(file_path, 'UpMarker')
        filepathLow = os.path.join(file_path, 'UpMarker')
        directory = os.path.join(file_path, 'Object')        
        filenameUp = 'UpMarker'
        filenameLow = 'LowMarker'
        
        bpy.ops.wm.append(
            filepath=filepathUp, 
            filename=filenameUp,
            directory=directory)

        bpy.ops.wm.append(
            filepath=filepathLow, 
            filename=filenameLow,
            directory=directory)
        
        ########################################################################################
        #Add Emptys

        def MoveToCollection(obj, CollName):

            OldColl = obj.users_collection  # list of all collection the obj is in
            NewColl = bpy.data.collections.get(CollName)
            if not NewColl:
                NewColl = bpy.data.collections.new(CollName)
                bpy.context.scene.collection.children.link(NewColl)
            if not obj in NewColl.objects[:]:
                NewColl.objects.link(obj)  # link obj to scene
            if OldColl:
                for Coll in OldColl:  # unlink from all  precedent obj collections
                    if Coll is not NewColl:
                        Coll.objects.unlink(obj)
        'PLAIN_AXES'

        def AddEmpty(type, name,location,radius,CollName=None):
            bpy.ops.object.empty_add(type=type, radius=radius, location=location)
            obj = bpy.context.object
            obj.name=name
            if CollName :
                MoveToCollection(obj, CollName)
                
            
        
        type = 'PLAIN_AXES'  
        radius = 10
        AddEmpty(type, "RightCond",(-50, 47, -76),radius,CollName='EmptysColl')
        AddEmpty(type, "LeftCond",(50, 47, -76),radius,CollName='EmptysColl')
        AddEmpty(type, "IncisialPoint",(0, -3, 0),radius,CollName='EmptysColl')
        bpy.ops.object.select_all(action='DESELECT')
        
        LowMarker = bpy.data.objects['LowMarker']
        Coll = bpy.data.collections.get('EmptysColl')
        CollObjects = Coll.objects
        for obj in CollObjects :
            obj.parent = LowMarker
        
        return {"FINISHED"}


#################################################################################################
# Registration :
#################################################################################################

classes = [
    JawTracker_OT_AddBoards,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
