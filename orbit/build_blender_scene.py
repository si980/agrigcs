# pyrefly: ignore [missing-import]
import bpy
import os
import math
import random

# Clear existing objects
bpy.ops.wm.read_factory_settings(use_empty=True)

dir_path = os.path.dirname(os.path.abspath(__file__))
tex_strata_path = os.path.join(dir_path, "tex_soil_strata.jpg")
tex_corn_path = os.path.join(dir_path, "tex_corn_canopy.jpg")
tex_kale_path = os.path.join(dir_path, "tex_kale_dry_soil.jpg")
tex_soy_path = os.path.join(dir_path, "tex_soy_rows.jpg")
tex_solar_path = os.path.join(dir_path, "tex_solar_mast.jpg")

# Helper to create textured material
def create_image_mat(name, img_path, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = metallic
    
    if os.path.exists(img_path):
        img = bpy.data.images.load(img_path)
        node_tex = nodes.new(type='ShaderNodeTexImage')
        node_tex.image = img
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
    else:
        node_bsdf.inputs['Base Color'].default_value = (0.2, 0.15, 0.1, 1.0)
        
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

def create_color_mat(name, color, roughness=0.5, metallic=0.0, emission=None, alpha=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = color
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = metallic
    
    if emission:
        # In Blender 4/5 Principled BSDF has Emission Color and Strength
        if 'Emission Color' in node_bsdf.inputs:
            node_bsdf.inputs['Emission Color'].default_value = emission
            node_bsdf.inputs['Emission Strength'].default_value = 3.0
        elif 'Emission' in node_bsdf.inputs:
            node_bsdf.inputs['Emission'].default_value = emission
            
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        if 'Alpha' in node_bsdf.inputs:
            node_bsdf.inputs['Alpha'].default_value = alpha
        if 'Transmission Weight' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission Weight'].default_value = 0.85
            
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

# Materials
mat_pedestal = create_color_mat("Pedestal_Metal", (0.04, 0.07, 0.1, 1.0), roughness=0.25, metallic=0.85)
mat_neon_cyan = create_color_mat("Neon_Cyan_Glow", (0.0, 0.82, 0.67, 1.0), roughness=0.2, emission=(0.0, 0.9, 0.75, 1.0))
mat_neon_amber = create_color_mat("Neon_Amber_Glow", (0.95, 0.6, 0.1, 1.0), roughness=0.2, emission=(1.0, 0.65, 0.1, 1.0))
mat_tray = create_color_mat("Chassis_Tray", (0.08, 0.12, 0.16, 1.0), roughness=0.2, metallic=0.9)
mat_strata = create_image_mat("Soil_Strata_CrossSection", tex_strata_path, roughness=0.85, metallic=0.1)
mat_corn = create_image_mat("ZoneA_Corn_Soil", tex_corn_path, roughness=0.75)
mat_kale = create_image_mat("ZoneB_Kale_Soil", tex_kale_path, roughness=0.95)
mat_soy = create_image_mat("ZoneC_Soy_Soil", tex_soy_path, roughness=0.85)
mat_solar = create_image_mat("Solar_Array_Texture", tex_solar_path, roughness=0.2, metallic=0.9)

mat_stalk = create_color_mat("Corn_Stalk", (0.13, 0.77, 0.37, 1.0), roughness=0.4)
mat_leaf = create_color_mat("Corn_Leaf", (0.08, 0.5, 0.24, 1.0), roughness=0.3)
mat_tassel = create_color_mat("Corn_Tassel", (0.98, 0.8, 0.08, 1.0), roughness=0.3)
mat_kale_plant = create_color_mat("Kale_Foliage", (0.18, 0.55, 0.34, 1.0), roughness=0.8)
mat_rover_body = create_color_mat("Rover_Body", (0.89, 0.91, 0.94, 1.0), roughness=0.2, metallic=0.8)
mat_rover_solar = create_color_mat("Rover_Solar", (0.01, 0.52, 0.78, 1.0), roughness=0.1, metallic=0.9)
mat_wheel = create_color_mat("Rover_Wheel", (0.06, 0.09, 0.16, 1.0), roughness=0.9)
mat_glass = create_color_mat("Catwalk_Glass", (0.22, 0.74, 0.97, 1.0), roughness=0.1, alpha=0.4)

# Create Collection
col = bpy.data.collections.new("AgriGCS_3D_Spatial_Platform")
bpy.context.scene.collection.children.link(col)

def add_box(name, size, location, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if material:
        obj.data.materials.append(material)
    # Move to collection
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj

def add_cylinder(name, radius, depth, location, rotation=(0,0,0), material=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj

# 1. Base Aerospace Pedestal
add_box("Pedestal_Base", (32.0, 24.0, 1.2), (0, 0, -2.0), mat_pedestal)
add_box("Neon_Cyan_Perimeter_Rim", (32.6, 24.6, 0.28), (0, 0, -1.4), mat_neon_cyan)
add_box("Upper_Chassis_Tray", (29.6, 21.6, 0.5), (0, 0, -1.0), mat_tray)

# 2. Subterranean Soil Strata Block
soil_block = add_box("Subterranean_Soil_Strata", (28.0, 20.0, 2.2), (0, 0, 0.2), mat_strata)

# 3. Crop Zone Beds
zone_a = add_box("Zone_A_Sweet_Corn_Bed", (12.5, 17.5, 0.45), (-6.5, 0, 1.4), mat_corn)
zone_b = add_box("Zone_B_Organic_Kale_Bed", (12.5, 8.2, 0.45), (6.5, -4.65, 1.4), mat_kale)
zone_c = add_box("Zone_C_Soybeans_Bed", (12.5, 8.2, 0.45), (6.5, 4.65, 1.4), mat_soy)

# 4. Zone A Stalks
random.seed(42)
for r in [-6.0, -4.2, -2.4, -0.6, 1.2, 3.0, 4.8, 6.6]:
    for c in [-10.8, -9.4, -8.0, -6.6, -5.2, -3.8, -2.4]:
        h = 1.8 + random.random() * 0.5
        x = c + (random.random() - 0.5) * 0.2
        y = r + (random.random() - 0.5) * 0.2
        z = 1.6 + h / 2.0
        add_cylinder("Corn_Stalk", 0.05, h, (x, y, z), material=mat_stalk)
        add_cylinder("Corn_Tassel", 0.08, 0.35, (x, y, z + h/2.0 + 0.15), material=mat_tassel)

# 5. Zone B Kale Clusters & Scout Rover
for r in [-7.5, -6.1, -4.7, -3.3, -1.9]:
    for c in [2.2, 3.6, 5.0, 6.4, 7.8, 9.2, 10.6]:
        x = c + (random.random() - 0.5) * 0.2
        y = r + (random.random() - 0.5) * 0.2
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.32, location=(x, y, 1.8))
        kp = bpy.context.active_object
        kp.name = "Kale_Plant"
        kp.scale = (1.2, 1.2, 0.65)
        kp.data.materials.append(mat_kale_plant)
        for cl in kp.users_collection: cl.objects.unlink(kp)
        col.objects.link(kp)

# Scout Rover
add_box("Rover_Chassis", (1.2, 0.8, 0.45), (8.5, -4.0, 1.8), mat_rover_body)
add_box("Rover_Solar_Roof", (1.1, 0.75, 0.05), (8.5, -4.0, 2.05), mat_rover_solar)
for dx, dy in [(-0.45, -0.45), (-0.45, 0.45), (0.45, -0.45), (0.45, 0.45)]:
    add_cylinder("Rover_Wheel", 0.18, 0.14, (8.5 + dx, -4.0 + dy, 1.65), rotation=(math.pi/2, 0, 0), material=mat_wheel)

# Zone B Deficit Probe Beacon
add_cylinder("Zone_B_Probe_Beacon", 0.12, 0.6, (6.2, -4.15, 1.9), material=mat_neon_amber)

# 6. Zone C Soybean Seedlings
for r in [1.8, 3.2, 4.6, 6.0, 7.4]:
    for c in range(2, 12):
        bpy.ops.mesh.primitive_cone_add(radius1=0.14, radius2=0.0, depth=0.35, location=(c * 1.0, r, 1.8))
        sp = bpy.context.active_object
        sp.name = "Soy_Sprout"
        sp.data.materials.append(mat_stalk)
        for cl in sp.users_collection: cl.objects.unlink(sp)
        col.objects.link(sp)

# 7. Inspection Walkways
add_box("Walkway_Spine", (1.4, 18.0, 0.15), (0, 0, 1.55), mat_glass)
add_box("Walkway_Cross", (13.0, 1.4, 0.15), (6.5, 0, 1.55), mat_glass)
add_cylinder("Conduit_Fiber", 0.04, 18.0, (0, 0, 1.45), rotation=(math.pi/2, 0, 0), material=mat_neon_cyan)

# 8. Central Solar IoT Gateway
add_box("IoT_Gateway_Mast", (0.4, 0.4, 3.8), (0, 0, 3.3), mat_pedestal)
add_box("IoT_Gateway_Solar_Left", (1.6, 0.8, 0.05), (-0.9, 0, 4.5), mat_solar)
add_box("IoT_Gateway_Solar_Right", (1.6, 0.8, 0.05), (0.9, 0, 4.5), mat_solar)
add_cylinder("IoT_Antenna", 0.04, 1.2, (0, 0, 5.7), material=mat_pedestal)
add_cylinder("IoT_Comms_Ring", 0.45, 0.06, (0, 0, 5.0), material=mat_neon_cyan)

# 9. Lighting Setup
def add_light(name, ltype, loc, energy, color=(1,1,1)):
    bpy.ops.object.light_add(type=ltype, location=loc)
    lt = bpy.context.active_object
    lt.name = name
    lt.data.energy = energy
    lt.data.color = color
    for c in lt.users_collection: c.objects.unlink(lt)
    col.objects.link(lt)
    return lt

add_light("Key_Sun_Light", 'SUN', (25, -25, 40), 4.5, (0.85, 0.95, 1.0))
add_light("Fill_Cyan_Light", 'SUN', (-20, 20, 30), 2.5, (0.0, 0.82, 0.67))
add_light("ZoneB_Warning_Point", 'POINT', (6.2, -4.15, 3.2), 60.0, (1.0, 0.4, 0.2))

# 10. Camera Setup (Isometric 45° Angle)
bpy.ops.object.camera_add(location=(34.0, -34.0, 28.0), rotation=(math.radians(60), 0, math.radians(45)))
cam = bpy.context.active_object
cam.name = "AgriGCS_Iso_Camera"
cam.data.lens = 50
bpy.context.scene.camera = cam
for c in cam.users_collection: c.objects.unlink(cam)
col.objects.link(cam)

# Save .blend file
blend_file = os.path.join(dir_path, "agrigcs_platform.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)
print("SUCCESSFULLY_SAVED_BLEND:", blend_file)

# Export GLTF / GLB as well
glb_file = os.path.join(dir_path, "agrigcs_platform.glb")
try:
    bpy.ops.export_scene.gltf(filepath=glb_file, export_format='GLB')
    print("SUCCESSFULLY_EXPORTED_GLB:", glb_file)
except Exception as e:
    print("GLB_EXPORT_NOTE:", e)

# Export OBJ as well
obj_file = os.path.join(dir_path, "agrigcs_platform.obj")
try:
    if hasattr(bpy.ops.wm, "obj_export"):
        bpy.ops.wm.obj_export(filepath=obj_file)
    elif hasattr(bpy.ops.export_scene, "obj"):
        bpy.ops.export_scene.obj(filepath=obj_file)
    print("SUCCESSFULLY_EXPORTED_OBJ:", obj_file)
except Exception as e:
    print("OBJ_EXPORT_NOTE:", e)

print("ALL_BLENDER_ASSETS_GENERATED_SUCCESSFULLY")
