#!/usr/bin/env python3
"""
Enhanced 2D Falling Sand Simulator (Pure Pygame version)
"""
import pygame
import random
import numpy as np
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 5
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS = 60
MAX_DEPTH = 5  # Number of "depth" layers to simulate

# Colors - Base colors for different particle types
SAND_COLOR = (194, 178, 128)
WATER_COLOR = (64, 164, 223)
STONE_COLOR = (128, 128, 128)
BACKGROUND = (25, 25, 35)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Sand Simulator")
clock = pygame.time.Clock()

# Particle class to store properties
class Particle:
    def __init__(self, x, y, depth, type_id):
        self.x = x
        self.y = y
        self.depth = depth  # z-coordinate for depth effect
        self.type_id = type_id
        self.velocity = [0, 0]
        self.mass = 1.0
        self.lifetime = random.randint(1000, 2000) if type_id == 1 else -1  # Water evaporates
        self.color = self.get_base_color()
        
        # Add slight color variation
        r, g, b = self.color
        variation = random.uniform(0.9, 1.1)
        self.color = (
            min(255, max(0, int(r * variation))),
            min(255, max(0, int(g * variation))),
            min(255, max(0, int(b * variation)))
        )
    
    def get_base_color(self):
        if self.type_id == 0:  # Sand
            return SAND_COLOR
        elif self.type_id == 1:  # Water
            return WATER_COLOR
        elif self.type_id == 2:  # Stone
            return STONE_COLOR
        return (255, 255, 255)

# Create 3D grid to track particles
grid = np.zeros((GRID_WIDTH, GRID_HEIGHT, MAX_DEPTH), dtype=np.int8)
particles = []

def add_particle(x, y, type_id, amount=5):
    """Add particles around the specified position"""
    for _ in range(amount):
        dx = random.randint(-2, 2)
        dy = random.randint(-2, 2)
        depth = random.randint(0, MAX_DEPTH-1)
        nx, ny = x + dx, y + dy
        
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[nx, ny, depth] == 0:
            grid[nx, ny, depth] = type_id + 1  # +1 offset so 0 means empty
            particles.append(Particle(nx, ny, depth, type_id))

