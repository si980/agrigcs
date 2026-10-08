import bpy
import math
import random
import os

# ==============================================================================
# AGRIGCS SMART AGRICULTURE TESTBED - PRODUCTION PROTOTYPE SCRIPT
# Real-world Dimensions: 3.0m (L) x 2.0m (W) x 1.2m (H)
# ==============================================================================

# 1. PURGE PREVIOUS SCENE
bpy.ops.wm.read_factory_settings(use_empty=True)

# 2. DEFINE REQUIRED COLLECTIONS
collection_names = [
    "AGRICGS_PLATFORM",
    "SOIL_SYSTEM",
    "ZONE_A_SWEET_CORN",
    "ZONE_B_ORGANIC_KALE",
    "ZONE_C_SOYBEAN",
    "IRRIGATION",
    "IOT_SENSORS",
    "WEATHER_STATION",
    "SOLAR_SYSTEM",
    "AUTONOMOUS_ROVER",
    "BRANDING",
    "CAMERAS",
    "LIGHTING"
]

cols = {}
for cname in collection_names:
    col = bpy.data.collections.new(cname)
    bpy.context.scene.collection.children.link(col)
    cols[cname] = col

# Create Master Turntable Parent for 360 Animation
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
turntable_root = bpy.context.active_object
turntable_root.name = "AgriGCS_Turntable_Root"
cols["AGRICGS_PLATFORM"].objects.link(turntable_root)

