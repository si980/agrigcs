# pyrefly: ignore [missing-import]
import bpy
import math
import random
import os
import traceback

log_file = r"c:\Users\Dell\OneDrive\Documents\gate for all\New folder\stitch_agrigcs_iot_command_platform\stitch_agrigcs_iot_command_platform\orbit\build_status.log"
with open(log_file, "w") as f:
    f.write("STARTING MASTER SCRIPT\n")

# ==============================================================================
# AGRIGCS SMART AGRICULTURE TESTBED - MASTER PROTOTYPE SPECIFICATION
# Physical Dimensions: 3.0m (L) x 2.0m (W) x 1.2m (H)
# Optimization: Mesh sharing & fast object creation (No slow operator loops)
# ==============================================================================

# Disable undo for instant execution
bpy.context.preferences.edit.use_global_undo = False

# Clear all previous objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
for me in list(bpy.data.meshes):
    bpy.data.meshes.remove(me)

# Create Master Turntable Parent
turntable_root = bpy.data.objects.new("AgriGCS_Turntable_Root", None)
turntable_root.empty_display_type = 'PLAIN_AXES'

# Create Required Collections
col_names = [
    "AGRICGS_PLATFORM",
    "ZONE_A_SWEET_CORN",
    "ZONE_B_ORGANIC_KALE",
    "ZONE_C_SOYBEAN",
    "SOIL_SYSTEM",
    "IOT_SENSORS",
    "WEATHER_STATION",
    "SOLAR_SYSTEM",
    "IRRIGATION",
    "AUTONOMOUS_ROVER",
    "BRANDING",
    "CAMERAS",
    "LIGHTING"
]

cols = {}
for name in col_names:
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    cols[name] = c

cols["AGRICGS_PLATFORM"].objects.link(turntable_root)

# ------------------------------------------------------------------------------
# PBR MATERIAL FACTORY
# ------------------------------------------------------------------------------
def create_mat(name, color, roughness=0.5, metallic=0.0, emission=None, alpha=1.0):
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
            bsdf.inputs['Emission Strength'].default_value = 2.0
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

# Materials
mat_concrete = create_mat("Concrete_Base", (0.78, 0.80, 0.82, 1.0), roughness=0.82)
mat_concrete_dark = create_mat("Concrete_Bevel", (0.64, 0.66, 0.68, 1.0), roughness=0.85)
mat_galv_steel = create_mat("Galvanized_Steel", (0.50, 0.52, 0.54, 1.0), roughness=0.35, metallic=0.85)
mat_glass = create_mat("Tempered_Glass_Cutaway", (0.88, 0.94, 0.98, 1.0), roughness=0.05, alpha=0.32)
mat_screws = create_mat("Stainless_Fasteners", (0.85, 0.86, 0.88, 1.0), roughness=0.2, metallic=0.95)

# Stratified Soil
mat_soil_top = create_mat("Soil_Organic_Topsoil", (0.22, 0.14, 0.08, 1.0), roughness=0.95)
mat_soil_mid = create_mat("Soil_Subsoil_Loam", (0.34, 0.22, 0.13, 1.0), roughness=0.96)
mat_soil_clay = create_mat("Soil_Moist_Clay", (0.28, 0.18, 0.12, 1.0), roughness=0.92)
mat_soil_drain = create_mat("Soil_Aggregate_Gravel", (0.38, 0.40, 0.42, 1.0), roughness=0.88, metallic=0.1)
mat_root = create_mat("Plant_Root_System", (0.82, 0.76, 0.62, 1.0), roughness=0.6)

# Plant materials
mat_corn_stalk = create_mat("Corn_Stalk_Green", (0.24, 0.48, 0.15, 1.0), roughness=0.45)
mat_corn_leaf = create_mat("Corn_Leaf_Green", (0.18, 0.44, 0.12, 1.0), roughness=0.4)
mat_corn_tassel = create_mat("Corn_Tassel_Yellow", (0.88, 0.72, 0.22, 1.0), roughness=0.55)
mat_kale_leaf = create_mat("Kale_Deep_Green", (0.10, 0.32, 0.18, 1.0), roughness=0.75)
mat_soy_leaf = create_mat("Soybean_Fresh_Green", (0.30, 0.62, 0.20, 1.0), roughness=0.4)

