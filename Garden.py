import bpy
import random
import math
import colorsys
import time

# --- 1. Utilities & Optimization ---
def clean_scene():
    """Cleans scene and purges unused data to prevent RAM bloating."""
    if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT') 
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Purge orphan data (materials/meshes with no users)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
            
    # Lighting
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
    bpy.context.object.data.energy = 5.0

def create_material(name, color, roughness=0.5, metallic=0.0, emission=False):
    # Check if material exists first to avoid duplicates
    if name in bpy.data.materials:
        return bpy.data.materials[name]
        
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    if emission:
        node_emission = mat.node_tree.nodes.new(type="ShaderNodeEmission")
        node_emission.inputs['Color'].default_value = color
        node_emission.inputs['Strength'].default_value = 15.0
        mat.node_tree.links.new(node_emission.outputs[0], mat.node_tree.nodes["Material Output"].inputs[0])
    return mat

def get_bright_color():
    h = random.random()
    s = random.uniform(0.8, 1.0)
    v = 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (r, g, b, 1)

# --- 2. Material Cache (The Speed Booster) ---
# We generate a palette ONCE, then reuse these materials.
class MaterialPalette:
    def __init__(self):
        self.flower_mats = []
        self.wing_mats = []
        self.grass_mat = None
        self.dirt_mat = None
        self.generate_palette()
        
    def generate_palette(self):
        # Create 10 variations of flower colors
        for i in range(10):
            col = get_bright_color()
            self.flower_mats.append(create_material(f"Cache_Flower_{i}", col, emission=True))
            
        # Create 10 variations of butterfly wings
        for i in range(10):
            col = get_bright_color()
            self.wing_mats.append(create_material(f"Cache_Wing_{i}", col))
            
        self.grass_mat = create_material("Cache_Grass", (0.05, 0.5, 0.05, 1))
        self.dirt_mat = create_material("Cache_Dirt", (0.1, 0.05, 0.02, 1))

    def get_flower_mat(self):
        return random.choice(self.flower_mats)
    
    def get_wing_mat(self):
        return random.choice(self.wing_mats)

# --- 3. Car & Environment ---
class RealisticCar:
    def __init__(self):
        self.root = None
        self.wheels = []
        
    def create_body_part(self, name, size, loc, mat, parent):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        obj = bpy.context.object
        obj.name = name
        obj.scale = size
        obj.data.materials.append(mat)
        obj.parent = parent
        
        # Reduced bevel segments for performance
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.05
        bevel.segments = 2 # Lower segment count is faster
        return obj

    def generate(self, start_pos=(0,0,0)):
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=start_pos)
        self.root = bpy.context.object
        self.root.name = "Car_Root"

        # Car Materials
        paint_mat = create_material("Car_Paint", (0.8, 0.1, 0.1, 1), roughness=0.2, metallic=0.7)
        glass_mat = create_material("Car_Glass", (0.1, 0.1, 0.2, 1), roughness=0.0, metallic=0.9)
        black_mat = create_material("Car_Plastic", (0.05, 0.05, 0.05, 1), roughness=0.5)
        chrome_mat = create_material("Car_Chrome", (0.8, 0.8, 0.8, 1), roughness=0.1, metallic=1.0)
        light_mat = create_material("Car_Headlight", (1, 1, 0.9, 1), emission=True)
        tail_mat = create_material("Car_Taillight", (1, 0, 0, 1), emission=True)

        # Build Body (Simplified Bevels)
        self.create_body_part("Chassis", (1.8, 4.5, 0.6), (0, 0, 0.6), paint_mat, self.root)
        self.create_body_part("Cabin", (1.4, 2.2, 0.5), (0, -0.3, 1.15), paint_mat, self.root)
        self.create_body_part("Windshield", (1.35, 0.1, 0.4), (0, 0.8, 1.2), glass_mat, self.root).rotation_euler.x = -0.5
        self.create_body_part("RearWindow", (1.35, 0.1, 0.4), (0, -1.4, 1.2), glass_mat, self.root).rotation_euler.x = 0.5
        self.create_body_part("FrontBumper", (1.85, 0.2, 0.3), (0, 2.25, 0.45), black_mat, self.root)
        self.create_body_part("RearBumper", (1.85, 0.2, 0.3), (0, -2.25, 0.45), black_mat, self.root)
        
        # Lights
        self.create_body_part("HL_L", (0.3, 0.1, 0.15), (-0.6, 2.26, 0.75), light_mat, self.root)
        self.create_body_part("HL_R", (0.3, 0.1, 0.15), (0.6, 2.26, 0.75), light_mat, self.root)
        self.create_body_part("TL_L", (0.3, 0.1, 0.15), (-0.6, -2.26, 0.75), tail_mat, self.root)
        self.create_body_part("TL_R", (0.3, 0.1, 0.15), (0.6, -2.26, 0.75), tail_mat, self.root)

        # Wheels
        wheel_locs = [(-0.9, 1.4), (0.9, 1.4), (-0.9, -1.4), (0.9, -1.4)]
        rubber_mat = create_material("Car_Rubber", (0.02, 0.02, 0.02, 1), roughness=0.8)
        
        for x, y in wheel_locs:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, y, 0.35))
            wheel_root = bpy.context.object
            wheel_root.parent = self.root
            
            bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.25, location=(0,0,0))
            tire = bpy.context.object
            tire.rotation_euler.y = math.radians(90)
            tire.data.materials.append(rubber_mat)
            tire.parent = wheel_root
            
            self.wheels.append(wheel_root)

    def animate(self, distance=100, end_frame=250):
        if not self.root: return
        self.root.location.y = 0
        self.root.keyframe_insert("location", frame=1)
        self.root.location.y = distance
        self.root.keyframe_insert("location", frame=end_frame)
        
        rotations = distance / 2.2 * (2 * math.pi)
        for wheel in self.wheels:
            wheel.rotation_euler.x = 0
            wheel.keyframe_insert("rotation_euler", frame=1)
            wheel.rotation_euler.x = -rotations 
            wheel.keyframe_insert("rotation_euler", frame=end_frame)