def update_particles():
    """Update particle positions and properties"""
    remove_indices = []
    
    # We process from bottom to top to avoid multiple movements in one frame
    for i, particle in enumerate(particles):
        # Reduce lifetime for water particles (evaporation)
        if particle.type_id == 1:  # Water
            particle.lifetime -= 1
            if particle.lifetime <= 0:
                grid[particle.x, particle.y, particle.depth] = 0
                remove_indices.append(i)
                continue
        
        x, y, depth = particle.x, particle.y, particle.depth
        type_id = particle.type_id
        
        # Skip stones - they don't move
        if type_id == 2:
            continue
            
        moved = False
        
        # Apply physics based on particle type
        if type_id == 0:  # Sand
            # Try to move down
            if y + 1 < GRID_HEIGHT and grid[x, y + 1, depth] == 0:
                grid[x, y, depth] = 0
                grid[x, y + 1, depth] = type_id + 1
                particle.y = y + 1
                moved = True
            else:
                # Try to move down-left or down-right
                direction = random.choice([-1, 1])
                alt_x = x + direction
                
                # Check boundaries
                if 0 <= alt_x < GRID_WIDTH:
                    if y + 1 < GRID_HEIGHT and grid[alt_x, y + 1, depth] == 0:
                        grid[x, y, depth] = 0
                        grid[alt_x, y + 1, depth] = type_id + 1
                        particle.x = alt_x
                        particle.y = y + 1
                        moved = True
                    # Try changing depth if can't move in current plane
                    elif not moved:
                        new_depth = (depth + random.choice([-1, 1])) % MAX_DEPTH
                        if grid[x, y, new_depth] == 0:
                            grid[x, y, depth] = 0
                            grid[x, y, new_depth] = type_id + 1
                            particle.depth = new_depth
                            moved = True
            
            # If sand is on top of water, swap them (sand sinks)
            if not moved and y + 1 < GRID_HEIGHT and grid[x, y + 1, depth] == 2:  # 2 is water (type_id 1 + 1)
                # Find the water particle
                for j, p in enumerate(particles):
                    if p.x == x and p.y == y + 1 and p.depth == depth and p.type_id == 1:
                        # Swap positions
                        grid[x, y, depth] = 2  # Water
                        grid[x, y + 1, depth] = 1  # Sand
                        particles[j].y -= 1
                        particle.y += 1
                        moved = True
                        break
                        
        elif type_id == 1:  # Water - more fluid movement
            directions = [(0, 1), (-1, 1), (1, 1), (-1, 0), (1, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[nx, ny, depth] == 0:
                    grid[x, y, depth] = 0
                    grid[nx, ny, depth] = type_id + 1
                    particle.x = nx
                    particle.y = ny
                    moved = True
                    break
            
            # Try changing depth if can't move in current plane
            if not moved:
                new_depth = (depth + random.choice([-1, 1])) % MAX_DEPTH
                if grid[x, y, new_depth] == 0:
                    grid[x, y, depth] = 0
                    grid[x, y, new_depth] = type_id + 1
                    particle.depth = new_depth

    # Remove particles that should be deleted (in reverse order)
    for i in sorted(remove_indices, reverse=True):
        particles.pop(i)

def render():
    """Draw the current state"""
    screen.fill(BACKGROUND)
    
    # Sort particles by depth for rendering order
    sorted_particles = sorted(particles, key=lambda p: p.depth)
    
    # Draw particles
    for particle in sorted_particles:
        x, y, depth = particle.x, particle.y, particle.depth
        
        # Add lighting effect based on depth
        color = particle.color
        r, g, b = color
        light_factor = 1.0 - (depth / MAX_DEPTH) * 0.4
        render_color = (
            int(r * light_factor),
            int(g * light_factor),
            int(b * light_factor)
        )
        
        # Draw with slight offset based on depth for a pseudo-3D effect
        offset = depth * 0.5
        rect = pygame.Rect(
            x * CELL_SIZE + offset, 
            y * CELL_SIZE + offset,
            CELL_SIZE, 
            CELL_SIZE
        )
        
        # Make water semi-transparent
        if particle.type_id == 1:  # Water
            # Create a surface with per-pixel alpha
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            s.fill((*render_color, 180))  # 180 is alpha (transparency)
            screen.blit(s, rect)
        else:
            pygame.draw.rect(screen, render_color, rect)
    
    pygame.display.flip()

def main():
    running = True
    mouse_down = False
    current_type = 0  # 0: Sand, 1: Water, 2: Stone
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_down = True
                elif event.button == 3:  # Right mouse button
                    # Cycle through particle types
                    current_type = (current_type + 1) % 3
                    type_names = ["Sand", "Water", "Stone"]
                    print(f"Current type: {type_names[current_type]}")
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_type = 0  # Sand
                elif event.key == pygame.K_2:
                    current_type = 1  # Water
                elif event.key == pygame.K_3:
                    current_type = 2  # Stone
                elif event.key == pygame.K_SPACE:
                    # Clear all particles
                    grid.fill(0)
                    particles.clear()
                elif event.key == pygame.K_f:  # Launch fighting game
                    pygame.quit()
                    import os
                    os.system("python3 run_game.py")
                    return
        
        # Add particles when mouse is pressed
        if mouse_down:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Convert mouse coordinates to grid coordinates
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            
            # Keep within grid bounds
            grid_x = max(0, min(GRID_WIDTH-1, grid_x))
            grid_y = max(0, min(GRID_HEIGHT-1, grid_y))
            
            add_particle(grid_x, grid_y, current_type, amount=3)
        
        # Update particle physics
        update_particles()
        
        # Render
        render()
        
        # Display current FPS in window title
        fps = clock.get_fps()
        pygame.display.set_caption(f"Enhanced Sand Simulator - FPS: {fps:.1f} (Press F for fighting game)")
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()