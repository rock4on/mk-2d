import pygame
import math
import random

class Character:
    """Base class for all fighter characters."""
    
    def __init__(self, is_player1=True):
        self.position = (0, 0)
        self.velocity = [0, 0]
        self.health = 100
        self.is_player1 = is_player1
        self.facing_right = is_player1  # Player 1 starts facing right, Player 2 faces left
        
        self.is_jumping = False
        self.is_attacking = False
        self.is_blocking = False
        self.is_hit = False
        self.is_knocked_out = False
        self.is_walking = False
        
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        
        self.attack_damage = 10
        self.attack_type = None  # punch, kick, special
        self.attack_cooldown = 0  # Frames until next attack is allowed
        
        self.gravity = 0.8
        self.jump_strength = -15
        self.move_speed = 5
        self.floor_height = 450  # Y coordinate where the character stands
        
        # Attack combo system
        self.combo_count = 0
        self.last_successful_hit_time = 0
        self.combo_timeout = 60  # Frames to consider attacks part of same combo
        
        # Improved stun and knockback
        self.is_stunned = False
        self.stun_timer = 0
        self.knockback_force = 0
        
        # AI attributes
        self.is_ai = False
        self.ai_difficulty = 1  # 1-3, higher is more difficult
        self.ai_reaction_time = 15  # Frames before AI reacts
        self.ai_decision_timer = 0
        self.ai_current_action = None
        self.ai_target = None  # Target character to fight
        
        # Colors for simple rendering (will be replaced with sprites)
        self.body_color = (50, 100, 200) if is_player1 else (200, 50, 50)
        
        # Animation frames dict to hold different poses for each animation
        self.animation_frames = {
            "idle": 4,   # Number of frames in idle animation
            "walk": 6,   # Number of frames in walk animation
            "jump": 3,   # Number of frames in jump animation
            "punch": 3,  # Number of frames in punch animation
            "kick": 4,   # Number of frames in kick animation
            "special": 5, # Number of frames in special animation
            "hit": 2,    # Number of frames in hit animation
            "ko": 1,     # Number of frames in KO animation
            "block": 1   # Number of frames in block animation
        }
    
    def move_left(self):
        if not self.is_attacking and not self.is_knocked_out and not self.is_stunned:
            self.velocity[0] = -self.move_speed
            self.facing_right = False
            self.is_walking = True
            if self.current_animation not in ["jump", "hit"]:
                self.current_animation = "walk"
    
    def move_right(self):
        if not self.is_attacking and not self.is_knocked_out and not self.is_stunned:
            self.velocity[0] = self.move_speed
            self.facing_right = True
            self.is_walking = True
            if self.current_animation not in ["jump", "hit"]:
                self.current_animation = "walk"
    
    def jump(self):
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned:
            self.velocity[1] = self.jump_strength
            self.is_jumping = True
            self.current_animation = "jump"
            self.animation_frame = 0
    
    def punch(self):
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_type = "punch"
            self.attack_damage = 10
            self.current_animation = "punch"
            self.animation_frame = 0
            self.attack_cooldown = 15  # 15 frames until next attack
    
    def kick(self):
        if not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_type = "kick"
            self.attack_damage = 15
            self.current_animation = "kick"
            self.animation_frame = 0
            self.attack_cooldown = 20  # 20 frames until next attack
    
    def special_move(self):
        if not self.is_jumping and not self.is_attacking and not self.is_knocked_out and not self.is_stunned and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_type = "special"
            self.attack_damage = 25
            self.current_animation = "special"
            self.animation_frame = 0
            self.attack_cooldown = 30  # 30 frames until next attack
    
    def block(self):
        if not self.is_attacking and not self.is_knocked_out and not self.is_stunned:
            self.is_blocking = True
            self.current_animation = "block"
    
    def stop_block(self):
        if self.is_blocking:
            self.is_blocking = False
            self.current_animation = "idle"
    
    def take_damage(self, amount):
        # Reduced damage when blocking
        if self.is_blocking:
            amount = max(0, amount // 2)
            # Briefly show hit animation even when blocking
            self.current_animation = "hit"
            self.animation_frame = 0
            # Slight knockback when blocking
            knockback_dir = -1 if self.facing_right else 1
            self.velocity[0] += knockback_dir * 2
        else:
            self.health = max(0, self.health - amount)
            self.is_hit = True
            # Briefly stun the character
            self.is_stunned = True
            self.stun_timer = 20  # Stun for 20 frames
            # Knockback effect
            knockback_dir = -1 if self.facing_right else 1
            self.velocity[0] += knockback_dir * 5
            # Change animation
            self.current_animation = "hit"
            self.animation_frame = 0
    
    def knock_out(self):
        self.is_knocked_out = True
        self.current_animation = "ko"
        self.animation_frame = 0
        self.velocity = [0, 0]
    
    def get_attack_damage(self):
        # Add some randomness to damage
        base_damage = self.attack_damage + random.randint(-2, 2)
        
        # Increase damage for combos
        if self.combo_count > 0:
            combo_multiplier = min(1.5, 1.0 + (self.combo_count * 0.1))
            base_damage = int(base_damage * combo_multiplier)
        
        return base_damage
    
    def successful_hit(self):
        # Update combo system
        current_time = pygame.time.get_ticks()
        if current_time - self.last_successful_hit_time < self.combo_timeout * 16:  # ~1 second at 60fps
            self.combo_count += 1
        else:
            self.combo_count = 1
        
        self.last_successful_hit_time = current_time
    
    def reset(self):
        """Reset character state."""
        self.health = 100
        self.velocity = [0, 0]
        self.is_jumping = False
        self.is_attacking = False
        self.is_blocking = False
        self.is_hit = False
        self.is_knocked_out = False
        self.is_walking = False
        self.is_stunned = False
        self.stun_timer = 0
        self.current_animation = "idle"
        self.animation_frame = 0
        self.combo_count = 0
    
    def update(self):
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update stun timer
        if self.is_stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.is_stunned = False
        
        # Apply gravity
        if self.position[1] < self.floor_height:
            self.velocity[1] += self.gravity
        
        # Update position
        new_x = self.position[0] + self.velocity[0]
        new_y = min(self.floor_height, self.position[1] + self.velocity[1])
        self.position = (new_x, new_y)
        
        # Check for landing
        if self.position[1] >= self.floor_height:
            self.position = (self.position[0], self.floor_height)
            if self.is_jumping:
                self.is_jumping = False
                if not self.is_attacking and not self.is_hit and not self.is_knocked_out:
                    self.current_animation = "idle"
        
        # Apply friction
        self.velocity[0] *= 0.8
        if abs(self.velocity[0]) < 0.1:
            self.velocity[0] = 0
            self.is_walking = False
            if not self.is_jumping and not self.is_attacking and not self.is_hit and not self.is_knocked_out and not self.is_blocking and not self.is_stunned:
                self.current_animation = "idle"
        
        # Advance animation
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.animation_frame += 1
            
            # Loop or end animations appropriately
            max_frames = self.animation_frames.get(self.current_animation, 1)
            
            if self.is_attacking and self.animation_frame >= max_frames:
                self.is_attacking = False
                self.animation_frame = 0
                self.current_animation = "idle"
            
            elif self.is_hit and self.animation_frame >= max_frames:
                self.is_hit = False
                self.animation_frame = 0
                if not self.is_knocked_out and not self.is_stunned:
                    self.current_animation = "idle"
            
            # Loop idle, walk animations
            elif self.current_animation in ["idle", "walk"] and self.animation_frame >= max_frames:
                self.animation_frame = 0
            
            # Other animations just cap at max frame
            else:
                self.animation_frame = min(self.animation_frame, max_frames - 1)
        
        # Keep within screen bounds (assuming 800x600 screen)
        self.position = (
            max(50, min(750, self.position[0])),
            self.position[1]
        )
        
        # Update AI if enabled
        if self.is_ai and self.ai_target and not self.is_knocked_out:
            self._update_ai()
    
    def _update_ai(self):
        """Update AI behavior"""
        if self.is_stunned or self.is_hit or self.is_knocked_out:
            return
            
        # Decrement the decision timer
        self.ai_decision_timer -= 1
        
        # Make a new decision when timer expires
        if self.ai_decision_timer <= 0:
            # Get distance to target
            target_x = self.ai_target.position[0]
            distance = abs(target_x - self.position[0])
            direction = 1 if target_x > self.position[0] else -1
            
            # Random decision with weights based on distance and difficulty
            decision = random.random()
            
            # High chance to block when attacked
            if self.ai_target.is_attacking and distance < 100 and random.random() < 0.3 * self.ai_difficulty:
                self.block()
                self.ai_current_action = "block"
                self.ai_decision_timer = 15
                
            # When close, attack
            elif distance < 80:
                if decision < 0.4 * self.ai_difficulty:  # Punch (common)
                    self.punch()
                    self.ai_current_action = "punch"
                    self.ai_decision_timer = 30
                elif decision < 0.7 * self.ai_difficulty:  # Kick (less common)
                    self.kick()
                    self.ai_current_action = "kick"
                    self.ai_decision_timer = 35
                elif decision < 0.8 * self.ai_difficulty:  # Special (rare)
                    self.special_move()
                    self.ai_current_action = "special"
                    self.ai_decision_timer = 40
                else:  # Sometimes back away
                    self.velocity[0] = -direction * self.move_speed
                    self.facing_right = direction > 0
                    self.ai_current_action = "move_away"
                    self.ai_decision_timer = 20
                    
            # At medium distance, approach or jump
            elif distance < 200:
                if decision < 0.6:  # Move toward player
                    if direction > 0:
                        self.move_right()
                    else:
                        self.move_left()
                    self.ai_current_action = "approach"
                    self.ai_decision_timer = 15
                elif decision < 0.8 and not self.is_jumping:  # Jump
                    self.jump()
                    self.ai_current_action = "jump"
                    self.ai_decision_timer = 30
                else:  # Wait
                    self.ai_current_action = "wait"
                    self.ai_decision_timer = 10
            
            # At long distance, definitely approach
            else:
                if direction > 0:
                    self.move_right()
                else:
                    self.move_left()
                self.ai_current_action = "approach"
                self.ai_decision_timer = 25
            
            # Add reaction time variability based on difficulty
            reaction_variance = random.randint(0, 20 - self.ai_difficulty * 5)
            self.ai_decision_timer += reaction_variance
            
        # Continue current action if in progress
        elif self.ai_current_action == "approach":
            target_x = self.ai_target.position[0]
            direction = 1 if target_x > self.position[0] else -1
            if direction > 0:
                self.move_right()
            else:
                self.move_left()
                
        elif self.ai_current_action == "move_away":
            target_x = self.ai_target.position[0]
            direction = 1 if target_x > self.position[0] else -1
            if direction > 0:
                self.move_left()  # Move opposite to direction
            else:
                self.move_right()  # Move opposite to direction
                
        elif self.ai_current_action == "block":
            # Keep blocking
            self.block()
            
            # Sometimes release block if not being attacked
            if not self.ai_target.is_attacking and random.random() < 0.1:
                self.stop_block()
                self.ai_current_action = None
                self.ai_decision_timer = 5
    
    def enable_ai(self, difficulty=1, target=None):
        """Enable AI control for this character"""
        self.is_ai = True
        self.ai_difficulty = max(1, min(3, difficulty))  # Clamp between 1-3
        self.ai_target = target
        self.ai_decision_timer = 30  # Initial delay before first decision
    
    def disable_ai(self):
        """Disable AI control"""
        self.is_ai = False
    
    def render(self, screen):
        """Render the character (basic shapes for now)."""
        x, y = self.position
        
        # Different rendering based on current animation
        if self.current_animation == "idle":
            self._render_idle(screen, x, y)
        elif self.current_animation == "walk":
            self._render_walk(screen, x, y)
        elif self.current_animation == "jump":
            self._render_jump(screen, x, y)
        elif self.current_animation == "punch":
            self._render_punch(screen, x, y)
        elif self.current_animation == "kick":
            self._render_kick(screen, x, y)
        elif self.current_animation == "special":
            self._render_special(screen, x, y)
        elif self.current_animation == "hit":
            self._render_hit(screen, x, y)
        elif self.current_animation == "ko":
            self._render_ko(screen, x, y)
        elif self.current_animation == "block":
            self._render_block(screen, x, y)
        else:
            self._render_idle(screen, x, y)
            
        # Draw combo counter if active
        if self.combo_count > 1:
            combo_surf = pygame.font.Font(None, 24).render(f"{self.combo_count}x", True, (255, 220, 0))
            combo_rect = combo_surf.get_rect(center=(x, y - 120))
            screen.blit(combo_surf, combo_rect)
            
        # Draw stunned effect
        if self.is_stunned:
            stun_size = 8
            stun_radius = 20
            
            for i in range(3):
                angle = pygame.time.get_ticks() * 0.01 + i * 2.0
                stun_x = x + math.cos(angle) * stun_radius
                stun_y = y - 110 + math.sin(angle) * stun_radius
                
                pygame.draw.circle(screen, (220, 220, 0), (int(stun_x), int(stun_y)), stun_size)
    
    def _render_idle(self, screen, x, y):
        # Basic character shape - will be replaced with sprites
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Animation: breathing effect
        frame = self.animation_frame % self.animation_frames["idle"]
        breathing_offset = math.sin(frame * 0.5 + pygame.time.get_ticks() * 0.002) * 2
        
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, 
                          (head_rect.x, head_rect.y + breathing_offset, head_rect.width, head_rect.height))
        
        # Draw eyes based on facing direction
        eye_color = (255, 255, 255)
        if self.facing_right:
            pygame.draw.circle(screen, eye_color, (int(x + 5), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(x + 7), int(y - 85)), 2)
        else:
            pygame.draw.circle(screen, eye_color, (int(x - 5), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(x - 7), int(y - 85)), 2)
    
    def _render_walk(self, screen, x, y):
        # Similar to idle but with leg movement
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Walk cycle animation
        frame = self.animation_frame % self.animation_frames["walk"]
        cycle_progress = frame / (self.animation_frames["walk"] - 1)
        leg_offset = math.sin(cycle_progress * math.pi * 2) * 8
        arm_offset = -math.sin(cycle_progress * math.pi * 2) * 6
        
        # Body and head
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw legs with animation
        leg_color = (self.body_color[0] * 0.8, self.body_color[1] * 0.8, self.body_color[2] * 0.8)
        pygame.draw.rect(screen, leg_color, (int(x - 15), int(y - 20), 10, int(20 + leg_offset)))
        pygame.draw.rect(screen, leg_color, (int(x + 5), int(y - 20), 10, int(20 - leg_offset)))
        
        # Draw arms with animation
        arm_color = (self.body_color[0] * 0.9, self.body_color[1] * 0.9, self.body_color[2] * 0.9)
        arm_width = 8
        arm_length = 20
        
        # Left arm
        left_arm_x = x - 20
        left_arm_y = y - 60 + arm_offset
        pygame.draw.rect(screen, arm_color, (int(left_arm_x - arm_length), int(left_arm_y), arm_length, arm_width))
        
        # Right arm
        right_arm_x = x + 20
        right_arm_y = y - 60 - arm_offset
        pygame.draw.rect(screen, arm_color, (int(right_arm_x), int(right_arm_y), arm_length, arm_width))
        
        # Draw eyes based on facing direction
        eye_color = (255, 255, 255)
        if self.facing_right:
            pygame.draw.circle(screen, eye_color, (int(x + 5), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(x + 7), int(y - 85)), 2)
        else:
            pygame.draw.circle(screen, eye_color, (int(x - 5), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(x - 7), int(y - 85)), 2)
    
    def _render_jump(self, screen, x, y):
        # Jumping pose
        frame = self.animation_frame % self.animation_frames["jump"]
        
        # Different pose based on jump phase
        if frame == 0:  # Crouch before jump
            body_rect = pygame.Rect(x - 18, y - 50, 36, 50)
            head_rect = pygame.Rect(x - 15, y - 80, 30, 30)
        else:  # In air
            body_rect = pygame.Rect(x - 15, y - 60, 30, 60)
            head_rect = pygame.Rect(x - 15, y - 90, 30, 30)
        
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw bent legs
        leg_color = (self.body_color[0] * 0.8, self.body_color[1] * 0.8, self.body_color[2] * 0.8)
        if frame == 0:  # Crouch legs
            pygame.draw.rect(screen, leg_color, (int(x - 15), int(y - 10), 10, 10))
            pygame.draw.rect(screen, leg_color, (int(x + 5), int(y - 10), 10, 10))
        else:  # Extended legs in air
            leg_spread = 15
            pygame.draw.rect(screen, leg_color, (int(x - 20), int(y), 10, 15))
            pygame.draw.rect(screen, leg_color, (int(x + 10), int(y), 10, 15))
        
        # Draw determined eyes
        eye_color = (255, 255, 255)
        if self.facing_right:
            pygame.draw.circle(screen, eye_color, (int(x + 5), int(y - 75)), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(x + 7), int(y - 75)), 3)
        else:
            pygame.draw.circle(screen, eye_color, (int(x - 5), int(y - 75)), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(x - 7), int(y - 75)), 3)
    
    def _render_punch(self, screen, x, y):
        # Punching animation
        frame = self.animation_frame % self.animation_frames["punch"]
        
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Animate body leaning into punch
        if self.facing_right:
            body_offset_x = frame * 3
        else:
            body_offset_x = -frame * 3
        
        pygame.draw.rect(screen, self.body_color, (int(body_rect.x + body_offset_x), body_rect.y, body_rect.width, body_rect.height))
        pygame.draw.ellipse(screen, self.body_color, (int(head_rect.x + body_offset_x), head_rect.y, head_rect.width, head_rect.height))
        
        # Draw arm extended for punch based on facing direction
        arm_color = (self.body_color[0] * 0.9, self.body_color[1] * 0.9, self.body_color[2] * 0.9)
        punch_extend = min(40, frame * 20)
        
        if self.facing_right:
            pygame.draw.rect(screen, arm_color, (int(x + 10 + body_offset_x), int(y - 60), int(10 + punch_extend), 10))
            pygame.draw.circle(screen, arm_color, (int(x + 20 + punch_extend + body_offset_x), int(y - 55)), 8)
            
            # Draw impact effect on final frame
            if frame == 2:
                impact_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                impact_color = (255, 255, 100, 150)
                pygame.draw.polygon(impact_surf, impact_color, [(0, 15), (30, 0), (15, 15), (30, 30), (0, 15)])
                screen.blit(impact_surf, (int(x + 30 + punch_extend), int(y - 70)))
        else:
            pygame.draw.rect(screen, arm_color, (int(x - 20 - punch_extend + body_offset_x), int(y - 60), int(10 + punch_extend), 10))
            pygame.draw.circle(screen, arm_color, (int(x - 20 - punch_extend + body_offset_x), int(y - 55)), 8)
            
            # Draw impact effect on final frame
            if frame == 2:
                impact_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                impact_color = (255, 255, 100, 150)
                pygame.draw.polygon(impact_surf, impact_color, [(30, 15), (0, 0), (15, 15), (0, 30), (30, 15)])
                screen.blit(impact_surf, (int(x - 60 - punch_extend), int(y - 70)))
        
        # Draw determined eyes
        eye_color = (255, 255, 255)
        if self.facing_right:
            pygame.draw.circle(screen, eye_color, (int(x + 5 + body_offset_x), int(y - 85)), 5)
            pygame.draw.circle(screen, (255, 0, 0), (int(x + 7 + body_offset_x), int(y - 85)), 3)
        else:
            pygame.draw.circle(screen, eye_color, (int(x - 5 + body_offset_x), int(y - 85)), 5)
            pygame.draw.circle(screen, (255, 0, 0), (int(x - 7 + body_offset_x), int(y - 85)), 3)
    
    def _render_kick(self, screen, x, y):
        # Kicking animation
        frame = self.animation_frame % self.animation_frames["kick"]
        
        # Animate kick in phases
        if frame == 0:  # Wind up
            body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
            head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
            
            pygame.draw.rect(screen, self.body_color, body_rect)
            pygame.draw.ellipse(screen, self.body_color, head_rect)
            
            # Draw legs in pre-kick position
            leg_color = (self.body_color[0] * 0.8, self.body_color[1] * 0.8, self.body_color[2] * 0.8)
            if self.facing_right:
                pygame.draw.rect(screen, leg_color, (int(x - 10), int(y - 20), 10, 20))  # Standing leg
                pygame.draw.rect(screen, leg_color, (int(x + 5), int(y - 25), 10, 25))   # Kicking leg (bent)
            else:
                pygame.draw.rect(screen, leg_color, (int(x), int(y - 20), 10, 20))       # Standing leg
                pygame.draw.rect(screen, leg_color, (int(x - 15), int(y - 25), 10, 25))  # Kicking leg (bent)
                
        else:  # Execute kick
            # Body leans into kick
            lean_offset = 5 if self.facing_right else -5
            
            body_rect = pygame.Rect(int(x - 20 + lean_offset), y - 70, 40, 70)
            head_rect = pygame.Rect(int(x - 15 + lean_offset), y - 100, 30, 30)
            
            pygame.draw.rect(screen, self.body_color, body_rect)
            pygame.draw.ellipse(screen, self.body_color, head_rect)
            
            # Draw legs with kick extended
            leg_color = (self.body_color[0] * 0.8, self.body_color[1] * 0.8, self.body_color[2] * 0.8)
            kick_extend = min(50, (frame - 1) * 25)
            
            if self.facing_right:
                pygame.draw.rect(screen, leg_color, (int(x - 10 + lean_offset), int(y - 20), 10, 20))  # Standing leg
                pygame.draw.rect(screen, leg_color, (int(x + 10 + lean_offset), int(y - 30), int(10 + kick_extend), 10))  # Kicking leg
                pygame.draw.rect(screen, leg_color, (int(x + 10 + kick_extend + lean_offset), int(y - 30), 10, 15))  # Foot
                
                # Impact effect on mid-frames of kick
                if frame == 2:
                    impact_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                    impact_color = (255, 200, 0, 180)
                    pygame.draw.polygon(impact_surf, impact_color, [(0, 20), (40, 0), (20, 20), (40, 40), (0, 20)])
                    screen.blit(impact_surf, (int(x + 20 + kick_extend), int(y - 35)))
            else:
                pygame.draw.rect(screen, leg_color, (int(x + lean_offset), int(y - 20), 10, 20))  # Standing leg
                pygame.draw.rect(screen, leg_color, (int(x - 20 - kick_extend + lean_offset), int(y - 30), int(10 + kick_extend), 10))  # Kicking leg
                pygame.draw.rect(screen, leg_color, (int(x - 30 - kick_extend + lean_offset), int(y - 30), 10, 15))  # Foot
                
                # Impact effect on mid-frames of kick
                if frame == 2:
                    impact_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                    impact_color = (255, 200, 0, 180)
                    pygame.draw.polygon(impact_surf, impact_color, [(40, 20), (0, 0), (20, 20), (0, 40), (40, 20)])
                    screen.blit(impact_surf, (int(x - 60 - kick_extend), int(y - 35)))
        
        # Draw determined eyes
        eye_color = (255, 255, 255)
        eye_offset = 5 if self.facing_right else -5
        if frame > 0:  # During actual kick
            if self.facing_right:
                pygame.draw.circle(screen, eye_color, (int(x + 5 + eye_offset), int(y - 85)), 5)
                pygame.draw.circle(screen, (255, 0, 0), (int(x + 7 + eye_offset), int(y - 85)), 3)
            else:
                pygame.draw.circle(screen, eye_color, (int(x - 5 + eye_offset), int(y - 85)), 5)
                pygame.draw.circle(screen, (255, 0, 0), (int(x - 7 + eye_offset), int(y - 85)), 3)
        else:  # Wind up
            if self.facing_right:
                pygame.draw.circle(screen, eye_color, (int(x + 5), int(y - 85)), 5)
                pygame.draw.circle(screen, (0, 0, 0), (int(x + 7), int(y - 85)), 2)
            else:
                pygame.draw.circle(screen, eye_color, (int(x - 5), int(y - 85)), 5)
                pygame.draw.circle(screen, (0, 0, 0), (int(x - 7), int(y - 85)), 2)
    
    def _render_special(self, screen, x, y):
        # Special move animation (character-specific, this is just a general effect)
        frame = self.animation_frame % self.animation_frames["special"]
        
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Pulsing effect
        pulse = 0.8 + math.sin(frame * 0.5 + pygame.time.get_ticks() * 0.01) * 0.2
        special_color = (
            min(255, int(self.body_color[0] * 1.5 * pulse)),
            min(255, int(self.body_color[1] * 1.5 * pulse)),
            min(255, int(self.body_color[2] * 1.5 * pulse))
        )
        
        # Make character float slightly during special move
        float_offset = math.sin(frame * 0.5) * 5
        
        pygame.draw.rect(screen, special_color, (body_rect.x, int(body_rect.y - float_offset), body_rect.width, body_rect.height))
        pygame.draw.ellipse(screen, special_color, (head_rect.x, int(head_rect.y - float_offset), head_rect.width, head_rect.height))
        
        # Draw special effect (energy aura)
        effect_size = 5 + frame * 10
        effect_alpha = 150 - frame * 20
        
        # Create a surface for the aura with transparency
        aura_surf = pygame.Surface((effect_size * 2, effect_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (*special_color, effect_alpha), (effect_size, effect_size), effect_size)
        screen.blit(aura_surf, (int(x - effect_size), int(y - 70 - effect_size - float_offset)))
        
        # Draw energy waves emanating from character
        for i in range(3):
            wave_size = 50 + frame * 15 + i * 20
            wave_alpha = max(0, 150 - frame * 30 - i * 30)
            wave_surf = pygame.Surface((wave_size * 2, wave_size), pygame.SRCALPHA)
            
            wave_color = (*special_color, wave_alpha)
            pygame.draw.ellipse(wave_surf, wave_color, (0, 0, wave_size * 2, wave_size))
            
            wave_x = x - wave_size
            wave_y = y - 50 - wave_size/2 - float_offset
            screen.blit(wave_surf, (int(wave_x), int(wave_y)))
        
        # Draw glowing eyes
        eye_color = (255, 255, 255)
        glow_color = (255, 255, 0)
        if self.facing_right:
            pygame.draw.circle(screen, glow_color, (int(x + 5), int(y - 85 - float_offset)), 7)
            pygame.draw.circle(screen, eye_color, (int(x + 5), int(y - 85 - float_offset)), 5)
        else:
            pygame.draw.circle(screen, glow_color, (int(x - 5), int(y - 85 - float_offset)), 7)
            pygame.draw.circle(screen, eye_color, (int(x - 5), int(y - 85 - float_offset)), 5)
    
    def _render_hit(self, screen, x, y):
        # Hit animation - character recoils
        frame = self.animation_frame % self.animation_frames["hit"]
        
        recoil_x = (-10 if self.facing_right else 10) * (1 - frame/2)
        twist = 10 * (1 - frame/2)  # Body twist effect
        
        # Distorted body when hit
        body_points = [
            (int(x - 20 + recoil_x - twist), int(y - 70)),       # Top-left
            (int(x + 20 + recoil_x + twist), int(y - 70)),       # Top-right
            (int(x + 20 + recoil_x - twist), int(y)),            # Bottom-right
            (int(x - 20 + recoil_x + twist), int(y)),            # Bottom-left
        ]
        
        # Draw distorted body
        pygame.draw.polygon(screen, self.body_color, body_points)
        
        # Head with recoil
        head_rect = pygame.Rect(int(x - 15 + recoil_x), int(y - 100), 30, 30)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw pained expression
        eye_color = (255, 255, 255)
        if self.facing_right:
            pygame.draw.line(screen, (0, 0, 0), (int(x + recoil_x), int(y - 90)), (int(x + 10 + recoil_x), int(y - 80)), 2)
            pygame.draw.circle(screen, eye_color, (int(x + 5 + recoil_x), int(y - 85)), 5)
            pygame.draw.line(screen, (0, 0, 0), (int(x + 2 + recoil_x), int(y - 88)), (int(x + 8 + recoil_x), int(y - 82)), 2)
        else:
            pygame.draw.line(screen, (0, 0, 0), (int(x - 10 + recoil_x), int(y - 90)), (int(x + recoil_x), int(y - 80)), 2)
            pygame.draw.circle(screen, eye_color, (int(x - 5 + recoil_x), int(y - 85)), 5)
            pygame.draw.line(screen, (0, 0, 0), (int(x - 8 + recoil_x), int(y - 88)), (int(x - 2 + recoil_x), int(y - 82)), 2)
        
        # Add impact stars effect
        if frame == 0:
            for i in range(5):
                star_angle = i * 72 + pygame.time.get_ticks() * 0.1
                star_dist = 25
                star_x = x + recoil_x + math.cos(math.radians(star_angle)) * star_dist
                star_y = y - 70 + math.sin(math.radians(star_angle)) * star_dist
                
                pygame.draw.circle(screen, (255, 255, 100), (int(star_x), int(star_y)), 3)
    
    def _render_ko(self, screen, x, y):
        # Knocked out animation - character lies on ground
        body_rect = pygame.Rect(x - 35, y - 20, 70, 20)
        head_rect = pygame.Rect(x - 60 if self.facing_right else x + 30, y - 30, 30, 30)
        
        pygame.draw.ellipse(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw X eyes
        eye_offset_x = -60 if self.facing_right else 30
        
        # Eyelid effect
        eyelid_offset = math.sin(pygame.time.get_ticks() * 0.002) * 2
        
        pygame.draw.line(screen, (0, 0, 0), (int(x + eye_offset_x + 5), int(y - 35 - eyelid_offset)), (int(x + eye_offset_x + 15), int(y - 25 + eyelid_offset)), 2)
        pygame.draw.line(screen, (0, 0, 0), (int(x + eye_offset_x + 15), int(y - 35 - eyelid_offset)), (int(x + eye_offset_x + 5), int(y - 25 + eyelid_offset)), 2)
        
        pygame.draw.line(screen, (0, 0, 0), (int(x + eye_offset_x + 25), int(y - 35 - eyelid_offset)), (int(x + eye_offset_x + 35), int(y - 25 + eyelid_offset)), 2)
        pygame.draw.line(screen, (0, 0, 0), (int(x + eye_offset_x + 35), int(y - 35 - eyelid_offset)), (int(x + eye_offset_x + 25), int(y - 25 + eyelid_offset)), 2)
        
        # Draw stars spinning around head
        for i in range(6):
            star_angle = pygame.time.get_ticks() * 0.1 + i * 60
            star_radius = 25
            star_x = x + eye_offset_x + 20 + math.cos(math.radians(star_angle)) * star_radius
            star_y = y - 30 + math.sin(math.radians(star_angle)) * star_radius
            
            # Draw a small star
            pygame.draw.circle(screen, (255, 255, 0), (int(star_x), int(star_y)), 2)
    
    def _render_block(self, screen, x, y):
        # Blocking pose - arms crossed in front
        body_rect = pygame.Rect(x - 20, y - 70, 40, 70)
        head_rect = pygame.Rect(x - 15, y - 100, 30, 30)
        
        # Draw body slightly crouched
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, self.body_color, head_rect)
        
        # Draw crossed arms
        arm_color = (self.body_color[0] * 0.9, self.body_color[1] * 0.9, self.body_color[2] * 0.9)
        
        # First arm (in back)
        arm_rect1 = pygame.Rect(x - 25, y - 65, 50, 15)
        pygame.draw.rect(screen, arm_color, arm_rect1)
        
        # Second arm (in front, slightly rotated for crossing effect)
        arm_points = [
            (x - 25, y - 50),
            (x + 25, y - 50),
            (x + 20, y - 35),
            (x - 20, y - 35)
        ]
        pygame.draw.polygon(screen, arm_color, arm_points)
        
        # Shield effect
        shield_surf = pygame.Surface((60, 80), pygame.SRCALPHA)
        shield_color = (200, 200, 255, 50 + int(math.sin(pygame.time.get_ticks() * 0.01) * 20))
        pygame.draw.ellipse(shield_surf, shield_color, (0, 0, 60, 80))
        
        shield_x = x - 30
        shield_y = y - 90
        screen.blit(shield_surf, (int(shield_x), int(shield_y)))
        
        # Draw determined eyes
        eye_color = (255, 255, 255)
        if self.facing_right:
            pygame.draw.circle(screen, eye_color, (int(x + 5), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 0, 255), (int(x + 7), int(y - 85)), 3)  # Blue eyes for block
        else:
            pygame.draw.circle(screen, eye_color, (int(x - 5), int(y - 85)), 5)
            pygame.draw.circle(screen, (0, 0, 255), (int(x - 7), int(y - 85)), 3)  # Blue eyes for block