import pygame
import math
import random
from game.engine.character import Character

class Monk(Character):
    """
    Monk character - balanced stats with chi energy for special moves.
    This is an example of how to create a new character using the character template.
    """
    
    def __init__(self, is_player1=True):
        super().__init__(is_player1)
        
        # Override base class attributes
        self.health = 110        # Slightly above average health
        self.max_health = 110    # For proper scaling
        self.move_speed = 5.5    # Good mobility
        self.jump_strength = -15 # Higher jump
        self.attack_damage = 9   # Moderate base damage
        self.block_timer=0
        # Monk-specific attributes
        self.chi_energy = 100        # Chi energy for special moves
        self.max_chi_energy = 100
        self.chi_regen = 0.4         # Chi regeneration per frame
        self.meditation_active = False
        self.meditation_timer = 0
        self.combo_count = 0
        
        # Define monk's colors (player 1 and player 2 variations)
        self.body_color = (60, 80, 140) if is_player1 else (140, 60, 60)
        self.chi_color = (220, 220, 80) if is_player1 else (220, 180, 80)
        
        # Animation frames dictionary
        self.animation_frames = {
            "idle": 4,       
            "walk": 6,       
            "jump": 3,       
            "punch": 4,      # Fast multi-hit punches
            "kick": 3,       
            "special": 5,    
            "hit": 2,        
            "ko": 1,         
            "block": 2,      
            "meditate": 3    # Unique monk meditation stance
        }
    
    def punch(self):
        """Fast combo punches with increasing damage."""
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_type = "punch"
            
            # Increase damage for successive hits in combo
            self.combo_count = min(self.combo_count + 1, 3)
            self.attack_damage = 7 + (self.combo_count * 2)
            
            self.current_animation = "punch"
            self.animation_frame = 0
            self.attack_cooldown = 12  # Fast attacks
    
    def kick(self):
        """Strong roundhouse kick that costs chi energy."""
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            if self.chi_energy >= 15:
                self.chi_energy -= 15
                self.is_attacking = True
                self.attack_type = "kick"
                self.attack_damage = 18  # Strong attack
                self.current_animation = "kick"
                self.animation_frame = 0
                self.attack_cooldown = 25
                self.combo_count = 0  # Reset combo after kick
    
    def special_move(self):
        """Chi blast - powerful ranged attack that costs significant chi."""
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            if self.chi_energy >= 40:
                self.chi_energy -= 40
                self.is_attacking = True
                self.attack_type = "special"
                self.attack_damage = 22
                self.current_animation = "special"
                self.animation_frame = 0
                self.attack_cooldown = 40
                self.combo_count = 0  # Reset combo after special
    
    def block(self):
        """
        Override block to add meditation stance.
        Holding block will eventually trigger meditation for faster chi regeneration.
        """
        
        if not self.is_attacking and not self.is_knocked_out and not self.is_stunned:
            self.is_blocking = True
            
            # Check if we should enter meditation stance
            if self.block_timer > 60:  # After holding block for 1 second
                self.meditation_active = True
                self.current_animation = "meditate"
            else:
                self.current_animation = "block"
    
    def stop_block(self):
        """Override to handle exiting meditation state."""
        super().stop_block()
        self.meditation_active = False
        self.meditation_timer = 0
    
    def successful_hit(self):
        """Override to maintain combo counter."""
        super().successful_hit()
        if self.attack_type == "punch":
            # Only maintain combo for punches
            self.combo_count = min(self.combo_count + 1, 3)
        else:
            self.combo_count = 0
    
    def take_damage(self, amount):
        """Override to reset combo when taking damage."""
        result = super().take_damage(amount)
        self.combo_count = 0
        self.meditation_active = False
        return result
    
    def update(self):
        """Update character state."""
        super().update()
        
        # Reset combo if too much time passes between attacks
        if self.combo_count > 0 and not self.is_attacking:
            if self.attack_cooldown > 30:
                self.combo_count = 0
        
        # Regenerate chi energy (faster during meditation)
        if self.chi_energy < self.max_chi_energy and not self.is_knocked_out:
            regen_rate = self.chi_regen * (3 if self.meditation_active else 1)
            self.chi_energy = min(self.max_chi_energy, self.chi_energy + regen_rate)
        
        # Update meditation timer
        if self.meditation_active:
            self.meditation_timer += 1
    
