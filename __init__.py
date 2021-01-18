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
    "name": "BD_Jaw_Tracker",  ###################Addon name
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
import sys, os, bpy, subprocess, socket, time, addon_utils, zipfile
from importlib import import_module
from os.path import dirname, join, realpath, abspath, exists

if sys.platform == "win32":
    SS = "\\"
if sys.platform in ["darwin", "linux"]:
    SS = "/"
ADDON_DIR = dirname(abspath(__file__))
# activate unicode characters in windows CLI :
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="cp65001")

REQ_DIR = join(ADDON_DIR, join(f"Resources{SS}Requirements"))
REQ_ZIP = join(REQ_DIR, "BDJT_Req.zip")
if exists(REQ_ZIP):
    with zipfile.ZipFile(REQ_ZIP, "r") as Zip_File:
        Zip_File.extractall(REQ_DIR)
    os.remove(REQ_ZIP)
print("Requirements Unzipped!")

#############################################################

sysPaths = [ADDON_DIR, REQ_DIR]

for path in sysPaths:
    if not path in sys.path:
        sys.path.insert(0, path)

# Addon modules imports :
from . import BDJawTrackerProps, BDJawTrackerPanel
from .Operators import BDJawTracker_Operators

addon_modules = [
    BDJawTrackerProps,
    BDJawTrackerPanel,
    BDJawTracker_Operators,
]
############################################################################################
# Registration :
############################################################################################

# Registration :
def register():

    for module in addon_modules:
        module.register()


def unregister():

    for module in reversed(addon_modules):
        module.unregister()


if __name__ == "__main__":
    register()


# Requirements = {
#     "cv2.aruco": "opencv-contrib-python==4.4.0.46",
# }


# def isConnected():
#     try:
#         sock = socket.create_connection(("www.google.com", 80))
#         if sock is not None:
#             # print("Clossing socket")
#             sock.close
#         return True
#     except OSError:
#         pass
#         return False


# ###########################################################################


# def BlenderRequirementsPipInstall(path, modules):
#     # Download and install requirement if not AddonPacked version:
#     if sys.platform == "win32":
#         Blender_python_path = sys.executable
#     if sys.platform in ["darwin", "linux"]:
#         Blender_python_path = join(sys.base_exec_prefix, f"bin{SS}python3.7m")
#     subprocess.call(
#         f"{Blender_python_path} -m ensurepip ",
#         shell=True,
#     )
#     subprocess.call(
#         f"{Blender_python_path} -m pip install -U pip ",
#         shell=True,
#     )
#     print("Blender pip upgraded")

#     for module in modules:
#         command = f'{Blender_python_path} -m pip install {module} --target "{path}"'
#         subprocess.call(command, shell=True)
#         print(f"{module}Downloaded and installed")

#     ##########################
#     print("requirements installed successfuly.")


# ######################################################################################
# ######################################################################################
# #######################################################################################
# NotFoundPkgs = []
# for mod, pkg in Requirements.items():
#     try:
#         import_module(mod)
#     except ImportError:
#         NotFoundPkgs.append(pkg)

# if NotFoundPkgs == []:
#     print("Requirement already installed")

#     # Addon modules imports :
#     from . import BDJawTrackerProps, BDJawTrackerPanel
#     from .Operators import BDJawTracker_Operators

#     addon_modules = [
#         BDJawTrackerProps,
#         BDJawTrackerPanel,
#         BDJawTracker_Operators,
#     ]
#     ############################################################################################
#     # Registration :
#     ############################################################################################

#     # Registration :
#     def register():

#         for module in addon_modules:
#             module.register()

#     def unregister():

#         for module in reversed(addon_modules):
#             module.unregister()

#     if __name__ == "__main__":
#         register()

# else:

#     for pkg in NotFoundPkgs:
#         print(f"{pkg} : not installed")
#     ######################################################################################
#     if isConnected():
#         BlenderRequirementsPipInstall(path=REQ_DIR, modules=NotFoundPkgs)
#         # Addon modules imports :
#         from . import BDJawTrackerProps, BDJawTrackerPanel
#         from .Operators import BDJawTracker_Operators

#         addon_modules = [
#             BDJawTrackerProps,
#             BDJawTrackerPanel,
#             BDJawTracker_Operators,
#         ]
#         ############################################################################################
#         # Registration :
#         ############################################################################################

#         # Registration :
#         def register():

#             for module in addon_modules:
#                 module.register()

#         def unregister():

#             for module in reversed(addon_modules):
#                 module.unregister()

#         if __name__ == "__main__":
#             register()

#     else:

#         def register():

#             print("Please Check Internet Connexion and restart Blender!")

#         def unregister():
#             pass

#         if __name__ == "__main__":
#             register()