# Technical parts
mat_drip_tube = create_mat("Drip_Matte_Black", (0.05, 0.05, 0.06, 1.0), roughness=0.3)
mat_drip_emitter = create_mat("Drip_Emitter_Blue", (0.1, 0.35, 0.7, 1.0), roughness=0.3)
mat_sensor_white = create_mat("Industrial_ABS_White", (0.94, 0.94, 0.95, 1.0), roughness=0.25)
mat_sensor_stem = create_mat("Sensor_Stainless_Stem", (0.7, 0.72, 0.75, 1.0), roughness=0.2, metallic=0.9)
mat_solar_pv = create_mat("PV_Solar_Cell", (0.04, 0.12, 0.32, 1.0), roughness=0.15, metallic=0.88)
mat_rover_body = create_mat("Rover_Body_White", (0.92, 0.93, 0.95, 1.0), roughness=0.25)
mat_rover_trim = create_mat("Rover_Dark_Trim", (0.12, 0.13, 0.15, 1.0), roughness=0.4, metallic=0.6)
mat_rover_tire = create_mat("Rover_Tire_Rubber", (0.06, 0.06, 0.07, 1.0), roughness=0.92)

# Branding & Signs
mat_placard_bg = create_mat("Placard_Black_Matte", (0.08, 0.10, 0.12, 1.0), roughness=0.4)
mat_brand_green = create_mat("AgriGCS_Dark_Green", (0.05, 0.45, 0.22, 1.0), roughness=0.3)
mat_brand_white = create_mat("AgriGCS_Text_White", (0.98, 0.98, 0.98, 1.0), roughness=0.2)
mat_led_cyan = create_mat("Status_Cyan_LED", (0.0, 0.85, 0.72, 1.0), roughness=0.1, emission=(0.0, 0.9, 0.75, 1.0))

# Aliases
mat_brackets_steel = mat_screws
mat_rover_rubber = mat_rover_tire

# ------------------------------------------------------------------------------
# PROTOTYPE PRIMITIVE MESHES (INSTANCED FOR MAXIMUM EFFICIENCY)
# ------------------------------------------------------------------------------
# Box generator
def make_cube_mesh(name, sx, sy, sz, mat):
    me = bpy.data.meshes.new(name)
    verts = [
        (-sx/2, -sy/2, -sz/2), (sx/2, -sy/2, -sz/2), (sx/2, sy/2, -sz/2), (-sx/2, sy/2, -sz/2),
        (-sx/2, -sy/2, sz/2),  (sx/2, -sy/2, sz/2),  (sx/2, sy/2, sz/2),  (-sx/2, sy/2, sz/2)
    ]
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
        (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)
    ]
    me.from_pydata(verts, [], faces)
    me.update()
    if mat:
        me.materials.append(mat)
    return me

def make_cylinder_mesh(name, r, d, segments, mat):
    me = bpy.data.meshes.new(name)
    verts = []
    # Bottom circle
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        verts.append((r * math.cos(theta), r * math.sin(theta), -d/2))
    # Top circle
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        verts.append((r * math.cos(theta), r * math.sin(theta), d/2))
    # Center caps
    verts.append((0, 0, -d/2))
    verts.append((0, 0, d/2))
    b_center = segments * 2
    t_center = segments * 2 + 1
    
    faces = []
    # Side quads
    for i in range(segments):
        nxt = (i + 1) % segments
        faces.append((i, nxt, nxt + segments, i + segments))
    # Bottom fan
    for i in range(segments):
        nxt = (i + 1) % segments
        faces.append((b_center, nxt, i))
    # Top fan
    for i in range(segments):
        nxt = (i + 1) % segments
        faces.append((t_center, i + segments, nxt + segments))
        
    me.from_pydata(verts, [], faces)
    me.update()
    if mat:
        me.materials.append(mat)
    return me

# Instant Object Spawner
def spawn(col_name, name, mesh, loc, rot=(0,0,0), scale=(1,1,1), parent=turntable_root):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    obj.scale = scale
    cols[col_name].objects.link(obj)
    if parent:
        obj.parent = parent
    return obj

# ==============================================================================
# 1. MAIN PLATFORM STRUCTURE (3.0m x 2.0m x 1.2m)
# ==============================================================================
# Concrete Base (0.45m height)
mesh_base = make_cube_mesh("Me_Base", 3.0, 2.0, 0.45, mat_concrete)
spawn("AGRICGS_PLATFORM", "Concrete_Base_Platform", mesh_base, (0, 0, 0.225))

# Skid channels for forklift transport
mesh_skid = make_cube_mesh("Me_Skid", 0.35, 2.02, 0.12, mat_concrete_dark)
spawn("AGRICGS_PLATFORM", "Skid_Channel_Left", mesh_skid, (-0.75, 0, 0.06))
spawn("AGRICGS_PLATFORM", "Skid_Channel_Right", mesh_skid, (0.75, 0, 0.06))

# Galvanized Steel Containment Trough (Height = 0.75m from Z=0.45 to 1.20)
mesh_wall_back = make_cube_mesh("Me_WBack", 3.0, 0.05, 0.75, mat_galv_steel)
spawn("AGRICGS_PLATFORM", "Trough_Wall_Back", mesh_wall_back, (0, 0.975, 0.825))

