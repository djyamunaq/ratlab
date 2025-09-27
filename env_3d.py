import pygame
import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from random import randint, random

class Env3D:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        # OpenGL display mode
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), 
                                            pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("RatLab OpenGL")
        
        # OpenGL setup
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, width/height, 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Camera coordinates
        self.camera_pos = [0, 5, 0]
        self.camera_yaw = 0
        self.objects_3d = [[randint(-100, 100), randint(0, 100), randint(-100, 100), 
                          2.0*random(), (random(), random(), random())] for i in range(100)]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: 
                return False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: 
            self.camera_pos[0] += 0.5*math.sin(self.camera_yaw)
            self.camera_pos[2] += 0.5*math.cos(self.camera_yaw)
        if keys[pygame.K_s]: 
            self.camera_pos[0] -= 0.5*math.sin(self.camera_yaw)
            self.camera_pos[2] -= 0.5*math.cos(self.camera_yaw)
        if keys[pygame.K_a]: self.camera_yaw += 0.1
        if keys[pygame.K_d]: self.camera_yaw -= 0.1
        

        if self.camera_pos[0] > 100.0:
            self.camera_pos[0] = 100.0
        if self.camera_pos[2] > 100.0:
            self.camera_pos[2] = 100.0
        if self.camera_pos[0] < -100.0:
            self.camera_pos[0] = -100.0
        if self.camera_pos[2] < -100.0:
            self.camera_pos[2] = -100.0

        return True
    
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Set camera using OpenGL
        cam_x, cam_y, cam_z = self.camera_pos
        look_x = cam_x + math.sin(self.camera_yaw)
        look_z = cam_z + math.cos(self.camera_yaw)
        gluLookAt(cam_x, cam_y, cam_z, look_x, cam_y, look_z, 0, 1, 0)
        
        # Draw floor grid
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        for i in range(-100, 101, 10):
            glVertex3f(i, 0, -100); glVertex3f(i, 0, 100)
            glVertex3f(-100, 0, i); glVertex3f(100, 0, i)
        glEnd()

        tile_size = 10

        for x in range(-100, 101, 10):
            for z in range(-100, 101, 10):
                color = (255, 255, 255)
                glColor3f(*color)
                glBegin(GL_QUADS)
                glVertex3f(x, 0, z)
                glVertex3f(x+tile_size, 0, z) 
                glVertex3f(x+tile_size, 0, z+tile_size)
                glVertex3f(x, 0, z+tile_size)
                glEnd()
    
        # Draw objects as cubes
        for obj in self.objects_3d:
            x, y, z, size, color = obj
            glColor3f(*color)
            glPushMatrix()
            glTranslatef(x, y, z)
            # Simple cube drawing
            glBegin(GL_QUADS)
            
            # Front face
            glVertex3f(-size, -size, size)
            glVertex3f(size, -size, size)
            glVertex3f(size, size, size)
            glVertex3f(-size, size, size)
            # Back face  
            glVertex3f(-size, -size, -size)
            glVertex3f(-size, size, -size)
            glVertex3f(size, size, -size)
            glVertex3f(size, -size, -size)
            # Top face
            glVertex3f(-size, size, -size)
            glVertex3f(-size, size, size)
            glVertex3f(size, size, size)
            glVertex3f(size, size, -size)
            # Bottom face
            glVertex3f(-size, -size, -size)
            glVertex3f(size, -size, -size)
            glVertex3f(size, -size, size)
            glVertex3f(-size, -size, size)
            # Right face
            glVertex3f(size, -size, -size)
            glVertex3f(size, size, -size)
            glVertex3f(size, size, size)
            glVertex3f(size, -size, size)
            # Left face
            glVertex3f(-size, -size, -size)
            glVertex3f(-size, -size, size)
            glVertex3f(-size, size, size)
            glVertex3f(-size, size, -size)

            glEnd()
            glPopMatrix()
        
        pygame.display.flip()

    def capture_view(self):
        """Capture current OpenGL view as image data"""
        # Read pixels from framebuffer
        data = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
        
        # Convert to Pygame surface
        view = pygame.image.fromstring(data, (self.width, self.height), 'RGB')
        view = pygame.transform.flip(view, False, True)  # Flip vertically
        
        return view
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(60)
            running = self.handle_events()
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Env3D()
    game.run()