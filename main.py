import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time

class FirstPersonGame:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.fov = 60
        self.aspect_ratio = width / height
        
        # Camera parameters
        self.camera_pos = np.array([0.0, 1.0, 5.0], dtype=np.float32)
        self.camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.camera_right = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        
        # Mouse look
        self.yaw = -90.0
        self.pitch = 0.0
        self.last_mouse_x = width // 2
        self.last_mouse_y = height // 2
        self.first_mouse = True
        
        # Movement
        self.movement_speed = 5.0
        self.mouse_sensitivity = 0.1
        
        # Visual data capture
        self.visual_data = []
        self.capture_interval = 0.1  # Capture every 100ms
        self.last_capture_time = 0
        
        # Initialize pygame and OpenGL
        self.init_pygame()
        self.init_opengl()
        
        # Create a simple environment
        self.create_environment()
    
    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), 
                                            pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("Hippocampus Visual Data Generator")
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
    
    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        
        # Set up lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 10, 0, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        
        glMatrixMode(GL_PROJECTION)
        gluPerspective(self.fov, self.aspect_ratio, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def create_environment(self):
        # Simple environment with colored cubes
        self.objects = []
        
        # Floor
        self.objects.append({
            'type': 'cube',
            'position': [0, -1, 0],
            'size': [20, 1, 20],
            'color': [0.3, 0.3, 0.3]
        })
        
        # Some objects in the environment
        objects_data = [
            ([2, 0, 0], [1, 1, 1], [1, 0, 0]),    # Red cube
            ([-2, 0, 0], [1, 1, 1], [0, 1, 0]),   # Green cube
            ([0, 0, -3], [1, 2, 1], [0, 0, 1]),   # Blue tall cube
            ([4, 0, 2], [1, 1, 1], [1, 1, 0]),    # Yellow cube
        ]
        
        for pos, size, color in objects_data:
            self.objects.append({
                'type': 'cube',
                'position': pos,
                'size': size,
                'color': color
            })
    
    def draw_cube(self, position, size, color):
        x, y, z = position
        w, h, d = size
        
        vertices = [
            # Front face
            [x-w/2, y-h/2, z+d/2], [x+w/2, y-h/2, z+d/2],
            [x+w/2, y+h/2, z+d/2], [x-w/2, y+h/2, z+d/2],
            # Back face
            [x-w/2, y-h/2, z-d/2], [x+w/2, y-h/2, z-d/2],
            [x+w/2, y+h/2, z-d/2], [x-w/2, y+h/2, z-d/2],
        ]
        
        faces = [
            [0, 1, 2, 3],  # Front
            [4, 5, 6, 7],  # Back
            [0, 3, 7, 4],  # Left
            [1, 2, 6, 5],  # Right
            [0, 1, 5, 4],  # Bottom
            [3, 2, 6, 7],  # Top
        ]
        
        glColor3f(*color)
        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3f(*vertices[vertex])
        glEnd()
    
    def process_input(self, dt):
        keys = pygame.key.get_pressed()
        
        # Camera movement
        velocity = self.movement_speed * dt
        
        if keys[pygame.K_w]:
            self.camera_pos += self.camera_front * velocity
        if keys[pygame.K_s]:
            self.camera_pos -= self.camera_front * velocity
        if keys[pygame.K_a]:
            self.camera_pos -= self.camera_right * velocity
        if keys[pygame.K_d]:
            self.camera_pos += self.camera_right * velocity
        if keys[pygame.K_SPACE]:
            self.camera_pos[1] += velocity
        if keys[pygame.K_LSHIFT]:
            self.camera_pos[1] -= velocity
        
        # Mouse look
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if self.first_mouse:
            self.last_mouse_x = mouse_x
            self.last_mouse_y = mouse_y
            self.first_mouse = False
        
        x_offset = (mouse_x - self.last_mouse_x) * self.mouse_sensitivity
        y_offset = (self.last_mouse_y - mouse_y) * self.mouse_sensitivity
        
        self.last_mouse_x = mouse_x
        self.last_mouse_y = mouse_y
        
        self.yaw += x_offset
        self.pitch += y_offset
        
        # Constrain pitch
        self.pitch = max(-89.0, min(89.0, self.pitch))
        
        # Update camera vectors
        front_x = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front_y = math.sin(math.radians(self.pitch))
        front_z = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        
        self.camera_front = np.array([front_x, front_y, front_z], dtype=np.float32)
        self.camera_front = self.camera_front / np.linalg.norm(self.camera_front)
        
        self.camera_right = np.cross(self.camera_front, np.array([0, 1, 0]))
        self.camera_right = self.camera_right / np.linalg.norm(self.camera_right)
        self.camera_up = np.cross(self.camera_right, self.camera_front)
    
    def capture_visual_data(self):
        """Capture current visual scene data for hippocampus processing"""
        current_time = time.time()
        if current_time - self.last_capture_time >= self.capture_interval:
            # Capture simplified visual data (object positions relative to camera)
            visual_frame = {
                'timestamp': current_time,
                'camera_position': self.camera_pos.copy(),
                'camera_direction': self.camera_front.copy(),
                'visible_objects': []
            }
            
            # Simple visibility check (distance-based)
            for obj in self.objects:
                obj_pos = np.array(obj['position'])
                distance = np.linalg.norm(obj_pos - self.camera_pos)
                direction = (obj_pos - self.camera_pos) / distance
                
                # Simple dot product for rough visibility check
                dot_product = np.dot(direction, self.camera_front)
                
                if dot_product > 0.5 and distance < 15:  # In front of camera and close enough
                    visual_frame['visible_objects'].append({
                        'position': obj['position'],
                        'type': obj['type'],
                        'color': obj['color'],
                        'distance': distance,
                        'relative_direction': direction.tolist()
                    })
            
            self.visual_data.append(visual_frame)
            self.last_capture_time = current_time
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set camera view
        target = self.camera_pos + self.camera_front
        gluLookAt(*self.camera_pos, *target, *self.camera_up)
        
        # Draw environment
        for obj in self.objects:
            if obj['type'] == 'cube':
                self.draw_cube(obj['position'], obj['size'], obj['color'])
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        print("Controls: WASD to move, Mouse to look, ESC to exit")
        print("Visual data is being captured for hippocampus processing...")
        
        while running:
            dt = clock.tick(60) / 1000.0  # Delta time in seconds
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self.process_input(dt)
            self.capture_visual_data()
            self.render()
            
            # Print some stats occasionally
            if len(self.visual_data) % 100 == 0 and len(self.visual_data) > 0:
                print(f"Captured {len(self.visual_data)} visual frames")
        
        pygame.quit()
        return self.visual_data

# Hippocampus data processor example
class HippocampusProcessor:
    def __init__(self):
        self.spatial_memory = {}
        self.object_memory = {}
    
    def process_visual_data(self, visual_data):
        """Process visual data to simulate hippocampus-like spatial memory"""
        for frame in visual_data:
            # Create spatial context
            spatial_context = self._create_spatial_context(frame)
            
            # Store object memories
            self._store_object_memories(frame, spatial_context)
            
            # Update spatial map
            self._update_spatial_map(frame)
    
    def _create_spatial_context(self, frame):
        """Create a spatial context based on camera position and visible objects"""
        camera_pos = tuple(np.round(frame['camera_position'], 2))
        
        if camera_pos not in self.spatial_memory:
            self.spatial_memory[camera_pos] = {
                'timestamp': frame['timestamp'],
                'visible_objects': [],
                'connections': set()
            }
        
        return camera_pos
    
    def _store_object_memories(self, frame, spatial_context):
        """Store memories of objects in their spatial context"""
        for obj in frame['visible_objects']:
            obj_key = (tuple(obj['position']), tuple(obj['color']))
            
            if obj_key not in self.object_memory:
                self.object_memory[obj_key] = {
                    'first_seen': frame['timestamp'],
                    'spatial_contexts': set(),
                    'appearances': 0
                }
            
            self.object_memory[obj_key]['spatial_contexts'].add(spatial_context)
            self.object_memory[obj_key]['appearances'] += 1
    
    def _update_spatial_map(self, frame):
        """Update spatial relationships between locations"""
        # This is a simplified version - real hippocampus does much more!
        pass
    
    def print_memory_stats(self):
        print(f"\n=== Hippocampus Memory Stats ===")
        print(f"Spatial locations remembered: {len(self.spatial_memory)}")
        print(f"Unique objects remembered: {len(self.object_memory)}")
        
        # Show some sample memories
        print("\nSample spatial memories:")
        for i, (pos, memory) in enumerate(list(self.spatial_memory.items())[:3]):
            print(f"Position {pos}: {len(memory['visible_objects'])} objects visible")
        
        print("\nSample object memories:")
        for i, (obj_key, memory) in enumerate(list(self.object_memory.items())[:3]):
            print(f"Object at {obj_key[0]}: seen {memory['appearances']} times")

# Main execution
if __name__ == "__main__":
    # Create and run the game
    game = FirstPersonGame()
    visual_data = game.run()
    
    # Process the visual data with hippocampus-like algorithm
    if visual_data:
        processor = HippocampusProcessor()
        processor.process_visual_data(visual_data)
        processor.print_memory_stats()
        
        # Save visual data for further analysis
        import json
        import datetime
        
        # Convert numpy arrays to lists for JSON serialization
        serializable_data = []
        for frame in visual_data:
            serializable_frame = {
                'timestamp': frame['timestamp'],
                'camera_position': frame['camera_position'].tolist(),
                'camera_direction': frame['camera_front'].tolist(),
                'visible_objects': frame['visible_objects']
            }
            serializable_data.append(serializable_frame)
        
        filename = f"hippocampus_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        
        print(f"\nVisual data saved to {filename}")