mesh_wall_side = make_cube_mesh("Me_WSide", 0.05, 1.95, 0.75, mat_galv_steel)
spawn("AGRICGS_PLATFORM", "Trough_Wall_Left", mesh_wall_side, (-1.475, 0.025, 0.825))
spawn("AGRICGS_PLATFORM", "Trough_Wall_Right", mesh_wall_side, (1.475, 0.025, 0.825))

# Front Tempered Glass / Acrylic Cutaway Retaining Pane
mesh_front_glass = make_cube_mesh("Me_FrontGlass", 2.95, 0.02, 0.74, mat_glass)
spawn("AGRICGS_PLATFORM", "Front_Glass_Cutaway_Pane", mesh_front_glass, (0, -0.99, 0.82))

# Corner Brackets and Bolts
mesh_bracket = make_cube_mesh("Me_CornerBracket", 0.08, 0.08, 0.78, mat_brackets_steel)
mesh_bolt = make_cylinder_mesh("Me_Bolt", 0.015, 0.03, 6, mat_screws)
for cx in [-1.48, 1.48]:
    for cy in [-0.98, 0.98]:
        spawn("AGRICGS_PLATFORM", "Corner_Bracket", mesh_bracket, (cx, cy, 0.825))
        for bz in [0.55, 0.85, 1.15]:
            spawn("AGRICGS_PLATFORM", "Bolt", mesh_bolt, (cx, cy, bz), rot=(0, math.pi/2, 0))

# Glass Retainers
mesh_retainer = make_cube_mesh("Me_GlassRetainer", 0.04, 0.04, 0.75, mat_brackets_steel)
spawn("AGRICGS_PLATFORM", "Glass_Retainer_Left", mesh_retainer, (-1.0, -1.0, 0.825))
spawn("AGRICGS_PLATFORM", "Glass_Retainer_Right", mesh_retainer, (1.0, -1.0, 0.825))

# ==============================================================================
# 2. STRATIFIED SOIL BED & SUBTERRANEAN PROFILES
# ==============================================================================
# 4 distinct horizontal soil strata layers
mesh_soil_drain = make_cube_mesh("Me_SoilDrain", 2.90, 1.90, 0.10, mat_soil_drain)
mesh_soil_clay = make_cube_mesh("Me_SoilClay", 2.90, 1.90, 0.18, mat_soil_clay)
mesh_soil_mid = make_cube_mesh("Me_SoilMid", 2.90, 1.90, 0.24, mat_soil_mid)
mesh_soil_top = make_cube_mesh("Me_SoilTop", 2.90, 1.90, 0.20, mat_soil_top)

spawn("SOIL_SYSTEM", "Layer_1_Drainage_Aggregate", mesh_soil_drain, (0, 0, 0.51))
spawn("SOIL_SYSTEM", "Layer_2_Moist_Clay", mesh_soil_clay, (0, 0, 0.65))
spawn("SOIL_SYSTEM", "Layer_3_Sandy_Loam", mesh_soil_mid, (0, 0, 0.86))
spawn("SOIL_SYSTEM", "Layer_4_Organic_Topsoil", mesh_soil_top, (0, 0, 1.08))

# Subterranean Root Networks in Cutaway View
mesh_root_tap = make_cylinder_mesh("Me_RootTap", 0.012, 0.45, 8, mat_root)
mesh_root_fine = make_cylinder_mesh("Me_RootFine", 0.005, 0.15, 6, mat_root)

# Corn deep roots (Zone A)
for rx in [-1.2, -0.95, -0.7]:
    spawn("SOIL_SYSTEM", "Corn_Deep_Root", mesh_root_tap, (rx, -0.97, 0.85), rot=(0.1, 0, 0.05))
    for bi in range(4):
        spawn("SOIL_SYSTEM", "Corn_Fine_Root", mesh_root_fine, (rx + (bi-1.5)*0.05, -0.97, 0.75 + bi*0.06), rot=(0.2, 0.3, bi*0.4))

# Kale fibrous spreading roots (Zone B)
for rk in [-0.25, 0.0, 0.25]:
    spawn("SOIL_SYSTEM", "Kale_Root", mesh_root_tap, (rk, -0.97, 0.95), rot=(0, 0.2, 0), scale=(0.7, 0.7, 0.7))
    for bi in range(3):
        spawn("SOIL_SYSTEM", "Kale_Fine_Root", mesh_root_fine, (rk + (bi-1)*0.05, -0.97, 0.88 + bi*0.05), rot=(0.3, 0.1, bi*0.6))

