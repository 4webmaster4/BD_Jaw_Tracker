import bpy, os

# Selected icons :
red_icon = "COLORSET_01_VEC"
orange_icon = "COLORSET_02_VEC"
green_icon = "COLORSET_03_VEC"
blue_icon = "COLORSET_04_VEC"
violet_icon = "COLORSET_06_VEC"
yellow_icon = "COLORSET_09_VEC"
yellow_point = "KEYTYPE_KEYFRAME_VEC"
blue_point = "KEYTYPE_BREAKDOWN_VEC"


class BDJAWTRACKER_PT_MainPanel(bpy.types.Panel):
    """ This Panel description """

    bl_idname = (
        "BDJAWTRACKER_PT_MainPanel"  # Not importatnt alwas the same as class name
    )
    bl_label = " BLENDER DENTAL JAW TRACKER "  # this is the title (Top panel bare)
    bl_space_type = "VIEW_3D"  # always the same if you want side panel
    bl_region_type = "UI"  # always the same if you want side panel
    bl_category = "BDJ-Tracker"  # this is the vertical name in the side usualy the name of addon :)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        col.label(text="VERSION : 2021.01.05")


class BDJAWTRACKER_PT_DataPreparation(bpy.types.Panel):
    """ This Panel description """

    bl_idname = (
        "BDJAWTRACKER_PT_DataPreparation"  # Not importatnt alwas the same as class name
    )
    bl_label = " DATA PREPARATION "  # this is the title (Top panel bare)
    bl_space_type = "VIEW_3D"  # always the same if you want side panel
    bl_region_type = "UI"  # always the same if you want side panel
    bl_category = "BDJ-Tracker"  # this is the vertical name in the side usualy the name of addon :)

    def draw(self, context):
        BDJawTracker_Props = context.scene.BDJawTrackerProps
        yellow_point = "KEYTYPE_KEYFRAME_VEC"
        red_icon = "COLORSET_01_VEC"
        green_icon = "COLORSET_03_VEC"
        CalibFile = os.path.join(BDJawTracker_Props.UserProjectDir, "calibration.pckl")
        active_object = context.active_object

        # Draw Addon UI :

        layout = self.layout

        row = layout.row()
        split = row.split()
        col = split.column()
        col.label(text="Project Directory :")
        col = split.column()
        col.prop(BDJawTracker_Props, "UserProjectDir", text="")

        ProjDir = BDJawTracker_Props.UserProjectDir
        if os.path.exists(ProjDir):

            if not os.path.exists(CalibFile):
                row = layout.row()
                split = row.split()
                col = split.column()
                col.label(text="Calibration Images :")
                col = split.column()
                col.prop(BDJawTracker_Props, "CalibImages", text="")

                row = layout.row()
                split = row.split()
                col = split.column()
                col.label(text="Square length in meters :")
                col = split.column()
                col.label(text="Marker length in meters :")

                row = layout.row()
                split = row.split()
                col = split.column()
                col.prop(BDJawTracker_Props, "UserSquareLength", text="")
                col = split.column()
                col.prop(BDJawTracker_Props, "UserMarkerLength", text="")
                row = layout.row()
                row.operator("bdjawtracker.calibration")

            else:
                layout.label(text="Camera Calibration OK!", icon=green_icon)

                row = layout.row()
                split = row.split()
                col = split.column()
                col.label(text="Video-Track :")
                col = split.column()
                col.prop(BDJawTracker_Props, "TrackFile", text="")

                row = layout.row()
                split = row.split()
                col = split.column()
                col.label(text="Tracking type :")
                col = split.column()
                col.prop(BDJawTracker_Props, "TrackingType", text="")

                row = layout.row()
                row.operator("bdjawtracker.startrack")


