import pygame
import math
import random
from game.engine.character import Character

class Samurai(Character):
    """Samurai character - stronger but slower."""
    
    def __init__(self, is_player1=True):
        super().__init__(is_player1)
        
        # Override base class attributes
        self.health = 120
        self.max_health = 120  # More health but slower
        self.move_speed = 4
        self.jump_strength = -14
        self.attack_damage = 15  # Higher base damage
        
        # Samurai specific attributes
        self.rage_mode = False
        self.rage_timer = 0
        self.rage_duration = 180  # frames (3 seconds at 60fps)
        self.rage_cooldown = 0
        self.rage_max_cooldown = 300  # frames (5 seconds at 60fps)
        
        self.body_color = (150, 60, 20) if is_player1 else (150, 20, 60)
    
    def special_move(self):
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out:
            if not self.rage_mode and self.rage_cooldown <= 0:
                self.is_attacking = True
                self.attack_type = "special"
                self.current_animation = "special"
                self.animation_frame = 0
                
                # Activate rage mode
                self.rage_mode = True
                self.rage_timer = self.rage_duration
    
    def update(self):
        super().update()
        
        # Update rage mode
        if self.rage_mode:
            self.rage_timer -= 1
            if self.rage_timer <= 0:
                self.rage_mode = False
                self.rage_cooldown = self.rage_max_cooldown
        
        # Update cooldowns
        if self.rage_cooldown > 0:
            self.rage_cooldown -= 1
    
    def get_attack_damage(self):
        # Increased damage during rage mode
        base_damage = super().get_attack_damage()
        if self.rage_mode:
            return base_damage * 1.5
        return base_damage
    
    def take_damage(self, amount):
        # Reduced damage during rage mode
        if self.rage_mode:
            amount = amount * 0.7
        super().take_damage(amount)
    
    def render(self, screen):
        """Custom rendering for samurai."""
        x, y = self.position
        
        # Call the parent render method first
        super().render(screen)
        
        # Add samurai-specific details
        if self.current_animation not in ["hit", "ko"]:
            # Draw samurai helmet
            helmet_color = (80, 30, 10) if self.is_player1 else (80, 10, 30)
            
            # Helmet shape
            helmet_points = [
                (x - 15, y - 100),  # Left bottom
                (x - 20, y - 110),  # Left top
                (x - 10, y - 118),  # Left peak
                (x, y - 120),       # Center peak
                (x + 10, y - 118),  # Right peak
                (x + 20, y - 110),  # Right top
                (x + 15, y - 100),  # Right bottom
            ]
            
            pygame.draw.polygon(screen, helmet_color, helmet_points)
            
            # Draw armor plates on body
            armor_color = (100, 40, 15) if self.is_player1 else (100, 15, 40)
            shoulder_left = pygame.Rect(x - 25, y - 70, 15, 10)
            shoulder_right = pygame.Rect(x + 10, y - 70, 15, 10)
            chest_plate = pygame.Rect(x - 15, y - 60, 30, 25)
            
            pygame.draw.rect(screen, armor_color, shoulder_left)
            pygame.draw.rect(screen, armor_color, shoulder_right)
            pygame.draw.rect(screen, armor_color, chest_plate)
            
            # Draw samurai sword on back when not attacking
            if self.current_animation not in ["punch", "kick", "special"]:
                hilt_color = (200, 150, 50)
                blade_color = (200, 200, 220)
                
                if self.facing_right:
                    pygame.draw.rect(screen, blade_color, (x - 25, y - 90, 5, 60))
                    pygame.draw.rect(screen, hilt_color, (x - 27, y - 30, 9, 15))
                else:
                    pygame.draw.rect(screen, blade_color, (x + 20, y - 90, 5, 60))
                    pygame.draw.rect(screen, hilt_color, (x + 18, y - 30, 9, 15))
        
        # Rage mode effect
        if self.rage_mode:
            # Pulsing aura
            aura_size = 50 + math.sin(pygame.time.get_ticks() * 0.01) * 10
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            
            # Red aura with pulsing transparency
            aura_alpha = 100 + int(math.sin(pygame.time.get_ticks() * 0.01) * 50)
            pygame.draw.circle(aura_surf, (255, 50, 0, aura_alpha), (aura_size, aura_size), aura_size)
            
            screen.blit(aura_surf, (x - aura_size, y - 70 - aura_size))
            
            # Red eyes
            eye_color = (255, 50, 0)
            if self.facing_right:
                pygame.draw.circle(screen, eye_color, (x + 5, y - 85), 6)
            else:
                pygame.draw.circle(screen, eye_color, (x - 5, y - 85), 6)
        
        # Draw cooldown indicator if ability is on cooldown
        if self.rage_cooldown > 0:
            cooldown_pct = self.rage_cooldown / self.rage_max_cooldown
            cooldown_width = 30 * cooldown_pct
            cooldown_rect = pygame.Rect(x - 15, y - 110, cooldown_width, 5)
            pygame.draw.rect(screen, (255, 100, 0), cooldown_rect)
        
        # Draw rage timer if rage mode is active
        elif self.rage_mode:
            rage_pct = self.rage_timer / self.rage_duration
            rage_width = 30 * rage_pct
            rage_rect = pygame.Rect(x - 15, y - 110, rage_width, 5)
            pygame.draw.rect(screen, (255, 0, 0), rage_rect)