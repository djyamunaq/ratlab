import pygame
import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from random import randint, random
import numpy as np
import matplotlib.pyplot as plt

class Env3D:
    def __init__(self, width=800, FPS=60, height=600, auto=False, print=False, points=-1):
        self.width = width
        self.height = height
        self.FPS = FPS
        self.auto = auto
        self.print = print
        self.agent_linear_vel = 0
        self.agent_angular_vel = 0
        self.agent_trajectory = []
        self.time = 0
        self.dt = 0.05
        self.points = points

        # OpenGL display mode
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), 
                                            pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        pygame.display.set_caption("RatLab OpenGL")
        
        # OpenGL setup
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, width/height, 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)
        
        # agent coordinates
        self.agent_pos = [0, 5, 0]
        self.agent_yaw = 0
        self.objects_3d = [[randint(-100, 100), randint(0, 100), randint(-100, 100), 
                          2.0*random(), (random(), random(), random())] for i in range(100)]
    
    def handle_events(self):
        coord = (self.agent_pos[0], self.agent_pos[2], self.agent_yaw, self.time)
        self.agent_trajectory.append(coord)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: 
                return False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: 
            self.agent_pos[0] += 0.5*math.sin(self.agent_yaw)
            self.agent_pos[2] += 0.5*math.cos(self.agent_yaw)
        if keys[pygame.K_s]: 
            self.agent_pos[0] -= 0.5*math.sin(self.agent_yaw)
            self.agent_pos[2] -= 0.5*math.cos(self.agent_yaw)
        if keys[pygame.K_a]: self.agent_yaw += 0.1
        if keys[pygame.K_d]: self.agent_yaw -= 0.1

        if self.agent_pos[0] > 100.0:
            self.agent_pos[0] = 100.0
        if self.agent_pos[2] > 100.0:
            self.agent_pos[2] = 100.0
        if self.agent_pos[0] < -100.0:
            self.agent_pos[0] = -100.0
        if self.agent_pos[2] < -100.0:
            self.agent_pos[2] = -100.0

        return True
    
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Set agent using OpenGL
        cam_x, cam_y, cam_z = self.agent_pos
        look_x = cam_x + math.sin(self.agent_yaw)
        look_z = cam_z + math.cos(self.agent_yaw)
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
    
    def ornstein_unlenbeck_position_update(self):
        # --- 2. Ornstein-Uhlenbeck Parameters ---
        # These parameters govern the 'wiggliness' and speed of the movement.
        # Subscript '_v' for Linear Velocity, '_w' for Angular Velocity (omega).

        # Linear Velocity (v) Parameters
        theta_v = 3.0      # Mean-reversion rate (how quickly v returns to mu_v)
        mu_v = 0.5         # Mean velocity (the desired speed)
        sigma_v = 0.2      # Volatility (noise magnitude)
        v_max = 1.0        # Max speed constraint

        # Angular Velocity (omega) Parameters
        theta_w = 4.0      # Mean-reversion rate
        mu_w = 0.0         # Mean angular velocity (tends toward straight movement)
        sigma_w = 4.0      # Volatility (noise magnitude - higher means faster/sharper turns)
        w_max = 15.0       # Max rotation rate constraint (rad/s)

        # A. Discrete Ornstein-Uhlenbeck Process Update
    
        # Generate Gaussian white noise (dW_t ~ N(0, 1))
        noise_v = np.random.normal(0, 1)
        noise_w = np.random.normal(0, 1)
        
        # Calculate velocity changes (dv and d_omega) using the discretized SDE:
        # dx = theta * (mu - x) * dt + sigma * sqrt(dt) * N(0, 1)
        dv = theta_v * (mu_v - self.agent_linear_vel) * self.dt + sigma_v * np.sqrt(self.dt) * noise_v
        d_omega = theta_w * (mu_w - self.agent_angular_vel) * self.dt + sigma_w * np.sqrt(self.dt) * noise_w
        
        # B. Update and Bound Velocities
        self.agent_linear_vel = self.agent_linear_vel + dv
        self.agent_angular_vel = self.agent_angular_vel + d_omega
        
        # Apply constraints (optional, but prevents unrealistically high speeds)
        self.agent_linear_vel = np.clip(self.agent_linear_vel, 0, v_max)
        self.agent_angular_vel = np.clip(self.agent_angular_vel, -w_max, w_max)
        
        # C. Update Agent State (Position and Orientation)
        
        # Update orientation (phi)
        self.agent_yaw = self.agent_yaw + self.agent_angular_vel * self.dt
        
        # Update position (x, y) using the current velocity and heading
        self.agent_pos[0] = self.agent_pos[0] + self.agent_linear_vel * np.cos(self.agent_yaw) * self.dt
        self.agent_pos[2] = self.agent_pos[2] + self.agent_linear_vel * np.sin(self.agent_yaw) * self.dt

        if self.agent_pos[0] > 100.0:
            self.agent_pos[0] = 100.0
        if self.agent_pos[2] > 100.0:
            self.agent_pos[2] = 100.0
        if self.agent_pos[0] < -100.0:
            self.agent_pos[0] = -100.0
        if self.agent_pos[2] < -100.0:
            self.agent_pos[2] = -100.0

    def print_trajectory(self):
        self.agent_trajectory = np.asarray(self.agent_trajectory)

        xs = self.agent_trajectory[:, 0]
        ys = self.agent_trajectory[:, 1]
        yaws = self.agent_trajectory[:, 2]
        times = self.agent_trajectory[:, 3]

        plt.figure(figsize=(10, 10))

        # 6a. Plot trajectory line with color gradient (Time)
        # We use scatter to apply the color map, with small markers to create a continuous line effect
        scatter = plt.scatter(xs, ys, c=times, cmap='viridis', s=5, label='_nolegend_')

        # Add a color bar to interpret the time axis
        cbar = plt.colorbar(scatter, orientation='vertical')
        cbar.set_label('Time Elapsed (s)')

        # # 6b. Add Orientation Arrows (Yaw)
        # # We subsample the data to place arrows every 30 steps to prevent clutter
        # subsample_k = 50
        # quiver_x = xs[::subsample_k]
        # quiver_y = ys[::subsample_k]
        # quiver_phi = yaws[::subsample_k]

        # # Calculate directional components (u = cos(phi), v = sin(phi))
        # quiver_u = np.cos(quiver_phi)
        # quiver_v = np.sin(quiver_phi)

        # # Plot arrows using plt.quiver
        # plt.quiver(
        #     quiver_x, quiver_y, 
        #     quiver_u, quiver_v, 
        #     color='red', 
        #     scale=30,          # Adjusts the length/density of the arrows
        #     headwidth=3, 
        #     headlength=5, 
        #     alpha=0.6,
        #     label='Orientation (Yaw)'
        # )

        # 6c. Plot Start/End Points
        plt.plot(xs[0], ys[0], 'o', markersize=10, color='green', label='Start')
        plt.plot(xs[-1], ys[-1], 's', markersize=10, color='red', label='End')

        # Final Touches
        plt.title(f'OU Random Walk Trajectory: Time & Orientation Visualization')
        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.legend(loc='lower left')
        plt.grid(True, linestyle='--', alpha=0.5)

        # Save the plot
        plt.savefig('trajectory.png', dpi=300, bbox_inches='tight')
        # plt.show()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(self.FPS)

            if self.auto:
                self.ornstein_unlenbeck_position_update()

            running = self.handle_events()
            self.draw()

            self.time += self.dt

            print(int(self.time / self.dt))
            
            if self.points > 0 and self.time / self.dt > self.points:
                break

        if print:
            self.print_trajectory()

        pygame.quit()
        sys.exit()