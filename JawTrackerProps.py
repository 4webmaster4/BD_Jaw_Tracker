import bpy

from bpy.props import (
    StringProperty,
    FloatProperty,
    EnumProperty,
    FloatVectorProperty,
    BoolProperty,
    IntProperty,
)

# JawTrackerProps group property :


class JawTrackerProps(bpy.types.PropertyGroup):

    # String Props :
    #########################################################################################

    UserProjectDir: StringProperty(
        name="",
        default="",
        description="Location of JawTracker project Directory",
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
        description="Square length in meters", default=0.0382, step=1, precision=4
    )
    UserMarkerLength: FloatProperty(
        description="Marker length in meters", default=0.0192, step=1, precision=4
    )

        
    
    #####################

    Tracking_Types = ["Precision", "Fast"]
    items = []
    for i in range(len(Tracking_Types)):
        item = (str(Tracking_Types[i]), str(Tracking_Types[i]), str(""), int(i))
        items.append(item)

    TrackingType: EnumProperty(
        items=items, description="Tracking method", default="Precision"
    )


#################################################################################################
# Registration :
#################################################################################################

classes = [
    JawTrackerProps,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.JawTrackerProps = bpy.props.PointerProperty(type=JawTrackerProps)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.JawTrackerProps
