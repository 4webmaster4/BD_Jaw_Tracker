# Python imports :
import sys, os, bpy, socket, shutil
from importlib import import_module
from os.path import dirname, join, realpath, abspath, exists
from subprocess import call


#############################################################
def ShowMessageBox(message=[], title="INFO", icon="INFO"):
    def draw(self, context):
        for txtLine in message:
            self.layout.label(text=txtLine)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

#############################################################
def isConnected():
    try:
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            print("Clossing socket")
            sock.close
        return True
    except OSError:
        pass
        return False
    
#############################################################
def ImportReq(REQ_DICT):
    Pkgs = []
    for mod, pkg in REQ_DICT.items():
        try:
            import_module(mod)
        except ImportError:
            Pkgs.append(pkg)

    return Pkgs
#############################################################
def ReqInternetInstall(path, modules):
    # Download and install requirement if not AddonPacked version:
    if sys.platform == 'darwin' :
        PythonPath = join(sys.base_exec_prefix, "bin", "python3.7m")
    if sys.platform in ['win32', 'linux'] :
        PythonPath = sys.executable
    call(
        f"{PythonPath} -m ensurepip ",
        shell=True,
    )
    call(
        f"{PythonPath} -m pip install -U pip==21.0 ",
        shell=True,
    )
    for module in modules:
        command = f' {PythonPath} -m pip install {module} --target "{path}" '
        call(command, shell=True)

#############################################################
def ReqInstall(REQ_DICT, REQ_ARCHIVE, REQ_DIR):
    
    NotFoundPkgs = ImportReq(REQ_DICT)
    print("1rst check not found modules: ",NotFoundPkgs)
    if NotFoundPkgs :
        if exists(REQ_ARCHIVE):

            shutil.unpack_archive(REQ_ARCHIVE, REQ_DIR)
            os.remove(REQ_ARCHIVE)

            print("Requirements installed from ARCHIVE!")
            message = ["Required Modules installation completed! ",
                        "Please Restart Blender"]
            ShowMessageBox(message=message, icon="COLORSET_03_VEC")
            
        else :
            if isConnected():
                
                ReqInternetInstall(path=REQ_DIR, modules=NotFoundPkgs)

                ##########################
                print("requirements Internet installation completed.")
                message = ["Required Modules installation completed! ",
                            "Please Restart Blender"]
                ShowMessageBox(message=message, icon="COLORSET_03_VEC")

            else :
                message = ["Please Check Internet Connexion and retry! "]
                ShowMessageBox(message=message, icon="COLORSET_02_VEC")
                print(message)

        
#############################################################
# Install Requirements Operators :
#############################################################

class BDJT_OT_InstallRequirements(bpy.types.Operator):
    """ Requirement installer """

    bl_idname = "bdjt.installreq"
    bl_label = "INSTALL BD_Jaw_Tracker MODULES"

    def execute(self, context):

        REQ_DICT = {
                    "cv2.aruco": "opencv-contrib-python==4.4.0.46",  
                    }
        ADDON_DIR = dirname(dirname(abspath(__file__)))
        REQ_DIR = join(ADDON_DIR, "Resources", "Requirements")

        if sys.platform == 'darwin' :
            REQ_ARCHIVE = join(REQ_DIR, "BDJT_REQ_MAC.tar.xz")
        if sys.platform == 'linux' :
            REQ_ARCHIVE = join(REQ_DIR, "BDJT_REQ_LINUX.tar.xz")
        if sys.platform == 'win32' :
            REQ_ARCHIVE = join(REQ_DIR, "BDJT_REQ_WIN.zip")

        ReqInstall(REQ_DICT, REQ_ARCHIVE, REQ_DIR)

        return {"FINISHED"}

class BDJT_PT_InstallReqPanel(bpy.types.Panel):
    """ Install Req Panel"""

    bl_idname = "BDJT_PT_InstallReqPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = "BDJ-Tracker"
    bl_label = " BLENDER DENTAL JAW TRACKER "
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("bdjt.installreq")
                               

#################################################################################################
# Registration :
#################################################################################################

classes = [
    BDJT_OT_InstallRequirements,
    BDJT_PT_InstallReqPanel,
]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
