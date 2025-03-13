import pygame
import random
import numpy as np

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 4
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
SAND_COLOR = (194, 178, 128)
BACKGROUND = (50, 50, 50)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sand Falling Simulator")
clock = pygame.time.Clock()

# Create grid to track sand particles
grid = np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=bool)

def add_sand(x, y, amount=5):
    """Add sand particles around the specified position"""
    for _ in range(amount):
        dx = random.randint(-2, 2)
        dy = random.randint(-2, 2)
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
            grid[nx, ny] = True

def update_sand():
    """Update sand positions based on simple physics"""
    # We process from bottom to top to avoid multiple movements in one frame
    for y in range(GRID_HEIGHT - 2, -1, -1):
        for x in range(GRID_WIDTH):
            if grid[x, y]:
                moved = False
                
                # Try to move down
                if not grid[x, y + 1]:
                    grid[x, y] = False
                    grid[x, y + 1] = True
                    moved = True
                else:
                    # Try to move down-left or down-right
                    direction = random.choice([-1, 1])
                    alt_x = x + direction
                    
                    # Check boundaries
                    if 0 <= alt_x < GRID_WIDTH:
                        if not grid[alt_x, y + 1]:
                            grid[x, y] = False
                            grid[alt_x, y + 1] = True
                            moved = True

def render():
    """Draw the current state"""
    screen.fill(BACKGROUND)
    
    # Draw sand particles
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[x, y]:
                pygame.draw.rect(screen, SAND_COLOR, 
                                (x * CELL_SIZE, y * CELL_SIZE, 
                                 CELL_SIZE, CELL_SIZE))
    
    pygame.display.flip()

def main():
    running = True
    mouse_down = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
        
        # Add sand when mouse is pressed
        if mouse_down:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            add_sand(grid_x, grid_y)
        
        # Update sand physics
        update_sand()
        
        # Render
        render()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()