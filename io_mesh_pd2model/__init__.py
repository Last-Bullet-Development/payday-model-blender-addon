"""
Import/export Payday 2 Model File format files to Blender.

"""


bl_info = {    
    "name": "Payday Unit Import/\"Export\"",
    "author": "I am not a spy..., Zwagoth, PoueT",
    "version": (0, 1),
    "blender": (2, 68, 0),
    "location": "File > Import-Export > Payday model (.model) ",
    "description": "Import-Export Payday MODEL, Import Payday MODEL mesh, UV's, "
                   "materials",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

if "bpy" in locals():
    import imp
    if "import_pd2model" in locals():
        imp.reload(import_pd2model)
    if "export_pd2model" in locals():
        imp.reload(export_pd2model)
else:
    import bpy

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
import ctypes
import os

hashlist = {}

hllDll = None
hllDllPath = "C:\\Users\\craft\\Desktop\\Bundle Modder\\Hash64.dll"
try:
    hllDll = ctypes.CDLL(hllDllPath)
except:
    raise NameError("Could not load Hash64 dll %s" % hllDllPath)

class PD2ModelImporter(bpy.types.Operator):
    """Load PD2Model data"""
    bl_idname = "import_mesh.model"
    bl_label = "Import Payday MODEL"
    bl_options = {'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(default="*.model;*.object;*.scene", options={'HIDDEN'})

    def execute(self, context):
        from . import import_pd2model
        pd2ModelImport = import_pd2model.Pd2ModelImport()
        pd2ModelImport.read(self.filepath, hashlist)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
 
 
class PD2ModelExporter(bpy.types.Operator, ExportHelper):
    """Save PD2Model data"""
    bl_idname = "export_mesh.model"
    bl_label = "Export Payday MODEL"
    filename_ext = ".model"
    #filename_ext = ".model*.object;*.scene"
    filter_glob = StringProperty(default="*.model*.object;*.scene", options={'HIDDEN'})

    apply_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Use transformed mesh data from each object",
            default=True,
            )
    triangulate = BoolProperty(
            name="Triangulate",
            description="Triangulate quads",
            default=True,
            )
    #Add properties for email and source file
    def execute(self, context):
        from . import export_pd2model
        export_pd2model.write(self.filepath, context, hashlist, get_hash)

        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(PD2ModelImporter.bl_idname, text="Payday model (.model)")


def menu_export(self, context):
    self.layout.operator(PD2ModelExporter.bl_idname, text="Payday model (.model)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)
    HashlistPath = "C:\\Program Files (x86)\\Steam\\SteamApps\\common\\PAYDAY 2\\pdmodtool\\1.16 Beta\\hashlist"  
    with open(HashlistPath) as f:
        lines = f.read().splitlines() 
        for line in lines:
            hashcode = int(get_hash(str(line)))
            hashlist[hashcode] = line
            #print("[" + str(hashcode) + "] = " + self.dictionary[hashcode])
    
def get_hash(text):
      str_bytes = bytes(text, 'UTF8')

      hllDll.Hash.restype = ctypes.c_ulonglong
      hllDll.Hash.argtypes = [(ctypes.c_ubyte * len(str_bytes)), ctypes.c_ulonglong, ctypes.c_ulonglong]

      dll_p1 = (ctypes.c_ubyte * len(str_bytes)).from_buffer_copy(str_bytes)
      dll_p2 = ctypes.c_ulonglong (len(dll_p1))
      dll_p3 = ctypes.c_ulonglong (0)
      
      return (hllDll.Hash(dll_p1, dll_p2, dll_p3))

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
    register()