def create_environment(road_len, palette):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, road_len/2, 0.02))
    road = bpy.context.object
    road.scale = (6, road_len, 1)
    road_mat = create_material("Asphalt", (0.15, 0.15, 0.15, 1), roughness=0.9)
    road.data.materials.append(road_mat)
    
    for side_x in [-8, 8]:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(side_x, road_len/2, 0))
        belt = bpy.context.object
        belt.scale = (10, road_len, 1)
        belt.data.materials.append(palette.dirt_mat) 
        
        bpy.ops.object.particle_system_add()
        psys = belt.particle_systems.active
        pset = psys.settings
        pset.type = 'HAIR'
        
        # --- OPTIMIZATION: High Render Count, Low Viewport Count ---
        pset.count = 4000 
        pset.hair_length = 0.2
        pset.child_type = 'INTERPOLATED'
        
        # This keeps the VIEWPORT fast (10 children), but RENDER dense (80 children)
        pset.display_step = 5 # Show only 20% of particles in viewport
        pset.rendered_child_count = 80 
        
        if len(belt.data.materials) < 2:
            belt.data.materials.append(palette.grass_mat)
        pset.material = 2

class VisibleFlower:
    def generate(self, location, palette):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.0, location=(location[0], location[1], 0.5))
        stem = bpy.context.object
        stem.data.materials.append(palette.grass_mat)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(location[0], location[1], 1.0))
        head = bpy.context.object
        # REUSE material from palette
        head.data.materials.append(palette.get_flower_mat())
        head.parent = stem

class Butterfly:
    def generate(self, center, end_frame, palette):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.15, location=center)
        body = bpy.context.object
        body.rotation_euler.x = math.radians(90)
        body.data.materials.append(create_material("BugBlack", (0,0,0,1)))
        
        w_mat = palette.get_wing_mat()
        
        wings = []
        for x_mod in [-1, 1]:
            bpy.ops.mesh.primitive_plane_add(size=0.25, location=(x_mod*0.1, 0, 0))
            w = bpy.context.object
            w.data.materials.append(w_mat)
            w.parent = body
            wings.append((w, x_mod))
            
        start_y = center[1]
        for f in range(1, end_frame, 2):
            for w, mod in wings:
                w.rotation_euler.y = math.radians(60 * mod)
                w.keyframe_insert("rotation_euler", frame=f)
                w.rotation_euler.y = math.radians(-20 * mod)
                w.keyframe_insert("rotation_euler", frame=f+1)
        
        for f in range(1, end_frame, 10):
            prog = f / end_frame
            y = start_y + (prog * 30) 
            x = center[0] + math.sin(f * 0.1) * 2
            z = center[2] + math.sin(f * 0.3) * 0.5
            body.location = (x, y, z)
            body.keyframe_insert("location", frame=f)

# --- 4. Main Execution ---
def generate_scene():
    print("Initializing Scene...")
    clean_scene()
    end_frame = 300
    bpy.context.scene.frame_end = end_frame
    
    # Init Palette (Faster)
    palette = MaterialPalette()
    
    road_len = 150
    create_environment(road_len, palette)
    
    print("Building Car...")
    car = RealisticCar()
    car.generate(start_pos=(0, 0, 0))
    car.animate(distance=road_len - 20, end_frame=end_frame)
    
    print("Planting Flowers...")
    for i in range(60):
        side_offset = random.choice([-8, 8])
        x = side_offset + random.uniform(-4, 4)
        y = random.uniform(0, road_len)
        f = VisibleFlower()
        f.generate((x, y, 0), palette)
        
        if random.random() < 0.25:
            b = Butterfly()
            b.generate((x, y, 1.8), end_frame, palette)

    bpy.ops.object.camera_add(location=(6, -8, 3))
    cam = bpy.context.object
    cam.parent = car.root 
    con = cam.constraints.new(type='TRACK_TO')
    con.target = car.root
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    
    # Switch to Camera View
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].region_3d.view_perspective = 'CAMERA'
            break

    print("Scene Ready! Starting Animation...")
    # --- AUTO-PLAY COMMAND ---
    bpy.ops.screen.animation_play()

if __name__ == "__main__":
    generate_scene()