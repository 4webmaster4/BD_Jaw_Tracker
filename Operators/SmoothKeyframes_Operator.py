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
class Facebow_OT_SmoothKeyframes(bpy.types.Operator):
    """ Pick Lower Board """

    bl_idname = "facebow.smoothkeyframes"
    bl_label = "Smooth keyframes"

    def execute(self, context):
        FacebowProps = bpy.context.scene.FacebowProps
        start = time.perf_counter()
        active_object = bpy.context.selected_objects
        

        if not active_object:
            print("Pick Object!")
            self.report({'ERROR'}, "Pick Lower board!")
        else:
            current_area = bpy.context.area.type
            layer = bpy.context.view_layer
            
            # change to graph editor
            bpy.context.area.type = "GRAPH_EDITOR"

            # smooth curves of all selected bones
            bpy.ops.graph.smooth()

            # switch back to original area
            bpy.context.area.type = current_area
            self.report({'INFO'}, "DONE!")
                
        
        
        return {"FINISHED"}


#################################################################################################
# Registration :
#################################################################################################

classes = [
    Facebow_OT_SmoothKeyframes,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
