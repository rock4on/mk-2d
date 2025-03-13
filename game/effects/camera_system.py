import pygame
import random
import math

class CameraSystem:
    """A camera system that follows the action and provides cinematic effects."""
    
    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height
        
        self.target_x = screen_width // 2
        self.camera_x = self.target_x
        
        self.shake_amount = 0
        self.follow_speed = 0.1
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_speed = 0.05
        
        # Camera effects
        self.effects = []
    
    def update(self, player1_pos, player2_pos, round_started, round_over):
        """Update camera position and effects."""
        # Update camera target to keep both players in view
        if round_started and not round_over:
            # Find midpoint between players
            midpoint_x = (player1_pos[0] + player2_pos[0]) / 2
            
            # Keep within bounds
            midpoint_x = max(self.screen_width // 2, min(self.world_width - self.screen_width // 2, midpoint_x))
            
            # Set as target
            self.target_x = midpoint_x
            
            # Calculate distance between players for zoom control
            distance = abs(player1_pos[0] - player2_pos[0])
            margin = 100  # Extra viewing margin
            
            # Determine target zoom based on player distance
            if distance + margin > self.screen_width:
                # Zoom out to fit both players
                self.target_zoom = self.screen_width / (distance + margin)
                self.target_zoom = max(0.7, min(1.0, self.target_zoom))  # Limit zoom levels
            else:
                # Stay at normal zoom
                self.target_zoom = 1.0
        else:
            # Return to center and normal zoom during round intro/outro
            self.target_x = self.world_width // 2
            self.target_zoom = 1.0
        
        # Smooth camera movement towards target
        self.camera_x += (self.target_x - self.camera_x) * self.follow_speed
        
        # Smooth zoom adjustment
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed
        
        # Decay screen shake
        if self.shake_amount > 0:
            self.shake_amount *= 0.9
            if self.shake_amount < 0.1:
                self.shake_amount = 0
        
        # Update camera effects
        i = 0
        while i < len(self.effects):
            effect = self.effects[i]
            
            effect["duration"] -= 1
            
            if effect["type"] == "zoom_pulse":
                # Update pulse effect
                effect["progress"] = 1 - (effect["duration"] / effect["total_duration"])
                
                # Apply zoom offset using sine curve for smooth pulse
                if effect["progress"] <= 1:
                    effect["zoom_offset"] = math.sin(effect["progress"] * math.pi) * effect["intensity"]
                
            # Remove expired effects
            if effect["duration"] <= 0:
                self.effects.pop(i)
            else:
                i += 1
    
    def add_shake(self, amount):
        """Add screen shake effect."""
        self.shake_amount = min(amount, 10)  # Cap shake amount
    
    def add_zoom_pulse(self, intensity=0.1, duration=20):
        """Add a zoom pulse effect."""
        self.effects.append({
            "type": "zoom_pulse",
            "intensity": intensity,
            "duration": duration,
            "total_duration": duration,
            "progress": 0,
            "zoom_offset": 0
        })
    
    def apply_to_surface(self, source_surface):
        """Apply camera transformations to the surface."""
        # Calculate final zoom including effects
        final_zoom = self.zoom
        
        # Apply zoom effects
        for effect in self.effects:
            if effect["type"] == "zoom_pulse":
                final_zoom += effect["zoom_offset"]
        
        # Create target surface
        if final_zoom != 1.0:
            # Calculate zoomed size
            zoomed_width = int(self.screen_width / final_zoom)
            zoomed_height = int(self.screen_height / final_zoom)
            
            # Calculate view rect
            view_rect = pygame.Rect(
                int(self.camera_x - zoomed_width // 2),
                0,
                zoomed_width,
                zoomed_height
            )
            
            # Ensure the view rectangle stays within the world bounds
            if view_rect.left < 0:
                view_rect.left = 0
            elif view_rect.right > self.world_width:
                view_rect.right = self.world_width
                
            # Extract the visible part of the world
            subsurface = source_surface.subsurface(view_rect)
            
            # Scale it up to screen size
            scaled = pygame.transform.scale(subsurface, (self.screen_width, self.screen_height))
            result = scaled
        else:
            # No zoom, just camera position offset
            view_left = int(self.camera_x - self.screen_width // 2)
            
            # Ensure view stays within world bounds
            if view_left < 0:
                view_left = 0
            elif view_left + self.screen_width > self.world_width:
                view_left = self.world_width - self.screen_width
                
            view_rect = pygame.Rect(view_left, 0, self.screen_width, self.screen_height)
            result = source_surface.subsurface(view_rect).copy()
        
        # Apply screen shake
        if self.shake_amount > 0:
            shake_x = random.uniform(-self.shake_amount, self.shake_amount)
            shake_y = random.uniform(-self.shake_amount, self.shake_amount)
            
            # Create a slightly larger surface to accommodate shake
            shake_margin = int(self.shake_amount * 2)
            shake_surface = pygame.Surface((self.screen_width + shake_margin, self.screen_height + shake_margin))
            shake_surface.fill((0, 0, 0))  # Fill with black
            
            # Place the rendered view with offset
            shake_surface.blit(result, (shake_margin//2 + shake_x, shake_margin//2 + shake_y))
            
            # Crop to original size
            result = shake_surface.subsurface(pygame.Rect(
                shake_margin//2, shake_margin//2, self.screen_width, self.screen_height
            ))
        
        return result
    
    def get_world_to_screen_coords(self, world_pos):
        """Convert world coordinates to screen coordinates."""
        # Apply camera offset
        screen_x = world_pos[0] - (self.camera_x - self.screen_width // 2)
        screen_y = world_pos[1]  # Y stays the same since we only move on X axis
        
        # Apply zoom (if any)
        if self.zoom != 1.0:
            # Calculate zoom center
            center_x = self.screen_width // 2
            center_y = self.screen_height // 2
            
            # Adjust position relative to center
            rel_x = screen_x - center_x
            rel_y = screen_y - center_y
            
            # Apply zoom
            zoomed_x = rel_x * self.zoom
            zoomed_y = rel_y * self.zoom
            
            # Translate back
            screen_x = center_x + zoomed_x
            screen_y = center_y + zoomed_y
        
        return (screen_x, screen_y)
    
    def add_impact_effect(self, position, intensity=1.0):
        """Add a compound effect for significant impacts."""
        # Add shake and zoom effects
        self.add_shake(intensity * 5)
        self.add_zoom_pulse(intensity * 0.05, duration=int(10 * intensity))
        
        # Add an additional effect for very strong impacts
        if intensity > 1.5:
            # Add a dramatic zoom-out followed by zoom-in
            self.effects.append({
                "type": "zoom_pulse",
                "intensity": -intensity * 0.03,  # Zoom out
                "duration": 15,
                "total_duration": 15,
                "progress": 0,
                "zoom_offset": 0,
                "delay": 5  # Delayed effect
            })
            
            # Add slower, secondary shake
            self.effects.append({
                "type": "secondary_shake",
                "intensity": intensity * 2,
                "duration": 30,
                "decay": 0.85,
                "current": 0
            })