# Soybean tap roots with nodule clusters (Zone C)
for rs in [0.7, 0.95, 1.2]:
    spawn("SOIL_SYSTEM", "Soybean_Tap_Root", mesh_root_tap, (rs, -0.97, 0.90), rot=(-0.1, 0, -0.05), scale=(0.85, 0.85, 0.85))

# Multi-Depth Embedded Soil Sensor Probes (10cm, 30cm, 60cm depths)
mesh_probe_stem = make_cylinder_mesh("Me_CutawayProbeStem", 0.012, 0.12, 8, mat_sensor_stem)
mesh_probe_cable = make_cylinder_mesh("Me_CutawayProbeCable", 0.004, 1.0, 6, mat_rover_trim)

spawn("SOIL_SYSTEM", "Cutaway_Probe_10cm", mesh_probe_stem, (-0.5, -0.97, 1.08), rot=(math.pi/2, 0, 0))
spawn("SOIL_SYSTEM", "Cutaway_Probe_30cm", mesh_probe_stem, (-0.5, -0.97, 0.88), rot=(math.pi/2, 0, 0))
spawn("SOIL_SYSTEM", "Cutaway_Probe_60cm", mesh_probe_stem, (-0.5, -0.97, 0.58), rot=(math.pi/2, 0, 0))
spawn("SOIL_SYSTEM", "Cutaway_Probe_Conduit", mesh_probe_cable, (-0.5, -0.97, 0.85), scale=(1, 1, 0.7))

# ==============================================================================
# 3. ZONE A: SWEET CORN
# ==============================================================================
mesh_corn_stalk = make_cylinder_mesh("Me_CornStalk", 0.016, 0.88, 8, mat_corn_stalk)
mesh_corn_tassel = make_cylinder_mesh("Me_CornTassel", 0.025, 0.14, 6, mat_corn_tassel)
mesh_corn_leaf = make_cube_mesh("Me_CornLeaf", 0.24, 0.06, 0.006, mat_corn_leaf)

random.seed(101)
corn_x = [-1.32, -1.16, -1.00, -0.84, -0.68]
corn_y = [-0.75, -0.55, -0.35, -0.15, 0.05, 0.25, 0.45, 0.65, 0.80]

for cx in corn_x:
    for cy in corn_y:
        jx = cx + (random.random() - 0.5) * 0.04
        jy = cy + (random.random() - 0.5) * 0.04
        sh = 0.85 + random.random() * 0.25
        spawn("ZONE_A_SWEET_CORN", "Corn_Stalk", mesh_corn_stalk, (jx, jy, 1.18 + sh/2), scale=(1, 1, sh/0.88))
        spawn("ZONE_A_SWEET_CORN", "Corn_Tassel", mesh_corn_tassel, (jx, jy, 1.18 + sh + 0.06))
        for li in range(2):
            ang = li * 2.5 + random.random() * 0.4
            spawn("ZONE_A_SWEET_CORN", "Corn_Leaf", mesh_corn_leaf, 
                  (jx + math.cos(ang)*0.10, jy + math.sin(ang)*0.10, 1.18 + sh*(0.4 + li*0.25)), 
                  rot=(0.3, 0.2, ang))

# ==============================================================================
# 4. ZONE B: ORGANIC KALE
# ==============================================================================
mesh_kale_cluster = make_cube_mesh("Me_KaleCluster", 0.16, 0.16, 0.10, mat_kale_leaf)

kale_x = [-0.38, -0.22, -0.06, 0.10, 0.26, 0.38]
kale_y = [-0.72, -0.50, -0.28, -0.06, 0.16, 0.38]

for kx in kale_x:
    for ky in kale_y:
        # Keep clear for rover and tower
        if (abs(kx - 0.12) < 0.25 and abs(ky + 0.35) < 0.35) or (abs(kx) < 0.30 and ky > 0.40):
            continue
        jx = kx + (random.random() - 0.5) * 0.05
        jy = ky + (random.random() - 0.5) * 0.05
        spawn("ZONE_B_ORGANIC_KALE", "Kale_Bush", mesh_kale_cluster, (jx, jy, 1.23), 
              rot=(random.random()*0.3, random.random()*0.3, random.random()*math.pi))

# ==============================================================================
# 5. ZONE C: SOYBEAN & DRIP IRRIGATION
# ==============================================================================
mesh_drip_tube = make_cylinder_mesh("Me_DripTube", 0.012, 1.84, 8, mat_drip_tube)
mesh_drip_emitter = make_cylinder_mesh("Me_Emitter", 0.008, 0.025, 6, mat_drip_emitter)
mesh_moist_spot = make_cylinder_mesh("Me_MoistSpot", 0.05, 0.005, 8, mat_soil_clay)
mesh_soy_stem = make_cylinder_mesh("Me_SoyStem", 0.008, 0.16, 6, mat_soy_leaf)
mesh_soy_leaf = make_cube_mesh("Me_SoyLeaf", 0.06, 0.04, 0.006, mat_soy_leaf)

