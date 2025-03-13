import pygame
import math
import random
from game.engine.character import Character

class Guardian(Character):
    """Guardian character - high health, strong defense and counter attacks."""
    
    def __init__(self, is_player1=True):
        super().__init__(is_player1)
        
        # Override base class attributes
        self.health = 150  # High health
        self.max_health = 150  # For proper scaling
        self.move_speed = 3  # Very slow
        self.jump_strength = -12  # Lower jump
        self.attack_damage = 12  # High base damage
        
        # Guardian specific attributes
        self.shield_energy = 100  # Shield energy for special blocks
        self.max_shield_energy = 100
        self.shield_regen = 0.2
        self.is_charging = False
        self.charge_level = 0
        self.max_charge = 60  # Frames to fully charge
        self.is_countering = False  # Special counter-attack state
        
        # Colors
        self.body_color = (50, 100, 50) if is_player1 else (100, 50, 50)
        self.shield_color = (220, 220, 100)
        self.armor_color = (100, 150, 100) if is_player1 else (150, 100, 100)
        
        # Animation frames dict - specific for Guardian
        self.animation_frames = {
            "idle": 4,
            "walk": 4,
            "jump": 3,
            "punch": 4,
            "kick": 4,
            "special": 6,
            "hit": 2,
            "ko": 1,
            "block": 3,
            "charge": 5,
            "counter": 3
        }
    
    def punch(self):
        # Guardian's punch is a powerful hammer strike
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_type = "punch"
            self.attack_damage = 15  # Higher damage
            self.current_animation = "punch"
            self.animation_frame = 0
            self.attack_cooldown = 25  # Slower attack
    
    def kick(self):
        # Guardian's kick starts charging a powerful attack
        if not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.is_charging = True
            self.charge_level = 0
            self.attack_type = "charge"
            self.current_animation = "charge"
            self.animation_frame = 0
            self.attack_cooldown = 5  # Short cooldown, but charge takes time
    
    def special_move(self):
        # Guardian's special is a defensive counter-attack stance
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            if self.shield_energy >= 25:
                self.shield_energy -= 25
                self.is_attacking = False  # Not actually attacking yet
                self.is_countering = True  # Enter counter state
                self.attack_type = "counter"
                self.current_animation = "counter"
                self.animation_frame = 0
                self.attack_cooldown = 45  # Long cooldown after counter ends
    
    def block(self):
        if not self.is_attacking and not self.is_knocked_out and not self.is_stunned:
            self.is_blocking = True
            self.current_animation = "block"
            # Guardian's block gradually consumes shield energy for enhanced protection
            if self.shield_energy > 0:
                self.shield_energy = max(0, self.shield_energy - 0.2)  # Slow drain
    
    def take_damage(self, amount):
        """Override to implement counter-attack mechanics"""
        if self.is_countering:
            # Counter attack! Return damage to attacker instead of taking it
            self.is_countering = False
            self.is_attacking = True  # Now we're attacking
            self.attack_type = "special"
            self.current_animation = "special"
            self.animation_frame = 0
            self.attack_damage = amount * 1.5  # Return 150% damage
            return False  # Indicate that we didn't actually take damage
        
        # Enhanced blocking for Guardian
        if self.is_blocking:
            if self.shield_energy > 0:
                # Super block with shield energy
                block_reduction = 0.8  # Block 80% of damage
                amount = max(0, int(amount * (1 - block_reduction)))
                # Visual feedback but no actual hit state
                self.current_animation = "block"
                self.animation_frame = 0
            else:
                # Normal block
                amount = max(0, amount // 2)
                # Briefly show hit animation even when blocking
                self.current_animation = "hit"
                self.animation_frame = 0
            
            # Slight knockback when blocking
            knockback_dir = -1 if self.facing_right else 1
            self.velocity[0] += knockback_dir * 1  # Less knockback for Guardian
        else:
            self.health = max(0, self.health - amount)
            self.is_hit = True
            # Briefly stun the character
            self.is_stunned = True
            self.stun_timer = 15  # Less stun time than normal characters
            # Knockback effect
            knockback_dir = -1 if self.facing_right else 1
            self.velocity[0] += knockback_dir * 3  # Less knockback for Guardian
            # Change animation
            self.current_animation = "hit"
            self.animation_frame = 0
        
        return True  # Damage was processed
    
    def get_attack_damage(self):
        """Override to implement charge attacks"""
        if self.attack_type == "charge" and self.charge_level > 0:
            # Calculate damage based on charge level
            charge_percent = min(1.0, self.charge_level / self.max_charge)
            return int(self.attack_damage * (1 + charge_percent * 2))  # Up to 3x damage
        
        return super().get_attack_damage()
    
    def update(self):
        super().update()
        
        # Handle charging mechanics
        if self.is_charging:
            self.charge_level += 1
            
            # Release charge attack if fully charged or key released
            if self.charge_level >= self.max_charge:
                self.is_charging = False
                self.is_attacking = True
                self.attack_type = "kick"  # Powerful ground slam
                self.current_animation = "kick"
                self.animation_frame = 0
            
            # Animation frame based on charge level
            charge_frame = int((self.charge_level / self.max_charge) * (self.animation_frames["charge"] - 1))
            self.animation_frame = min(charge_frame, self.animation_frames["charge"] - 1)
        
        # Handle counter state timing
        if self.is_countering and not self.is_attacking:
            # Counter state times out after a certain number of frames
            if self.animation_frame >= self.animation_frames["counter"] - 1:
                self.is_countering = False
                self.current_animation = "idle"
                self.animation_frame = 0
        
        # Regenerate shield energy when not blocking or countering
        if not self.is_blocking and not self.is_countering and self.shield_energy < self.max_shield_energy:
            self.shield_energy = min(self.max_shield_energy, self.shield_energy + self.shield_regen)
    
    def render(self, screen):
        """Custom rendering for guardian."""
        super().render(screen)
        
        # Draw shield energy bar above guardian if not full
        if self.shield_energy < self.max_shield_energy:
            bar_width = 40
            bar_height = 5
            energy_fill = int(bar_width * (self.shield_energy / self.max_shield_energy))
            energy_bg_rect = pygame.Rect(self.position[0] - bar_width//2, self.position[1] - 120, bar_width, bar_height)
            energy_fill_rect = pygame.Rect(self.position[0] - bar_width//2, self.position[1] - 120, energy_fill, bar_height)
            
            pygame.draw.rect(screen, (30, 30, 30), energy_bg_rect)
            pygame.draw.rect(screen, self.shield_color, energy_fill_rect)
            pygame.draw.rect(screen, (220, 220, 200), energy_bg_rect, 1)
        
        # Draw charge meter when charging
        if self.is_charging:
            charge_percent = self.charge_level / self.max_charge
            meter_width = 50
            meter_height = 8
            
            meter_bg = pygame.Rect(self.position[0] - meter_width//2, self.position[1] - 140, meter_width, meter_height)
            meter_fill = pygame.Rect(self.position[0] - meter_width//2, self.position[1] - 140, 
                                   int(meter_width * charge_percent), meter_height)
            
            # Color changes with charge level
            charge_color = (
                min(255, int(50 + charge_percent * 205)),  # Red increases with charge
                min(255, int(200 - charge_percent * 150)),  # Green decreases with charge
                50  # Blue stays low
            )
            
            pygame.draw.rect(screen, (40, 40, 40), meter_bg)
            pygame.draw.rect(screen, charge_color, meter_fill)
            pygame.draw.rect(screen, (255, 255, 255), meter_bg, 1)
    
    def _render_idle(self, screen, x, y):
        # Body - wider for Guardian
        body_rect = pygame.Rect(x - 25, y - 70, 50, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Animation
        frame = self.animation_frame % self.animation_frames["idle"]
        breathing_offset = math.sin(frame * 0.5 + pygame.time.get_ticks() * 0.002) * 1  # Less movement
        
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, 
                          (head_rect.x, head_rect.y + breathing_offset, head_rect.width, head_rect.height))
        
        # Draw armor plates
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 70, 50, 15))  # Shoulder plate
        pygame.draw.rect(screen, self.armor_color, (x - 20, y - 40, 40, 20))  # Chest plate
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 15, 50, 15))  # Belt
        
        # Draw helmet
        helmet_color = self.armor_color
        helmet_rect = pygame.Rect(x - 18, y - 105 + breathing_offset, 36, 35)
        pygame.draw.rect(screen, helmet_color, helmet_rect, border_radius=5)
        
        # Helmet visor
        visor_color = (50, 50, 50) if not self.is_countering else (200, 50, 50)
        visor_rect = pygame.Rect(x - 15, y - 95 + breathing_offset, 30, 10)
        pygame.draw.rect(screen, visor_color, visor_rect)
        
        # Shoulder guards
        pygame.draw.circle(screen, self.armor_color, (int(x - 25), int(y - 60)), 8)
        pygame.draw.circle(screen, self.armor_color, (int(x + 25), int(y - 60)), 8)
        
        # Weapon: Large hammer or shield
        if self.facing_right:
            # Draw hammer on back
            handle_rect = pygame.Rect(x + 25, y - 90, 5, 90)
            pygame.draw.rect(screen, (100, 70, 40), handle_rect)
            
            # Hammer head
            hammer_head = [
                (x + 25, y - 90),
                (x + 45, y - 90),
                (x + 45, y - 110),
                (x + 25, y - 110)
            ]
            pygame.draw.polygon(screen, (150, 150, 150), hammer_head)
            pygame.draw.polygon(screen, (100, 100, 100), hammer_head, 2)
        else:
            # Draw hammer on back
            handle_rect = pygame.Rect(x - 30, y - 90, 5, 90)
            pygame.draw.rect(screen, (100, 70, 40), handle_rect)
            
            # Hammer head
            hammer_head = [
                (x - 30, y - 90),
                (x - 50, y - 90),
                (x - 50, y - 110),
                (x - 30, y - 110)
            ]
            pygame.draw.polygon(screen, (150, 150, 150), hammer_head)
            pygame.draw.polygon(screen, (100, 100, 100), hammer_head, 2)
    
    def _render_block(self, screen, x, y):
        # Guardian's block stance with shield
        frame = self.animation_frame % self.animation_frames["block"]
        
        # Body and head - crouched slightly
        body_rect = pygame.Rect(x - 25, y - 65, 50, 65)  # Shorter body in block stance
        head_rect = pygame.Rect(x - 15, y - 95, 30, 30)  # Head lower
        
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw armor plates
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 65, 50, 15))  # Shoulder plate
        pygame.draw.rect(screen, self.armor_color, (x - 20, y - 40, 40, 20))  # Chest plate
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 15, 50, 15))  # Belt
        
        # Draw helmet
        helmet_color = self.armor_color
        helmet_rect = pygame.Rect(x - 18, y - 100, 36, 35)
        pygame.draw.rect(screen, helmet_color, helmet_rect, border_radius=5)
        
        # Helmet visor
        visor_color = (50, 100, 200)  # Blue when blocking
        visor_rect = pygame.Rect(x - 15, y - 90, 30, 10)
        pygame.draw.rect(screen, visor_color, visor_rect)
        
        # Draw shield - position depends on facing direction
        shield_width = 40
        shield_height = 60
        
        if self.facing_right:
            shield_x = x - 40  # Shield on left side when facing right
            shield_y = y - 70
        else:
            shield_x = x + 5  # Shield on right side when facing left
            shield_y = y - 70
        
        shield_rect = pygame.Rect(shield_x, shield_y, shield_width, shield_height)
        
        # Shield with energy effect
        pygame.draw.rect(screen, self.shield_color, shield_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 50), shield_rect, 3, border_radius=5)
        
        # Shield emblem
        emblem_color = (150, 50, 50) if self.is_player1 else (50, 50, 150)
        emblem_rect = pygame.Rect(shield_x + shield_width//2 - 10, shield_y + shield_height//2 - 10, 20, 20)
        pygame.draw.rect(screen, emblem_color, emblem_rect)
        
        # Shield energy effect based on shield_energy
        if self.shield_energy > 0:
            energy_percent = self.shield_energy / self.max_shield_energy
            glow_size = int(10 + energy_percent * 20)
            glow_alpha = int(50 + energy_percent * 100)
            
            # Create shield energy glow
            glow_surf = pygame.Surface((shield_width + glow_size*2, shield_height + glow_size*2), pygame.SRCALPHA)
            glow_color = (*self.shield_color, glow_alpha)
            pygame.draw.rect(glow_surf, glow_color, 
                          (glow_size, glow_size, shield_width, shield_height), 
                          border_radius=10)
            
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.2 + 0.8
            glow_size = int(glow_size * pulse)
            
            # Only show glow when shield energy is being used
            if frame > 0:
                screen.blit(glow_surf, (shield_x - glow_size, shield_y - glow_size))
    
    def _render_punch(self, screen, x, y):
        # Powerful hammer swing
        frame = self.animation_frame % self.animation_frames["punch"]
        
        # Body and head
        body_rect = pygame.Rect(x - 25, y - 70, 50, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Animate body twisting during swing
        twist_factor = frame / (self.animation_frames["punch"] - 1)
        twist_angle = math.sin(twist_factor * math.pi) * (30 if self.facing_right else -30)
        
        # Basic body and head
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw armor plates
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 70, 50, 15))  # Shoulder plate
        pygame.draw.rect(screen, self.armor_color, (x - 20, y - 40, 40, 20))  # Chest plate
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 15, 50, 15))  # Belt
        
        # Draw helmet
        helmet_color = self.armor_color
        helmet_rect = pygame.Rect(x - 18, y - 105, 36, 35)
        pygame.draw.rect(screen, helmet_color, helmet_rect, border_radius=5)
        
        # Helmet visor - red during attack
        visor_color = (200, 50, 50)
        visor_rect = pygame.Rect(x - 15, y - 95, 30, 10)
        pygame.draw.rect(screen, visor_color, visor_rect)
        
        # Draw hammer with swing animation
        hammer_handle_width = 6
        hammer_handle_length = 90
        hammer_head_width = 30
        hammer_head_height = 25
        
        # Calculate swing position - initial position is up, then swings down
        if self.facing_right:
            if frame == 0:
                # Wind up - hammer raised
                handle_start_x = x + 20
                handle_start_y = y - 70
                handle_angle = -60  # Raised position
            else:
                # Swing progression
                handle_angle = -60 + (frame / (self.animation_frames["punch"] - 1)) * 150
                handle_start_x = x + 20
                handle_start_y = y - 70
            
            # Calculate handle end point
            handle_end_x = handle_start_x + math.cos(math.radians(handle_angle)) * hammer_handle_length
            handle_end_y = handle_start_y + math.sin(math.radians(handle_angle)) * hammer_handle_length
            
            # Draw handle
            pygame.draw.line(screen, (100, 70, 40), 
                           (handle_start_x, handle_start_y), 
                           (handle_end_x, handle_end_y), 
                           hammer_handle_width)
            
            # Calculate hammer head position
            hammer_center_x = handle_end_x
            hammer_center_y = handle_end_y
            
            # Rotate points around head center
            hammer_head_points = []
            hammer_corners = [
                (-hammer_head_width//2, -hammer_head_height//2),
                (hammer_head_width//2, -hammer_head_height//2),
                (hammer_head_width//2, hammer_head_height//2),
                (-hammer_head_width//2, hammer_head_height//2)
            ]
            
            for hx, hy in hammer_corners:
                # Rotate point
                rotated_x = hx * math.cos(math.radians(handle_angle)) - hy * math.sin(math.radians(handle_angle))
                rotated_y = hx * math.sin(math.radians(handle_angle)) + hy * math.cos(math.radians(handle_angle))
                
                # Add to hammer center
                point_x = hammer_center_x + rotated_x
                point_y = hammer_center_y + rotated_y
                
                hammer_head_points.append((point_x, point_y))
            
            # Draw hammer head
            pygame.draw.polygon(screen, (150, 150, 150), hammer_head_points)
            pygame.draw.polygon(screen, (100, 100, 100), hammer_head_points, 2)
            
            # Impact effect at end of swing
            if frame == self.animation_frames["punch"] - 1:
                impact_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                impact_color = (255, 200, 0, 180)
                
                # Explosion-like shape
                pygame.draw.circle(impact_surf, impact_color, (30, 30), 30)
                pygame.draw.circle(impact_surf, (255, 255, 255, 100), (30, 30), 20)
                
                screen.blit(impact_surf, (int(hammer_center_x - 30), int(hammer_center_y - 30)))
                
                # Radial impact lines
                for i in range(8):
                    angle = i * 45
                    line_length = 40
                    end_x = hammer_center_x + math.cos(math.radians(angle)) * line_length
                    end_y = hammer_center_y + math.sin(math.radians(angle)) * line_length
                    pygame.draw.line(screen, (255, 255, 0), 
                                   (hammer_center_x, hammer_center_y), 
                                   (end_x, end_y), 2)
        else:
            # Left-facing version - mirror of right-facing
            if frame == 0:
                # Wind up - hammer raised
                handle_start_x = x - 20
                handle_start_y = y - 70
                handle_angle = -120  # Raised position (mirrored)
            else:
                # Swing progression
                handle_angle = -120 - (frame / (self.animation_frames["punch"] - 1)) * 150
                handle_start_x = x - 20
                handle_start_y = y - 70
            
            # Calculate handle end point
            handle_end_x = handle_start_x + math.cos(math.radians(handle_angle)) * hammer_handle_length
            handle_end_y = handle_start_y + math.sin(math.radians(handle_angle)) * hammer_handle_length
            
            # Draw handle
            pygame.draw.line(screen, (100, 70, 40), 
                           (handle_start_x, handle_start_y), 
                           (handle_end_x, handle_end_y), 
                           hammer_handle_width)
            
            # Calculate hammer head position
            hammer_center_x = handle_end_x
            hammer_center_y = handle_end_y
            
            # Rotate points around head center
            hammer_head_points = []
            hammer_corners = [
                (-hammer_head_width//2, -hammer_head_height//2),
                (hammer_head_width//2, -hammer_head_height//2),
                (hammer_head_width//2, hammer_head_height//2),
                (-hammer_head_width//2, hammer_head_height//2)
            ]
            
            for hx, hy in hammer_corners:
                # Rotate point
                rotated_x = hx * math.cos(math.radians(handle_angle)) - hy * math.sin(math.radians(handle_angle))
                rotated_y = hx * math.sin(math.radians(handle_angle)) + hy * math.cos(math.radians(handle_angle))
                
                # Add to hammer center
                point_x = hammer_center_x + rotated_x
                point_y = hammer_center_y + rotated_y
                
                hammer_head_points.append((point_x, point_y))
            
            # Draw hammer head
            pygame.draw.polygon(screen, (150, 150, 150), hammer_head_points)
            pygame.draw.polygon(screen, (100, 100, 100), hammer_head_points, 2)
            
            # Impact effect at end of swing
            if frame == self.animation_frames["punch"] - 1:
                impact_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                impact_color = (255, 200, 0, 180)
                
                # Explosion-like shape
                pygame.draw.circle(impact_surf, impact_color, (30, 30), 30)
                pygame.draw.circle(impact_surf, (255, 255, 255, 100), (30, 30), 20)
                
                screen.blit(impact_surf, (int(hammer_center_x - 30), int(hammer_center_y - 30)))
                
                # Radial impact lines
                for i in range(8):
                    angle = i * 45
                    line_length = 40
                    end_x = hammer_center_x + math.cos(math.radians(angle)) * line_length
                    end_y = hammer_center_y + math.sin(math.radians(angle)) * line_length
                    pygame.draw.line(screen, (255, 255, 0), 
                                   (hammer_center_x, hammer_center_y), 
                                   (end_x, end_y), 2)
    
    def _render_kick(self, screen, x, y):
        # Guardian's "kick" is a ground slam with hammer
        frame = self.animation_frame % self.animation_frames["kick"]
        
        # Body and head - position changes during slam
        body_rect = pygame.Rect(x - 25, y - 70 + frame * 5, 50, 70 - frame * 5)  # Body compresses
        head_rect = pygame.Rect(x - 15, y - 100 + frame * 5, 30, 30)  # Head lowers
        
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw armor plates
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 70 + frame * 5, 50, 15))  # Shoulder plate
        pygame.draw.rect(screen, self.armor_color, (x - 20, y - 40 + frame * 5, 40, 20))  # Chest plate
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 15 + frame * 5, 50, 15))  # Belt
        
        # Draw helmet
        helmet_color = self.armor_color
        helmet_rect = pygame.Rect(x - 18, y - 105 + frame * 5, 36, 35)
        pygame.draw.rect(screen, helmet_color, helmet_rect, border_radius=5)
        
        # Helmet visor - red during attack
        visor_color = (200, 50, 50)
        visor_rect = pygame.Rect(x - 15, y - 95 + frame * 5, 30, 10)
        pygame.draw.rect(screen, visor_color, visor_rect)
        
        # Draw hammer - slams down with both hands
        hammer_handle_width = 6
        hammer_handle_length = 60 - frame * 10  # Handle shortens as it's brought down
        hammer_head_width = 40
        hammer_head_height = 30
        
        # Hammer position - starts up, then slams down in front
        handle_start_x = x
        handle_start_y = y - 50 + frame * 5
        handle_angle = 90  # Vertical
        
        # Calculate handle end point
        handle_end_x = handle_start_x + math.cos(math.radians(handle_angle)) * hammer_handle_length
        handle_end_y = handle_start_y + math.sin(math.radians(handle_angle)) * hammer_handle_length
        
        # Draw handle
        pygame.draw.line(screen, (100, 70, 40), 
                       (handle_start_x, handle_start_y), 
                       (handle_end_x, handle_end_y), 
                       hammer_handle_width)
        
        # Calculate hammer head position
        hammer_center_x = handle_end_x
        hammer_center_y = handle_end_y
        
        # Hammer head as rectangle
        hammer_head_rect = pygame.Rect(
            hammer_center_x - hammer_head_width // 2,
            hammer_center_y - hammer_head_height // 2,
            hammer_head_width,
            hammer_head_height
        )
        
        pygame.draw.rect(screen, (150, 150, 150), hammer_head_rect)
        pygame.draw.rect(screen, (100, 100, 100), hammer_head_rect, 2)
        
        # Ground impact effect on final frame
        if frame == self.animation_frames["kick"] - 1:
            # Shockwave effect
            for i in range(3):
                radius = 20 + i * 20
                alpha = 180 - i * 50
                wave_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                wave_color = (255, 200, 0, alpha)
                
                pygame.draw.circle(wave_surf, wave_color, (radius, radius), radius, 5)
                screen.blit(wave_surf, (x - radius, y - radius))
            
            # Ground cracks
            crack_color = (100, 50, 0)
            for i in range(5):
                angle = i * 72
                length = random.randint(30, 80)
                end_x = x + math.cos(math.radians(angle)) * length
                end_y = y + math.sin(math.radians(angle)) * length
                
                # Draw jagged line for crack
                points = [(x, y)]
                segments = 4
                for j in range(1, segments + 1):
                    segment_x = x + (end_x - x) * (j / segments)
                    segment_y = y + (end_y - y) * (j / segments)
                    # Add some randomness to make it jagged
                    segment_x += random.uniform(-5, 5)
                    segment_y += random.uniform(-5, 5)
                    points.append((segment_x, segment_y))
                
                pygame.draw.lines(screen, crack_color, False, points, 3)
    
    def _render_counter(self, screen, x, y):
        # Counter stance - ready to parry attacks
        frame = self.animation_frame % self.animation_frames["counter"]
        
        # Body in defensive stance
        body_rect = pygame.Rect(x - 25, y - 70, 50, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw armor plates
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 70, 50, 15))  # Shoulder plate
        pygame.draw.rect(screen, self.armor_color, (x - 20, y - 40, 40, 20))  # Chest plate
        pygame.draw.rect(screen, self.armor_color, (x - 25, y - 15, 50, 15))  # Belt
        
        # Draw helmet
        helmet_color = self.armor_color
        helmet_rect = pygame.Rect(x - 18, y - 105, 36, 35)
        pygame.draw.rect(screen, helmet_color, helmet_rect, border_radius=5)
        
        # Helmet visor - glowing intense red during counter
        visor_alpha = 150 + int(math.sin(pygame.time.get_ticks() * 0.02) * 105)
        visor_surf = pygame.Surface((30, 10), pygame.SRCALPHA)
        visor_surf.fill((255, 0, 0, visor_alpha))
        screen.blit(visor_surf, (x - 15, y - 95))
        
        # Draw shield with counter stance animation
        shield_width = 50
        shield_height = 70
        
        # Shield position based on direction and animation
        if self.facing_right:
            shield_x = x - 20 - frame * 5  # Shield moves forward slightly
            shield_y = y - 80
        else:
            shield_x = x - 30 + frame * 5  # Shield moves forward slightly
            shield_y = y - 80
        
        shield_rect = pygame.Rect(shield_x, shield_y, shield_width, shield_height)
        
        # Shield with energy effect
        pygame.draw.rect(screen, self.shield_color, shield_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 50), shield_rect, 3, border_radius=8)
        
        # Shield emblem - glowing during counter
        emblem_color = (255, 50, 50) if self.is_player1 else (50, 50, 255)
        emblem_rect = pygame.Rect(shield_x + shield_width//2 - 15, shield_y + shield_height//2 - 15, 30, 30)
        pygame.draw.rect(screen, emblem_color, emblem_rect)
        
        # Counter energy effect around guardian
        energy_radius = 40 + frame * 10
        energy_alpha = 100 - frame * 20
        energy_surf = pygame.Surface((energy_radius * 2, energy_radius * 2), pygame.SRCALPHA)
        energy_color = (255, 200, 0, energy_alpha)
        
        pygame.draw.circle(energy_surf, energy_color, (energy_radius, energy_radius), energy_radius, 3)
        screen.blit(energy_surf, (x - energy_radius, y - 60 - energy_radius))
        
        # Floating runes/symbols around guardian during counter stance
        num_runes = 5
        for i in range(num_runes):
            angle = pygame.time.get_ticks() * 0.001 + i * (360 / num_runes)
            rune_distance = 50 + math.sin(pygame.time.get_ticks() * 0.01 + i) * 5
            rune_x = x + math.cos(math.radians(angle)) * rune_distance
            rune_y = y - 60 + math.sin(math.radians(angle)) * rune_distance
            
            # Simple square rune with glow
            rune_size = 8
            glow_surf = pygame.Surface((rune_size * 3, rune_size * 3), pygame.SRCALPHA)
            glow_color = (255, 200, 0, 100)
            pygame.draw.rect(glow_surf, glow_color, (rune_size, rune_size, rune_size, rune_size))
            
            screen.blit(glow_surf, (rune_x - rune_size * 1.5, rune_y - rune_size * 1.5))
            pygame.draw.rect(screen, (255, 220, 0), (rune_x - rune_size/2, rune_y - rune_size/2, rune_size, rune_size))
    
    def _render_special(self, screen, x, y):
        # Special counter-attack after successful parry
        frame = self.animation_frame % self.animation_frames["special"]
        
        # Body lunges forward during counter-attack
        body_offset = frame * 8 if self.facing_right else -frame * 8
        body_rect = pygame.Rect(x - 25 + body_offset, y - 70, 50, 70)
        head_rect = pygame.Rect(x - 15 + body_offset, y - 100, 30, 30)
        
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw armor plates
        pygame.draw.rect(screen, self.armor_color, (x - 25 + body_offset, y - 70, 50, 15))  # Shoulder plate
        pygame.draw.rect(screen, self.armor_color, (x - 20 + body_offset, y - 40, 40, 20))  # Chest plate
        pygame.draw.rect(screen, self.armor_color, (x - 25 + body_offset, y - 15, 50, 15))  # Belt
        
        # Draw helmet
        helmet_color = self.armor_color
        helmet_rect = pygame.Rect(x - 18 + body_offset, y - 105, 36, 35)
        pygame.draw.rect(screen, helmet_color, helmet_rect, border_radius=5)
        
        # Helmet visor - intense red during counter-attack
        visor_color = (255, 0, 0)
        visor_rect = pygame.Rect(x - 15 + body_offset, y - 95, 30, 10)
        pygame.draw.rect(screen, visor_color, visor_rect)
        
        # Counter energy effect - builds up then releases
        if frame < 3:
            # Energy gathering
            energy_radius = 20 + frame * 10
            energy_alpha = 200 - frame * 20
            energy_surf = pygame.Surface((energy_radius * 2, energy_radius * 2), pygame.SRCALPHA)
            energy_color = (255, 50, 0, energy_alpha)
            
            pygame.draw.circle(energy_surf, energy_color, (energy_radius, energy_radius), energy_radius)
            screen.blit(energy_surf, (x - energy_radius + body_offset, y - 60 - energy_radius))
        else:
            # Energy release
            direction = 1 if self.facing_right else -1
            energy_width = (frame - 2) * 40
            energy_height = 60
            energy_x = x + (30 * direction) + body_offset
            energy_y = y - 60
            
            if self.facing_right:
                energy_rect = pygame.Rect(energy_x, energy_y - energy_height//2, energy_width, energy_height)
            else:
                energy_rect = pygame.Rect(energy_x - energy_width, energy_y - energy_height//2, energy_width, energy_height)
                
            energy_surf = pygame.Surface((energy_width, energy_height), pygame.SRCALPHA)
            
            # Gradient energy beam
            for i in range(energy_width):
                alpha = 200 - (i / energy_width) * 150
                color = (255, 100 - (i / energy_width) * 100, 0, alpha)
                pygame.draw.line(energy_surf, color, 
                              (i if self.facing_right else energy_width - i, 0), 
                              (i if self.facing_right else energy_width - i, energy_height))
            
            screen.blit(energy_surf, (energy_rect.x, energy_rect.y))
            
            # Particles along beam
            for i in range(10):
                particle_x = energy_rect.x + (random.random() * energy_width if self.facing_right else random.random() * energy_width)
                particle_y = energy_rect.y + random.random() * energy_height
                particle_size = random.randint(2, 5)
                particle_color = (255, 200, 0)
                
                pygame.draw.circle(screen, particle_color, (int(particle_x), int(particle_y)), particle_size)
        
        # Shield with counter-attack stance (raised overhead)
        if frame < 3:
            shield_width = 50
            shield_height = 70
            
            shield_y = y - 120 + frame * 10  # Shield raises then lowers
            
            if self.facing_right:
                shield_x = x - 25 + body_offset
            else:
                shield_x = x - 25 + body_offset
                
            shield_rect = pygame.Rect(shield_x, shield_y, shield_width, shield_height)
            
            # Draw shield
            pygame.draw.rect(screen, self.shield_color, shield_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 100, 50), shield_rect, 3, border_radius=8)
            
            # Shield emblem - glowing during counter
            emblem_color = (255, 50, 50) if self.is_player1 else (50, 50, 255)
            emblem_rect = pygame.Rect(shield_x + shield_width//2 - 15, shield_y + shield_height//2 - 15, 30, 30)
            pygame.draw.rect(screen, emblem_color, emblem_rect)