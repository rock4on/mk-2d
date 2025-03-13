import pygame
import math
import random
from game.engine.character import Character

class Ninja(Character):
    """Ninja character - fast but lower health."""
    
    def __init__(self, is_player1=True):
        super().__init__(is_player1)
        
        # Override base class attributes
        self.health = 90 
        self.max_health = 90  # For proper scaling
 # Less health but faster
        self.move_speed = 6.5
        self.jump_strength = -16
        self.attack_damage = 8  # Lower base damage
        
        # Ninja specific attributes
        self.shadow_step_cooldown = 0
        self.body_color = (70, 70, 120) if is_player1 else (120, 70, 70)
    
    def special_move(self):
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out:
            if self.shadow_step_cooldown <= 0:
                self.is_attacking = True
                self.attack_type = "special"
                self.attack_damage = 20
                self.current_animation = "special"
                self.animation_frame = 0
                
                # Shadow step teleport
                teleport_distance = 150
                if self.facing_right:
                    self.position = (self.position[0] + teleport_distance, self.position[1])
                else:
                    self.position = (self.position[0] - teleport_distance, self.position[1])
                
                # Set cooldown
                self.shadow_step_cooldown = 120  # frames (2 seconds at 60fps)
    
    def update(self):
        super().update()
        
        # Update cooldowns
        if self.shadow_step_cooldown > 0:
            self.shadow_step_cooldown -= 1
    
    def render(self, screen):
        """Custom rendering for ninja."""
        x, y = self.position
        
        # Call the parent render method first
        super().render(screen)
        
        # Add ninja-specific details
        if self.current_animation not in ["hit", "ko"]:
            # Draw ninja mask
            mask_color = (30, 30, 60) if self.is_player1 else (60, 30, 30)
            mask_rect = pygame.Rect(
                x - 15, 
                y - 95, 
                30, 
                20
            )
            pygame.draw.rect(screen, mask_color, mask_rect)
            
            # Draw ninja scarf
            scarf_color = (200, 50, 50) if self.is_player1 else (50, 200, 50)
            scarf_points = []
            
            if self.facing_right:
                wind_effect = math.sin(pygame.time.get_ticks() * 0.01) * 5
                scarf_points = [
                    (x - 10, y - 85),
                    (x - 25, y - 85 + wind_effect),
                    (x - 40, y - 75 + wind_effect * 1.5),
                    (x - 35, y - 65 + wind_effect),
                    (x - 15, y - 75)
                ]
            else:
                wind_effect = math.sin(pygame.time.get_ticks() * 0.01) * 5
                scarf_points = [
                    (x + 10, y - 85),
                    (x + 25, y - 85 + wind_effect),
                    (x + 40, y - 75 + wind_effect * 1.5),
                    (x + 35, y - 65 + wind_effect),
                    (x + 15, y - 75)
                ]
            
            if len(scarf_points) > 2:  # Need at least 3 points for a polygon
                pygame.draw.polygon(screen, scarf_color, scarf_points)
        
        # Special move effect
        if self.current_animation == "special":
            # Trail effect for shadow step
            alpha_step = 150 // 5
            for i in range(5):
                alpha = 150 - i * alpha_step
                offset = i * (30 if self.facing_right else -30)
                
                ghost_surf = pygame.Surface((40, 100), pygame.SRCALPHA)
                ghost_color = (*self.body_color, alpha)
                pygame.draw.rect(ghost_surf, ghost_color, (0, 0, 40, 70))
                pygame.draw.ellipse(ghost_surf, ghost_color, (5, 0, 30, 30))
                
                ghost_x = x - 20 - offset if self.facing_right else x - 20 + offset
                screen.blit(ghost_surf, (ghost_x, y - 100))
        
        # Draw cooldown indicator if ability is on cooldown
        if self.shadow_step_cooldown > 0:
            cooldown_pct = self.shadow_step_cooldown / 120
            cooldown_width = 30 * cooldown_pct
            cooldown_rect = pygame.Rect(x - 15, y - 110, cooldown_width, 5)
            pygame.draw.rect(screen, (100, 100, 255), cooldown_rect)