soy_x = [0.60, 0.80, 1.00, 1.20, 1.36]

for rx in soy_x:
    # Black continuous drip tube
    spawn("IRRIGATION", "Drip_Tube", mesh_drip_tube, (rx, 0.0, 1.20), rot=(math.pi/2, 0, 0))
    for sy in [-0.75, -0.58, -0.41, -0.24, -0.07, 0.10, 0.27, 0.44, 0.61, 0.78]:
        spawn("IRRIGATION", "Drip_Emitter", mesh_drip_emitter, (rx + 0.03, sy, 1.205))
        spawn("IRRIGATION", "Moist_Soil_Spot", mesh_moist_spot, (rx, sy, 1.185))
        spawn("ZONE_C_SOYBEAN", "Soy_Stem", mesh_soy_stem, (rx - 0.04, sy, 1.26))
        spawn("ZONE_C_SOYBEAN", "Soy_Leaflet", mesh_soy_leaf, (rx - 0.04, sy, 1.33), rot=(0.2, 0.3, 0))

# Main manifold pipe across back
mesh_manifold = make_cylinder_mesh("Me_Manifold", 0.022, 0.95, 8, mat_drip_tube)
mesh_valve = make_cylinder_mesh("Me_Valve", 0.035, 0.08, 8, mat_rover_trim)
spawn("IRRIGATION", "Drip_Manifold", mesh_manifold, (0.98, 0.93, 1.22), rot=(0, math.pi/2, 0))
spawn("IRRIGATION", "Pressure_Valve", mesh_valve, (1.42, 0.93, 1.22), rot=(0, math.pi/2, 0))

# ==============================================================================
# 6. CENTRAL MONITORING TOWER (WEATHER STATION & IOT GATEWAY)
# ==============================================================================
tower_loc = (0.0, 0.65, 1.18)

# Mast legs
mesh_mast_leg = make_cylinder_mesh("Me_MastLeg", 0.016, 1.6, 8, mat_galv_steel)
mesh_mast_strut = make_cylinder_mesh("Me_MastStrut", 0.008, 0.26, 6, mat_galv_steel)

spawn("WEATHER_STATION", "Mast_Leg_FL", mesh_mast_leg, (tower_loc[0] - 0.12, tower_loc[1] - 0.12, tower_loc[2] + 0.8))
spawn("WEATHER_STATION", "Mast_Leg_FR", mesh_mast_leg, (tower_loc[0] + 0.12, tower_loc[1] - 0.12, tower_loc[2] + 0.8))
spawn("WEATHER_STATION", "Mast_Leg_BK", mesh_mast_leg, (tower_loc[0], tower_loc[1] + 0.12, tower_loc[2] + 0.8))

for si in range(4):
    sz = tower_loc[2] + 0.3 + si * 0.38
    spawn("WEATHER_STATION", "Mast_Strut", mesh_mast_strut, (tower_loc[0], tower_loc[1] - 0.12, sz), rot=(0, math.pi/2, 0))

# IoT Gateway Enclosure Box & LED
mesh_gw_box = make_cube_mesh("Me_GWBox", 0.32, 0.22, 0.38, mat_sensor_white)
mesh_led = make_cylinder_mesh("Me_StatusLED", 0.008, 0.01, 8, mat_led_cyan)
mesh_conduit = make_cylinder_mesh("Me_Conduit", 0.012, 0.95, 8, mat_rover_trim)

spawn("WEATHER_STATION", "IoT_Gateway_Enclosure", mesh_gw_box, (tower_loc[0], tower_loc[1] - 0.08, tower_loc[2] + 0.95))
spawn("WEATHER_STATION", "Gateway_Status_LED", mesh_led, (tower_loc[0] + 0.12, tower_loc[1] - 0.19, tower_loc[2] + 1.08), rot=(math.pi/2, 0, 0))
spawn("WEATHER_STATION", "Cable_Conduit", mesh_conduit, (tower_loc[0] + 0.08, tower_loc[1] - 0.06, tower_loc[2] + 0.48))

# Solar Panel Array: 2 x Photovoltaic Panels
mesh_pv_panel = make_cube_mesh("Me_SolarPanel", 0.42, 0.32, 0.025, mat_solar_pv)
mesh_pv_frame = make_cube_mesh("Me_SolarFrame", 0.44, 0.34, 0.02, mat_brackets_steel)
mesh_pv_bar = make_cylinder_mesh("Me_SolarBar", 0.015, 0.92, 8, mat_galv_steel)

