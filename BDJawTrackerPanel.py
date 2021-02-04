import bpy, os, sys
from os.path import join, dirname, exists, abspath

##########################################
if sys.platform == "win32":
    SS = "\\"
if sys.platform in ["darwin", "linux"]:
    SS = "/"
ADDON_DIR = dirname(abspath(__file__))
Addon_Version_Path = join(ADDON_DIR, f"Resources{SS}Addon_Version.txt")
with open(Addon_Version_Path, "r") as rf:
    lines = rf.readlines()
    Addon_Version_Date = lines[0].split(";")[0]
    # print(lines[0].split(";"))

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
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.alert = False
        row.alignment = "CENTER"
        row.label(text=f"VERSION : {Addon_Version_Date}")


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
        CalibFile = join(BDJawTracker_Props.UserProjectDir, "calibration.pckl")
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
        if exists(ProjDir):

            if not exists(CalibFile):
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
        CalibFile = join(BDJawTracker_Props.UserProjectDir, "calibration.pckl")
        active_object = context.active_object
        #UpJaw = bpy.data.objects['UpJaw']

        layout = self.layout

        row = layout.row()
        split = row.split()
        col = split.column()
        col.label(text="Tracking data file :")
        col = split.column()
        col.prop(BDJawTracker_Props, "TrackedData", text="")

        # row.prop(BDJawTracker_Props, "TrackedData", text="Tracked data file")
        row = layout.row()
        row.operator("bdjawtracker.setupjaw")
        if bpy.context.scene.objects.get("UpJaw") is not None:
            row.operator("bdjawtracker.setlowjaw")
        else:            
            row.alert = True
            row.alignment = "CENTER"
            row.label(text="Set UpJaw First!")
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

        BDJawTracker_ALIGN_Props = context.scene.BDJawTracker_ALIGN_Props
        AlignModalState = BDJawTracker_ALIGN_Props.AlignModalState

        layout = self.layout
        split = layout.split(factor=2 / 3, align=False)
        col = split.column()
        row = col.row()
        row.operator("bdjawtracker_align.alignpoints", text="ALIGN")
        col = split.column()
        row = col.row()
        row.alert = True
        row.operator("bdjawtracker_align.alignpointsinfo", text="INFO", icon="INFO")

        Condition_1 = len(bpy.context.selected_objects) != 2
        Condition_2 = bpy.context.selected_objects and not bpy.context.active_object
        Condition_3 = bpy.context.selected_objects and not (
            bpy.context.active_object in bpy.context.selected_objects
        )
        Condition_4 = not bpy.context.active_object in bpy.context.visible_objects

        Conditions = Condition_1 or Condition_2 or Condition_3 or Condition_4
        if AlignModalState:
            self.AlignLabels = "MODAL"
        else:
            if Conditions:
                self.AlignLabels = "INVALID"

            else:
                self.AlignLabels = "READY"

        #########################################

        if self.AlignLabels == "READY":
            TargetObjectName = context.active_object.name
            SourceObjectName = [
                obj
                for obj in bpy.context.selected_objects
                if not obj is bpy.context.active_object
            ][0].name

            box = layout.box()

            row = box.row()
            row.alert = True
            row.alignment = "CENTER"
            row.label(text="READY FOR ALIGNEMENT.")

            row = box.row()
            row.alignment = "CENTER"
            row.label(text=f"{SourceObjectName} will be aligned to, {TargetObjectName}")

        if self.AlignLabels == "INVALID" or self.AlignLabels == "NOTREADY":
            box = layout.box()
            row = box.row(align=True)
            row.alert = True
            row.alignment = "CENTER"
            row.label(text="STANDBY MODE", icon="ERROR")

        if self.AlignLabels == "MODAL":
            box = layout.box()
            row = box.row()
            row.alert = True
            row.alignment = "CENTER"
            row.label(text="WAITING FOR ALIGNEMENT...")


##################################################################################
class BDJAWTRACKER_PT_Waxup(bpy.types.Panel):
    """ WaxUp Panel"""

    bl_idname = "BDJAWTRACKER_PT_Waxup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = "BDJ-Tracker"
    bl_label = "WAXUP TOOLS :"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        BDJawTracker_WAXUP_Props = context.scene.BDJawTracker_WAXUP_Props
#        scn = bpy.context.scene
#        Occlusal_Plane = bpy.data.objects.get["Occlusal_Plane"]
#        if bpy.data.objects.get("ObjectName") is not None:
        layout = self.layout
        row = layout.row()
        row.operator("bdjawtracker.lowjawchildtolowmarker", text="Start LowJaw Movings", icon="LIBRARY_DATA_INDIRECT")

        
        layout = self.layout
        split = layout.split(factor=2 / 3, align=False)
        col = split.column()
        row = col.row()
        row.operator("bdjawtracker.addocclusalplane", text="Occlusal Plane")
        col = split.column()
        row = col.row()
#        row.alert = True
        row.operator("bdjawtracker.occlusalplaneinfo", text="INFO", icon="INFO")
        
        
        
        layout = self.layout        
        row = layout.row()
        row.prop(BDJawTracker_WAXUP_Props, "BakeLowPlane", text="Bake Lower")
        row.prop(BDJawTracker_WAXUP_Props, "BakeUpPlane", text="Bake Upper")
        Occlusal_Plane = bpy.data.objects.get("Occlusal_Plane")
        UpJaw = bpy.data.objects.get("UpJaw")
        LowJaw = bpy.data.objects.get("LowJaw")

       
        if BDJawTracker_WAXUP_Props.BakeLowPlane or BDJawTracker_WAXUP_Props.BakeUpPlane:         
            if Occlusal_Plane is not None and UpJaw is not None and LowJaw is not None:
                row = layout.row()
                row.operator("bdjawtracker.bakeplane", text="START", icon="ONIONSKIN_ON")
            
            elif Occlusal_Plane is None:
                row = layout.row()
                row.alert = True
                row.label(text="Occlusal plane is not detected!")
            elif UpJaw is None:
                row = layout.row()
                row.alert = True
                row.label(text="UpJaw is not detected!")
            elif LowJaw is None:
                row = layout.row()
                row.alert = True
                row.label(text="LowJaw is not detected!")
                
        
        


        
        
        if (BDJawTracker_WAXUP_Props.BakeLowPlane == True):
            print ("Low Enabled")
        else:
            print ("Low Disabled")

        if (BDJawTracker_WAXUP_Props.BakeUpPlane == True):
            print ("Up Enabled")
        else:
            print ("Up Disabled")
        



#################################################################################################
# Registration :
#################################################################################################

classes = [
    BDJAWTRACKER_PT_MainPanel,
    BDJAWTRACKER_PT_DataPreparation,
    BDJAWTRACKER_PT_DataRead,
    BDJAWTRACKER_PT_AlignPanel,
    BDJAWTRACKER_PT_Waxup,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
