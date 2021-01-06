import bpy, threading, sys, os, math
import numpy as np
from math import degrees as deg, radians as rad, pi
from mathutils import Matrix, Vector
import cv2
import time



# Global variables :

# Popup message box function :
def ShowMessageBox(message="", title="INFO", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


#######################################################################################
########################### Model Operations : Operators ##############################

#######################################################################################
# Data reading operator
class JawTracker_OT_DataReader(bpy.types.Operator):
    """ Start data reading """

    bl_idname = "jawtracker.datareader"
    bl_label = "Start Read Data"


    def execute(self, context):
        JawTrackerProps = bpy.context.scene.JawTrackerProps
        start = time.perf_counter()

        def DataToCvMatrix(DataFile):

            UpCvMatrix_List, LowCvMatrix_List = [], []

            with open(DataFile, "r") as DataRead:
                Data = DataRead.read()
                Data_dict = eval(Data)

            width = Data_dict["Width"]
            heihgt = Data_dict["Heihgt"]
            fps = Data_dict["Fps"]
            TrackingType = Data_dict["TrackingType"]
            Stream = Data_dict["Stream"]

            for k, v in Stream.items():
                FrameNumber = k
                FrameData = v

                UpBoard_tvec, UpBoard_rvec = (
                    Vector(FrameData["UpBoard"][0]) * 1000,
                    FrameData["UpBoard"][1],
                )
                LowBoard_tvec, LowBoard_rvec = (
                    Vector(FrameData["LowBoard"][0]) * 1000,
                    FrameData["LowBoard"][1],
                )

                UpRotMat, LowRotMat = Matrix(cv2.Rodrigues(UpBoard_rvec)[0]), Matrix(
                    cv2.Rodrigues(LowBoard_rvec)[0]
                )

                UpCvMatrix = UpRotMat.to_4x4()
                UpCvMatrix[0][3], UpCvMatrix[1][3], UpCvMatrix[2][3] = UpBoard_tvec
                UpCvMatrix_List.append(UpCvMatrix)

                LowCvMatrix = LowRotMat.to_4x4()
                LowCvMatrix[0][3], LowCvMatrix[1][3], LowCvMatrix[2][3] = LowBoard_tvec
                LowCvMatrix_List.append(LowCvMatrix)

            TotalFrames = len(UpCvMatrix_List)

            return (
                width,
                heihgt,
                fps,
                TrackingType,
                TotalFrames,
                UpCvMatrix_List,
                LowCvMatrix_List,
            )


        def Blender_Matrix(
            UpBoard_Obj,
            LowBoard_Obj,
            UpCvMatrix_List,
            LowCvMatrix_List,
            TotalFrames,
            Stab=False,
        ):

            UpBoard_Aligned = UpBoard_Obj.matrix_world.copy()
            LowBoard_Aligned = LowBoard_Obj.matrix_world.copy()

            Transform = UpBoard_Aligned @ UpCvMatrix_List[0].inverted()

            UpBlender_Matrix_List, LowBlender_Matrix_List = [], []

            for i in range(TotalFrames):
                UpBlender_Matrix = Transform @ UpCvMatrix_List[i]
                LowBlender_Matrix = Transform @ LowCvMatrix_List[i]

                UpBlender_Matrix_List.append(UpBlender_Matrix)
                LowBlender_Matrix_List.append(LowBlender_Matrix)
            if not Stab:
                return UpBlender_Matrix_List, LowBlender_Matrix_List
            else:
                UpStabMatrix_List, LowStabMatrix_List = Stab_Low_function(
                    UpBlender_Matrix_List, LowBlender_Matrix_List, TotalFrames
                )
                return UpStabMatrix_List, LowStabMatrix_List


        def Stab_Low_function(UpBlender_Matrix_List, LowBlender_Matrix_List, TotalFrames):

            UpStabMatrix_List, LowStabMatrix_List = [], []
            for i in range(TotalFrames):
                StabTransform = UpBlender_Matrix_List[0] @ UpBlender_Matrix_List[i].inverted()
                LowStabMatrix = StabTransform @ LowBlender_Matrix_List[i]

                UpStabMatrix_List.append(UpBlender_Matrix_List[0])
                LowStabMatrix_List.append(LowStabMatrix)

            return UpStabMatrix_List, LowStabMatrix_List


        def MatrixToAnimation(i, UpMtxList, lowMtxList, UpBoard_Obj, LowBoard_Obj):
            Offset = 1
            UpBoard_Obj.matrix_world = UpMtxList[i]
            UpBoard_Obj.keyframe_insert("location", frame=i * Offset)
            UpBoard_Obj.keyframe_insert("rotation_quaternion", frame=i * Offset)

            LowBoard_Obj.matrix_world = lowMtxList[i]
            LowBoard_Obj.keyframe_insert("location", frame=i * Offset)
            LowBoard_Obj.keyframe_insert("rotation_quaternion", frame=i * Offset)

            print(f"Keyframe {i} added..")


        def progress_bar(counter, n, Delay):

            X, Y = WindowWidth, WindowHeight = (500, 100)
            BackGround = np.ones((Y, X, 3), dtype=np.uint8) * 255
            Title = "JawTracker progress"
            # Progress bar Parameters :
            maxFill = X - 70
            minFill = 40
            barColor = (50, 200, 0)
            BarHeight = 20
            barUp = Y - 60
            barBottom = barUp + BarHeight
            # Text :
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 0.5
            fontThikness = 1
            fontColor = (0, 0, 0)
            lineStyle = cv2.LINE_AA

            chunk = (maxFill - 40) / n

            img = BackGround.copy()
            fill = minFill + int(counter * chunk)
            pourcentage = int(counter * 100 / n)
            img[barUp:barBottom, minFill:fill] = barColor

            img = cv2.putText(
                img,
                f"{pourcentage}%",
                (maxFill + 10, barBottom - 8),
                # (fill + 10, barBottom - 10),
                font,
                fontScale,
                fontColor,
                fontThikness,
                lineStyle,
            )

            img = cv2.putText(
                img,
                "Processing...",
                (minFill, barUp - 10),
                font,
                fontScale,
                fontColor,
                fontThikness,
                lineStyle,
            )
            img = cv2.putText(
                img,
                f"Frame {i}/{n}...",
                (minFill, barBottom + 20),
                font,
                fontScale,
                fontColor,
                fontThikness,
                lineStyle,
            )
            cv2.imshow(Title, img)

            cv2.waitKey(Delay)
            # cv2.destroyAllWindows()
            counter += 1

            # if i == n - 1:
            if counter == n:
                img = BackGround.copy()
                img[barUp:barBottom, minFill:maxFill] = (50, 200, 0)
                img = cv2.putText(
                    img,
                    "100%",
                    (maxFill + 10, barBottom - 8),
                    font,
                    fontScale,
                    fontColor,
                    fontThikness,
                    lineStyle,
                )

                img = cv2.putText(
                    img,
                    "Finished.",
                    (minFill, barUp - 10),
                    font,
                    fontScale,
                    fontColor,
                    fontThikness,
                    lineStyle,
                )
                img = cv2.putText(
                img,
                f"Total Frames added : {n}",
                (minFill, barBottom + 20),
                font,
                fontScale,
                fontColor,
                fontThikness,
                lineStyle,
                )
                cv2.imshow(Title, img)
                cv2.waitKey(3000)
                cv2.destroyAllWindows()


        ########################################################################################
        ######################################################################################

        DataFile = JawTrackerProps.TrackedData  # DataFile

        (
            width,
            heihgt,
            fps,
            TrackingType,
            TotalFrames,
            UpCvMatrix_List,
            LowCvMatrix_List,
        ) = DataToCvMatrix(DataFile)

        # point to the 2 boards here :
        UpBoard_Obj, LowBoard_Obj = bpy.data.objects.get("UpMarker"), bpy.data.objects.get(
            "LowMarker"
        )

        if UpBoard_Obj and LowBoard_Obj:
            UpStabMatrix_List, LowStabMatrix_List = Blender_Matrix(
                UpBoard_Obj,
                LowBoard_Obj,
                UpCvMatrix_List,
                LowCvMatrix_List,
                TotalFrames,
                Stab=True,
            )

            for obj in [UpBoard_Obj, LowBoard_Obj]:
                obj.animation_data_clear()
                obj.rotation_mode = "QUATERNION"

            for i in range(TotalFrames):
                t = threading.Thread(
                    target=MatrixToAnimation,
                    args=[i, UpStabMatrix_List, LowStabMatrix_List, UpBoard_Obj, LowBoard_Obj],
                    daemon=True,
                )
                t.start()
                t.join()
                progress_bar(i, TotalFrames, 1)
            Start = 0
            Offset = 1 
            bpy.context.scene.frame_start = Start
            End = (TotalFrames - 1) * Offset
            bpy.context.scene.frame_end = End
            bpy.context.scene.frame_current = 0
            bpy.context.scene.render.fps = float(fps)
            print(float(fps))

            
            return {"FINISHED"}

#################################################################################################
# Registration :
#################################################################################################

classes = [
    JawTracker_OT_DataReader,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)