panel_z = tower_loc[2] + 1.45
for px in [-0.36, 0.36]:
    spawn("SOLAR_SYSTEM", "Solar_Panel", mesh_pv_panel, (tower_loc[0] + px, tower_loc[1] - 0.06, panel_z), rot=(math.radians(-30), 0, 0))
    spawn("SOLAR_SYSTEM", "Solar_Frame", mesh_pv_frame, (tower_loc[0] + px, tower_loc[1] - 0.06, panel_z - 0.005), rot=(math.radians(-30), 0, 0))
spawn("SOLAR_SYSTEM", "Solar_Crossbar", mesh_pv_bar, (tower_loc[0], tower_loc[1] - 0.02, panel_z - 0.08), rot=(0, math.pi/2, 0))

# Weather Station Instruments (Anemometer, Wind Vane, Radiation Shield, Antennas)
mesh_w_pole = make_cylinder_mesh("Me_WPole", 0.016, 0.85, 8, mat_galv_steel)
mesh_anemometer = make_cylinder_mesh("Me_Anemometer", 0.03, 0.08, 8, mat_sensor_white)
mesh_wind_vane = make_cube_mesh("Me_WindVane", 0.004, 0.14, 0.08, mat_sensor_white)
mesh_shield_plate = make_cylinder_mesh("Me_ShieldDisc", 0.07, 0.012, 12, mat_sensor_white)
mesh_lora_ant = make_cylinder_mesh("Me_LoRaAnt", 0.008, 0.45, 8, mat_rover_trim)
mesh_gps_ant = make_cylinder_mesh("Me_GPSAnt", 0.045, 0.03, 12, mat_sensor_white)

spawn("WEATHER_STATION", "Weather_Pole", mesh_w_pole, (tower_loc[0], tower_loc[1], tower_loc[2] + 1.95))
spawn("WEATHER_STATION", "Anemometer", mesh_anemometer, (tower_loc[0] - 0.22, tower_loc[1], tower_loc[2] + 2.35))
spawn("WEATHER_STATION", "Wind_Vane", mesh_wind_vane, (tower_loc[0] + 0.22, tower_loc[1] + 0.08, tower_loc[2] + 2.42))
for di in range(6):
    spawn("WEATHER_STATION", "Radiation_Shield", mesh_shield_plate, (tower_loc[0] + 0.05, tower_loc[1] + 0.16, tower_loc[2] + 2.18 + di*0.028))
spawn("WEATHER_STATION", "LoRa_Antenna", mesh_lora_ant, (tower_loc[0] - 0.05, tower_loc[1] + 0.16, tower_loc[2] + 2.45))
spawn("WEATHER_STATION", "GPS_Antenna", mesh_gps_ant, (tower_loc[0] - 0.08, tower_loc[1] - 0.12, tower_loc[2] + 1.62))

# ==============================================================================
# 7. FIELD IOT SOIL PROBES (Distributed across zones)
# ==============================================================================
mesh_probe_stem_f = make_cylinder_mesh("Me_FieldProbeStem", 0.012, 0.28, 8, mat_sensor_stem)
mesh_probe_head_f = make_cube_mesh("Me_FieldProbeHead", 0.07, 0.07, 0.09, mat_sensor_white)
mesh_probe_cap_f = make_cube_mesh("Me_FieldProbeCap", 0.065, 0.065, 0.008, mat_solar_pv)

probe_coords = [
    (-1.35, -0.65), (-0.75, -0.65), (-1.35, 0.65), (-0.75, 0.65), # Zone A
    (-0.35, -0.65), (0.35, -0.65),                                # Zone B
    (0.60, -0.80), (0.80, -0.80), (1.00, -0.80), (1.20, -0.80), (1.36, -0.80), # Zone C
    (0.60, 0.80), (1.00, 0.80), (1.36, 0.80)
]

for px, py in probe_coords:
    spawn("IOT_SENSORS", "IoT_Probe_Stake", mesh_probe_stem_f, (px, py, 1.26))
    spawn("IOT_SENSORS", "IoT_Probe_Enclosure", mesh_probe_head_f, (px, py, 1.42))
    spawn("IOT_SENSORS", "IoT_Probe_SolarCap", mesh_probe_cap_f, (px, py, 1.47))

# ==============================================================================
# 8. AUTONOMOUS SCOUT ROVER (Zone B, between crop rows)
# ==============================================================================
rover_pos = (0.12, -0.35, 1.18)

