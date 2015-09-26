"""
This script exports PayDay 2 Model File format files to Blender.

Usage:
Execute this script from the "File->Export" menu and choose where to
save the file.

"""

import bpy
import random
from struct import pack
from struct import calcsize

random.seed()

animation_data_tag = 1572868536 # Animation data
author_tag = 1982055525 # Author tag
material_group_tag = 690449181 # Material Group
material_tag = 1012162716 # Material
object3D_tag = 268226816 # Object3D
model_data_tag = 1646341512 # Model data
geometry_tag = 2058384083 # Geometry
topology_tag = 1280342547 # Topology
passthroughGP_tag = 3819155914 # PassthroughGP
topologyIP_tag = 62272701 # TopologyIP
quatLinearRotationController_tag = 1686773868 # QuatLinearRotationController
quatBezRotationController_tag = 426984869# QuatBezRotationController
skinbones_tag = 1707874341 # SkinBones
bones_tag = 783563895 # Bones

def write(filepath, context, hashlist, hash_get):
    #TODO: implement export code
    get_hash = hash_get
    IDStart = 19000000
    sections = []
    author = "I-need-to-set-up-this-property"
    source_path = "Like-seriously"
    
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    
    scene = context.scene
    
    objects = scene.objects
    
    IDStart += 1
    sections.append(AuthorSection(get_hash, context, IDStart, author, source_path))
    
    for ob_main in objects:
        if ob_main.type == "EMPTY": # Tag, ID, Size, HashedName
            IDStart += 1
            sections.append(Object3DSection(get_hash, ob_main, IDStart))
            print(ob_main.name)
        
        print(ob_main.name)
        print(ob_main.type)
    
    total_size = 0
    file_body = str.encode("")
    
    for section in sections:
        total_size += section[2]
        file_body += pack("<III", section[0], section[1], section[2]) + section[3]
        
    file_data = pack("<III", 4294967295, total_size + 12, len(sections)) + file_body
    
    file = open(filepath, "wb")
    file.write(file_data)
    file.close()

    
def Object3DSection(get_hash, object, ID):
    #Object3Ds[len(Object3Ds) + 1] = {object3D_tag, random.randint(100000000, 400000000), 0, get_hash(ob_main.name)}
    # Count is number of items? So if count == 0 then it should go straight to the mat.scale?
    content = pack("<Qi", get_hash(object.name), 0)
    
    return [object3D_tag, ID, len(content), content]
    
def AuthorSection(get_hash, context, ID, author, source_path):

    content = pack("<Q", 0) 
    
    # Need to check if Python version is 2.7 or 3+ as pack returns string in 2.7 and byte object in 3+
    # Currently setup for 3+
    
    for char in list(author):
        content += str.encode(char)
    
    content += str.encode("\x00")
    
    for char in list(source_path):
        content += str.encode(char)
    
    content += str.encode("\x00")
    
    content += pack("<i", 0)
    
    return [author_tag, ID, len(content), content]
	
	
	
	
	
	
