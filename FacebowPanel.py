import bpy, os


class FACEBOW_PT_PANEL(bpy.types.Panel):
    """ This Panel description """

    bl_idname = "FACEBOW_PT_ARUCO"  # Not importatnt alwas the same as class name
    bl_label = "Facebow"  # this is the title (Top panel bare)
    bl_space_type = "VIEW_3D"  # always the same if you want side panel
    bl_region_type = "UI"  # always the same if you want side panel
    bl_category = (
        "Facebow"  # this is the vertical name in the side usualy the name of addon :)
    )

    def draw(self, context):

        # Model operation property group :
        FACEBOW_Props = context.scene.FacebowProps
        yellow_point = "KEYTYPE_KEYFRAME_VEC"
        red_icon = "COLORSET_01_VEC"
        green_icon = "COLORSET_03_VEC"
        CalibFile = os.path.join(FACEBOW_Props.UserProjectDir, "calibration.pckl")
        active_object = context.active_object
        
        # Draw Addon UI :

        layout = self.layout

        row = layout.row()
        row.prop(FACEBOW_Props, "UserProjectDir", text="FaceBow Project")
                   

        ProjDir = FACEBOW_Props.UserProjectDir
        if os.path.exists(ProjDir):

            if not os.path.exists(CalibFile):

                row = layout.row()
                row.prop(FACEBOW_Props, "CalibImages", text="Calibration Images")
                row = layout.row()
                row.prop(FACEBOW_Props, "UserSquareLength", text="Square length in m")
                row = layout.row()
                row.prop(FACEBOW_Props, "UserMarkerLength", text="Marker length in m")
                row = layout.row()
                row.operator("facebow.calibration", icon=green_icon)

            else:
                layout.label(text="Camera Calibration OK!", icon=green_icon)
                row = layout.row()
                row.prop(FACEBOW_Props, "TrackFile", text="Video-Track")
                row = layout.row()
                row.prop(FACEBOW_Props, "TrackingType", text="Tracking type")
                row = layout.row()
                row.operator("facebow.startrack", icon=green_icon)

        row = layout.row()
        row.prop(FACEBOW_Props, "TrackedData", text="Tracked data file")
        row = layout.row()
        row.operator("facebow.addboards", icon=green_icon)
        row = layout.row()
        row.operator("facebow.datareader", icon=green_icon)
        row = layout.row()
        row.operator("facebow.smoothkeyframes", icon=green_icon)
        


#################################################################################################
# Registration :
#################################################################################################

classes = [
    FACEBOW_PT_PANEL,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