def render(self, screen):
    """Custom rendering for monk character."""
    x, y = self.position
    
    # Call the parent render method first
    super().render(screen)
    
    # Add monk-specific details
    if self.current_animation not in ["hit", "ko"]:
        # Monk headband
        headband_color = (180, 180, 200) if self.is_player1 else (200, 180, 180)
        headband_rect = pygame.Rect(x - 20, y - 105, 40, 10)
        pygame.draw.rect(screen, headband_color, headband_rect)
        
        # Monk belt/sash
        sash_color = (150, 100, 50) if self.is_player1 else (100, 50, 30)
        pygame.draw.line(screen, sash_color, (x - 25, y - 60), (x + 25, y - 60), 5)
    
    # Draw chi energy bar
    if self.chi_energy < self.max_chi_energy:
        bar_width = 40
        bar_height = 5
        chi_fill = int(bar_width * (self.chi_energy / self.max_chi_energy))
        chi_bg_rect = pygame.Rect(x - bar_width//2, y - 120, bar_width, bar_height)
        chi_fill_rect = pygame.Rect(x - bar_width//2, y - 120, chi_fill, bar_height)
        
        pygame.draw.rect(screen, (30, 30, 30), chi_bg_rect)
        pygame.draw.rect(screen, self.chi_color, chi_fill_rect)
        pygame.draw.rect(screen, (200, 200, 200), chi_bg_rect, 1)
    
    # Draw combo counter if active
    if self.combo_count > 1:
        combo_text = f"{self.combo_count}x"
        combo_color = (220, 220, 80) if self.combo_count == 2 else (255, 150, 0)
        combo_surf = pygame.font.Font(None, 24).render(combo_text, True, combo_color)
        combo_rect = combo_surf.get_rect(center=(x, y - 140))
        screen.blit(combo_surf, combo_rect)
    
    # Draw meditation effects if active
    if self.meditation_active:
        # Mandala-like energy pattern
        for i in range(8):
            angle = self.meditation_timer * 0.1 + i * (2 * math.pi / 8)
            radius = 40 + math.sin(self.meditation_timer * 0.05) * 10
            
            # Outer ring particles
            particle_x = x + math.cos(angle) * radius
            particle_y = y - 60 + math.sin(angle) * radius * 0.5
            
            # Create particle surface with varying size and transparency
            particle_size = 3 + math.sin(self.meditation_timer * 0.1 + i) * 2
            particle_surf = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
            
            # Gradient particle effect
            for j in range(int(particle_size), 0, -1):
                alpha = int(150 * (j / particle_size))
                particle_color = (*self.chi_color, alpha)
                pygame.draw.circle(particle_surf, particle_color, (particle_size, particle_size), j)
            
            screen.blit(particle_surf, (particle_x - particle_size, particle_y - particle_size))
        
        # Inner energy core
        core_size = 5 + math.sin(self.meditation_timer * 0.05) * 2
        core_surf = pygame.Surface((core_size*2, core_size*2), pygame.SRCALPHA)
        core_color = (*self.chi_color, 200)
        pygame.draw.circle(core_surf, core_color, (core_size, core_size), core_size)
        screen.blit(core_surf, (x - core_size, y - 60 - core_size))
    
    # Special move charge effect
    if self.current_animation == "special":
        # Energy trail effect
        for i in range(5):
            alpha = 150 - i * 30
            trail_x = x - 20 + (10 * i if self.facing_right else -10 * i)
            trail_y = y - 60
            
            trail_surf = pygame.Surface((20, 40), pygame.SRCALPHA)
            trail_color = (*self.chi_color, alpha)
            pygame.draw.rect(trail_surf, trail_color, (0, 0, 20, 40))
            
            screen.blit(trail_surf, (trail_x, trail_y))
    
    # Low chi energy warning
    if self.chi_energy < self.max_chi_energy * 0.2:
        warning_color = (255, 50, 50, 100)
        warning_surf = pygame.Surface((40, 80), pygame.SRCALPHA)
        pygame.draw.ellipse(warning_surf, warning_color, (0, 0, 40, 80))
        screen.blit(warning_surf, (x - 20, y - 110))
    
    def _render_punch(self, screen, x, y):
        """Render monk's multi-hit punch animation."""
        # Body and head
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Determine animation frame and calculate rapid punch positions
        frame = self.animation_frame % self.animation_frames["punch"]
        
        # Draw body and head (with slight leaning forward)
        lean_amount = frame * 2
        body_x = x - 20 + (lean_amount if self.facing_right else -lean_amount)
        
        pygame.draw.rect(screen, self.body_color, (body_x, body_rect.y, body_rect.width, body_rect.height))
        pygame.draw.ellipse(screen, self.body_color, 
                          (body_x - 5 + body_rect.width//2, head_rect.y, head_rect.width, head_rect.height))
        
        # Draw multiple punch afterimages based on combo count
        num_afterimages = min(self.combo_count, 3)
        arm_width = 8
        arm_length = 25
        
        for i in range(num_afterimages):
            # Calculate random position variation for afterimages
            variation_x = random.randint(-5, 5)
            variation_y = random.randint(-5, 5)
            
            # Calculate alpha for fading effect
            alpha = 180 - i * 50
            
            # Create arm surface with transparency
            arm_surf = pygame.Surface((arm_length, arm_width), pygame.SRCALPHA)
            arm_color = (*self.body_color, alpha)
            
            # Fill the arm surface
            pygame.draw.rect(arm_surf, arm_color, (0, 0, arm_length, arm_width))
            
            # Position and draw the arm
            if self.facing_right:
                arm_x = x + 20 + variation_x
                arm_y = y - 60 + variation_y
                screen.blit(arm_surf, (arm_x, arm_y))
            else:
                # Flip the arm for left-facing
                flipped_arm = pygame.transform.flip(arm_surf, True, False)
                arm_x = x - 20 - arm_length + variation_x
                arm_y = y - 60 + variation_y
                screen.blit(flipped_arm, (arm_x, arm_y))
            
            # Add impact effect at the end of punch
            if i == 0 and frame == self.animation_frames["punch"] - 1:
                impact_x = x + 20 + arm_length if self.facing_right else x - 20 - arm_length
                impact_y = y - 60
                
                impact_color = (255, 220, 50)
                pygame.draw.circle(screen, impact_color, (impact_x, impact_y), 5 + self.combo_count * 2)
    
    def _render_kick(self, screen, x, y):
        """Render monk's roundhouse kick with chi energy."""
        # Body and head
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Determine animation frame
        frame = self.animation_frame % self.animation_frames["kick"]
        
        # Rotate body during roundhouse kick
        rotation = frame * 20  # Rotate up to 60 degrees
        
        # Draw body in rotated state
        # For simplicity, we'll just shift the body instead of properly rotating
        body_shift = frame * 5
        pygame.draw.rect(screen, self.body_color, 
                       (x - 20 + (body_shift if self.facing_right else -body_shift), 
                        body_rect.y, body_rect.width, body_rect.height))
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw kicking leg with chi energy
        leg_width = 10
        leg_length = 30 + frame * 10
        
        # Create leg surface with rotation
        leg_surf = pygame.Surface((leg_length, leg_width), pygame.SRCALPHA)
        pygame.draw.rect(leg_surf, self.body_color, (0, 0, leg_length, leg_width))
        
        # Add chi energy effect around leg
        chi_surf = pygame.Surface((leg_length, leg_width*3), pygame.SRCALPHA)
        chi_color = (*self.chi_color, 150 - frame * 30)
        pygame.draw.ellipse(chi_surf, chi_color, (0, 0, leg_length, leg_width*3))
        
        # Position and draw the leg and chi effect
        if self.facing_right:
            # Transform leg based on frame
            if frame == 0:
                # Wind up
                leg_x = x
                leg_y = y - 40
                leg_angle = -30
            elif frame == 1:
                # Mid kick
                leg_x = x + 10
                leg_y = y - 50
                leg_angle = 0
            else:
                # Full extension
                leg_x = x + 20
                leg_y = y - 60
                leg_angle = 30
                
            # Rotate leg
            rotated_leg = pygame.transform.rotate(leg_surf, leg_angle)
            rotated_chi = pygame.transform.rotate(chi_surf, leg_angle)
            
            # Position accounting for rotation
            leg_rect = rotated_leg.get_rect(center=(leg_x + leg_length//2, leg_y))
            chi_rect = rotated_chi.get_rect(center=(leg_x + leg_length//2, leg_y))
            
            # Draw chi behind leg
            screen.blit(rotated_chi, chi_rect)
            screen.blit(rotated_leg, leg_rect)
        else:
            # Transform leg based on frame for left-facing
            if frame == 0:
                # Wind up
                leg_x = x
                leg_y = y - 40
                leg_angle = 30
            elif frame == 1:
                # Mid kick
                leg_x = x - 10
                leg_y = y - 50
                leg_angle = 0
            else:
                # Full extension
                leg_x = x - 20
                leg_y = y - 60
                leg_angle = -30
                
            # Flip and rotate leg
            flipped_leg = pygame.transform.flip(leg_surf, True, False)
            flipped_chi = pygame.transform.flip(chi_surf, True, False)
            rotated_leg = pygame.transform.rotate(flipped_leg, -leg_angle)
            rotated_chi = pygame.transform.rotate(flipped_chi, -leg_angle)
            
            # Position accounting for rotation
            leg_rect = rotated_leg.get_rect(center=(leg_x - leg_length//2, leg_y))
            chi_rect = rotated_chi.get_rect(center=(leg_x - leg_length//2, leg_y))
            
            # Draw chi behind leg
            screen.blit(rotated_chi, chi_rect)
            screen.blit(rotated_leg, leg_rect)
    
    def _render_special(self, screen, x, y):
        """Render monk's chi blast special attack."""
        # Body and head
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Determine animation frame
        frame = self.animation_frame % self.animation_frames["special"]
        
        # Draw body and head
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw monk in chi blast stance
        if frame < 3:
            # Charging pose - hands together
            hand_x = x
            hand_y = y - 60
            hand_size = 12 + frame * 2
            
            # Chi orb growing between hands
            pygame.draw.circle(screen, self.chi_color, (hand_x, hand_y), hand_size)
            
            # Energy gathering effects
            for i in range(8):
                angle = self.animation_timer * 0.1 + i * 0.8
                radius = 40 - frame * 10  # Shrinking radius as energy gathers
                particle_x = x + math.cos(angle) * radius
                particle_y = y - 60 + math.sin(angle) * radius * 0.5
                particle_size = 2 + math.sin(self.animation_timer * 0.1 + i) * 1
                
                # Draw particle trail toward hands
                pygame.draw.line(screen, self.chi_color, 
                               (particle_x, particle_y), 
                               (hand_x, hand_y), 1)
                pygame.draw.circle(screen, self.chi_color, (int(particle_x), int(particle_y)), int(particle_size))
        else:
            # Release blast
            blast_width = 150
            blast_height = 40
            
            # Create beam surface with transparency
            blast_surf = pygame.Surface((blast_width, blast_height), pygame.SRCALPHA)
            
            # Draw beam with gradient
            for i in range(blast_width):
                alpha = 200 - (i / blast_width) * 150
                color = (self.chi_color[0], self.chi_color[1], self.chi_color[2], alpha)
                
                # Draw vertical line for beam
                pygame.draw.line(blast_surf, color, (i, 0), (i, blast_height))
            
            # Position based on facing direction
            if self.facing_right:
                blast_x = x + 20
                blast_y = y - 60 - blast_height/2
                screen.blit(blast_surf, (blast_x, blast_y))
            else:
                # Flip for left facing
                flipped_blast = pygame.transform.flip(blast_surf, True, False)
                blast_x = x - 20 - blast_width
                blast_y = y - 60 - blast_height/2
                screen.blit(flipped_blast, (blast_x, blast_y))
            
            # Add impact particles at end of beam
            impact_x = x + 20 + blast_width if self.facing_right else x - 20 - blast_width
            impact_y = y - 60
            
            for i in range(10):
                particle_angle = random.uniform(0, 2 * math.pi)
                particle_dist = random.uniform(5, 15)
                particle_x = impact_x + math.cos(particle_angle) * particle_dist
                particle_y = impact_y + math.sin(particle_angle) * particle_dist
                particle_size = random.randint(2, 5)
                
                pygame.draw.circle(screen, self.chi_color, (int(particle_x), int(particle_y)), particle_size)
    
    def _render_meditate(self, screen, x, y):
        """Render monk's meditation stance."""
        # Determine animation frame
        frame = self.animation_frame % self.animation_frames["meditate"]
        
        # Body in meditation pose (cross-legged)
        body_width = 40
        body_height = 50  # Shorter when sitting
        
        # Calculate floating effect
        float_offset = math.sin(self.meditation_timer * 0.05) * 3
        
        # Draw body in meditation pose
        pygame.draw.rect(screen, self.body_color, 
                      (x - body_width/2, y - body_height - float_offset, body_width, body_height))
        
        # Draw head
        pygame.draw.ellipse(screen, self.body_color, 
                          (x - 15, y - body_height - 30 - float_offset, 30, 30))
        
        # Draw crossed legs
        leg_width = 35
        leg_height = 15
        pygame.draw.ellipse(screen, self.body_color, 
                          (x - leg_width/2, y - 20 - float_offset, leg_width, leg_height))
        
        # Draw arms in meditation pose
        arm_width = 10
        arm_height = 25
        pygame.draw.rect(screen, self.body_color, 
                       (x - 30, y - 50 - float_offset, arm_width, arm_height))
        pygame.draw.rect(screen, self.body_color, 
                       (x + 20, y - 50 - float_offset, arm_width, arm_height))
        
        # Draw hands together
        hand_size = 8
        pygame.draw.circle(screen, self.body_color, 
                         (x, y - 40 - float_offset), hand_size)
        
        # Draw chi energy aura
        aura_intensity = (frame / 2) + (self.meditation_timer % 20) / 20
        aura_size = 50 + aura_intensity * 10
        
        # Create aura surface with transparency
        aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
        
        # Gradient aura effect
        for radius in range(int(aura_size), 0, -10):
            alpha = max(10, int(50 * (radius / aura_size)))
            color = (self.chi_color[0], self.chi_color[1], self.chi_color[2], alpha)
            pygame.draw.circle(aura_surf, color, (aura_size, aura_size), radius, 5)
        
        # Position and draw aura
        screen.blit(aura_surf, (x - aura_size, y - 60 - float_offset - aura_size/2))
        
        # Draw floating chi energy symbols
        num_symbols = 5
        for i in range(num_symbols):
            angle = self.meditation_timer * 0.01 + i * (2 * math.pi / num_symbols)
            symbol_distance = 30 + math.sin(self.meditation_timer * 0.05 + i) * 5
            symbol_x = x + math.cos(angle) * symbol_distance
            symbol_y = (y - 60 - float_offset) + math.sin(angle) * symbol_distance * 0.5
            
            # Simple symbol representation (small square)
            symbol_size = 4 + math.sin(self.meditation_timer * 0.1 + i) * 1
            
            # Create symbol with glow effect
            symbol_surf = pygame.Surface((symbol_size * 3, symbol_size * 3), pygame.SRCALPHA)
            glow_color = (self.chi_color[0], self.chi_color[1], self.chi_color[2], 100)
            symbol_color = (self.chi_color[0], self.chi_color[1], self.chi_color[2], 200)
            
            # Draw glow
            pygame.draw.circle(symbol_surf, glow_color, (symbol_size * 1.5, symbol_size * 1.5), symbol_size * 1.5)
            
            # Draw symbol
            pygame.draw.rect(symbol_surf, symbol_color, 
                          (symbol_size, symbol_size, symbol_size, symbol_size))
            
            # Position and draw
            screen.blit(symbol_surf, (symbol_x - symbol_size * 1.5, symbol_y - symbol_size * 1.5))
        
        # Eye effect (closed or glowing)
        if frame < 2:
            # Closed eyes - peaceful meditation
            eye_y = y - body_height - 30 - float_offset
            pygame.draw.line(screen, (0, 0, 0), (x - 8, eye_y), (x - 2, eye_y), 2)
            pygame.draw.line(screen, (0, 0, 0), (x + 2, eye_y), (x + 8, eye_y), 2)
        else:
            # Glowing eyes during deep meditation
            eye_color = self.chi_color
            eye_y = y - body_height - 30 - float_offset
            pygame.draw.circle(screen, eye_color, (x - 5, eye_y), 4)
            pygame.draw.circle(screen, eye_color, (x + 5, eye_y), 4)