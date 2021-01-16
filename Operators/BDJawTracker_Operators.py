import os, sys, time, bpy
from mathutils import Vector, Matrix

import cv2
import numpy as np
import cv2.aruco as aruco
import pickle
import glob
import threading

# Addon Imports :

# Global variables :

# Popup message box function :
def ShowMessageBox(message="", title="INFO", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


#######################################################################################
########################### BDJawTracker Operators ##############################
#######################################################################################

#######################################################################################
# AddBoards Operator :
#######################################################################################
class BDJawTracker_OT_AddBoards(bpy.types.Operator):
    """ will Add meshes of boards with markers """

    bl_idname = "bdjawtracker.addboards"
    bl_label = "Add Boards with Markers"

    def execute(self, context):
        BDJawTrackerProps = bpy.context.scene.BDJawTrackerProps
        start = time.perf_counter()

        # set scene grid scale
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.overlay.grid_scale = 0.001
        
        # set scene units
        Units = bpy.context.scene.unit_settings
        Units.system = "METRIC"
        Units.scale_length = 0.001
        Units.length_unit = "MILLIMETERS"

        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(addon_dir, "Resources\\boards.blend")

        filepathUp = os.path.join(file_path, "UpMarker")
        filepathLow = os.path.join(file_path, "UpMarker")
        directory = os.path.join(file_path, "Object")
        filenameUp = "UpMarker"
        filenameLow = "LowMarker"

        bpy.ops.wm.append(filepath=filepathUp, filename=filenameUp, directory=directory)

        bpy.ops.wm.append(
            filepath=filepathLow, filename=filenameLow, directory=directory
        )

        ########################################################################################
        # Add Emptys

        def MoveToCollection(obj, CollName):

            OldColl = obj.users_collection  # list of all collection the obj is in
            NewColl = bpy.data.collections.get(CollName)
            if not NewColl:
                NewColl = bpy.data.collections.new(CollName)
                bpy.context.scene.collection.children.link(NewColl)
            if not obj in NewColl.objects[:]:
                NewColl.objects.link(obj)  # link obj to scene
            if OldColl:
                for Coll in OldColl:  # unlink from all  precedent obj collections
                    if Coll is not NewColl:
                        Coll.objects.unlink(obj)

        "PLAIN_AXES"

        def AddEmpty(type, name, location, radius, CollName=None):
            bpy.ops.object.empty_add(type=type, radius=radius, location=location)
            obj = bpy.context.object
            obj.name = name
            if CollName:
                MoveToCollection(obj, CollName)

        type = "PLAIN_AXES"
        radius = 10
        AddEmpty(type, "RightCond", (-50, 47, -76), radius, CollName="EmptysColl")
        AddEmpty(type, "LeftCond", (50, 47, -76), radius, CollName="EmptysColl")
        AddEmpty(type, "IncisialPoint", (0, -3, 0), radius, CollName="EmptysColl")
        bpy.ops.object.select_all(action="DESELECT")

        LowMarker = bpy.data.objects["LowMarker"]
        Coll = bpy.data.collections.get("EmptysColl")
        CollObjects = Coll.objects
        for obj in CollObjects:
            obj.parent = LowMarker

        return {"FINISHED"}


#######################################################################################

#######################################################################################
# Calibration Operator :
#######################################################################################
class BDJawTracker_OT_Calibration(bpy.types.Operator):
    """ will check for user camera Calibration file or make new one """

    bl_idname = "bdjawtracker.calibration"
    bl_label = "Start Calibration"

    def execute(self, context):
        BDJawTrackerProps = bpy.context.scene.BDJawTrackerProps
        start = time.perf_counter()

        # ChAruco board variables
        CHARUCOBOARD_ROWCOUNT = 7
        CHARUCOBOARD_COLCOUNT = 5
        ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_5X5_1000)

        # Create constants to be passed into OpenCV and Aruco methods
        CHARUCO_BOARD = aruco.CharucoBoard_create(
            squaresX=CHARUCOBOARD_COLCOUNT,
            squaresY=CHARUCOBOARD_ROWCOUNT,
            squareLength=BDJawTrackerProps.UserSquareLength,
            markerLength=BDJawTrackerProps.UserMarkerLength,
            dictionary=ARUCO_DICT,
        )

        # Create the arrays and variables we'll use to store info like corners and IDs from images processed
        corners_all = []  # Corners discovered in all images processed
        ids_all = []  # Aruco ids corresponding to corners discovered
        image_size = None  # Determined at runtime

        # This requires a set of images or a video taken with the camera you want to calibrate
        # I'm using a set of images taken with the camera with the naming convention:
        # 'camera-pic-of-charucoboard-<NUMBER>.jpg'
        # All images used should be the same size, which if taken with the same camera shouldn't be a problem
        # images = BDJawTracker_Props.UserProjectDir
        # images = glob.glob(BDJawTrackerProps.UserProjectDir+'*.*')
        images = glob.glob(os.path.join(BDJawTrackerProps.CalibImages, "*"))
        # Loop through images glob'ed
        if images:

            for iname in images:
                # Open the image
                try:
                    img = cv2.imread(iname)

                    if not img is None:

                        # Grayscale the image
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                        # Find aruco markers in the query image
                        corners, ids, _ = aruco.detectMarkers(
                            image=gray, dictionary=ARUCO_DICT
                        )

                        # Outline the aruco markers found in our query image
                        img = aruco.drawDetectedMarkers(image=img, corners=corners)

                        # Get charuco corners and ids from detected aruco markers
                        (
                            response,
                            charuco_corners,
                            charuco_ids,
                        ) = aruco.interpolateCornersCharuco(
                            markerCorners=corners,
                            markerIds=ids,
                            image=gray,
                            board=CHARUCO_BOARD,
                        )

                        # If a Charuco board was found, let's collect image/corner points
                        # Requiring at least 20 squares
                        if response > 20:
                            # Add these corners and ids to our calibration arrays
                            corners_all.append(charuco_corners)
                            ids_all.append(charuco_ids)

                            # Draw the Charuco board we've detected to show our calibrator the board was properly detected
                            img = aruco.drawDetectedCornersCharuco(
                                image=img,
                                charucoCorners=charuco_corners,
                                charucoIds=charuco_ids,
                            )

                            # If our image size is unknown, set it now
                            if not image_size:
                                image_size = gray.shape[::-1]

                            # Reproportion the image, maxing width or height at 1000
                            proportion = max(img.shape) / 1000.0
                            img = cv2.resize(
                                img,
                                (
                                    int(img.shape[1] / proportion),
                                    int(img.shape[0] / proportion),
                                ),
                            )
                            # Pause to display each image, waiting for key press
                            cv2.imshow("Charuco board", img)
                            cv2.waitKey(1000)
                            print(f"read {os.path.split(iname)[1]} ")
                        else:
                            print(
                                "Not able to detect a charuco board in image: {}".format(
                                    os.path.split(iname)[1]
                                )
                            )
                except Exception:
                    print(f"Can't read {os.path.split(iname)[1]}")
                    pass
            # Destroy any open CV windows
            cv2.destroyAllWindows()

        # Make sure at least one image was found
        else:
            message = [
                "Calibration was unsuccessful!",
                "No valid Calibration images found,",
                "Retry with differents Calibration Images.",
            ]
            ShowMessageBox(message=message, title="INFO", icon="COLORSET_01_VEC")
            print(message)

            # Calibration failed because there were no images, warn the user
            # print(
            #     "Calibration was unsuccessful. No images of charucoboards were found. Add images of charucoboards and use or alter the naming conventions used in this file."
            # )
            # Exit for failure
            return {"CANCELLED"}

        # Make sure we were able to calibrate on at least one charucoboard by checking
        # if we ever determined the image size
        if not image_size:
            # message = "Calibration was unsuccessful. We couldn't detect charucoboards in any of the images supplied. Try changing the patternSize passed into Charucoboard_create(), or try different pictures of charucoboards."
            message = [
                "Calibration was unsuccessful!",
                "Retry with differents Calibration Images.",
            ]
            ShowMessageBox(message=message, title="INFO", icon="COLORSET_01_VEC")
            # Calibration failed because we didn't see any charucoboards of the PatternSize used
            print(message)
            # Exit for failure
            return {"CANCELLED"}

        # Now that we've seen all of our images, perform the camera calibration
        # based on the set of points we've discovered
        (
            calibration,
            cameraMatrix,
            distCoeffs,
            rvecs,
            tvecs,
        ) = aruco.calibrateCameraCharuco(
            charucoCorners=corners_all,
            charucoIds=ids_all,
            board=CHARUCO_BOARD,
            imageSize=image_size,
            cameraMatrix=None,
            distCoeffs=None,
        )

        # Print matrix and distortion coefficient to the console
        print(BDJawTrackerProps.UserSquareLength)
        print(BDJawTrackerProps.UserMarkerLength)
        print(cameraMatrix)
        print(distCoeffs)

        # Save values to be used where matrix+dist is required, for instance for posture estimation
        # I save files in a pickle file, but you can use yaml or whatever works for you
        f = open(BDJawTrackerProps.UserProjectDir + "calibration.pckl", "wb")
        pickle.dump((cameraMatrix, distCoeffs, rvecs, tvecs), f)
        f.close()

        message = ("Calibration was unsuccessful!",)
        ShowMessageBox(message=message, title="INFO", icon="COLORSET_03_VEC")

        # Print to console our success
        print(
            "Calibration successful. Calibration file used: {}".format(
                BDJawTrackerProps.UserProjectDir + "calibration.pckl"
            )
        )

        return {"FINISHED"}


