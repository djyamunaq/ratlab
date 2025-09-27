# game_3d_step1.py
import pygame
import sys
import math

class Game3D:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("3D Environment - Step 1")
        
        # Basic 3D camera setup
        self.camera_pos = [0, 0, 5]  # x, y, z position in 3D space
        self.camera_yaw = 0  # camera yaw
        self.camera_target = [0, 0, 0]  # Where camera is looking
        
        # Simple 3D objects: list of (x, y, z, size, color)
        self.objects_3d = [
            # Position x, y, z, size, color
            [0, 0, 0, 1.0, (255, 0, 0)],    # Red cube at center
            [2, 0, -3, 0.8, (0, 255, 0)],   # Green cube
            [-2, 1, -5, 1.2, (0, 0, 255)],  # Blue cube
        ]
        
        self.background_color = (255, 255, 255)
    
    def project_3d_to_2d(self, point_3d):
        """
        Simple 3D to 2D projection
        Converts a 3D point (x, y, z) to 2D screen coordinates (screen_x, screen_y)
        """
        x, y, z = point_3d

        rotated_x = x*math.cos(self.camera_yaw) - z*math.sin(self.camera_yaw) 
        rotated_z = x*math.sin(self.camera_yaw) + z*math.cos(self.camera_yaw)
        
        x = rotated_x
        z = rotated_z

        # Simple perspective projection
        # When z is larger (further away), objects appear smaller
        if z - self.camera_pos[2] >= 0:  # Behind or at camera plane
            return None
            
        # Perspective scaling factor
        scale = 200 / abs(z - self.camera_pos[2])
        
        # Convert to screen coordinates (center of screen is origin)
        screen_x = x * scale + self.width // 2
        screen_y = -y * scale + self.height // 2  # Negative because screen y goes down
        
        return (int(screen_x), int(screen_y))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_w:
                    self.camera_pos[2] -= 0.5   # Move camera forward
                if event.key == pygame.K_s:
                    self.camera_pos[2] += 0.5   # Move camera backward
                if event.key == pygame.K_a:    
                    self.camera_yaw += 0.1        # Rotate camera left
                if event.key == pygame.K_d:     
                    self.camera_yaw -= 0.1        # Rotate camera left

        return True
    
    def draw_3d_point(self, point_3d, color, size=5):
        """Draw a single 3D point projected to 2D"""
        screen_pos = self.project_3d_to_2d(point_3d)
        if screen_pos:
            pygame.draw.circle(self.screen, color, screen_pos, size)
    
    def draw(self):
        self.screen.fill(self.background_color)
        
        # Draw a grid to help visualize 3D space
        for x in range(-10, 11, 2):
            for z in range(-10, 0, 2):
                grid_point = [x, 0, z]
                self.draw_3d_point(grid_point, (100, 100, 150), 2)
        
        # Draw our 3D objects as points
        for obj in self.objects_3d:
            x, y, z, size, color = obj
            self.draw_3d_point([x, y, z], color, 8)
        
        # Display camera info
        font = pygame.font.Font(None, 36)
        info_text = f"Camera Z: {self.camera_pos[2]:.1f} (Use UP/DOWN arrows)"
        text = font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        print("3D Environment - Step 1")
        print("You should see colored points in 3D space")
        print("Press UP/DOWN arrows to move camera forward/backward")
        print("Press ESC to exit")
        
        while running:
            clock.tick(60)
            running = self.handle_events()
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game3D()
    game.run()