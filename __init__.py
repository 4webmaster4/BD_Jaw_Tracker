# ----------------------------------------------------------
# File __init__.py
# ----------------------------------------------------------

#    Addon info
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
##############################################################################################
bl_info = {
    "name": "BD_Jaw_Tracker_WIN",  ###################Addon name
    "authors": "Dr.Ilya Fomenko",
    "Dr. Issam Dakir" "version": (1, 1, 0),
    "blender": (2, 90, 1),  ################# Blender working version
    "location": "3D View -> UI SIDE PANEL ",
    "description": "Blender Dental Jaw Tracker using OpenCV and aruco module",  ########### Addon description
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Dental",  ################## Addon category
}
#############################################################################################
# IMPORTS :
#############################################################################################
# Python imports :
import sys, os, bpy, subprocess, socket, time, addon_utils, zipfile, shutil
from importlib import import_module
from os.path import dirname, join, realpath, abspath, exists
from subprocess import call

if sys.platform == "win32":
    sys.stdout.reconfigure(
        encoding="cp65001"
    )  # activate unicode characters in windows CLI

#############################################################

def ImportReq(REQ_DICT):
    Pkgs = []
    for mod, pkg in REQ_DICT.items():
        try:
            import_module(mod)
        except ImportError:
            Pkgs.append(pkg)

    return Pkgs

###################################################
REQ_DICT = {
    "cv2.aruco": "opencv-contrib-python==4.4.0.46",  
}
ADDON_DIR = dirname(abspath(__file__))
REQ_DIR = join(ADDON_DIR, "Resources", "Requirements")


if not sys.path[0] == REQ_DIR :
    sys.path.insert(0, REQ_DIR)

NotFoundPkgs = ImportReq(REQ_DICT)

if NotFoundPkgs :
    ############################
    # Install Req Registration :
    ############################
    from .Operators import BDJawTracker_InstallReq
    
    def register():

        BDJawTracker_InstallReq.register()
     
    def unregister():

        BDJawTracker_InstallReq.unregister()


    if __name__ == "__main__":
        register()      

else : 
    ######################
    # Addon Registration :
    ######################

    # Addon modules imports :
    from . import BDJawTrackerProps, BDJawTrackerPanel
    from .Operators import BDJawTracker_Operators
    from .Operators import BDJawTracker_WAXUP_Operators

    addon_modules = [
        BDJawTrackerProps,
        BDJawTrackerPanel,
        BDJawTracker_Operators,
        BDJawTracker_WAXUP_Operators,
    ]
    


    def register():

        for module in addon_modules:
            module.register()
        
    def unregister():
        
        for module in reversed(addon_modules):
            module.unregister()


    if __name__ == "__main__":
        register()      

