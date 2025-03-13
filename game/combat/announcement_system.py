import pygame
import math

class AnnouncementSystem:
    """Manages and renders text announcements during the fight."""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.announcements = []
    
    def add_announcement(self, text, color=(255, 255, 255), size="medium", 
                        position=(400, 300), timer=60, delay=0, scale=1.0):
        """
        Add a new announcement to be displayed.
        
        Args:
            text: The text to display
            color: RGB color tuple
            size: Text size ("small", "medium", "large")
            position: Position on screen (x, y)
            timer: Frames to display the text
            delay: Frames to wait before showing
            scale: Initial scale factor
        """
        self.announcements.append({
            "text": text,
            "color": color,
            "size": size,
            "position": position,
            "timer": timer,
            "delay": delay,
            "scale": scale
        })
    
    def update(self):
        """Update all announcements."""
        # Update existing announcements
        i = 0
        while i < len(self.announcements):
            announcement = self.announcements[i]
            
            # Check for delay
            if "delay" in announcement and announcement["delay"] > 0:
                announcement["delay"] -= 1
                i += 1
                continue
            
            # Decrement timer
            announcement["timer"] -= 1
            
            # Update scale for pulsing effect
            announcement["scale"] = 1.0 + math.sin(pygame.time.get_ticks() * 0.005) * 0.1
            
            # Remove expired announcements
            if announcement["timer"] <= 0:
                self.announcements.pop(i)
            else:
                i += 1
    
    def render(self, screen):
        """Render all active announcements."""
        for announcement in self.announcements:
            # Skip if still delayed
            if "delay" in announcement and announcement["delay"] > 0:
                continue
                
            # Get the right font size
            if announcement["size"] == "small":
                font = self.game_engine.fonts['small']
            elif announcement["size"] == "medium":
                font = self.game_engine.fonts['medium']
            else:  # large
                font = self.game_engine.fonts['large']
            
            # Apply scale effect
            text_surf = font.render(announcement["text"], True, announcement["color"])
            scaled_width = int(text_surf.get_width() * announcement["scale"])
            scaled_height = int(text_surf.get_height() * announcement["scale"])
            
            # Don't scale if too small or too large
            if scaled_width < 10 or scaled_width > 1000:
                scaled_width = text_surf.get_width()
                scaled_height = text_surf.get_height()
            
            # Create fancy announcement background (only for large and medium announcements)
            if announcement["size"] in ["large", "medium"]:
                bg_padding = 20
                bg_width = scaled_width + bg_padding * 2
                bg_height = scaled_height + bg_padding
                
                # Create background surface with alpha channel
                bg_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
                
                # Draw a rounded rect with gradient
                for y in range(bg_height):
                    progress = y / bg_height
                    alpha = int(180 - progress * 80)
                    shadow_alpha = 80 if y == 0 else max(0, int(60 - progress * 60))
                    
                    # Main horizontal line with gradient alpha
                    color_with_alpha = (
                        max(0, min(255, announcement["color"][0])),
                        max(0, min(255, announcement["color"][1])),
                        max(0, min(255, announcement["color"][2])),
                        alpha
                    )
                    pygame.draw.line(bg_surf, color_with_alpha, 
                                  (0, y), (bg_width, y), 1)
                    
                    # Shadow line below
                    pygame.draw.line(bg_surf, (0, 0, 0, shadow_alpha), 
                                  (0, y + 2), (bg_width, y + 2), 1)
                
                # Draw border
                border_color = (
                    max(0, min(255, announcement["color"][0])),
                    max(0, min(255, announcement["color"][1])),
                    max(0, min(255, announcement["color"][2])),
                    200
                )
                pygame.draw.rect(bg_surf, border_color, (0, 0, bg_width, bg_height), 2, border_radius=10)
                
                # Position and draw background
                bg_rect = bg_surf.get_rect(center=announcement["position"])
                screen.blit(bg_surf, bg_rect)
                
            # Draw text with glow effect for emphasis
            if announcement["size"] == "large":
                # Draw outer glow
                glow_iterations = 3
                for i in range(glow_iterations):
                    glow_size = i * 2
                    glow_alpha = max(0, 120 - i * 40)
                    glow_color = (
                        max(0, min(255, announcement["color"][0])),
                        max(0, min(255, announcement["color"][1])),
                        max(0, min(255, announcement["color"][2])),
                        glow_alpha
                    )
                    
                    glow_surf = font.render(announcement["text"], True, glow_color)
                    glow_surf = pygame.transform.scale(glow_surf, (scaled_width, scaled_height))
                    
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        glow_pos = (
                            announcement["position"][0] + dx * glow_size,
                            announcement["position"][1] + dy * glow_size
                        )
                        glow_rect = glow_surf.get_rect(center=glow_pos)
                        screen.blit(glow_surf, glow_rect)
            
            # Draw text shadow (make more prominent for large announcements)
            shadow_offset = 3 if announcement["size"] == "large" else 2
            shadow_surf = font.render(announcement["text"], True, (0, 0, 0))
            shadow_scaled = pygame.transform.scale(shadow_surf, (scaled_width, scaled_height))
            shadow_rect = shadow_scaled.get_rect(center=(
                announcement["position"][0] + shadow_offset, 
                announcement["position"][1] + shadow_offset
            ))
            screen.blit(shadow_scaled, shadow_rect)
            
            # Draw the text
            scaled_surf = pygame.transform.scale(text_surf, (scaled_width, scaled_height))
            text_rect = scaled_surf.get_rect(center=announcement["position"])
            screen.blit(scaled_surf, text_rect)
    
    def clear(self):
        """Clear all announcements."""
        self.announcements = []