class BDJAWTRACKER_PT_DataRead(bpy.types.Panel):
    """ This Panel description """

    bl_idname = (
        "BDJAWTRACKER_PT_DataRead"  # Not importatnt alwas the same as class name
    )
    bl_label = " DATA READ "  # this is the title (Top panel bare)
    bl_space_type = "VIEW_3D"  # always the same if you want side panel
    bl_region_type = "UI"  # always the same if you want side panel
    bl_category = "BDJ-Tracker"  # this is the vertical name in the side usualy the name of addon :)

    def draw(self, context):

        BDJawTracker_Props = context.scene.BDJawTrackerProps
        yellow_point = "KEYTYPE_KEYFRAME_VEC"
        red_icon = "COLORSET_01_VEC"
        green_icon = "COLORSET_03_VEC"
        CalibFile = os.path.join(BDJawTracker_Props.UserProjectDir, "calibration.pckl")
        active_object = context.active_object

        layout = self.layout

        row = layout.row()
        split = row.split()
        col = split.column()
        col.label(text="Tracking data file :")
        col = split.column()
        col.prop(BDJawTracker_Props, "TrackedData", text="")

        # row.prop(BDJawTracker_Props, "TrackedData", text="Tracked data file")
        row = layout.row()
        row.operator("bdjawtracker.addboards")
        row = layout.row()
        row.operator("bdjawtracker.datareader")
        row = layout.row()
        row.operator("bdjawtracker.smoothkeyframes")
        row = layout.row()
        row.operator("bdjawtracker.drawpath")


##################################################################################
class BDJAWTRACKER_PT_AlignPanel(bpy.types.Panel):
    """ Align Tools Panel"""

    bl_idname = "BDJAWTRACKER_PT_AlignPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = "BDJ-Tracker"
    bl_label = "ALIGN TOOLS :"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        BDJawTracker_Props = context.scene.BDJawTrackerProps
        AlignModalState = BDJawTracker_Props.AlignModalState
        layout = self.layout
        row = layout.row()
        row.operator("bdjawtracker.alignpoints")
        row.operator("bdjawtracker.alignpointsinfo", text="", icon="INFO")
        if not bpy.context.selected_objects:
            self.AlignLabels = "NOTREADY"
            BaseObjectLabel = " NO Base object !"
            BaseObjectIcon = red_icon
            AlignObjectLabel = " NO Align object !"
            AlignObjectIcon = red_icon

        if len(bpy.context.selected_objects) == 1:
            self.AlignLabels = "NOTREADY"
            BaseObject = bpy.context.selected_objects[0]
            BaseObjectLabel = f" {BaseObject.name}"
            BaseObjectIcon = green_icon
            AlignObjectLabel = " NO Align object ! "
            AlignObjectIcon = red_icon

        if len(bpy.context.selected_objects) == 2:
            self.AlignLabels = "GOOD"
            BaseObject = bpy.context.active_object
            AlignObject = [
                obj
                for obj in bpy.context.selected_objects
                if not obj is bpy.context.active_object
            ][0]
            BaseObjectLabel = f" {BaseObject.name}"
            BaseObjectIcon = green_icon
            AlignObjectLabel = f" {AlignObject.name}"
            AlignObjectIcon = orange_icon

        Condition_1 = len(bpy.context.selected_objects) > 2
        Condition_2 = bpy.context.selected_objects and not bpy.context.active_object
        Condition_3 = bpy.context.selected_objects and not (
            bpy.context.active_object in bpy.context.selected_objects
        )

        if Condition_1 or Condition_2 or Condition_3:
            self.AlignLabels = "INVALID"
        if AlignModalState:
            self.AlignLabels = "MODAL"

        if self.AlignLabels in ("GOOD", "NOTREADY"):

            box = layout.box()

            row = box.row()
            row.label(text=f"BASE object :{BaseObjectLabel}", icon=BaseObjectIcon)
            row = box.row()
            row.label(text=f"ALIGN object :{AlignObjectLabel}", icon=AlignObjectIcon)

        if self.AlignLabels == "INVALID":
            box = layout.box()
            box.alert = True
            row = box.row()
            row.label(text="Invalid selection !", icon="ERROR")

        if self.AlignLabels == "MODAL":
            box = layout.box()
            box.alert = True
            row = box.row()
            row.label(text="WAITING FOR ALIGNEMENT.")


#################################################################################################
# Registration :
#################################################################################################

classes = [
    BDJAWTRACKER_PT_MainPanel,
    BDJAWTRACKER_PT_DataPreparation,
    BDJAWTRACKER_PT_DataRead,
    BDJAWTRACKER_PT_AlignPanel,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
