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

def get_object_id(ObjectIDs, Name):
    for object_def in ObjectIDs:
        if object_def[0] == Name:
            return object_def[1]

def write(filepath, context, hashlist, hash_get):
    #TODO: implement export code
    get_hash = hash_get
    IDStart = 120000000
    ObjectIDS = []
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
        IDStart += 1
        ObjectIDS.append((ob_main.name, IDStart))
    
    for ob_main in objects:
        if ob_main.type == "EMPTY": # Tag, ID, Size, HashedName
            #IDStart += 1
            ObjectID = get_object_id(ObjectIDS, ob_main.name)
            parentID = 0
            if ob_main.parent != None and ob_main.parent.name != None:
                parentID = get_object_id(ObjectIDS, ob_main.parent.name)
            sections.append(Object3DSection(get_hash, ob_main, ObjectID, parentID))
            ObjectIDS.append((ob_main.name, ObjectID))
            print(ob_main.name)
        if ob_main.type == "MESH":
            IDStart += 1
            MatID = IDStart
            active_mat_section = MaterialSection(get_hash, ob_main.active_material, MatID)
            
            IDStart += 1
            MatGroupID = IDStart
            material_group_section = MaterialGroupSection(get_hash, MatGroupID, [MatID])
            
            IDStart += 1
            GeometryID = IDStart
            geometry_section = GeometrySection(get_hash, ob_main, GeometryID)
            
            IDStart += 1
            TopologyID = IDStart
            topology_section = TopologySection(get_hash, ob_main, TopologyID)
            
            IDStart += 1
            PassthroughGPID = IDStart
            passthrough_section = PassthroughGPSection(get_hash, PassthroughGPID, GeometryID, TopologyID)
            
            IDStart += 1
            TopologyIPID = IDStart
            topology_ip_section = TopologyIPSection(get_hash, ob_main, TopologyIPID, TopologyID)
            
            ObjectID = get_object_id(ObjectIDS, ob_main.name)
            model_section = ModelSection(get_hash, ob_main, ObjectID, get_object_id(ObjectIDS, ob_main.parent.name), MatGroupID, PassthroughGPID, TopologyIPID)
            
            sections.append(material_group_section)
            sections.append(active_mat_section)
            sections.append(model_section)
            sections.append(geometry_section)
            sections.append(topology_section)
            sections.append(passthrough_section)
            sections.append(topology_ip_section)
            
            #ObjectIDS.append((ob_main.name, IDStart))
            print(ob_main.name)
        print(ob_main.name)
        print(ob_main.type)
    
    total_size = 0
    file_body = str.encode("")
    
    for section in sections:
        total_size += section[2]
        file_body += pack("<III", section[0], section[1], section[2]) + section[3]
        
    file_data = pack("<III", 4294967295, len(file_body) + 12, len(sections)) + file_body
    
    file = open(filepath, "wb")
    file.write(file_data)
    file.close()

def GeometrySection(get_hash, object, ID):
    content = pack("<i", len(object.data.vertices)) #for count
    content += pack("<i", 1) #header count
    
    vert_header = pack("<ii", 3, 1)
    
    vert_data = string.encode("")
    for vert in object.data.vertices:
        vert_data += pack("<fff", vert.co[0], vert.co[1], vert.co[2])
    
    content += pack("<Q", get_hash(object.name + ".Geometry"))
    
    return [geometry_tag, ID, len(content), content]
    
def TopologySection(get_hash, object, ID):
    content = pack("<ii", 0, 0)# stuff ~
    
    content += pack("<Q", get_hash(object.name + ".Topology")) #Hashname
    
    return [topology_tag, ID, len(content), content]
    
def PassthroughGPSection(get_hash, ID, GeometryID, TopologyID):
    content = pack("<ii", GeometryID, TopologyID)
    
    return [passthroughGP_tag, ID, len(content), content]
    
def TopologyIPSection(get_hash, object, ID, TopologyID):
    content = pack("<i", TopologyID)
    
    return [topologyIP_tag, ID, len(content), content]
    
def ModelSection(get_hash, object, ID, ParentID, MatGroupID, PassthroughGPID, TopologyIPID):
    object_3d = Object3DSection(get_hash, object, ID, ParentID)
    version = 3
    content = object_3d[3] + pack("<i", version)
    content += pack("<ii", PassthroughGPID, TopologyIPID)
    
    item_count = 0
    content += pack("<i", item_count)
    
    if item_count > 0:
        for x in range(item_count):
            #don't really know what goes on here
            content += pack("<i", 0)
            
    content += pack("<i", MatGroupID)
    
    #More stuff~
    
    return [model_data_tag, ID, len(content), content]
    
def Object3DSection(get_hash, object, ID, ParentID):
    #Object3Ds[len(Object3Ds) + 1] = {object3D_tag, random.randint(100000000, 400000000), 0, get_hash(ob_main.name)}
    # Count is number of items? So if count == 0 then it should go straight to the mat.scale?
    content = pack("<Qi", get_hash(object.name), 0)
    
    content += pack("<i", ParentID)
    
    return [object3D_tag, ID, len(content), content]
    
def MaterialGroupSection(get_hash, ID, Materials):
    content = pack("<i", len(Materials))
    for material in Materials:
        content += pack("<i", material)
    
    return [material_group_tag, ID, len(content), content]

def MaterialSection(get_hash, material, ID):
    content = pack("<Qi", get_hash(material.name), 0)
    
    return [material_tag, ID, len(content), content]
    
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
	
	
	
	
	
	