#######################################################################################

#######################################################################################
# StarTrack Operator :
#######################################################################################
class BDJawTracker_OT_StarTrack(bpy.types.Operator):
    """ will write down tracking data to _DataFile.txt """

    bl_idname = "bdjawtracker.startrack"
    bl_label = "Start Tracking"

    def execute(self, context):
        BDJawTrackerProps = bpy.context.scene.BDJawTrackerProps
        start = time.perf_counter()
        resize=1
        #############################################################################################
        # create file and erase :

        with open(BDJawTrackerProps.TrackFile + "_DataFile.txt", "w+") as fw:
            fw.truncate(0)

        #############################################################################################

        # Make a dictionary of {MarkerId : corners}
        MarkersIdCornersDict = dict()
        ARUCO_PARAMETERS = aruco.DetectorParameters_create()
        ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_APRILTAG_36h11)

        if BDJawTrackerProps.TrackingType == "Precision":
            ARUCO_PARAMETERS.cornerRefinementMethod = aruco.CORNER_REFINE_APRILTAG
            resize=1
        elif BDJawTrackerProps.TrackingType == "Fast":
            ARUCO_PARAMETERS.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
            resize=1
        elif BDJawTrackerProps.TrackingType == "Precision resized(1/2)":
            ARUCO_PARAMETERS.cornerRefinementMethod = aruco.CORNER_REFINE_APRILTAG
            resize=2
        elif BDJawTrackerProps.TrackingType == "Fast resized(1/2)":
            ARUCO_PARAMETERS.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
            resize=2

        CalibFile = os.path.join(BDJawTrackerProps.UserProjectDir, "calibration.pckl")

        ##############################################################################################
        # Upper board corners
        board_corners_lower = [
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

        Board_corners_upper = [
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
        if not os.path.exists(BDJawTrackerProps.TrackFile):
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

        cap = cv2.VideoCapture(BDJawTrackerProps.TrackFile)
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
        print(BDJawTrackerProps.TrackingType)
        #############################################################################################
        Data_dict = {
            "Width": width,
            "Heihgt": height,
            "Fps": fps,
            "TrackingType": BDJawTrackerProps.TrackingType,
            "Stream": {},
        }
        while True:
            success, img = cap.read()
            imgGrey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #imgBlur = imgGrey
            imgBlur = cv2.GaussianBlur(imgGrey, (7, 7), cv2.BORDER_DEFAULT)
            if resize == 2:
                imgBlur = cv2.pyrDown(imgBlur)  # reduce the image by 2 times

            cv2.namedWindow("img", cv2.WINDOW_NORMAL)
            #cv2.namedWindow("imgBlur", cv2.WINDOW_NORMAL)

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
                    cameraMatrix/resize,
                    distCoeffs,
                    None,
                    None,
                )
                Upretval, Uprvec, Uptvec = cv2.aruco.estimatePoseBoard(
                    UpCorners,
                    UpBoard_ids,
                    UpBoard,
                    cameraMatrix/resize,
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
                        0.05
                    )
                    img = aruco.drawAxis(
                        img,
                        cameraMatrix,
                        distCoeffs,
                        Lowrvec,
                        Lowtvec,
                        0.05,
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

                    if resize == 2:
                        img = cv2.pyrDown(img)
                        img = cv2.aruco.drawDetectedMarkers(img, corners, ids, (0,255,0))
                    
                    else:
                        img = cv2.aruco.drawDetectedMarkers(img, corners, ids, (0,255,0))    

                    cv2.imshow("img", img)
                    #cv2.imshow("imgBlur", imgBlur)

                    if currentFrame == total:
                        cv2.destroyAllWindows()
                        break

            # cv2.imshow("img", img)

            if cv2.waitKey(1) & 0xFF == ord("q"):

                cv2.destroyAllWindows()
                break

        with open(BDJawTrackerProps.TrackFile + "_DataFile.txt", "a") as DataFile:
            Data = str(Data_dict)
            DataFile.write(Data)

        return {"FINISHED"}


#######################################################################################

#######################################################################################
# Data reading operator :
#######################################################################################
class BDJawTracker_OT_DataReader(bpy.types.Operator):
    """ Data reading and Transfert to Blender animation """

    bl_idname = "bdjawtracker.datareader"
    bl_label = "Start Read Data"

    def execute(self, context):
        BDJawTrackerProps = bpy.context.scene.BDJawTrackerProps
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

        def Stab_Low_function(
            UpBlender_Matrix_List, LowBlender_Matrix_List, TotalFrames
        ):

            UpStabMatrix_List, LowStabMatrix_List = [], []
            for i in range(TotalFrames):
                StabTransform = (
                    UpBlender_Matrix_List[0] @ UpBlender_Matrix_List[i].inverted()
                )
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
            Title = "BD Jaw Tracker"
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

        DataFile = BDJawTrackerProps.TrackedData  # DataFile

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
        UpBoard_Obj, LowBoard_Obj = (
            bpy.data.objects.get("UpMarker"),
            bpy.data.objects.get("LowMarker"),
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
                    args=[
                        i,
                        UpStabMatrix_List,
                        LowStabMatrix_List,
                        UpBoard_Obj,
                        LowBoard_Obj,
                    ],
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


#######################################################################################

#######################################################################################
# SmoothKeyframes operator :
#######################################################################################
class BDJawTracker_OT_SmoothKeyframes(bpy.types.Operator):
    """ will smooth animation curve """

    bl_idname = "bdjawtracker.smoothkeyframes"
    bl_label = "Smooth keyframes"

    def execute(self, context):
        BDJawTrackerProps = bpy.context.scene.BDJawTrackerProps
        start = time.perf_counter()
        active_object = bpy.context.selected_objects

        if not active_object:
            print("Pick Object!")
            self.report({"ERROR"}, "Pick Lower board!")
        else:
            current_area = bpy.context.area.type
            layer = bpy.context.view_layer

            # change to graph editor
            bpy.context.area.type = "GRAPH_EDITOR"

            # smooth curves of all selected bones
            bpy.ops.graph.smooth()

            # switch back to original area
            bpy.context.area.type = current_area
            self.report({"INFO"}, "DONE!")

        return {"FINISHED"}


#######################################################################################
# Draw or redraw motion path operator :
#######################################################################################
class BDJawTracker_OT_DrawPath(bpy.types.Operator):
    """ Draw or redraw motion path """

    bl_idname = "bdjawtracker.drawpath"
    bl_label = "Draw motion path"

    def execute(self, context):
        scene = bpy.context.scene
        JawTrackerProps = bpy.context.scene.BDJawTrackerProps
        start = time.perf_counter()
        active_object = bpy.context.selected_objects
        bpy.ops.object.paths_calculate(start_frame=scene.frame_start, end_frame=scene.frame_end)
                
        return {"FINISHED"}

#######################################################################################

# Popup message box function :
def ShowMessageBox(message=[], title="INFO", icon="INFO"):
    def draw(self, context):
        for txtLine in message:
            self.layout.label(text=txtLine)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def ShowMessageBox2(message=[], title="INFO", icon="INFO"):
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        for txtLine in message:
            row = box.row()
            row.label(text=txtLine)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def MoveToCollection(obj, CollName):

    OldColl = obj.users_collection  # list of all collection the obj is in
    NewColl = bpy.data.collections.get(CollName)
    if not NewColl:
        NewColl = bpy.data.collections.new(CollName)
        bpy.context.scene.collection.children.link(NewColl)
    if not obj in NewColl.objects[:]:
        NewColl.objects.link(obj)  # link obj to scene
    if OldColl:
        for Coll in OldColl:  # unlink from all  precedent obj collections
            if Coll is not NewColl:
                Coll.objects.unlink(obj)


def AddRefPoint(name, color, CollName=None):

    loc = bpy.context.scene.cursor.location
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=loc)
    RefP = bpy.context.object
    RefP.name = name
    RefP.data.name = name + "_mesh"
    if CollName:
        MoveToCollection(RefP, CollName)
    if name.startswith("B"):
        matName = "BaseRefMat"
    if name.startswith("M"):
        matName = "AlignRefMat"

    mat = bpy.data.materials.get(matName) or bpy.data.materials.new(matName)
    mat.diffuse_color = color
    mat.use_nodes = True
    RefP.active_material = mat
    RefP.show_name = True
    return RefP


def RefPointsToTransformMatrix(BaseRefPoints, AlignRefPoints):
    # TransformMatrix = Matrix()  # identity Matrix (4x4)

    # make 2 arrays of coordinates :
    BaseArray = np.array([obj.location for obj in BaseRefPoints], dtype=np.float64).T
    AlignArray = np.array([obj.location for obj in AlignRefPoints], dtype=np.float64).T

    # Calculate centers of Base and Align RefPoints :
    BaseCenter, AlignCenter = np.mean(BaseArray, axis=1), np.mean(AlignArray, axis=1)

    # Calculate Translation :
    ###################################

    # TransMatrix_1 : Matrix(4x4) will translate center of AlignRefPoints...
    # to origine (0,0,0) location.
    TransMatrix_1 = Matrix.Translation(Vector(-AlignCenter))

    # TransMatrix_2 : Matrix(4x4) will translate center of AlignRefPoints...
    #  to the center of BaseRefPoints location.
    TransMatrix_2 = Matrix.Translation(Vector(BaseCenter))

    # Calculate Rotation :
    ###################################

    # Home Arrays will get the Centered Base and Align RefPoints around origin (0,0,0).
    HomeBaseArray, HomeAlignArray = (
        BaseArray - BaseCenter.reshape(3, 1),
        AlignArray - AlignCenter.reshape(3, 1),
    )
    # Rigid transformation via SVD of covariance matrix :
    U, S, Vt = np.linalg.svd(np.dot(HomeBaseArray, HomeAlignArray.T))

    # rotation matrix from SVD orthonormal bases :
    R = np.dot(U, Vt)
    if np.linalg.det(R) < 0.0:
        Vt[2, :] *= -1
        R = np.dot(U, Vt)
        print(" Reflection fixed ")

    RotationMatrix = Matrix(R).to_4x4()
    TransformMatrix = TransMatrix_2 @ RotationMatrix @ TransMatrix_1

    return TransformMatrix


class BDJawTracker_OT_AlignPoints(bpy.types.Operator):
    """ Add Align Refference points """

    bl_idname = "bdjawtracker.alignpoints"
    bl_label = "ALIGN POINTS"
    bl_options = {"REGISTER", "UNDO"}

    BaseColor = (1, 0, 0, 1)  # red
    AlignColor = (0, 0, 1, 1)  # blue
    CollName = "ALIGN POINTS"
    BaseChar = "B"
    AlignChar = "A"

    def modal(self, context, event):

        ############################################
        if not event.type in {
            self.BaseChar,
            self.AlignChar,
            "DEL",
            "RET",
            "ESC",
        }:
            # allow navigation

            return {"PASS_THROUGH"}
        #########################################
        if event.type == self.BaseChar:
            # Add Base Refference point :
            if event.value == ("PRESS"):
                color = self.BaseColor
                CollName = self.CollName
                self.BaseCounter += 1
                name = f"B{self.BaseCounter}"
                RefP = AddRefPoint(name, color, CollName)
                self.BaseRefPoints.append(RefP)
                self.TotalRefPoints.append(RefP)
                bpy.ops.object.select_all(action="DESELECT")

        #########################################
        if event.type == self.AlignChar:
            # Add Base Refference point :
            if event.value == ("PRESS"):
                color = self.AlignColor
                CollName = self.CollName
                self.AlignCounter += 1
                name = f"M{self.AlignCounter}"
                RefP = AddRefPoint(name, color, CollName)
                self.AlignRefPoints.append(RefP)
                self.TotalRefPoints.append(RefP)
                bpy.ops.object.select_all(action="DESELECT")

        ###########################################
        elif event.type == ("DEL"):
            if event.value == ("PRESS"):
                if self.TotalRefPoints:
                    obj = self.TotalRefPoints.pop()
                    name = obj.name
                    if name.startswith("B"):
                        self.BaseCounter -= 1
                        self.BaseRefPoints.pop()
                    if name.startswith("M"):
                        self.AlignCounter -= 1
                        self.AlignRefPoints.pop()
                    bpy.data.objects.remove(obj)
                    bpy.ops.object.select_all(action="DESELECT")

        ###########################################
        elif event.type == "RET":

            if event.value == ("PRESS"):

                #############################################
                condition = (
                    len(self.BaseRefPoints) == len(self.AlignRefPoints)
                    and len(self.BaseRefPoints) >= 3
                )
                if not condition:
                    message = [
                        "          Please check the following :",
                        "   - The number of Base Refference points and,",
                        "       Align Refference points should match!",
                        "   - The number of Base Refference points ,",
                        "         and Align Refference points,",
                        "       should be superior or equal to 3",
                        "        <<Please check and retry !>>",
                    ]
                    ShowMessageBox(message=message, icon="COLORSET_02_VEC")
                else:
                    TransformMatrix = RefPointsToTransformMatrix(
                        self.BaseRefPoints, self.AlignRefPoints
                    )

                    self.AlignObject.matrix_world = (
                        TransformMatrix @ self.AlignObject.matrix_world
                    )
                    for obj in self.TotalRefPoints:
                        bpy.data.objects.remove(obj)

                    ##########################################################
                    bpy.context.space_data.overlay.show_outline_selected = True
                    bpy.context.space_data.overlay.show_object_origins = True
                    bpy.context.space_data.overlay.show_annotation = True
                    bpy.context.space_data.overlay.show_text = True
                    bpy.context.space_data.overlay.show_extras = True
                    bpy.context.space_data.overlay.show_floor = True
                    bpy.context.space_data.overlay.show_axis_x = True
                    bpy.context.space_data.overlay.show_axis_y = True
                    ###########################################################

                    bpy.ops.object.hide_view_clear()
                    bpy.ops.object.select_all(action="DESELECT")
                    bpy.ops.wm.tool_set_by_id(name="builtin.select")
                    bpy.context.scene.tool_settings.use_snap = False
                    bpy.context.space_data.shading.background_color = (
                        self.background_color
                    )
                    bpy.context.space_data.shading.background_type = (
                        self.background_type
                    )

                    return {"FINISHED"}

        ###########################################
        elif event.type == ("ESC"):

            if event.value == ("PRESS"):

                for RefP in self.TotalRefPoints:
                    bpy.data.objects.remove(RefP)

                ##########################################################
                bpy.context.space_data.overlay.show_outline_selected = True
                bpy.context.space_data.overlay.show_object_origins = True
                bpy.context.space_data.overlay.show_annotation = True
                bpy.context.space_data.overlay.show_text = True
                bpy.context.space_data.overlay.show_extras = True
                bpy.context.space_data.overlay.show_floor = True
                bpy.context.space_data.overlay.show_axis_x = True
                bpy.context.space_data.overlay.show_axis_y = True
                ###########################################################

                bpy.ops.object.hide_view_clear()
                bpy.ops.wm.tool_set_by_id(name="builtin.select")
                bpy.context.scene.tool_settings.use_snap = False
                bpy.ops.object.select_all(action="DESELECT")
                bpy.context.space_data.shading.background_color = self.background_color
                bpy.context.space_data.shading.background_type = self.background_type

                message = [
                    " The Align Operation was Cancelled!",
                ]

                ShowMessageBox(message=message, icon="COLORSET_03_VEC")
                return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        Condition_1 = len(bpy.context.selected_objects) != 2
        Condition_2 = bpy.context.selected_objects and not bpy.context.active_object
        Condition_3 = bpy.context.selected_objects and not (
            bpy.context.active_object in bpy.context.selected_objects
        )

        if Condition_1 or Condition_2 or Condition_3:

            message = [
                "       Selection is invalid !",
                "     Please Deselect all objects,",
                "    Select the Object to Align and ,",
                "   <SHIFT + Select> the Base Object.",
            ]
            ShowMessageBox(message=message, icon="COLORSET_02_VEC")

            return {"CANCELLED"}

        else:

            if context.space_data.type == "VIEW_3D":

                # Prepare scene  :

                self.BaseObject = bpy.context.active_object
                self.AlignObject = [
                    obj
                    for obj in bpy.context.selected_objects
                    if not obj is self.BaseObject
                ][0]

                self.BaseRefPoints = []
                self.AlignRefPoints = []
                self.TotalRefPoints = []

                self.BaseCounter = 0
                self.AlignCounter = 0
                self.background_type = bpy.context.space_data.shading.background_type
                self.background_color = bpy.context.space_data.shading.background_color

                ##########################################################
                bpy.context.space_data.overlay.show_outline_selected = False
                bpy.context.space_data.overlay.show_object_origins = False
                bpy.context.space_data.overlay.show_annotation = False
                bpy.context.space_data.overlay.show_text = False
                bpy.context.space_data.overlay.show_extras = False
                bpy.context.space_data.overlay.show_floor = False
                bpy.context.space_data.overlay.show_axis_x = False
                bpy.context.space_data.overlay.show_axis_y = False
                ###########################################################
                bpy.context.scene.tool_settings.use_snap = True
                bpy.context.scene.tool_settings.snap_elements = {"FACE"}
                bpy.context.scene.tool_settings.transform_pivot_point = (
                    "INDIVIDUAL_ORIGINS"
                )
                bpy.ops.wm.tool_set_by_id(name="builtin.cursor")
                bpy.ops.object.hide_view_set(unselected=True)
                bpy.context.space_data.shading.background_type = "VIEWPORT"
                bpy.context.space_data.shading.background_color = (0, 0, 0)

                # bpy.ops.object.select_all(action="DESELECT")
                context.window_manager.modal_handler_add(self)

                return {"RUNNING_MODAL"}

            else:

                self.report({"WARNING"}, "Active space must be a View3d")

                return {"CANCELLED"}


class BDJawTracker_OT_AlignPointsInfo(bpy.types.Operator):
    """ Align Points info """

    bl_idname = "bdjawtracker.alignpointsinfo"
    bl_label = "INFO"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        message = [
            "        Deselect all objects,",
            "      Select the Object to Align,",
            "    <SHIFT + Select> the Base Object,",
            "      Click <ALIGN POINTS> button,",
            "     <Left Click> to Place Cursor,",
            "   <Press 'B'> to Add red Point (Base),",
            "  <Press 'A'> to Add blue Point (Align),",
            "Minimum of 3 red Points, and 3 blue Points,",
            "      <Press 'DEL'> to delete Point,",
            "    <Press 'ESC'> to Cancel Operation,",
            "  <Press 'ENTER'> to execute Alignement.",
        ]
        ShowMessageBox2(message=message, title="INFO", icon="INFO")

        return {"FINISHED"}


#################################################################################################
# Registration :
#################################################################################################

classes = [
    BDJawTracker_OT_AddBoards,
    BDJawTracker_OT_Calibration,
    BDJawTracker_OT_StarTrack,
    BDJawTracker_OT_DataReader,
    BDJawTracker_OT_SmoothKeyframes,
    BDJawTracker_OT_AlignPoints,
    BDJawTracker_OT_AlignPointsInfo,
    BDJawTracker_OT_DrawPath,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
