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
class JawTracker_OT_DrawPath(bpy.types.Operator):
    """ Draw or redraw motion path """

    bl_idname = "jawtracker.drawpath"
    bl_label = "Draw motion path"

    def execute(self, context):
        scene = bpy.context.scene
        JawTrackerProps = bpy.context.scene.JawTrackerProps
        start = time.perf_counter()
        active_object = bpy.context.selected_objects
        bpy.ops.object.paths_calculate(start_frame=scene.frame_start, end_frame=scene.frame_end)
        
        
        return {"FINISHED"}


#################################################################################################
# Registration :
#################################################################################################

classes = [
    JawTracker_OT_DrawPath,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
