import bpy, os


class JawTracker_PT_PANEL(bpy.types.Panel):
    """ This Panel description """

    bl_idname = "BD_Jaw_Tracker"  # Not importatnt alwas the same as class name
    bl_label = "Jaw_Tracker"  # this is the title (Top panel bare)
    bl_space_type = "VIEW_3D"  # always the same if you want side panel
    bl_region_type = "UI"  # always the same if you want side panel
    bl_category = (
        "Jaw Tracker"  # this is the vertical name in the side usualy the name of addon :)
    )

    def draw(self, context):

        # Model operation property group :
        JawTracker_Props = context.scene.JawTrackerProps
        yellow_point = "KEYTYPE_KEYFRAME_VEC"
        red_icon = "COLORSET_01_VEC"
        green_icon = "COLORSET_03_VEC"
        CalibFile = os.path.join(JawTracker_Props.UserProjectDir, "calibration.pckl")
        active_object = context.active_object
        
        # Draw Addon UI :

        layout = self.layout

        row = layout.row()
        row.prop(JawTracker_Props, "UserProjectDir", text="JawTracker Project")
                   

        ProjDir = JawTracker_Props.UserProjectDir
        if os.path.exists(ProjDir):

            if not os.path.exists(CalibFile):

                row = layout.row()
                row.prop(JawTracker_Props, "CalibImages", text="Calibration Images")
                row = layout.row()
                row.prop(JawTracker_Props, "UserSquareLength", text="Square length in m")
                row = layout.row()
                row.prop(JawTracker_Props, "UserMarkerLength", text="Marker length in m")
                row = layout.row()
                row.operator("jawtracker.calibration", icon=green_icon)

            else:
                layout.label(text="Camera Calibration OK!", icon=green_icon)
                row = layout.row()
                row.prop(JawTracker_Props, "TrackFile", text="Video-Track")
                row = layout.row()
                row.prop(JawTracker_Props, "TrackingType", text="Tracking type")
                row = layout.row()
                row.operator("jawtracker.startrack", icon=green_icon)

        row = layout.row()
        row.prop(JawTracker_Props, "TrackedData", text="Tracked data file")
        row = layout.row()
        row.operator("jawtracker.addboards", icon=green_icon)
        row = layout.row()
        row.operator("jawtracker.datareader", icon=green_icon)
        row = layout.row()
        row.operator("jawtracker.smoothkeyframes", icon=green_icon)
        row = layout.row()
        row.operator("jawtracker.drawpath", icon=green_icon)
        


#################################################################################################
# Registration :
#################################################################################################

classes = [
    JawTracker_PT_PANEL,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
