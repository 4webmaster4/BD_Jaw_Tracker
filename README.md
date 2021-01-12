# BD_Jaw_Tracker
It is Blender add-on for tracking mandibula position from recorded video.

![alt][logo]

[logo]: ./Resources/Images/1.jpg "Screenshot from Blender with path of condule and incisial point"

## Video source
Video can be recorded on any device with focus control. We used video Ultra HD 4K (3840 x 2160) 60fps, captured on iPhone X.

## Plugin installation

1. Press Code(green button) -> Download zip
2. Start Blender 3d(you may download it from https://www.blender.org/). Go to Edit -> Preferences. In Addons tab press Install and pick BD_Jaw_Tracker-main.zip 


## Calibration
*Calibration done once, if you use only one camera and same focus distance.*

1. Print CalibrationBoard from ForPrinting directory. Stick it on flat surface of suitable size. 
2. Lock focus of your camera and remember its value.
3. Make seria of photos changing the position of the board.
4. Mesure with calipers width of single marker and width of single square. (Near 12.3 mm and 24.4 mm). Convert it to m (0.0123 m and 0.0244 m).
5. Create directory, paste there directory with captured photos.
6. In plugin menu choose Project Directory. In Calibration Images choose directory with captured photos.
7. Paste mesured marker and square width to suit fields and press Start Calibration button.

*If calibration ok, you will see "Camera Calibration OK!". You will find calibration.pckl in Project Directory. You may use this file in future trackings, if you will use same camera and same manual focus parameter.*

## Using
1. Pick Project Directory. Copy to it calibration.pckl and recorded video.
2. In Video-Track pick video for tracking and press Start Tracking button.
3. Pick Tracking data file -  txt file that you will find in project directory after tracking.
4. Press Add Boards with Markers. Align UpMarker in correct place and press Start Read Data button.
5. When progress is finished you may pick LowMarker and press Smooth Keyframes. Also you may align IncisialPoint LeftCond and RightCond in correct place and press Draw motion path.

