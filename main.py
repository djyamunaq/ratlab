import pygame
import sys

class BasicWindow:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Step 1: Basic Window")
        
        # Colors
        self.background_color = (50, 50, 80)  # Dark blue-gray
        
    def handle_events(self):
        """Handle basic window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def draw(self):
        """Draw the basic scene"""
        self.screen.fill(self.background_color)
        
        # Draw some simple shapes to verify everything works
        pygame.draw.rect(self.screen, (100, 200, 100), (100, 100, 200, 100))  # Green rectangle
        pygame.draw.circle(self.screen, (200, 100, 100), (400, 300), 50)      # Red circle
        
        # Update the display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        print("Step 1: Basic Window")
        print("Press ESC or close window to exit")
        
        while running:
            # Limit to 60 frames per second
            clock.tick(60)
            
            # Handle events
            running = self.handle_events()
            
            # Draw everything
            self.draw()
        
        pygame.quit()
        sys.exit()

# Run the basic window
if __name__ == "__main__":
    game = BasicWindow()
    game.run()