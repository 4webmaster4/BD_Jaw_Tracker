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
import sys, os, bpy, subprocess, socket, time, addon_utils, platform
from importlib import import_module

# activate unicode characters in windows CLI :
if platform.system() == "Windows":
    sys.stdout.reconfigure(encoding="cp65001")  # set PYTHONIOENCODING=utf-8"

#############################################################
# Add sys Paths : Addon directory and requirements directory
addon_dir = os.path.dirname(os.path.abspath(__file__))
requirements_path = os.path.join(addon_dir, "Resources/Requirements")

sysPaths = [addon_dir, requirements_path]

for path in sysPaths:
    if not path in sys.path:
        sys.path.append(path)
Requirements = [
    "opencv-contrib-python==4.4.0.46"
]  # tested working versions 4.4.0.46 and 4.5.1.48 (update Jan/08/2021)
CheckList = [
    "cv2",
    "cv2.aruco",
]


# Popup message box function :
def ShowMessageBox(message=[], title="INFO", icon="INFO"):
    def draw(self, context):
        for txtLine in message:
            self.layout.label(text=txtLine)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def isConnected():
    try:
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            # print("Clossing socket")
            sock.close
        return True
    except OSError:
        pass
        return False


###########################################################################


def BlenderRequirementsPipInstall(path, modules):
    # Download and install requirement if not AddonPacked version:
    Blender_python_path = os.path.join(sys.base_exec_prefix, "bin")
    site_packages = os.path.join(Blender_python_path, "lib\\site-packages\\*.*")
    subprocess.call(
        f"cd {Blender_python_path} && python -m ensurepip ",
        shell=True,
    )
    subprocess.call(
        f"cd {Blender_python_path} && python -m pip install -U pip ",
        shell=True,
    )
    print("Blender pip upgraded")

    for module in modules:
        command = f'cd "{Blender_python_path}" && python -m pip install {module} --target "{path}"'
        subprocess.call(command, shell=True)
        print(f"{module}Downloaded and installed")

    ##########################
    print("requirements installed successfuly.")


def PipInstallModules(modules):
    Blender_python_path = os.path.join(sys.base_exec_prefix, "bin")
    site_packages = os.path.join(sys.base_exec_prefix, "lib\\site-packages")
    subprocess.call(
        f"cd {Blender_python_path} && python -m ensurepip ",
        shell=True,
    )
    subprocess.call(
        f"cd {Blender_python_path} && python -m pip install -U pip ",
        shell=True,
    )
    print("Blender pip upgraded")

    for module in modules:
        command = f'cd "{Blender_python_path}" && python -m pip install {module} --target "{site_packages}"'
        subprocess.call(command, shell=True)
        print(f"{module}Downloaded and installed")


def UninstallPipPackages(module):
    print("Uninstaling ", module)
    Blender_python_path = os.path.join(sys.base_exec_prefix, "bin")
    command = f'cd "{Blender_python_path}" && python -m pip uninstall {module}'
    subprocess.call(command, shell=True)
    print(f"{module} Uninstalled")


######################################################################################
######################################################################################
#######################################################################################
NotFoundPkgs = []
for mod in CheckList:
    try:
        import_module(mod)
    except ImportError:
        NotFoundPkgs.append(mod)

if NotFoundPkgs == []:
    print("Requirement already installed")

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

if NotFoundPkgs:
    print("Not found packages : ", NotFoundPkgs)
    ######################################################################################
    if isConnected():
        if NotFoundPkgs == ["cv2.aruco"]:
            UninstallPipPackages(module="opencv-python")
            PipInstallModules(modules=Requirements)
        if "cv2" in NotFoundPkgs:
            BlenderRequirementsPipInstall(path=requirements_path, modules=Requirements)
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

    else:

        def register():

            print("Please Check Internet Connexion and restart Blender!")

        def unregister():
            pass

        if __name__ == "__main__":
            register()
