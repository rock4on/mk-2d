import pygame
import math
import random
from game.engine.character import Character

class Pirate(Character):
    """
    Pirate character - focused on unpredictable attacks and treasure-based mechanics.
    Introduces a unique treasure and combo system that rewards aggressive play.
    """
    
    def __init__(self, is_player1=True):
        super().__init__(is_player1)
        
        # Override base class attributes
        self.health = 100        # Slightly lower health
        self.max_health = 100    # For proper scaling
        self.move_speed = 6      # Slightly faster movement
        self.jump_strength = -14 # Good jump
        self.attack_damage = 8   # Base damage
        
        # Pirate-specific attributes
        self.treasure_coins = 0      # Coins collected during combat
        self.max_treasure_coins = 50 # Maximum coins that can be collected
        self.coin_multiplier = 1     # Multiplier for coin collection
        self.parry_timer = 0         # Parry window timer
        self.grog_meter = 0          # Grog (rage) meter
        self.max_grog_meter = 100    # Maximum grog level
        
        # Define pirate's colors (player 1 and player 2 variations)
        self.body_color = (100, 60, 40) if is_player1 else (60, 40, 20)
        self.accent_color = (200, 150, 100) if is_player1 else (150, 100, 50)
        
        # Animation frames dictionary
        self.animation_frames = {
            "idle": 4,       
            "walk": 6,       
            "jump": 3,       
            "sword_slash": 4, 
            "punch": 4,
            "kick": 4,
            "special": 4,        # Primary attack
            "pistol_shot": 3,      # Secondary attack
            "parry": 2,            # Defensive move
            "hit": 2,        
            "ko": 1,         
            "block": 2,      
            "grog_rage": 3    # Unique rage mode
        }
    
    def sword_slash(self):
        """Pirate's primary sword attack with combo potential."""
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_type = "sword_slash"
            
            # Increase damage based on grog meter
            grog_bonus = self.grog_meter / 20
            self.attack_damage = 8 + grog_bonus
            
            self.current_animation = "sword_slash"
            self.animation_frame = 0
            self.attack_cooldown = 15  # Relatively fast attack
            
            # Increase grog meter slightly
            self.grog_meter = min(self.max_grog_meter, self.grog_meter + 10)
    
    def pistol_shot(self):
        """Ranged attack that costs treasure coins."""
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            if self.treasure_coins >= 10:
                self.treasure_coins -= 10
                self.is_attacking = True
                self.attack_type = "pistol_shot"
                self.attack_damage = 15  # Higher damage
                self.current_animation = "pistol_shot"
                self.animation_frame = 0
                self.attack_cooldown = 30
                
                # Bonus: Chance to stun opponent
                if random.random() < 0.3:
                    # Signal to opponent's take_damage method
                    self.stun_chance = True
    
    def parry(self):
        """
        Defensive move that can counter attacks and generate coins.
        Timing-based mechanic similar to a perfect block.
        """
        if not self.is_attacking and not self.is_knocked_out and not self.is_stunned:
            self.is_blocking = True
            self.current_animation = "parry"
            
            # Activate parry window
            self.parry_timer = 15  # Frames of active parry
    
    def take_damage(self, amount):
        """
        Override take damage to incorporate parry and coin mechanics.
        """
        # Check for successful parry
        if self.parry_timer > 0:
            # Parry successful - reduce damage and generate coins
            amount = max(0, amount - 5)  # Reduce incoming damage
            coin_gain = min(5 * self.coin_multiplier, self.max_treasure_coins - self.treasure_coins)
            self.treasure_coins += coin_gain
            
            # Reset parry timer
            self.parry_timer = 0
        
        # Reduce grog meter when taking damage
        self.grog_meter = max(0, self.grog_meter - amount)
        
        # Call parent method
        return super().take_damage(amount)
    
    def successful_hit(self):
        """Modify successful hit to increase coin multiplier."""
        super().successful_hit()
        
        # Increase coin multiplier
        if self.attack_type == "sword_slash":
            self.coin_multiplier = min(3, self.coin_multiplier + 0.2)
    
    def update(self):
        """Update character state with unique pirate mechanics."""
        super().update()
        
        # Reduce parry timer
        if self.parry_timer > 0:
            self.parry_timer -= 1
        
        # Grog meter mechanics
        if self.grog_meter > 0 and not self.is_knocked_out:
            # Slowly decay grog meter
            self.grog_meter = max(0, self.grog_meter - 0.5)
        
        # Coin multiplier decay
        self.coin_multiplier = max(1, self.coin_multiplier - 0.05)
    
    def render(self, screen):
        """Custom rendering for pirate character."""
        x, y = self.position
        
        # Call the parent render method first
        super().render(screen)
        
        # Add pirate-specific details
        if self.current_animation not in ["hit", "ko"]:
            # Pirate hat
            hat_color = (50, 40, 30) if self.is_player1 else (30, 20, 10)
            hat_points = []
            
            if self.facing_right:
                # Tricorn hat with wind effect
                wind_effect = math.sin(pygame.time.get_ticks() * 0.01) * 3
                hat_points = [
                    (x - 25, y - 110 + wind_effect),   # Left point
                    (x, y - 120 + wind_effect * 1.5),  # Top point
                    (x + 25, y - 110 + wind_effect),   # Right point
                    (x + 20, y - 100),                 # Bottom right
                    (x - 20, y - 100)                  # Bottom left
                ]
            else:
                wind_effect = math.sin(pygame.time.get_ticks() * 0.01) * 3
                hat_points = [
                    (x + 25, y - 110 + wind_effect),   # Right point
                    (x, y - 120 + wind_effect * 1.5),  # Top point
                    (x - 25, y - 110 + wind_effect),   # Left point
                    (x - 20, y - 100),                 # Bottom left
                    (x + 20, y - 100)                  # Bottom right
                ]
            
            # Draw hat
            if len(hat_points) > 2:
                pygame.draw.polygon(screen, hat_color, hat_points)
            
            # Pirate coat/vest
            coat_color = (100, 80, 60) if self.is_player1 else (80, 60, 40)
            coat_rect = pygame.Rect(x - 25, y - 90, 50, 30)
            pygame.draw.rect(screen, coat_color, coat_rect)
            
            # Sash or belt
            sash_color = (200, 150, 100) if self.is_player1 else (150, 100, 50)
            pygame.draw.line(screen, sash_color, (x - 25, y - 60), (x + 25, y - 60), 5)
        
        # Special move effect - Pistol shot trail
        if self.current_animation == "pistol_shot":
            # Bullet trail effect
            alpha_step = 150 // 5
            for i in range(5):
                alpha = 150 - i * alpha_step
                offset = i * (40 if self.facing_right else -40)
                
                trail_surf = pygame.Surface((30, 50), pygame.SRCALPHA)
                trail_color = (150, 150, 150, alpha)
                pygame.draw.rect(trail_surf, trail_color, (0, 0, 30, 30))
                
                trail_x = x - 15 - offset if self.facing_right else x - 15 + offset
                screen.blit(trail_surf, (trail_x, y - 90))
        
        # Coin collection effect
        if self.treasure_coins > 0:
            # Floating coin particles
            for i in range(min(self.treasure_coins // 10, 5)):
                angle = pygame.time.get_ticks() * 0.01 + i * 0.8
                coin_radius = 30 + math.sin(angle) * 10
                coin_x = x + math.cos(angle) * coin_radius
                coin_y = y - 140 + math.sin(angle * 1.5) * 10
                
                # Draw coin
                pygame.draw.circle(screen, (255, 215, 0), (int(coin_x), int(coin_y)), 3)
        
        # Grog rage visual indicator
        if self.grog_meter > self.max_grog_meter * 0.8:
            # Intense glow around the character
            glow_surf = pygame.Surface((80, 120), pygame.SRCALPHA)
            glow_color = (255, 100, 0, 50 + int(self.grog_meter / self.max_grog_meter * 100))
            pygame.draw.ellipse(glow_surf, glow_color, (0, 0, 80, 120))
            
            screen.blit(glow_surf, (x - 40, y - 120))
        
        # Draw cooldown indicator for special moves
        if self.treasure_coins < 10:
            # Coin collection cooldown
            cooldown_pct = self.treasure_coins / 10
            cooldown_width = 30 * cooldown_pct
            cooldown_rect = pygame.Rect(x - 15, y - 110, cooldown_width, 5)
            pygame.draw.rect(screen, (255, 215, 0), cooldown_rect)
        
    def _render_sword_slash(self, screen, x, y):
        """Render pirate's sword slash attack."""
        # Body and head
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Determine animation frame
        frame = self.animation_frame % self.animation_frames["sword_slash"]
        
        # Draw body
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Sword rendering
        sword_length = 40 + frame * 5
        sword_width = 5
        
        # Create sword surface
        sword_surf = pygame.Surface((sword_length, sword_width), pygame.SRCALPHA)
        sword_color = self.accent_color
        
        # Draw sword with motion blur effect
        for i in range(3):
            alpha = 255 - i * 80
            blur_color = (*sword_color, alpha)
            pygame.draw.rect(sword_surf, blur_color, (0, 0, sword_length - i * 10, sword_width))
        
        # Position sword based on animation frame and facing direction
        if self.facing_right:
            # Sword swing from low to high
            if frame < 2:
                sword_x = x + 10
                sword_y = y - 40
                sword_angle = -45 + frame * 30
            else:
                sword_x = x + 20
                sword_y = y - 60
                sword_angle = 45 - (frame - 2) * 30
            
            # Rotate sword
            rotated_sword = pygame.transform.rotate(sword_surf, sword_angle)
            sword_rect = rotated_sword.get_rect(center=(sword_x, sword_y))
            screen.blit(rotated_sword, sword_rect)
        else:
            # Sword swing from low to high (mirrored)
            if frame < 2:
                sword_x = x - 10
                sword_y = y - 40
                sword_angle = 45 - frame * 30
            else:
                sword_x = x - 20
                sword_y = y - 60
                sword_angle = -45 + (frame - 2) * 30
            
            # Flip and rotate sword
            flipped_sword = pygame.transform.flip(sword_surf, True, False)
            rotated_sword = pygame.transform.rotate(flipped_sword, sword_angle)
            sword_rect = rotated_sword.get_rect(center=(sword_x, sword_y))
            screen.blit(rotated_sword, sword_rect)
    
    def _render_pistol_shot(self, screen, x, y):
        """Render pirate's pistol shot attack."""
        # Body and head
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Determine animation frame
        frame = self.animation_frame % self.animation_frames["pistol_shot"]
        
        # Draw body
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Pistol rendering
        pistol_length = 25
        pistol_width = 8
        
        # Create pistol surface
        pistol_surf = pygame.Surface((pistol_length, pistol_width), pygame.SRCALPHA)
        pygame.draw.rect(pistol_surf, (100, 100, 100), (0, 0, pistol_length, pistol_width))
        
        # Position pistol based on animation frame and facing direction
        if self.facing_right:
            pistol_x = x + 20
            pistol_y = y - 50
            pistol_angle = -15 + frame * 10
            
            # Rotate pistol
            rotated_pistol = pygame.transform.rotate(pistol_surf, pistol_angle)
            pistol_rect = rotated_pistol.get_rect(center=(pistol_x, pistol_y))
            screen.blit(rotated_pistol, pistol_rect)
            
            # Muzzle flash and bullet
            if frame == 2:
                # Muzzle flash
                flash_length = 20
                pygame.draw.line(screen, (255, 150, 0), 
                               (pistol_x + pistol_length, pistol_y), 
                               (pistol_x + pistol_length + flash_length, pistol_y), 3)
                
                # Bullet trail
                for i in range(5):
                    bullet_x = pistol_x + pistol_length + flash_length + i * 20
                    bullet_y = pistol_y + math.sin(i) * 5
                    pygame.draw.circle(screen, (200, 200, 200), (int(bullet_x), int(bullet_y)), 2)
        else:
            pistol_x = x - 20
            pistol_y = y - 50
            pistol_angle = 15 - frame * 10
            
            # Flip and rotate pistol
            flipped_pistol = pygame.transform.flip(pistol_surf, True, False)
            rotated_pistol = pygame.transform.rotate(flipped_pistol, pistol_angle)
            pistol_rect = rotated_pistol.get_rect(center=(pistol_x, pistol_y))
            screen.blit(rotated_pistol, pistol_rect)
            
            # Muzzle flash and bullet
            if frame == 2:
                # Muzzle flash
                flash_length = 20
                pygame.draw.line(screen, (255, 150, 0), 
                               (pistol_x - pistol_length, pistol_y), 
                               (pistol_x - pistol_length - flash_length, pistol_y), 3)
                
                # Bullet trail
                for i in range(5):
                    bullet_x = pistol_x - pistol_length - flash_length - i * 20
                    bullet_y = pistol_y + math.sin(i) * 5
                    pygame.draw.circle(screen, (200, 200, 200), (int(bullet_x), int(bullet_y)), 2)
    
    def _render_parry(self, screen, x, y):
        """Render pirate's parry defensive stance."""
        # Body and head
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Determine animation frame
        frame = self.animation_frame % self.animation_frames["parry"]
        
        # Draw body in defensive stance
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Sword/dagger for parry
        dagger_length = 25
        dagger_width = 5
        
        # Create dagger surface
        dagger_surf = pygame.Surface((dagger_length, dagger_width), pygame.SRCALPHA)
        dagger_color = self.accent_color
        pygame.draw.rect(dagger_surf, dagger_color, (0, 0, dagger_length, dagger_width))
        
        # Position dagger based on animation frame and facing direction
        if self.facing_right:
            # Defensive stance with dagger
            dagger_x = x + 10
            dagger_y = y - 50
            dagger_angle = -30 + frame * 10
            
            # Rotate dagger
            rotated_dagger = pygame.transform.rotate(dagger_surf, dagger_angle)
            dagger_rect = rotated_dagger.get_rect(center=(dagger_x, dagger_y))
            screen.blit(rotated_dagger, dagger_rect)
            
            # Parry effect - sparks or deflection
            if self.parry_timer > 0:
                for i in range(5):
                    spark_x = dagger_x + random.randint(-10, 10)
                    spark_y = dagger_y + random.randint(-10, 10)
                    spark_color = (255, 200, 0)
                    pygame.draw.circle(screen, spark_color, (spark_x, spark_y), 2)
        else:
            # Defensive stance with dagger (left-facing)
            dagger_x = x - 10
            dagger_y = y - 50
            dagger_angle = 30 - frame * 10
            
            # Flip and rotate dagger
            flipped_dagger = pygame.transform.flip(dagger_surf, True, False)
            rotated_dagger = pygame.transform.rotate(flipped_dagger, dagger_angle)
            dagger_rect = rotated_dagger.get_rect(center=(dagger_x, dagger_y))
            screen.blit(rotated_dagger, dagger_rect)
            
            # Parry effect - sparks or deflection
            if self.parry_timer > 0:
                for i in range(5):
                    spark_x = dagger_x + random.randint(-10, 10)
                    spark_y = dagger_y + random.randint(-10, 10)
                    spark_color = (255, 200, 0)
                    pygame.draw.circle(screen, spark_color, (spark_x, spark_y), 2)
    
    def _render_grog_rage(self, screen, x, y):
        """Render pirate's grog rage mode - intense battle stance."""
        # Body and head
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Determine animation frame
        frame = self.animation_frame % self.animation_frames["grog_rage"]
        
        # Modify body color during rage (more intense)
        rage_color = tuple(min(255, int(c * (1.5 + frame * 0.1))) for c in self.body_color)
        
        # Draw body with rage effect
        pygame.draw.rect(screen, rage_color, body_rect)
        pygame.draw.ellipse(screen, rage_color, head_rect)
        
        # Rage energy effects
        for i in range(10):
            angle = self.animation_timer * 0.1 + i * 0.6
            radius = 40 + math.sin(self.animation_timer * 0.05 + i) * 10
            particle_x = x + math.cos(angle) * radius
            particle_y = y - 60 + math.sin(angle) * radius * 0.5
            particle_size = 3 + math.sin(self.animation_timer * 0.1 + i) * 2
            
            # Create particle with intensity based on grog meter
            particle_alpha = int(100 + (self.grog_meter / self.max_grog_meter) * 100)
            particle_color = (*self.accent_color, particle_alpha)
            
            # Create particle surface
            particle_surf = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, particle_color, (particle_size, particle_size), particle_size)
            
            screen.blit(particle_surf, (particle_x - particle_size, particle_y - particle_size))
        
        # Intense eye effect during rage
        eye_color = (255, 50, 0)  # Bright red eyes
        eye_y = y - 100
        pygame.draw.circle(screen, eye_color, (x - 5, eye_y), 4)
        pygame.draw.circle(screen, eye_color, (x + 5, eye_y), 4)
    
    def grog_rage(self):
        """
        Activate grog rage mode - temporary power boost.
        Requires full grog meter and no attacks in progress.
        """
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            if self.grog_meter >= self.max_grog_meter:
                # Activate rage mode
                self.is_attacking = True
                self.attack_type = "grog_rage"
                self.current_animation = "grog_rage"
                self.animation_frame = 0
                self.attack_cooldown = 45
                
                # Rage mode benefits
                self.attack_damage *= 2  # Double damage
                self.move_speed *= 1.5   # Increased speed
                
                # Temporary power-up duration
                self.rage_duration = 60  # Frames of rage mode