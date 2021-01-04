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
    "name": "Facebow_aruco",  ###################Addon name
    "authors": "Dr.Ilya Fomenko",
    "Dr. Issam Dakir" "version": (1, 1, 0),
    "blender": (2, 90, 1),  ################# Blender working version
    "location": "3D View -> UI SIDE PANEL ",
    "description": "Facebow aruco",  ########### Addon description
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Dental",  ################## Addon category
}
#############################################################################################
# IMPORTS :
#############################################################################################
# Python imports :
import sys, os, bpy, subprocess, socket, time, addon_utils, platform

# activate unicode characters in windows CLI :
if platform.system() == "Windows":
    cmd = "chcp 65001"  # "& set PYTHONIOENCODING=utf-8"
    subprocess.call(cmd, shell=True)

#############################################################
# Add sys Paths : Addon directory and requirements directory
addon_dir = os.path.dirname(os.path.abspath(__file__))
requirements_path = os.path.join(addon_dir, "Resources/Requirements")

sysPaths = [addon_dir, requirements_path]

for path in sysPaths:
    if not path in sys.path:
        sys.path.append(path)

Requirements = ["opencv-contrib-python"]


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
    # Download and install requirement if not Addon Packed :
    Blender_python_path = sys.base_exec_prefix
    # modules = ["SimpleITK", "opencv-contrib-python", "vtk"]
    site_packages = os.path.join(Blender_python_path, "lib/site-packages/*.*")
    subprocess.call(
        f"cd {Blender_python_path} && bin\python -m ensurepip ",
        shell=True,
    )
    subprocess.call(
        f"cd {Blender_python_path} && bin\python -m pip install -U pip ",
        shell=True,
    )
    print("Blender pip upgraded")

    for module in modules:
        command = f'cd "{Blender_python_path}" && bin\python -m pip install -U {module} --target "{path}"'
        subprocess.call(command, shell=True)
        print(f"{module}Downloaded and installed")

    ##########################
    print("requirements installed successfuly.")


######################################################################################
######################################################################################
#######################################################################################

try:
    import cv2
    from cv2 import aruco

    # Addon modules imports :
    from . import FacebowProps, FacebowPanel
    from .Operators import Facebow_Operators
    from .Operators import Calibration_Operator
    from .Operators import DataReader_Operator
    from .Operators import AddBoards_Operator
    from .Operators import SmoothKeyframes_Operator
   

    addon_modules = [
        FacebowProps,
        FacebowPanel,
        Facebow_Operators,
        Calibration_Operator,
        DataReader_Operator,
        AddBoards_Operator,
        SmoothKeyframes_Operator,
        
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

except ImportError:
    ######################################################################################
    if isConnected():
        BlenderRequirementsPipInstall(path=requirements_path, modules=Requirements)
        # Addon modules imports :
        from . import FacebowProps, FacebowPanel
        from .Operators import Facebow_Operators
        from .Operators import Calibration_Operator
        from .Operators import DataReader_Operator
        from .Operators import AddBoards_Operator
        from .Operators import SmoothKeyframes_Operator

        addon_modules = [
            FacebowProps,
            FacebowPanel,
            Facebow_Operators,
            Calibration_Operator,
            DataReader_Operator,
            AddBoards_Operator,
            SmoothKeyframes_Operator,
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
