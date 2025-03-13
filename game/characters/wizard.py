import pygame
import math
import random
from game.engine.character import Character

class Wizard(Character):
    """Wizard character - ranged attacks with projectiles but lower health."""
    
    def __init__(self, is_player1=True):
        super().__init__(is_player1)
        
        # Override base class attributes
        self.health = 80  # Less health but powerful range
        self.move_speed = 4  # Slower movement
        self.max_health = 80  # For proper scaling

        self.jump_strength = -13
        self.attack_damage = 7  # Lower base damage for basic attacks
        
        # Wizard specific attributes
        self.mana = 100  # Mana for casting spells
        self.max_mana = 100
        self.mana_regen = 0.3  # Mana regen per frame
        self.projectiles = []  # List of active projectiles
        
        # Colors
        self.body_color = (70, 20, 120) if is_player1 else (120, 20, 70)
        self.mana_color = (50, 100, 255)
        self.flame_colors = [(255, 50, 0), (255, 150, 0), (255, 255, 0)]
        self.ice_colors = [(200, 200, 255), (100, 150, 255), (50, 100, 255)]
        
        # Animation frames dict - specific for Wizard
        self.animation_frames = {
            "idle": 4,   # Number of frames in idle animation
            "walk": 6,   # Number of frames in walk animation
            "jump": 3,   # Number of frames in jump animation
            "punch": 3,  # Number of frames in punch (staff poke) animation
            "kick": 3,   # Number of frames in kick (blast) animation
            "special": 5, # Number of frames in special animation
            "hit": 2,    # Number of frames in hit animation
            "ko": 1,     # Number of frames in KO animation
            "block": 1,  # Number of frames in block animation
            "cast": 4    # Number of frames in cast animation
        }
    
    def punch(self):
        # Wizard's "punch" is a quick staff poke
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_type = "punch"
            self.attack_damage = 6  # Lower damage
            self.current_animation = "punch"
            self.animation_frame = 0
            self.attack_cooldown = 12  # Quicker cooldown
    
    def kick(self):
        # Wizard's "kick" is a fire projectile
        if not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            # Check if enough mana
            if self.mana >= 15:
                self.mana -= 15
                self.is_attacking = True
                self.attack_type = "kick"
                self.attack_damage = 12
                self.current_animation = "cast"
                self.animation_frame = 0
                self.attack_cooldown = 20
                
                # Create a fire projectile
                projectile = {
                    'type': 'fire',
                    'x': self.position[0] + (30 if self.facing_right else -30),
                    'y': self.position[1] - 50,
                    'velocity': 8 * (1 if self.facing_right else -1),
                    'lifetime': 60,  # frames
                    'damage': 12,
                    'size': 15,
                    'owner': self
                }
                self.projectiles.append(projectile)
    
    def special_move(self):
        # Wizard's special is an ice storm
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            # Check if enough mana
            if self.mana >= 35:
                self.mana -= 35
                self.is_attacking = True
                self.attack_type = "special"
                self.attack_damage = 20
                self.current_animation = "special"
                self.animation_frame = 0
                self.attack_cooldown = 40
                
                # Create multiple ice projectiles in a spread pattern
                for i in range(5):
                    angle = -30 + i * 15  # -30, -15, 0, 15, 30 degrees
                    speed = 6
                    direction = 1 if self.facing_right else -1
                    velocity_x = math.cos(math.radians(angle)) * speed * direction
                    velocity_y = math.sin(math.radians(angle)) * speed
                    
                    projectile = {
                        'type': 'ice',
                        'x': self.position[0] + (30 if self.facing_right else -30),
                        'y': self.position[1] - 60,
                        'velocity_x': velocity_x,
                        'velocity_y': velocity_y,
                        'lifetime': 50,  # frames
                        'damage': 8,  # each shard does less damage
                        'size': 10,
                        'owner': self
                    }
                    self.projectiles.append(projectile)
    
    def update(self):
        super().update()
        
        # Regenerate mana
        if self.mana < self.max_mana and not self.is_knocked_out:
            self.mana = min(self.max_mana, self.mana + self.mana_regen)
        
        # Update projectiles
        i = 0
        while i < len(self.projectiles):
            proj = self.projectiles[i]
            
            # Move projectile
            if proj['type'] == 'fire':
                proj['x'] += proj['velocity']
                proj['lifetime'] -= 1
            elif proj['type'] == 'ice':
                proj['x'] += proj['velocity_x']
                proj['y'] += proj['velocity_y']
                # Add gravity to ice shards
                proj['velocity_y'] += 0.2
                proj['lifetime'] -= 1
            
            # Remove projectiles that are off-screen or expired
            if proj['lifetime'] <= 0 or proj['x'] < -50 or proj['x'] > 850 or proj['y'] > 500:
                self.projectiles.pop(i)
            else:
                i += 1
    
    def render(self, screen):
        """Custom rendering for wizard."""
        super().render(screen)
        
        # Render all projectiles
        for proj in self.projectiles:
            if proj['type'] == 'fire':
                # Fire projectile with trailing particles
                for i in range(3):  # 3 size layers
                    size = proj['size'] - i * 3
                    if size <= 0:
                        continue
                    color = self.flame_colors[min(i, len(self.flame_colors)-1)]
                    pygame.draw.circle(screen, color, (int(proj['x']), int(proj['y'])), size)
                
                # Add trailing fire particles
                for i in range(5):
                    offset = i * 5 * (-1 if proj['velocity'] > 0 else 1)
                    alpha = 200 - i * 40
                    size = proj['size'] - i * 2
                    if size <= 0:
                        continue
                    
                    particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    particle_color = self.flame_colors[random.randint(0, len(self.flame_colors)-1)]
                    particle_color = (*particle_color, alpha)
                    pygame.draw.circle(particle_surf, particle_color, (size, size), size)
                    screen.blit(particle_surf, (int(proj['x'] + offset - size), int(proj['y'] - size)))
            
            elif proj['type'] == 'ice':
                # Ice shard projectile
                # Draw a diamond shape for ice shard
                points = [
                    (proj['x'], proj['y'] - proj['size']),
                    (proj['x'] + proj['size'], proj['y']),
                    (proj['x'], proj['y'] + proj['size']),
                    (proj['x'] - proj['size'], proj['y'])
                ]
                pygame.draw.polygon(screen, self.ice_colors[0], points)
                
                # Add sparkling effect
                if random.random() < 0.3:
                    sparkle_pos = (
                        int(proj['x'] + random.uniform(-proj['size'], proj['size'])),
                        int(proj['y'] + random.uniform(-proj['size'], proj['size']))
                    )
                    sparkle_size = random.randint(1, 3)
                    pygame.draw.circle(screen, (255, 255, 255), sparkle_pos, sparkle_size)
        
        # Draw mana bar above wizard if mana is not full
        if self.mana < self.max_mana:
            bar_width = 40
            bar_height = 5
            mana_fill = int(bar_width * (self.mana / self.max_mana))
            mana_bg_rect = pygame.Rect(self.position[0] - bar_width//2, self.position[1] - 120, bar_width, bar_height)
            mana_fill_rect = pygame.Rect(self.position[0] - bar_width//2, self.position[1] - 120, mana_fill, bar_height)
            
            pygame.draw.rect(screen, (30, 30, 60), mana_bg_rect)
            pygame.draw.rect(screen, self.mana_color, mana_fill_rect)
            pygame.draw.rect(screen, (200, 200, 255), mana_bg_rect, 1)
    
    def _render_idle(self, screen, x, y):
        # Body
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Animation
        frame = self.animation_frame % self.animation_frames["idle"]
        breathing_offset = math.sin(frame * 0.5 + pygame.time.get_ticks() * 0.002) * 2
        
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, 
                          (head_rect.x, head_rect.y + breathing_offset, head_rect.width, head_rect.height))
        
        # Draw wizard hat
        hat_color = (40, 0, 80) if self.is_player1 else (80, 0, 40)
        hat_points = [
            (x, y - 110 + breathing_offset),  # Tip of hat
            (x - 20, y - 100 + breathing_offset),  # Left base
            (x + 20, y - 100 + breathing_offset)   # Right base
        ]
        pygame.draw.polygon(screen, hat_color, hat_points)
        
        # Hat brim
        brim_rect = pygame.Rect(x - 25, y - 100 + breathing_offset, 50, 5)
        pygame.draw.rect(screen, hat_color, brim_rect)
        
        # Draw staff
        staff_color = (120, 80, 0)
        staff_height = 100
        staff_width = 5
        
        if self.facing_right:
            pygame.draw.rect(screen, staff_color, 
                           (x + 20, y - staff_height, staff_width, staff_height))
            # Staff orb
            pygame.draw.circle(screen, self.mana_color, 
                            (x + 22, y - staff_height), 10)
        else:
            pygame.draw.rect(screen, staff_color, 
                           (x - 25, y - staff_height, staff_width, staff_height))
            # Staff orb
            pygame.draw.circle(screen, self.mana_color, 
                            (x - 22, y - staff_height), 10)
        
        # Draw eyes
        eye_color = (255, 255, 255)
        if self.facing_right:
            pygame.draw.circle(screen, eye_color, (int(x + 5), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(x + 7), int(y - 85)), 2)
        else:
            pygame.draw.circle(screen, eye_color, (int(x - 5), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(x - 7), int(y - 85)), 2)
        
        # Occasionally add sparkles to the staff orb
        if random.random() < 0.1:
            sparkle_x = x + 22 if self.facing_right else x - 22
            sparkle_y = y - staff_height
            sparkle_size = random.randint(1, 3)
            sparkle_offset_x = random.uniform(-8, 8)
            sparkle_offset_y = random.uniform(-8, 8)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(sparkle_x + sparkle_offset_x), int(sparkle_y + sparkle_offset_y)), 
                             sparkle_size)
    
    def _render_cast(self, screen, x, y):
        # Similar to punch but with magic effects
        frame = self.animation_frame % self.animation_frames["cast"]
        
        # Body and head
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Animate body leaning into cast
        if self.facing_right:
            body_offset_x = frame * 2
        else:
            body_offset_x = -frame * 2
        
        pygame.draw.rect(screen, self.body_color, (int(body_rect.x + body_offset_x), body_rect.y, body_rect.width, body_rect.height))
        pygame.draw.ellipse(screen, self.body_color, (int(head_rect.x + body_offset_x), head_rect.y, head_rect.width, head_rect.height))
        
        # Draw wizard hat
        hat_color = (40, 0, 80) if self.is_player1 else (80, 0, 40)
        hat_points = [
            (x + body_offset_x, y - 110),  # Tip of hat
            (x - 20 + body_offset_x, y - 100),  # Left base
            (x + 20 + body_offset_x, y - 100)   # Right base
        ]
        pygame.draw.polygon(screen, hat_color, hat_points)
        
        # Hat brim
        brim_rect = pygame.Rect(x - 25 + body_offset_x, y - 100, 50, 5)
        pygame.draw.rect(screen, hat_color, brim_rect)
        
        # Draw staff with casting animation
        staff_color = (120, 80, 0)
        staff_width = 5
        
        if self.facing_right:
            # Staff moves forward during cast
            staff_extend = frame * 10
            pygame.draw.rect(screen, staff_color, 
                           (x + 20 + staff_extend, y - 80, staff_width, 80))
            
            # Growing energy orb
            orb_size = 10 + frame * 3
            orb_x = x + 22 + staff_extend
            orb_y = y - 80
            
            # Base orb
            pygame.draw.circle(screen, self.mana_color, (int(orb_x), int(orb_y)), orb_size)
            
            # Glowing effect
            for i in range(3):
                pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.3 + 0.7
                glow_size = orb_size * (1 + (i * 0.25 * pulse))
                alpha = 150 - i * 40
                glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
                glow_color = (*self.mana_color, alpha)
                pygame.draw.circle(glow_surf, glow_color, (int(glow_size), int(glow_size)), int(glow_size))
                screen.blit(glow_surf, (int(orb_x - glow_size), int(orb_y - glow_size)))
            
            # Particles emanating from orb
            for i in range(5):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(orb_size, orb_size * 2)
                particle_x = orb_x + math.cos(angle) * distance
                particle_y = orb_y + math.sin(angle) * distance
                particle_size = random.randint(1, 3)
                
                particle_colors = [(100, 150, 255), (150, 200, 255), (200, 230, 255)]
                particle_color = particle_colors[random.randint(0, len(particle_colors) - 1)]
                pygame.draw.circle(screen, particle_color, (int(particle_x), int(particle_y)), particle_size)
        else:
            # Staff moves forward during cast
            staff_extend = frame * 10
            pygame.draw.rect(screen, staff_color, 
                           (x - 25 - staff_extend, y - 80, staff_width, 80))
            
            # Growing energy orb
            orb_size = 10 + frame * 3
            orb_x = x - 22 - staff_extend
            orb_y = y - 80
            
            # Base orb
            pygame.draw.circle(screen, self.mana_color, (int(orb_x), int(orb_y)), orb_size)
            
            # Glowing effect
            for i in range(3):
                pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.3 + 0.7
                glow_size = orb_size * (1 + (i * 0.25 * pulse))
                alpha = 150 - i * 40
                glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
                glow_color = (*self.mana_color, alpha)
                pygame.draw.circle(glow_surf, glow_color, (int(glow_size), int(glow_size)), int(glow_size))
                screen.blit(glow_surf, (int(orb_x - glow_size), int(orb_y - glow_size)))
            
            # Particles emanating from orb
            for i in range(5):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(orb_size, orb_size * 2)
                particle_x = orb_x + math.cos(angle) * distance
                particle_y = orb_y + math.sin(angle) * distance
                particle_size = random.randint(1, 3)
                
                particle_colors = [(100, 150, 255), (150, 200, 255), (200, 230, 255)]
                particle_color = particle_colors[random.randint(0, len(particle_colors) - 1)]
                pygame.draw.circle(screen, particle_color, (int(particle_x), int(particle_y)), particle_size)
        
        # Draw determined eyes
        eye_color = (255, 255, 255)
        glow_color = (0, 100, 255)
        if self.facing_right:
            pygame.draw.circle(screen, glow_color, (int(x + 5 + body_offset_x), int(y - 85)), 7)
            pygame.draw.circle(screen, eye_color, (int(x + 5 + body_offset_x), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 50, 255), (int(x + 7 + body_offset_x), int(y - 85)), 3)
        else:
            pygame.draw.circle(screen, glow_color, (int(x - 5 + body_offset_x), int(y - 85)), 7)
            pygame.draw.circle(screen, eye_color, (int(x - 5 + body_offset_x), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 50, 255), (int(x - 7 + body_offset_x), int(y - 85)), 3)
    
    def _render_special(self, screen, x, y):
        # Special ice storm animation
        frame = self.animation_frame % self.animation_frames["special"]
        
        # Body and head
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Make wizard float during special
        float_offset = frame * 3
        
        pygame.draw.rect(screen, self.body_color, (body_rect.x, int(body_rect.y - float_offset), body_rect.width, body_rect.height))
        pygame.draw.ellipse(screen, self.body_color, (head_rect.x, int(head_rect.y - float_offset), head_rect.width, head_rect.height))
        
        # Draw wizard hat
        hat_color = (40, 0, 80) if self.is_player1 else (80, 0, 40)
        hat_points = [
            (x, y - 110 - float_offset),  # Tip of hat
            (x - 20, y - 100 - float_offset),  # Left base
            (x + 20, y - 100 - float_offset)   # Right base
        ]
        pygame.draw.polygon(screen, hat_color, hat_points)
        
        # Hat brim
        brim_rect = pygame.Rect(x - 25, y - 100 - float_offset, 50, 5)
        pygame.draw.rect(screen, hat_color, brim_rect)
        
        # Draw staff with raised position
        staff_color = (120, 80, 0)
        staff_width = 5
        
        if self.facing_right:
            pygame.draw.rect(screen, staff_color, 
                           (x + 20, y - 120 - float_offset, staff_width, 120))
            
            # Glowing orb on staff
            orb_x = x + 22
            orb_y = y - 120 - float_offset
        else:
            pygame.draw.rect(screen, staff_color, 
                           (x - 25, y - 120 - float_offset, staff_width, 120))
            
            # Glowing orb on staff
            orb_x = x - 22
            orb_y = y - 120 - float_offset
        
        # Pulsing orb with energy field
        orb_size = 15 + frame * 2
        for i in range(4):
            pulse = math.sin(pygame.time.get_ticks() * 0.01 + i) * 0.3 + 0.7
            glow_size = orb_size * (1 + (i * 0.3 * pulse))
            alpha = 180 - i * 40
            glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
            
            # Cycle between blue and white
            cycle = (pygame.time.get_ticks() // 100) % 3
            glow_colors = [
                (100, 150, 255, alpha),  # Blue
                (150, 200, 255, alpha),  # Light blue
                (220, 240, 255, alpha)   # Almost white
            ]
            glow_color = glow_colors[(cycle + i) % 3]
            
            pygame.draw.circle(glow_surf, glow_color, (int(glow_size), int(glow_size)), int(glow_size))
            screen.blit(glow_surf, (int(orb_x - glow_size), int(orb_y - glow_size)))
        
        # Energy waves emanating in circles
        for i in range(3):
            wave_size = 30 + frame * 20 + i * 30
            wave_alpha = max(0, 200 - frame * 30 - i * 40)
            wave_surf = pygame.Surface((wave_size * 2, wave_size * 2), pygame.SRCALPHA)
            
            wave_color = (150, 200, 255, wave_alpha)
            pygame.draw.circle(wave_surf, wave_color, (wave_size, wave_size), wave_size, 2)
            
            screen.blit(wave_surf, (int(orb_x - wave_size), int(orb_y - wave_size)))
        
        # Ice crystal particles floating around
        for i in range(10):
            angle = (i / 10 * 2 * math.pi) + (pygame.time.get_ticks() * 0.002)
            distance = 40 + frame * 5
            particle_x = orb_x + math.cos(angle) * distance
            particle_y = orb_y + math.sin(angle) * distance
            particle_size = 3 + (i % 3)
            
            # Simple diamond shape for ice crystals
            crystal_points = [
                (particle_x, particle_y - particle_size),
                (particle_x + particle_size, particle_y),
                (particle_x, particle_y + particle_size),
                (particle_x - particle_size, particle_y)
            ]
            
            pygame.draw.polygon(screen, self.ice_colors[i % len(self.ice_colors)], 
                              [(int(x), int(y)) for x, y in crystal_points])
        
        # Wizard's eyes glow during special
        eye_color = (200, 230, 255)
        glow_color = (100, 150, 255)
        eye_y = y - 85 - float_offset
        
        if self.facing_right:
            eye_x = x + 5
            pygame.draw.circle(screen, glow_color, (int(eye_x), int(eye_y)), 8)
            pygame.draw.circle(screen, eye_color, (int(eye_x), int(eye_y)), 5)
        else:
            eye_x = x - 5
            pygame.draw.circle(screen, glow_color, (int(eye_x), int(eye_y)), 8)
            pygame.draw.circle(screen, eye_color, (int(eye_x), int(eye_y)), 5)
    
    def _render_ko(self, screen, x, y):
        super()._render_ko(screen, x, y)
        
        # Add broken staff
        staff_color = (120, 80, 0)
        if self.facing_right:
            pygame.draw.rect(screen, staff_color, (x + 30, y - 15, 5, 40))
            pygame.draw.rect(screen, staff_color, (x + 35, y - 25, 30, 5))
            
            # Broken orb
            broken_orb = pygame.Surface((15, 15), pygame.SRCALPHA)
            for i in range(5):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(3, 6)
                shard_x = 7 + math.cos(angle) * distance
                shard_y = 7 + math.sin(angle) * distance
                pygame.draw.circle(broken_orb, self.mana_color, (int(shard_x), int(shard_y)), 2)
            
            screen.blit(broken_orb, (x + 50, y - 30))
        else:
            pygame.draw.rect(screen, staff_color, (x - 35, y - 15, 5, 40))
            pygame.draw.rect(screen, staff_color, (x - 65, y - 25, 30, 5))
            
            # Broken orb
            broken_orb = pygame.Surface((15, 15), pygame.SRCALPHA)
            for i in range(5):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(3, 6)
                shard_x = 7 + math.cos(angle) * distance
                shard_y = 7 + math.sin(angle) * distance
                pygame.draw.circle(broken_orb, self.mana_color, (int(shard_x), int(shard_y)), 2)
            
            screen.blit(broken_orb, (x - 65, y - 30))