mesh_rover_pan = make_cube_mesh("Me_RPan", 0.32, 0.44, 0.08, mat_rover_trim)
mesh_rover_body = make_cube_mesh("Me_RBody", 0.28, 0.38, 0.12, mat_rover_body)
mesh_rover_pv = make_cube_mesh("Me_RPV", 0.24, 0.30, 0.012, mat_solar_pv)
mesh_rover_cam = make_cube_mesh("Me_RCam", 0.16, 0.05, 0.04, mat_rover_trim)
mesh_rover_tire = make_cylinder_mesh("Me_RTire", 0.075, 0.06, 12, mat_rover_rubber)
mesh_rover_hub = make_cylinder_mesh("Me_RHub", 0.038, 0.065, 8, mat_brackets_steel)
mesh_rover_whip = make_cylinder_mesh("Me_RWhip", 0.005, 0.22, 6, mat_brackets_steel)

spawn("AUTONOMOUS_ROVER", "Rover_Lower_Pan", mesh_rover_pan, (rover_pos[0], rover_pos[1], rover_pos[2] + 0.12))
spawn("AUTONOMOUS_ROVER", "Rover_Upper_Body", mesh_rover_body, (rover_pos[0], rover_pos[1] - 0.01, rover_pos[2] + 0.20))
spawn("AUTONOMOUS_ROVER", "Rover_Solar_Roof", mesh_rover_pv, (rover_pos[0], rover_pos[1] - 0.01, rover_pos[2] + 0.265))
spawn("AUTONOMOUS_ROVER", "Rover_Camera_Module", mesh_rover_cam, (rover_pos[0], rover_pos[1] - 0.21, rover_pos[2] + 0.21))
spawn("AUTONOMOUS_ROVER", "Rover_Antenna", mesh_rover_whip, (rover_pos[0] + 0.10, rover_pos[1] + 0.15, rover_pos[2] + 0.37))

for wox, woy in [(-0.18, -0.14), (0.18, -0.14), (-0.18, 0.14), (0.18, 0.14)]:
    spawn("AUTONOMOUS_ROVER", "Rover_Tire", mesh_rover_tire, 
          (rover_pos[0] + wox, rover_pos[1] + woy, rover_pos[2] + 0.075), rot=(0, math.pi/2, 0))
    spawn("AUTONOMOUS_ROVER", "Rover_Wheel_Hub", mesh_rover_hub, 
          (rover_pos[0] + wox, rover_pos[1] + woy, rover_pos[2] + 0.075), rot=(0, math.pi/2, 0))

# ==============================================================================
# 9. BRANDING & ZONE PLACARDS
# ==============================================================================
# Front Face AgriGCS Logo Plate
mesh_brand_plate = make_cube_mesh("Me_BrandPlate", 1.2, 0.02, 0.25, mat_concrete_dark)
mesh_brand_logo = make_cube_mesh("Me_BrandLogo", 0.85, 0.01, 0.12, mat_brand_green)
mesh_brand_sub = make_cube_mesh("Me_BrandSub", 0.95, 0.01, 0.04, mat_brand_white)

spawn("BRANDING", "Brand_Plate_Front", mesh_brand_plate, (0, -1.01, 0.225))
spawn("BRANDING", "AgriGCS_Logo_Text", mesh_brand_logo, (0, -1.025, 0.25))
spawn("BRANDING", "AgriGCS_Subtitle", mesh_brand_sub, (0, -1.025, 0.16))

# 3 Zone Identification Placards on Front Rim
mesh_placard_bg = make_cube_mesh("Me_PlacardPlate", 0.42, 0.02, 0.16, mat_placard_bg)
mesh_placard_txt = make_cube_mesh("Me_PlacardText", 0.38, 0.008, 0.12, mat_brand_white)

# Zone A: "ZONE A \n Sweet Corn"
spawn("BRANDING", "Placard_Plate_A", mesh_placard_bg, (-0.95, -1.02, 1.20))
spawn("BRANDING", "Placard_Label_A", mesh_placard_txt, (-0.95, -1.032, 1.20))

# Zone B: "ZONE B \n Organic Kale"
spawn("BRANDING", "Placard_Plate_B", mesh_placard_bg, (0.0, -1.02, 1.20), scale=(1.05, 1, 1))
spawn("BRANDING", "Placard_Label_B", mesh_placard_txt, (0.0, -1.032, 1.20), scale=(1.05, 1, 1))

# Zone C: "ZONE C \n Soybean"
spawn("BRANDING", "Placard_Plate_C", mesh_placard_bg, (0.95, -1.02, 1.20))
spawn("BRANDING", "Placard_Label_C", mesh_placard_txt, (0.95, -1.032, 1.20))

# ==============================================================================
# 10. CAMERAS (5 CORE ORTHO/HERO VIEWS + 12-STEP 360 ROTATION)
# ==============================================================================
def make_camera(name, loc, rot_deg, lens=50):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = loc
    cam_obj.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
    cols["CAMERAS"].objects.link(cam_obj)
    return cam_obj

