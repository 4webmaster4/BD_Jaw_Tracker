import bpy

from bpy.props import (
    StringProperty,
    FloatProperty,
    EnumProperty,
    FloatVectorProperty,
    BoolProperty,
    IntProperty,
)

# BDJawTrackerProps group property :


class BDJawTrackerProps(bpy.types.PropertyGroup):

    # String Props :
    #########################################################################################

    UserProjectDir: StringProperty(
        name="",
        default="",
        description="Location of BDJawTracker project Directory",
        subtype="DIR_PATH",
    )

    CalibImages: StringProperty(
        name="Calibration Images path",
        default="",
        description="Location of calibration Images directory ",
        subtype="DIR_PATH",
    )

    TrackFile: StringProperty(
        name="Video Track File",
        default="",
        description="Location of tracking  Rec video file ",
        subtype="FILE_PATH",
    )

    TrackedData: StringProperty(
        name="",
        default="",
        description="Location tracked data file (.txt)",
        subtype="FILE_PATH",
    )

    UserSquareLength: FloatProperty(
        description="Square length in meters", default=0.0244, step=1, precision=4
    )
    UserMarkerLength: FloatProperty(
        description="Marker length in meters", default=0.0123, step=1, precision=4
    )

    #####################

    #Tracking_Types = ["Precision", "Precision resized(1/2)", "Fast", "Fast resized(1/2)"]
    Tracking_Types = ["Precision", "Fast resized(1/2)"]
    items = []
    for i in range(len(Tracking_Types)):
        item = (str(Tracking_Types[i]), str(Tracking_Types[i]), str(""), int(i))
        items.append(item)

    TrackingType: EnumProperty(
        items=items, description="Tracking method", default="Fast resized(1/2)"
    )


class BDJawTracker_ALIGN_Props(bpy.types.PropertyGroup):

    #############################################################################################
    # BDJawTracker_ALIGN Properties :
    #############################################################################################
    IcpVidDict: StringProperty(
        name="IcpVidDict",
        default="None",
        description="ICP Vertices Pairs str(Dict)",
    )

    #######################
    Progress_Bar: FloatProperty(
        name="Progress_Bar",
        description="Progress_Bar",
        subtype="PERCENTAGE",
        default=0.0,
        min=0.0,
        max=100.0,
        soft_min=0.0,
        soft_max=100.0,
        step=1,
        precision=1,
    )

    #######################
    AlignModalState: BoolProperty(description="Align Modal state ", default=False)

class BDJawTracker_WAXUP_Props(bpy.types.PropertyGroup):

    #############################################################################################
    # BDJawTracker_WAXUP Properties :
    #############################################################################################

    BakeLowPlane: BoolProperty(
        name="Enable or Disable Low occlusal plane baking", description="Lower occlusal plane baking", default = False        
    )

    BakeUpPlane: BoolProperty(
        name="Enable or Disable Up occlusal plane baking", description="Upper occlusal plane baking", default = False        
    )

    

#################################################################################################
# Registration :
#################################################################################################

classes = [
    BDJawTrackerProps,
    BDJawTracker_ALIGN_Props,
    BDJawTracker_WAXUP_Props,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.BDJawTrackerProps = bpy.props.PointerProperty(
        type=BDJawTrackerProps
    )
    bpy.types.Scene.BDJawTracker_ALIGN_Props = bpy.props.PointerProperty(
        type=BDJawTracker_ALIGN_Props
    )
    bpy.types.Scene.BDJawTracker_WAXUP_Props = bpy.props.PointerProperty(
        type=BDJawTracker_WAXUP_Props
    )


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.BDJawTrackerProps
    del bpy.types.Scene.BDJawTracker_ALIGN_Props
    del bpy.types.Scene.BDJawTracker_WAXUP_Props
