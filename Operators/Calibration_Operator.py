import time, bpy
import os
import cv2
import numpy
import pickle
import glob
from cv2 import aruco


# Global variables :

# Popup message box function :
def ShowMessageBox(message=[], title="INFO", icon="INFO"):
    def draw(self, context):
        for txtLine in message:
            self.layout.label(text=txtLine)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


#######################################################################################
########################### Model Operations : Operators ##############################

#######################################################################################
# Test_Operator_01
class Facebow_OT_Calibration(bpy.types.Operator):
    """ Start calibration """

    bl_idname = "facebow.calibration"
    bl_label = "Start Calibration"

    def execute(self, context):
        FacebowProps = bpy.context.scene.FacebowProps
        start = time.perf_counter()

        # ChAruco board variables
        CHARUCOBOARD_ROWCOUNT = 7
        CHARUCOBOARD_COLCOUNT = 5
        ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_5X5_1000)

        # Create constants to be passed into OpenCV and Aruco methods
        CHARUCO_BOARD = aruco.CharucoBoard_create(
            squaresX=CHARUCOBOARD_COLCOUNT,
            squaresY=CHARUCOBOARD_ROWCOUNT,
            squareLength=FacebowProps.UserSquareLength,
            markerLength=FacebowProps.UserMarkerLength,
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
        # images = Facebow_Props.UserProjectDir
        # images = glob.glob(FacebowProps.UserProjectDir+'*.*')
        images = glob.glob(os.path.join(FacebowProps.CalibImages, "*"))
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
        print(FacebowProps.UserSquareLength)
        print(FacebowProps.UserMarkerLength)
        print(cameraMatrix)
        print(distCoeffs)

        # Save values to be used where matrix+dist is required, for instance for posture estimation
        # I save files in a pickle file, but you can use yaml or whatever works for you
        f = open(FacebowProps.UserProjectDir + "calibration.pckl", "wb")
        pickle.dump((cameraMatrix, distCoeffs, rvecs, tvecs), f)
        f.close()

        message = ("Calibration was unsuccessful!",)
        ShowMessageBox(message=message, title="INFO", icon="COLORSET_03_VEC")

        # Print to console our success
        print(
            "Calibration successful. Calibration file used: {}".format(
                FacebowProps.UserProjectDir + "calibration.pckl"
            )
        )

        return {"FINISHED"}


#################################################################################################
# Registration :
#################################################################################################

classes = [
    Facebow_OT_Calibration,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