# 3. PBR MATERIAL LIBRARY (NATURAL, INDUSTRIAL, NON-CYBERPUNK)
def create_pbr_mat(name, color, roughness=0.5, metallic=0.0, bump=None, emission=None, alpha=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    if emission:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission
            bsdf.inputs['Emission Strength'].default_value = 1.5
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = emission
            
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = alpha
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.9
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 0.9
            
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# Professional Material Palette
mat_concrete = create_pbr_mat("Concrete_Rough_LightGray", (0.76, 0.78, 0.80, 1.0), roughness=0.82, metallic=0.02)
mat_concrete_beveled = create_pbr_mat("Concrete_Bevel_Edge", (0.68, 0.70, 0.72, 1.0), roughness=0.85)
mat_galvanized = create_pbr_mat("Galvanized_Steel_Trough", (0.45, 0.47, 0.49, 1.0), roughness=0.35, metallic=0.85)
mat_glass_cutaway = create_pbr_mat("Cutaway_Tempered_Glass", (0.85, 0.92, 0.95, 1.0), roughness=0.05, alpha=0.35)
mat_brackets_steel = create_pbr_mat("Stainless_Bolts_Brackets", (0.82, 0.84, 0.86, 1.0), roughness=0.2, metallic=0.95)

# Soil Layer Materials
mat_topsoil = create_pbr_mat("Soil_Topsoil_Organic", (0.22, 0.14, 0.08, 1.0), roughness=0.95)
mat_subsoil_loam = create_pbr_mat("Soil_Subsoil_Loamy", (0.34, 0.22, 0.13, 1.0), roughness=0.96)
mat_clay_moist = create_pbr_mat("Soil_Clay_Moist", (0.28, 0.18, 0.12, 1.0), roughness=0.9)
mat_drainage_gravel = create_pbr_mat("Soil_Drainage_Aggregate", (0.38, 0.40, 0.42, 1.0), roughness=0.88, metallic=0.1)
mat_root_organic = create_pbr_mat("Plant_Root_System", (0.82, 0.76, 0.62, 1.0), roughness=0.6)

# Crops
mat_corn_stalk = create_pbr_mat("Corn_Stalk_NaturalGreen", (0.24, 0.48, 0.15, 1.0), roughness=0.45)
mat_corn_leaf = create_pbr_mat("Corn_Leaf_NaturalGreen", (0.18, 0.44, 0.12, 1.0), roughness=0.4)
mat_corn_tassel = create_pbr_mat("Corn_Tassel_Golden", (0.88, 0.72, 0.22, 1.0), roughness=0.55)
mat_kale_leaf = create_pbr_mat("Kale_Curly_DeepGreen", (0.10, 0.32, 0.18, 1.0), roughness=0.75)
mat_soy_leaf = create_pbr_mat("Soybean_Sprout_FreshGreen", (0.30, 0.62, 0.20, 1.0), roughness=0.4)

# Technical Equipment
mat_drip_tube = create_pbr_mat("Irrigation_Matte_Black_Rubber", (0.05, 0.05, 0.06, 1.0), roughness=0.3)
mat_drip_emitter = create_pbr_mat("Drip_Micro_Emitter_Blue", (0.1, 0.35, 0.7, 1.0), roughness=0.3)
mat_sensor_white = create_pbr_mat("Industrial_ABS_White", (0.94, 0.94, 0.95, 1.0), roughness=0.25)
mat_sensor_stem = create_pbr_mat("Sensor_Stainless_Stem", (0.7, 0.72, 0.75, 1.0), roughness=0.2, metallic=0.9)
mat_pv_cell = create_pbr_mat("Solar_Photovoltaic_DarkBlue", (0.04, 0.12, 0.32, 1.0), roughness=0.15, metallic=0.88)
mat_rover_chassis = create_pbr_mat("Rover_Polymer_White", (0.92, 0.93, 0.95, 1.0), roughness=0.25)
mat_rover_dark = create_pbr_mat("Rover_Trim_DarkGray", (0.12, 0.13, 0.15, 1.0), roughness=0.4, metallic=0.6)
mat_rover_rubber = create_pbr_mat("Rover_Offroad_Tire_Rubber", (0.06, 0.06, 0.07, 1.0), roughness=0.92)

# Branding & Placards
mat_placard_bg = create_pbr_mat("Placard_Industrial_Dark", (0.08, 0.10, 0.12, 1.0), roughness=0.4)
mat_brand_green = create_pbr_mat("AgriGCS_Brand_Green", (0.05, 0.45, 0.22, 1.0), roughness=0.3)
mat_brand_white = create_pbr_mat("AgriGCS_Brand_White", (0.98, 0.98, 0.98, 1.0), roughness=0.2)
mat_led_cyan = create_pbr_mat("Subtle_Status_Cyan_LED", (0.0, 0.85, 0.72, 1.0), roughness=0.1, emission=(0.0, 0.9, 0.75, 1.0))

# 4. HELPER MESH GENERATORS
def add_part(col_name, name, mesh_type, size, loc, rot=(0,0,0), mat=None, parent=turntable_root):
    if mesh_type == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    elif mesh_type == 'cylinder':
        bpy.ops.mesh.primitive_cylinder_add(radius=size[0], depth=size[1], location=loc, rotation=rot)
    elif mesh_type == 'icosphere':
        bpy.ops.mesh.primitive_ico_sphere_add(radius=size[0], subdivisions=size[1], location=loc)
    elif mesh_type == 'cone':
        bpy.ops.mesh.primitive_cone_add(radius1=size[0], radius2=0.0, depth=size[1], location=loc, rotation=rot)
        
    obj = bpy.context.active_object
    obj.name = name
    if mesh_type == 'cube':
        obj.scale = size
    elif mesh_type == 'icosphere':
        obj.scale = (size[2], size[3], size[4])
        
    if mat:
        obj.data.materials.append(mat)
        
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    cols[col_name].objects.link(obj)
    
    if parent and obj != parent:
        obj.parent = parent
    return obj

# ==============================================================================
# 5. PLATFORM BASE & ENCLOSURE (3.0m x 2.0m x 1.2m)
# ==============================================================================
# Ground level: Z = 0
# Concrete Base: Height = 0.45m, Width (X) = 3.0m, Depth (Y) = 2.0m, Z_center = 0.225
base_slab = add_part("AGRICGS_PLATFORM", "Concrete_Base_Platform", 'cube', (3.0, 2.0, 0.45), (0, 0, 0.225), mat=mat_concrete)

# Forklift slots / Skid channels under base
add_part("AGRICGS_PLATFORM", "Skid_Channel_Left", 'cube', (0.35, 2.02, 0.12), (-0.75, 0, 0.06), mat=mat_concrete_beveled)
add_part("AGRICGS_PLATFORM", "Skid_Channel_Right", 'cube', (0.35, 2.02, 0.12), (0.75, 0, 0.06), mat=mat_concrete_beveled)

# Upper Galvanized Steel Soil Containment Trough (0.75m height, from Z=0.45 to Z=1.20)
# Back wall
add_part("AGRICGS_PLATFORM", "Trough_Wall_Back", 'cube', (3.0, 0.05, 0.75), (0, 0.975, 0.825), mat=mat_galvanized)
# Left wall
add_part("AGRICGS_PLATFORM", "Trough_Wall_Left", 'cube', (0.05, 1.95, 0.75), (-1.475, 0.025, 0.825), mat=mat_galvanized)
# Right wall
add_part("AGRICGS_PLATFORM", "Trough_Wall_Right", 'cube', (0.05, 1.95, 0.75), (1.475, 0.025, 0.825), mat=mat_galvanized)

# Structural Corner Mounting Brackets with Screws
for cx in [-1.48, 1.48]:
    for cy in [-0.98, 0.98]:
        add_part("AGRICGS_PLATFORM", "Corner_Bracket", 'cube', (0.08, 0.08, 0.78), (cx, cy, 0.825), mat=mat_brackets_steel)
        # Mounting bolts
        for bz in [0.55, 0.85, 1.15]:
            add_part("AGRICGS_PLATFORM", "Bolt", 'cylinder', (0.015, 0.03), (cx, cy, bz), rot=(0, math.pi/2, 0), mat=mat_brackets_steel)

# FRONT SOIL CROSS-SECTION CUTAWAY: Transparent tempered acrylic/glass retaining pane
front_glass = add_part("AGRICGS_PLATFORM", "Front_Glass_Cutaway_Pane", 'cube', (2.95, 0.02, 0.74), (0, -0.99, 0.82), mat=mat_glass_cutaway)
# Glass mounting retainers (vertical steel bars holding glass)
add_part("AGRICGS_PLATFORM", "Glass_Retainer_Left", 'cube', (0.04, 0.04, 0.75), (-1.0, -1.0, 0.825), mat=mat_brackets_steel)
add_part("AGRICGS_PLATFORM", "Glass_Retainer_Right", 'cube', (0.04, 0.04, 0.75), (1.0, -1.0, 0.825), mat=mat_brackets_steel)

# Cable channels on the sides
add_part("AGRICGS_PLATFORM", "Cable_Channel_Left", 'cube', (0.04, 1.8, 0.06), (-1.49, 0, 0.48), mat=mat_rover_dark)
add_part("AGRICGS_PLATFORM", "Cable_Channel_Right", 'cube', (0.04, 1.8, 0.06), (1.49, 0, 0.48), mat=mat_rover_dark)

# ==============================================================================
# 6. VISIBLE STRATIFIED SOIL BED & SUBTERRANEAN PROFILES
# ==============================================================================
# Total soil height = 0.72m (from Z=0.46 to Z=1.18)
# Layer 1: Drainage / gravel aggregate base (Z: 0.46 - 0.56, H=0.10)
add_part("SOIL_SYSTEM", "Soil_Layer_Drainage_Aggregate", 'cube', (2.90, 1.90, 0.10), (0, 0, 0.51), mat=mat_drainage_gravel)

# Layer 2: Moist compact clay layer (Z: 0.56 - 0.74, H=0.18)
add_part("SOIL_SYSTEM", "Soil_Layer_Moist_Clay", 'cube', (2.90, 1.90, 0.18), (0, 0, 0.65), mat=mat_clay_moist)

# Layer 3: Subsoil / Sandy-loamy layer (Z: 0.74 - 0.98, H=0.24)
add_part("SOIL_SYSTEM", "Soil_Layer_Sandy_Loam", 'cube', (2.90, 1.90, 0.24), (0, 0, 0.86), mat=mat_subsoil_loam)

# Layer 4: Topsoil / Rich organic loam (Z: 0.98 - 1.18, H=0.20)
add_part("SOIL_SYSTEM", "Soil_Layer_Organic_Topsoil", 'cube', (2.90, 1.90, 0.20), (0, 0, 1.08), mat=mat_topsoil)

# Front Visible Root Networks (visible through the front cutaway window)
# Corn deep vertical roots (Zone A: X ~ -0.9)
for rx in [-1.2, -0.95, -0.7]:
    # Main tap roots descending deep
    add_part("SOIL_SYSTEM", "Corn_Deep_Root_Main", 'cylinder', (0.012, 0.45), (rx, -0.97, 0.85), rot=(0.1, 0, 0.05), mat=mat_root_organic)
    for bi in range(5):
        add_part("SOIL_SYSTEM", "Corn_Fibrous_Root", 'cylinder', (0.005, 0.15), (rx + (bi-2)*0.04, -0.97, 0.75 + bi*0.06), rot=(0.2, 0.3, bi*0.4), mat=mat_root_organic)

# Kale fibrous spreading roots (Zone B: X ~ 0.0)
for rk in [-0.25, 0.0, 0.25]:
    add_part("SOIL_SYSTEM", "Kale_Root_Cluster", 'cylinder', (0.008, 0.30), (rk, -0.97, 0.95), rot=(0, 0.2, 0), mat=mat_root_organic)
    for bi in range(4):
        add_part("SOIL_SYSTEM", "Kale_Fine_Root", 'cylinder', (0.004, 0.12), (rk + (bi-1.5)*0.05, -0.97, 0.88 + bi*0.05), rot=(0.3, 0.1, bi*0.6), mat=mat_root_organic)

# Soybean tap roots with nodule clusters (Zone C: X ~ 0.9)
for rs in [0.7, 0.95, 1.2]:
    add_part("SOIL_SYSTEM", "Soybean_Tap_Root", 'cylinder', (0.01, 0.38), (rs, -0.97, 0.90), rot=(-0.1, 0, -0.05), mat=mat_root_organic)
    for ni in range(4):
        add_part("SOIL_SYSTEM", "Soybean_Nodule", 'icosphere', (0.015, 1, 1, 1, 1), (rs + (ni-1.5)*0.03, -0.97, 0.82 + ni*0.07), mat=mat_root_organic)

# Embedded Multi-Depth Probes in Cutaway View (at 10cm, 30cm, 60cm depths)
# 10cm depth probe (Z = 1.08)
add_part("SOIL_SYSTEM", "Probe_Sensor_10cm", 'cylinder', (0.012, 0.12), (-0.5, -0.97, 1.08), rot=(math.pi/2, 0, 0), mat=mat_sensor_stem)
add_part("SOIL_SYSTEM", "Probe_Cable_10cm", 'cylinder', (0.004, 0.15), (-0.5, -0.97, 1.15), mat=mat_rover_dark)

# 30cm depth probe (Z = 0.88)
add_part("SOIL_SYSTEM", "Probe_Sensor_30cm", 'cylinder', (0.012, 0.12), (-0.5, -0.97, 0.88), rot=(math.pi/2, 0, 0), mat=mat_sensor_stem)
add_part("SOIL_SYSTEM", "Probe_Cable_30cm", 'cylinder', (0.004, 0.35), (-0.5, -0.97, 1.05), mat=mat_rover_dark)

# 60cm depth probe (Z = 0.58)
add_part("SOIL_SYSTEM", "Probe_Sensor_60cm", 'cylinder', (0.012, 0.12), (-0.5, -0.97, 0.58), rot=(math.pi/2, 0, 0), mat=mat_sensor_stem)
add_part("SOIL_SYSTEM", "Probe_Cable_60cm", 'cylinder', (0.004, 0.65), (-0.5, -0.97, 0.90), mat=mat_rover_dark)

# ==============================================================================
# 7. ZONE A: SWEET CORN (X: -1.45 to -0.48, W=0.97m, D=1.9m)
# ==============================================================================
random.seed(42)
corn_x_steps = [-1.32, -1.16, -1.00, -0.84, -0.68]
corn_y_steps = [-0.75, -0.55, -0.35, -0.15, 0.05, 0.25, 0.45, 0.65, 0.80]

for cx in corn_x_steps:
    for cy in corn_y_steps:
        jx = cx + (random.random() - 0.5) * 0.04
        jy = cy + (random.random() - 0.5) * 0.04
        stalk_h = 0.85 + random.random() * 0.25  # Scaled to 3m platform
        # Stalk
        add_part("ZONE_A_SWEET_CORN", "Corn_Stalk", 'cylinder', (0.016, stalk_h), (jx, jy, 1.18 + stalk_h/2), mat=mat_corn_stalk)
        # Golden tassel
        add_part("ZONE_A_SWEET_CORN", "Corn_Tassel", 'cylinder', (0.025, 0.14), (jx, jy, 1.18 + stalk_h + 0.06), mat=mat_corn_tassel)
        # Leaves (2-4 broad arching green blades)
        for li in range(3):
            ang = li * 2.1 + random.random() * 0.4
            add_part("ZONE_A_SWEET_CORN", "Corn_Leaf", 'cube', (0.24, 0.06, 0.006), 
                     (jx + math.cos(ang)*0.12, jy + math.sin(ang)*0.12, 1.18 + stalk_h*(0.35 + li*0.2)), 
                     rot=(0.3, 0.2, ang), mat=mat_corn_leaf)

# ==============================================================================
# 8. ZONE B: ORGANIC KALE (X: -0.48 to 0.48, W=0.96m, D=1.9m)
# ==============================================================================
kale_x_steps = [-0.38, -0.22, -0.06, 0.10, 0.26, 0.38]
kale_y_steps = [-0.72, -0.50, -0.28, -0.06, 0.16, 0.38]

for kx in kale_x_steps:
    for ky in kale_y_steps:
        # Leave room for rover in front-center (kx around 0.1, ky around -0.4) and tower in back-center (ky > 0.45)
        if (abs(kx - 0.12) < 0.25 and abs(ky + 0.35) < 0.35) or (abs(kx) < 0.30 and ky > 0.40):
            continue
        jx = kx + (random.random() - 0.5) * 0.05
        jy = ky + (random.random() - 0.5) * 0.05
        # Clustered ruffled curly kale bush
        for ki in range(4):
            add_part("ZONE_B_ORGANIC_KALE", "Kale_Leaf_Cluster", 'icosphere', 
                     (0.08, 1, 1.1, 1.1, 0.65), 
                     (jx + (ki%2 - 0.5)*0.04, jy + (ki//2 - 0.5)*0.04, 1.22 + ki*0.02), 
                     rot=(random.random(), random.random(), random.random()), mat=mat_kale_leaf)

# ==============================================================================
# 9. ZONE C: SOYBEAN & DRIP IRRIGATION (X: 0.48 to 1.45, W=0.97m, D=1.9m)
# ==============================================================================
soy_x_rows = [0.60, 0.80, 1.00, 1.20, 1.36]

for rx in soy_x_rows:
    # Black micro-drip irrigation pipe running along each row
    add_part("IRRIGATION", "Drip_Tube", 'cylinder', (0.012, 1.84), (rx, 0.0, 1.20), rot=(math.pi/2, 0, 0), mat=mat_drip_tube)
    
    # Soybean plants along row with micro-emitters
    for sy in [-0.75, -0.58, -0.41, -0.24, -0.07, 0.10, 0.27, 0.44, 0.61, 0.78]:
        # Blue micro drip emitter beside plant
        add_part("IRRIGATION", "Drip_Emitter", 'cylinder', (0.008, 0.025), (rx + 0.03, sy, 1.205), mat=mat_drip_emitter)
        # Wet soil spot around emitter
        add_part("IRRIGATION", "Moist_Soil_Spot", 'cylinder', (0.05, 0.005), (rx, sy, 1.185), mat=mat_clay_moist)
        
        # Soybean young seedling bush
        add_part("ZONE_C_SOYBEAN", "Soy_Stem", 'cylinder', (0.008, 0.16), (rx - 0.04, sy, 1.26), mat=mat_soy_leaf)
        for sli in range(3):
            add_part("ZONE_C_SOYBEAN", "Soy_Leaflet", 'icosphere', (0.04, 1, 1.0, 0.8, 0.4), 
                     (rx - 0.04 + (sli-1)*0.03, sy, 1.32 + sli*0.02), rot=(0.2, sli*0.4, 0), mat=mat_soy_leaf)

# Irrigation Main Manifold Header Pipe at back edge
add_part("IRRIGATION", "Drip_Manifold_Header", 'cylinder', (0.022, 0.95), (0.98, 0.93, 1.22), rot=(0, math.pi/2, 0), mat=mat_drip_tube)
# Pressure regulator valve
add_part("IRRIGATION", "Pressure_Regulator", 'cylinder', (0.035, 0.08), (1.42, 0.93, 1.22), rot=(0, math.pi/2, 0), mat=mat_rover_dark)

# ==============================================================================
# 10. CENTRAL MONITORING TOWER / WEATHER STATION
# ==============================================================================
tower_loc = (0.0, 0.65, 1.18)

# Vertical Galvanized Steel Lattice Mast
add_part("WEATHER_STATION", "Mast_Leg_FL", 'cylinder', (0.016, 1.6), (tower_loc[0] - 0.12, tower_loc[1] - 0.12, tower_loc[2] + 0.8), mat=mat_galvanized)
add_part("WEATHER_STATION", "Mast_Leg_FR", 'cylinder', (0.016, 1.6), (tower_loc[0] + 0.12, tower_loc[1] - 0.12, tower_loc[2] + 0.8), mat=mat_galvanized)
add_part("WEATHER_STATION", "Mast_Leg_BK", 'cylinder', (0.016, 1.6), (tower_loc[0], tower_loc[1] + 0.12, tower_loc[2] + 0.8), mat=mat_galvanized)

# Horizontal & Diagonal Struts
for si in range(4):
    sz = tower_loc[2] + 0.3 + si * 0.38
    add_part("WEATHER_STATION", "Mast_Strut_H", 'cylinder', (0.008, 0.26), (tower_loc[0], tower_loc[1] - 0.12, sz), rot=(0, math.pi/2, 0), mat=mat_galvanized)

# IoT Gateway Electronics Enclosure (White UV-stabilized IP67 enclosure)
gw_box = add_part("WEATHER_STATION", "IoT_Gateway_Enclosure", 'cube', (0.32, 0.22, 0.38), (tower_loc[0], tower_loc[1] - 0.08, tower_loc[2] + 0.95), mat=mat_sensor_white)
# Status LED (subtle cyan indicator)
add_part("WEATHER_STATION", "Gateway_Status_LED", 'cylinder', (0.008, 0.01), (tower_loc[0] + 0.12, tower_loc[1] - 0.19, tower_loc[2] + 1.08), rot=(math.pi/2, 0, 0), mat=mat_led_cyan)
# Conduit feeding downward
add_part("WEATHER_STATION", "Cable_Conduit", 'cylinder', (0.012, 0.95), (tower_loc[0] + 0.08, tower_loc[1] - 0.06, tower_loc[2] + 0.48), mat=mat_rover_dark)

# Solar Panel Array: 2 x Photovoltaic Panels tilted 30° toward south
panel_z = tower_loc[2] + 1.45
for pxi, px in enumerate([-0.36, 0.36]):
    panel = add_part("SOLAR_SYSTEM", f"Solar_Panel_{pxi}", 'cube', (0.42, 0.32, 0.025), (tower_loc[0] + px, tower_loc[1] - 0.06, panel_z), mat=mat_pv_cell)
    panel.rotation_euler = (math.radians(-30), 0, 0)
    # Aluminum frame
    pframe = add_part("SOLAR_SYSTEM", f"Solar_Frame_{pxi}", 'cube', (0.44, 0.34, 0.02), (tower_loc[0] + px, tower_loc[1] - 0.06, panel_z - 0.005), mat=mat_brackets_steel)
    pframe.rotation_euler = (math.radians(-30), 0, 0)

# Crossbar mounting solar panels
add_part("SOLAR_SYSTEM", "Solar_Mount_Crossbar", 'cylinder', (0.015, 0.92), (tower_loc[0], tower_loc[1] - 0.02, panel_z - 0.08), rot=(0, math.pi/2, 0), mat=mat_galvanized)

# Weather Sensors (Top of Mast, Z ~ 2.8m - 3.2m total height)
# Central Mast Pole Extension
add_part("WEATHER_STATION", "Weather_Pole_Extension", 'cylinder', (0.016, 0.85), (tower_loc[0], tower_loc[1], tower_loc[2] + 1.95), mat=mat_galvanized)

# Anemometer (Wind Speed 3-Cup Rotor)
add_part("WEATHER_STATION", "Anemometer_Body", 'cylinder', (0.03, 0.08), (tower_loc[0] - 0.22, tower_loc[1], tower_loc[2] + 2.35), mat=mat_sensor_white)
for ci in [0, 2.09, 4.18]:
    add_part("WEATHER_STATION", "Cup_Arm", 'cylinder', (0.005, 0.10), 
             (tower_loc[0] - 0.22 + math.cos(ci)*0.05, tower_loc[1] + math.sin(ci)*0.05, tower_loc[2] + 2.38), 
             rot=(0, math.pi/2, ci), mat=mat_brackets_steel)
    add_part("WEATHER_STATION", "Cup_Cone", 'cone', (0.022, 0.03), 
             (tower_loc[0] - 0.22 + math.cos(ci)*0.10, tower_loc[1] + math.sin(ci)*0.10, tower_loc[2] + 2.38), 
             rot=(0, math.pi/2, ci + math.pi/2), mat=mat_rover_dark)

# Wind Direction Vane
add_part("WEATHER_STATION", "Wind_Vane_Body", 'cylinder', (0.025, 0.08), (tower_loc[0] + 0.22, tower_loc[1], tower_loc[2] + 2.35), mat=mat_sensor_white)
add_part("WEATHER_STATION", "Wind_Vane_Fin", 'cube', (0.004, 0.14, 0.08), (tower_loc[0] + 0.22, tower_loc[1] + 0.08, tower_loc[2] + 2.42), mat=mat_sensor_white)

# Temperature & Humidity Solar Radiation Shield (Multi-plate louver disc stack)
for di in range(6):
    add_part("WEATHER_STATION", "Radiation_Shield_Plate", 'cylinder', (0.07, 0.012), 
             (tower_loc[0] + 0.05, tower_loc[1] + 0.16, tower_loc[2] + 2.18 + di*0.028), mat=mat_sensor_white)

# Comms & GPS Antennas
add_part("WEATHER_STATION", "LoRa_Antenna", 'cylinder', (0.008, 0.45), (tower_loc[0] - 0.05, tower_loc[1] + 0.16, tower_loc[2] + 2.45), mat=mat_rover_dark)
add_part("WEATHER_STATION", "GPS_Mushroom_Antenna", 'cylinder', (0.045, 0.03), (tower_loc[0] - 0.08, tower_loc[1] - 0.12, tower_loc[2] + 1.62), mat=mat_sensor_white)

# ==============================================================================
# 11. FIELD IOT SOIL PROBES (Distributed Across Zones)
# ==============================================================================
probe_coords = [
    # Zone A (Corn)
    (-1.35, -0.65), (-0.75, -0.65), (-1.35, 0.65), (-0.75, 0.65),
    # Zone B (Kale)
    (-0.35, -0.65), (0.35, -0.65),
    # Zone C (Soybean row ends)
    (0.60, -0.80), (0.80, -0.80), (1.00, -0.80), (1.20, -0.80), (1.36, -0.80),
    (0.60, 0.80), (1.00, 0.80), (1.36, 0.80)
]

for pi, (px, py) in enumerate(probe_coords):
    # Stainless ground stake
    add_part("IOT_SENSORS", f"Probe_Stem_{pi}", 'cylinder', (0.012, 0.28), (px, py, 1.26), mat=mat_sensor_stem)
    # White sensor electronics head
    add_part("IOT_SENSORS", f"Probe_Head_{pi}", 'cube', (0.07, 0.07, 0.09), (px, py, 1.42), mat=mat_sensor_white)
    # Mini solar cap
    add_part("IOT_SENSORS", f"Probe_SolarCap_{pi}", 'cube', (0.065, 0.065, 0.008), (px, py, 1.47), mat=mat_pv_cell)

# ==============================================================================
# 12. AUTONOMOUS SCOUT ROVER (Zone B, Positioned between rows)
# ==============================================================================
rover_pos = (0.12, -0.35, 1.18)

# Lower Aluminum Chassis Pan
add_part("AUTONOMOUS_ROVER", "Rover_Lower_Pan", 'cube', (0.32, 0.44, 0.08), (rover_pos[0], rover_pos[1], rover_pos[2] + 0.12), mat=mat_rover_dark)
# Main White Polymer Body
add_part("AUTONOMOUS_ROVER", "Rover_Body_Upper", 'cube', (0.28, 0.38, 0.12), (rover_pos[0], rover_pos[1] - 0.01, rover_pos[2] + 0.20), mat=mat_rover_chassis)
# Top Solar Panel
add_part("AUTONOMOUS_ROVER", "Rover_Solar_Roof", 'cube', (0.24, 0.30, 0.012), (rover_pos[0], rover_pos[1] - 0.01, rover_pos[2] + 0.265), mat=mat_pv_cell)
# Front Stereo Camera Pod
add_part("AUTONOMOUS_ROVER", "Rover_Camera_Pod", 'cube', (0.16, 0.05, 0.04), (rover_pos[0], rover_pos[1] - 0.21, rover_pos[2] + 0.21), mat=mat_rover_dark)
add_part("AUTONOMOUS_ROVER", "Rover_Cam_Lens_L", 'cylinder', (0.012, 0.015), (rover_pos[0] - 0.05, rover_pos[1] - 0.23, rover_pos[2] + 0.21), rot=(math.pi/2, 0, 0), mat=mat_brackets_steel)
add_part("AUTONOMOUS_ROVER", "Rover_Cam_Lens_R", 'cylinder', (0.012, 0.015), (rover_pos[0] + 0.05, rover_pos[1] - 0.23, rover_pos[2] + 0.21), rot=(math.pi/2, 0, 0), mat=mat_brackets_steel)
# Rear Comms Whip Antenna
add_part("AUTONOMOUS_ROVER", "Rover_Antenna", 'cylinder', (0.005, 0.22), (rover_pos[0] + 0.10, rover_pos[1] + 0.15, rover_pos[2] + 0.37), mat=mat_brackets_steel)

# 4 Heavy-Duty Off-Road Tires
wheel_offsets = [(-0.18, -0.14), (0.18, -0.14), (-0.18, 0.14), (0.18, 0.14)]
for wi, (wox, woy) in enumerate(wheel_offsets):
    # Rubber knobby tire
    add_part("AUTONOMOUS_ROVER", f"Rover_Tire_{wi}", 'cylinder', (0.075, 0.06), 
             (rover_pos[0] + wox, rover_pos[1] + woy, rover_pos[2] + 0.075), 
             rot=(0, math.pi/2, 0), mat=mat_rover_rubber)
    # Steel wheel hub
    add_part("AUTONOMOUS_ROVER", f"Rover_Hub_{wi}", 'cylinder', (0.038, 0.065), 
             (rover_pos[0] + wox, rover_pos[1] + woy, rover_pos[2] + 0.075), 
             rot=(0, math.pi/2, 0), mat=mat_brackets_steel)

# ==============================================================================
# 13. ZONE IDENTIFICATION PLACARDS & BRANDING
# ==============================================================================
# Front Concrete Face AgriGCS Emblem & Slogan
add_part("BRANDING", "Brand_Plate_Front", 'cube', (1.2, 0.02, 0.25), (0, -1.01, 0.225), mat=mat_concrete_beveled)
add_part("BRANDING", "AgriGCS_Emblem_Text", 'cube', (0.85, 0.01, 0.12), (0, -1.025, 0.25), mat=mat_brand_green)
add_part("BRANDING", "AgriGCS_Subtitle_Text", 'cube', (0.95, 0.01, 0.04), (0, -1.025, 0.16), mat=mat_concrete)

# 3 Identification Boards Mounted on the Front Trough Lip
# Zone A: "ZONE A \n Sweet Corn"
add_part("BRANDING", "Placard_Plate_A", 'cube', (0.42, 0.02, 0.16), (-0.95, -1.02, 1.20), mat=mat_placard_bg)
add_part("BRANDING", "Placard_Text_A", 'cube', (0.38, 0.008, 0.12), (-0.95, -1.032, 1.20), mat=mat_brand_white)

# Zone B: "ZONE B \n Organic Kale"
add_part("BRANDING", "Placard_Plate_B", 'cube', (0.44, 0.02, 0.16), (0.0, -1.02, 1.20), mat=mat_placard_bg)
add_part("BRANDING", "Placard_Text_B", 'cube', (0.40, 0.008, 0.12), (0.0, -1.032, 1.20), mat=mat_brand_white)

# Zone C: "ZONE C \n Soybean"
add_part("BRANDING", "Placard_Plate_C", 'cube', (0.42, 0.02, 0.16), (0.95, -1.02, 1.20), mat=mat_placard_bg)
add_part("BRANDING", "Placard_Text_C", 'cube', (0.38, 0.008, 0.12), (0.95, -1.032, 1.20), mat=mat_brand_white)

# ==============================================================================
# 14. CAMERAS (5 STANDARD VIEWS + 12-STEP 360 ROTATION SET)
# ==============================================================================
def create_cam(name, loc, rot_deg, lens=50):
    bpy.ops.object.camera_add(location=loc, rotation=(math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2])))
    cam = bpy.context.active_object
    cam.name = name
    cam.data.lens = lens
    for c in list(cam.users_collection):
        c.objects.unlink(cam)
    cols["CAMERAS"].objects.link(cam)
    return cam

# 5 Core Orthogonal / Reference Cameras
create_cam("Camera_Front_0", (0, -4.5, 1.2), (90, 0, 0), lens=55)
create_cam("Camera_Right_90", (5.5, 0, 1.2), (90, 0, 90), lens=55)
create_cam("Camera_Back_180", (0, 4.5, 1.2), (90, 0, 180), lens=55)
create_cam("Camera_Left_270", (-5.5, 0, 1.2), (90, 0, -90), lens=55)
create_cam("Camera_Top", (0, 0, 6.0), (0, 0, 0), lens=50)

# Main Hero 3/4 Isometric Perspective Camera
hero_cam = create_cam("Camera_Hero_Isometric_34", (3.6, -4.2, 3.2), (64, 0, 40), lens=52)
bpy.context.scene.camera = hero_cam

# 12 Evenly Spaced 360-degree Cameras (Radius = 4.8m, Height = 2.4m, Looking at Platform Center Z=1.0)
cam_radius = 4.8
cam_height = 2.4
center_z = 0.95

for deg in [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]:
    rad = math.radians(deg)
    cx = cam_radius * math.sin(rad)
    cy = -cam_radius * math.cos(rad)
    
    # Calculate tracking rotation to point at center
    dx = -cx
    dy = -cy
    dz = center_z - cam_height
    dist_xy = math.sqrt(dx*dx + dy*dy)
    pitch = math.pi/2 - math.atan2(dz, dist_xy)
    yaw = math.atan2(dx, -dy)
    
    c_obj = create_cam(f"Camera_360_{deg:03d}", (cx, cy, cam_height), 
                       (math.degrees(pitch), 0, math.degrees(yaw)), lens=50)

# ==============================================================================
# 15. OPTIONAL TURNTABLE ANIMATION (120 Frames, 360° Rotation around Z-axis)
# ==============================================================================
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120
turntable_root.rotation_euler = (0, 0, 0)
turntable_root.keyframe_insert(data_path="rotation_euler", frame=1)
turntable_root.rotation_euler = (0, 0, math.radians(360))
turntable_root.keyframe_insert(data_path="rotation_euler", frame=120)

# Linear interpolation for seamless loop
if turntable_root.animation_data and turntable_root.animation_data.action:
    for fcurve in turntable_root.animation_data.action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'LINEAR'

# ==============================================================================
# 16. NATURAL DAYLIGHT LIGHTING
# ==============================================================================
# Sun Key Light (Soft Warm Sunlight)
bpy.ops.object.light_add(type='SUN', location=(15, -20, 25))
sun_key = bpy.context.active_object
sun_key.name = "Key_Sun_Daylight"
sun_key.data.energy = 4.8
sun_key.data.color = (1.0, 0.97, 0.92)
sun_key.data.angle = math.radians(2.0)  # Soft shadow penumbra
for c in list(sun_key.users_collection): sun_key.users_collection[0].objects.unlink(sun_key)
cols["LIGHTING"].objects.link(sun_key)

# Soft Sky Fill Light (Hemispheric ambient)
bpy.ops.object.light_add(type='SUN', location=(-15, 20, 20))
sky_fill = bpy.context.active_object
sky_fill.name = "Sky_Ambient_Fill"
sky_fill.data.energy = 2.0
sky_fill.data.color = (0.75, 0.88, 1.0)
for c in list(sky_fill.users_collection): sky_fill.users_collection[0].objects.unlink(sky_fill)
cols["LIGHTING"].objects.link(sky_fill)

# Save .blend mainfile
dir_path = os.path.dirname(os.path.abspath(__file__))
blend_file = os.path.join(dir_path, "agrigcs_platform.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)
print("SAVED_MASTER_BLEND:", blend_file)

# Export standard GLB
glb_file = os.path.join(dir_path, "agrigcs_platform.glb")
try:
    bpy.ops.export_scene.gltf(filepath=glb_file, export_format='GLB')
    print("SAVED_MASTER_GLB:", glb_file)
except Exception as e:
    print("GLB_NOTE:", e)

# Export standard OBJ
obj_file = os.path.join(dir_path, "agrigcs_platform.obj")
try:
    if hasattr(bpy.ops.wm, "obj_export"):
        bpy.ops.wm.obj_export(filepath=obj_file)
    elif hasattr(bpy.ops.export_scene, "obj"):
        bpy.ops.export_scene.obj(filepath=obj_file)
    print("SAVED_MASTER_OBJ:", obj_file)
except Exception as e:
    print("OBJ_NOTE:", e)

# Set 3D Viewport to Hero Camera and Material Preview
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'CAMERA'
                space.shading.type = 'MATERIAL'

print("AGRIGCS_PHYSICAL_PROTOTYPE_BUILT_SUCCESSFULLY")
