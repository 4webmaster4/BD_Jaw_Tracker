import os, sys, time, bpy

import cv2
import numpy as np
import cv2.aruco as aruco
import pickle
import glob

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
# Tracking operator
class Facebow_OT_StarTrack(bpy.types.Operator):
    """ description of this Operator """

    bl_idname = "facebow.startrack"
    bl_label = "Start Tracking"

    def execute(self, context):
        FacebowProps = bpy.context.scene.FacebowProps
        start = time.perf_counter()
        #############################################################################################
        # create file and erase :

        with open(FacebowProps.TrackFile + "_DataFile.txt", "w+") as fw:
            fw.truncate(0)

        #############################################################################################

        # Make a dictionary of {MarkerId : corners}
        MarkersIdCornersDict = dict()
        ARUCO_PARAMETERS = aruco.DetectorParameters_create()
        ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_APRILTAG_36h11)

        if FacebowProps.TrackingType == "Precision":
            ARUCO_PARAMETERS.cornerRefinementMethod = aruco.CORNER_REFINE_APRILTAG
        else:
            ARUCO_PARAMETERS.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
        
        CalibFile = os.path.join(FacebowProps.UserProjectDir, "calibration.pckl")

        ##############################################################################################
        # Upper board corners
        Board_corners_upper = [
            np.array(
                [
                    [-0.026058, 0.018993, 0.001106],
                    [-0.012144, 0.018993, 0.010849],
                    [-0.012144, 0.002007, 0.010849],
                    [-0.026058, 0.002007, 0.001106],
                ],
                dtype=np.float32,
            ),
            np.array(
                [
                    [-0.0085, 0.019, 0.012],
                    [0.0085, 0.019, 0.012],
                    [0.0085, 0.002, 0.012],
                    [-0.0085, 0.002, 0.012],
                ],
                dtype=np.float32,
            ),
            np.array(
                [
                    [0.012144, 0.018993, 0.010849],
                    [0.026058, 0.018993, 0.001106],
                    [0.026058, 0.002007, 0.001106],
                    [0.012144, 0.002007, 0.010849],
                ],
                dtype=np.float32,
            ),
        ]
        #############################################################################################
        # Lower board corners

        board_corners_lower = [
            np.array(
                [
                    [-0.026058, -0.002007, 0.001106],
                    [-0.012144, -0.002007, 0.010849],
                    [-0.012144, -0.018993, 0.010849],
                    [-0.026058, -0.018993, 0.001106],
                ],
                dtype=np.float32,
            ),
            np.array(
                [
                    [-0.0085, -0.002, 0.012],
                    [0.0085, -0.002, 0.012],
                    [0.0085, -0.019, 0.012],
                    [-0.0085, -0.019, 0.012],
                ],
                dtype=np.float32,
            ),
            np.array(
                [
                    [0.012144, -0.002007, 0.010849],
                    [0.026058, -0.002007, 0.001106],
                    [0.026058, -0.018993, 0.001106],
                    [0.012144, -0.018993, 0.010849],
                ],
                dtype=np.float32,
            ),
        ]

        #############################################################################################

        # Initiate 2 Bords LowBord and UpBoard
        LowBoard_ids = np.array([[0], [1], [2]], dtype=np.int32)
        LowBoard = aruco.Board_create(board_corners_lower, ARUCO_DICT, LowBoard_ids)
        UpBoard_ids = np.array([[3], [4], [5]], dtype=np.int32)
        UpBoard = aruco.Board_create(Board_corners_upper, ARUCO_DICT, UpBoard_ids)

        ##############################################################################################
        if not os.path.exists(FacebowProps.TrackFile):
            message = " Invalid Track file check and retry."
            ShowMessageBox(message=message, icon="COLORSET_01_VEC")
            return {"CANCELLED"}

        if not os.path.exists(CalibFile):
            message = "calibration.pckl not found in project directory check and retry."
            ShowMessageBox(message=message, icon="COLORSET_01_VEC")
            return {"CANCELLED"}

        with open(CalibFile, "rb") as rf:
            (cameraMatrix, distCoeffs, _, _) = pickle.load(rf)
            if cameraMatrix is None or distCoeffs is None:
                message = " Invalid Calibration File. Please replace calibration.pckl or recalibrate the camera."
                ShowMessageBox(message=message, icon="COLORSET_01_VEC")
                return {"CANCELLED"}

        cap = cv2.VideoCapture(FacebowProps.TrackFile)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        totalstr = str(total)
        count = 1
        #############################################################################################
        # Text parameters
        # font
        font = cv2.FONT_HERSHEY_SIMPLEX
        # org
        org = (150, 150)
        org1 = (150, 250)
        org2 = (150, 50)
        # fontScale
        fontScale = 2
        fontScaleSmall = 1
        # Blue color in BGR
        color = (0, 255, 228)
        # Line thickness of 2 px
        thickness = 4
        thickness1 = 2
        fps = format(cap.get(cv2.CAP_PROP_FPS), ".2f")
        height = str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = str(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        print(cameraMatrix)
        print(distCoeffs)

        
        #############################################################################################
        Data_dict = {
            "Width": width,
            "Heihgt": height,
            "Fps": fps,
            "TrackingType": FacebowProps.TrackingType,
            "Stream": {},
        }
        while True:
            success, img = cap.read()
            imgGrey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgBlur = cv2.GaussianBlur(imgGrey, (11, 11), cv2.BORDER_DEFAULT)
            #imgPyrDown = cv2.pyrDown(imgBlur)  # reduce the image by 2 times

            cv2.namedWindow("img", cv2.WINDOW_NORMAL)

            # lists of ids and the corners beloning to each id
            corners, ids, rejected = aruco.detectMarkers(
                imgBlur,
                ARUCO_DICT,
                parameters=ARUCO_PARAMETERS,
                cameraMatrix=cameraMatrix,
                distCoeff=distCoeffs,
            )

            # Require 2> markers before drawing axis
            if ids is not None and len(ids) >= 6:
                for i in range(len(ids)):
                    MarkersIdCornersDict[ids[i][0]] = (list(corners))[i]

                LowCorners = [
                    MarkersIdCornersDict[0],
                    MarkersIdCornersDict[1],
                    MarkersIdCornersDict[2],
                ]
                UpCorners = [
                    MarkersIdCornersDict[3],
                    MarkersIdCornersDict[4],
                    MarkersIdCornersDict[5],
                ]

                # Estimate the posture of the board, which is a construction of 3D space based on the 2D video
                Lowretval, Lowrvec, Lowtvec = cv2.aruco.estimatePoseBoard(
                    LowCorners,
                    LowBoard_ids,
                    LowBoard,
                    cameraMatrix,
                    distCoeffs,
                    None,
                    None,
                )
                Upretval, Uprvec, Uptvec = cv2.aruco.estimatePoseBoard(
                    UpCorners,
                    UpBoard_ids,
                    UpBoard,
                    cameraMatrix,
                    distCoeffs,
                    None,
                    None,
                )

                if Lowretval and Upretval:
                    # Draw the camera posture calculated from the board
                    Data_dict["Stream"][count] = {
                        "UpBoard": [
                            (Uptvec[0, 0], Uptvec[1, 0], Uptvec[2, 0]),
                            (Uprvec[0, 0], Uprvec[1, 0], Uprvec[2, 0]),
                        ],
                        "LowBoard": [
                            (Lowtvec[0, 0], Lowtvec[1, 0], Lowtvec[2, 0]),
                            (Lowrvec[0, 0], Lowrvec[1, 0], Lowrvec[2, 0]),
                        ],
                    }
                    count += 1
                    img = aruco.drawAxis(
                        img, 
                        cameraMatrix, 
                        distCoeffs, 
                        Uprvec, 
                        Uptvec, 
                        0.1
                    )
                    img = aruco.drawAxis(
                        img,
                        cameraMatrix,
                        distCoeffs,
                        Lowrvec,
                        Lowtvec,
                        0.1,
                    )

                    
                    currentFrame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    currentFramestr = str(currentFrame)
                    perсent = currentFrame / total * 100
                    perсent = str("{0:.2f}%".format(perсent))

                    img = cv2.putText(
                        img,
                        currentFramestr + " frame of " + totalstr,
                        org,
                        font,
                        fontScale,
                        color,
                        thickness,
                        cv2.LINE_AA,
                    )
                    img = cv2.putText(
                        img,
                        perсent,
                        org1,
                        font,
                        fontScale,
                        color,
                        thickness,
                        cv2.LINE_AA,
                    )
                    img = cv2.putText(
                        img,
                        'to stop tracking press "Q"',
                        org2,
                        font,
                        fontScaleSmall,
                        color,
                        thickness1,
                        cv2.LINE_AA,
                    )

                    cv2.imshow("img", img)

                    if currentFrame == total:
                        cv2.destroyAllWindows()
                        break

            # cv2.imshow("img", img)

            if cv2.waitKey(1) & 0xFF == ord("q"):

                cv2.destroyAllWindows()
                break

        with open(FacebowProps.TrackFile + "_DataFile.txt", "a") as DataFile:
            Data = str(Data_dict)
            DataFile.write(Data)

        return {"FINISHED"}


#################################################################################################
# Registration :
#################################################################################################

classes = [
    Facebow_OT_StarTrack,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