# 5 Requested Cameras
make_camera("Camera_Front_0", (0, -4.8, 1.2), (90, 0, 0), lens=55)
make_camera("Camera_Right_90", (5.6, 0, 1.2), (90, 0, 90), lens=55)
make_camera("Camera_Back_180", (0, 4.8, 1.2), (90, 0, 180), lens=55)
make_camera("Camera_Left_270", (-5.6, 0, 1.2), (90, 0, -90), lens=55)
make_camera("Camera_Top", (0, 0, 6.2), (0, 0, 0), lens=48)

# Main Hero 3/4 Isometric Perspective Camera
hero_cam = make_camera("Camera_Hero_Isometric_34", (3.2, -4.0, 2.8), (65, 0, 40), lens=50)
bpy.context.scene.camera = hero_cam

# 12 Evenly Spaced 360-degree Cameras (0°, 30°, 60°, ... 330°)
cam_radius = 4.8
cam_height = 2.4
center_z = 0.95

for deg in [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]:
    rad = math.radians(deg)
    cx = cam_radius * math.sin(rad)
    cy = -cam_radius * math.cos(rad)
    dx = -cx
    dy = -cy
    dz = center_z - cam_height
    dist_xy = math.sqrt(dx*dx + dy*dy)
    pitch = math.pi/2 - math.atan2(dz, dist_xy)
    yaw = math.atan2(dx, -dy)
    make_camera(f"Camera_360_{deg:03d}", (cx, cy, cam_height), 
                (math.degrees(pitch), 0, math.degrees(yaw)), lens=50)

# ==============================================================================
# 11. TURNTABLE ANIMATION (Frame 1 = 0°, Frame 120 = 360°)
# ==============================================================================
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120

turntable_root.rotation_euler = (0, 0, 0)
turntable_root.keyframe_insert(data_path="rotation_euler", frame=1)
turntable_root.rotation_euler = (0, 0, math.radians(360))
turntable_root.keyframe_insert(data_path="rotation_euler", frame=120)

# Set linear interpolation
try:
    if turntable_root.animation_data and turntable_root.animation_data.action:
        act = turntable_root.animation_data.action
        if hasattr(act, "fcurves"):
            for fcurve in act.fcurves:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = 'LINEAR'
        elif hasattr(act, "curves"):
            for curve in act.curves:
                for kp in curve.keyframe_points:
                    kp.interpolation = 'LINEAR'
except Exception as e:
    pass

# ==============================================================================
# 12. NATURAL DAYLIGHT LIGHTING
# ==============================================================================
sun_data = bpy.data.lights.new(name="Sun_Key_Data", type='SUN')
sun_data.energy = 4.8
sun_data.color = (1.0, 0.97, 0.92)
sun_data.angle = math.radians(2.0)
sun_obj = bpy.data.objects.new("Sun_Key_Daylight", sun_data)
sun_obj.location = (15, -20, 25)
cols["LIGHTING"].objects.link(sun_obj)

sky_data = bpy.data.lights.new(name="Sky_Fill_Data", type='SUN')
sky_data.energy = 2.0
sky_data.color = (0.75, 0.88, 1.0)
sky_obj = bpy.data.objects.new("Sky_Fill_Ambient", sky_data)
sky_obj.location = (-15, 20, 20)
cols["LIGHTING"].objects.link(sky_obj)

# Re-enable global undo
bpy.context.preferences.edit.use_global_undo = True

# Save to .blend file
dir_path = r"c:\Users\Dell\OneDrive\Documents\gate for all\New folder\stitch_agrigcs_iot_command_platform\stitch_agrigcs_iot_command_platform\orbit"
blend_file = os.path.join(dir_path, "agrigcs_platform.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)
print("SUCCESSFULLY_SAVED_MASTER_BLEND:", blend_file)

# Export standard GLB
glb_file = os.path.join(dir_path, "agrigcs_platform.glb")
try:
    bpy.ops.export_scene.gltf(filepath=glb_file, export_format='GLB')
    print("SUCCESSFULLY_SAVED_MASTER_GLB:", glb_file)
except Exception as e:
    print("GLB_NOTE:", e)

# Export standard OBJ
obj_file = os.path.join(dir_path, "agrigcs_platform.obj")
try:
    if hasattr(bpy.ops.wm, "obj_export"):
        bpy.ops.wm.obj_export(filepath=obj_file)
    elif hasattr(bpy.ops.export_scene, "obj"):
        bpy.ops.export_scene.obj(filepath=obj_file)
    print("SUCCESSFULLY_SAVED_MASTER_OBJ:", obj_file)
except Exception as e:
    print("OBJ_NOTE:", e)

with open(log_file, "a") as f:
    f.write("COMPLETED ALL SUCCESS\n")
print("ALL_OPERATIONS_COMPLETED_SUCCESSFULLY")
