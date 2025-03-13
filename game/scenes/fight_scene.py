import pygame
import random
import math
from game.engine.scene import Scene
from game.effects.weather_system import WeatherSystem
from game.effects.particle_system import EnhancedParticleSystem
from game.effects.interactive_background import InteractiveBackground
from game.effects.camera_system import CameraSystem

class FightScene(Scene):
    """Enhanced fighting scene with improved visuals and gameplay features."""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        
        # Stage backgrounds with different colors and properties
        self.stage_backgrounds = {
            "dojo": {"color": (100, 50, 50), "floor": 450, "gravity": 0.8, "weather": None},
            "forest": {"color": (40, 80, 40), "floor": 450, "gravity": 0.8, "weather": "rain"},
            "temple": {"color": (70, 70, 90), "floor": 450, "gravity": 0.8, "weather": None},
            "arena": {"color": (200, 180, 140), "floor": 450, "gravity": 0.8, "weather": None},
            "volcano": {"color": (60, 20, 20), "floor": 450, "gravity": 0.9, "weather": "sandstorm"}
        }
        
        # Round settings
        self.round_time = 60  # 60 seconds per round
        self.remaining_time = self.round_time
        self.round_started = False
        self.round_over = False
        self.round_start_time = 0
        self.round_number = 1
        self.max_rounds = 3
        self.victories = [0, 0]  # Player 1 and Player 2 victories
        
        # Visual effects systems
        self.particle_system = EnhancedParticleSystem()
        self.weather_system = WeatherSystem(self.game_engine.width, self.game_engine.height)
        self.interactive_bg = InteractiveBackground(self.game_engine.width, self.game_engine.height)
        self.camera_system = CameraSystem(self.game_engine.width, self.game_engine.height, 
                                        self.game_engine.width, self.game_engine.height)
        
        # Screen effects
        self.show_hit_effect = False
        self.hit_effect_time = 0
        self.hit_location = (0, 0)
        self.hit_strength = 0
        self.hit_type = ""  # Type of hit (punch, kick, special)
        
        # Game modes
        self.ai_enabled = True  # By default, Player 2 is AI-controlled
        self.ai_difficulty = 2  # Medium difficulty
        
        # Setup players
        self._setup_players()
        
        # Combat stats
        self.hit_counter = 0
        self.combo_counter = 0
        self.max_combo = 0
        
        # Add sound effects (placeholders - replace with actual sounds)
        self.sounds = {
            "hit": None,
            "block": None,
            "special": None,
            "ko": None,
            "round_start": None,
            "round_end": None
        }
        
        # Announcements
        self.announcements = []
        
        # Start the round
        self._start_round()
    
    # Keyboard state for smoother controls
    key_states = {
        # Player 1 controls
        pygame.K_a: False,  # Left
        pygame.K_d: False,  # Right
        pygame.K_w: False,  # Jump
        pygame.K_s: False,  # Block
        pygame.K_g: False,  # Punch
        pygame.K_h: False,  # Kick
        pygame.K_j: False,  # Special
        
        # Player 2 controls (only used if AI is disabled)
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False,
        pygame.K_KP1: False,
        pygame.K_KP2: False,
        pygame.K_KP3: False,
    }
    
    def _setup_players(self):
        """Set up initial player positions and properties."""
        # Set up player positions
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        player1.position = (200, 400)
        player2.position = (600, 400)
        player1.facing_right = True
        player2.facing_right = False
        
        # Set floor height based on stage
        stage = self.game_engine.current_stage
        if stage in self.stage_backgrounds:
            floor_height = self.stage_backgrounds[stage]["floor"]
            gravity = self.stage_backgrounds[stage]["gravity"]
            player1.floor_height = floor_height
            player2.floor_height = floor_height
            player1.gravity = gravity
            player2.gravity = gravity
        
        # Enable AI for player 2 if AI mode is on
        if self.ai_enabled:
            player2.enable_ai(self.ai_difficulty, player1)
        
        # Set up weather for the current stage
        if stage in self.stage_backgrounds and self.stage_backgrounds[stage]["weather"]:
            weather_type = self.stage_backgrounds[stage]["weather"]
            self.weather_system.set_weather(weather_type, 0.7)
        
        # Generate interactive background elements
        self.interactive_bg.generate_elements(stage)
    
    def _start_round(self):
        """Start a new round with enhanced effects."""
        self.round_started = False
        self.round_over = False
        self.remaining_time = self.round_time
        
        # Get stage info
        stage = self.game_engine.current_stage
        floor_height = self.stage_backgrounds[stage]["floor"] if stage in self.stage_backgrounds else 450
        gravity = self.stage_backgrounds[stage]["gravity"] if stage in self.stage_backgrounds else 0.8
        
        # Reset player health
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        # Set original health based on character
        player1.health = player1.max_health
        player2.health = player2.max_health
        
        # Reset player positions
        player1.position = (200, floor_height)
        player2.position = (600, floor_height)
        
        # Set floor height and gravity for stage
        player1.floor_height = floor_height
        player2.floor_height = floor_height
        player1.gravity = gravity
        player2.gravity = gravity
        
        # Reset player states
        player1.reset()
        player2.reset()
        
        # Set up AI targeting
        if self.ai_enabled:
            player2.enable_ai(self.ai_difficulty, player1)
        else:
            player2.disable_ai()
        
        # Reset combat stats
        self.hit_counter = 0
        self.combo_counter = 0
        self.max_combo = 0
        
        # Clear particles and effects
        self.particle_system = EnhancedParticleSystem()
        self.announcements = []
        
        # Reset camera
        self.camera_system = CameraSystem(self.game_engine.width, self.game_engine.height, 
                                        self.game_engine.width, self.game_engine.height)
        
        # Add "Round X" announcement
        self.announcements.append({
            "text": f"ROUND {self.round_number}",
            "color": (255, 220, 50),
            "size": "large",
            "position": (self.game_engine.width // 2, self.game_engine.height // 2),
            "timer": 120,  # Frames to display
            "scale": 1.0
        })
        
        # Add "FIGHT!" announcement with delay
        self.announcements.append({
            "text": "FIGHT!",
            "color": (255, 50, 50),
            "size": "large",
            "position": (self.game_engine.width // 2, self.game_engine.height // 2 + 60),
            "timer": 30,  # Shorter display time
            "delay": 60,  # Delay before showing
            "scale": 1.0
        })
        
        # Set up weather for the current stage
        if stage in self.stage_backgrounds and self.stage_backgrounds[stage]["weather"]:
            weather_type = self.stage_backgrounds[stage]["weather"]
            self.weather_system.set_weather(weather_type, 0.7)
        
        # Generate fresh interactive background elements
        self.interactive_bg.generate_elements(stage)
        
        # Add special round start camera effect
        self.camera_system.add_zoom_pulse(0.1, 45)
        
        # Start after a short delay
        pygame.time.set_timer(pygame.USEREVENT, 2000, 1)  # Trigger once after 2 seconds
    
    def handle_event(self, event):
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        if event.type == pygame.USEREVENT:
            self.round_started = True
            self.round_start_time = pygame.time.get_ticks()
            # Camera zoom effect when fight starts
            self.camera_system.add_zoom_pulse(0.15, 30)
            
        elif event.type == pygame.KEYDOWN:
            # Update key states for smooth movement
            if event.key in self.key_states:
                self.key_states[event.key] = True
            
            # Handle immediate responses like toggling AI
            if event.key == pygame.K_t and self.round_started and not self.round_over:
                # Toggle AI on/off for player 2
                self.ai_enabled = not self.ai_enabled
                if self.ai_enabled:
                    player2.enable_ai(self.ai_difficulty, player1)
                else:
                    player2.disable_ai()
                
                # Show AI toggle announcement
                self.announcements.append({
                    "text": f"AI: {'ON' if self.ai_enabled else 'OFF'}",
                    "color": (100, 255, 100) if self.ai_enabled else (255, 100, 100),
                    "size": "medium",
                    "position": (self.game_engine.width // 2, 100),
                    "timer": 60,
                    "scale": 1.0
                })
            
            elif event.key == pygame.K_y and self.round_started and not self.round_over:
                # Cycle AI difficulty
                self.ai_difficulty = (self.ai_difficulty % 3) + 1
                if self.ai_enabled:
                    player2.enable_ai(self.ai_difficulty, player1)
                
                # Show AI difficulty announcement
                self.announcements.append({
                    "text": f"AI DIFFICULTY: {self.ai_difficulty}",
                    "color": (100, 200, 100),
                    "size": "medium",
                    "position": (self.game_engine.width // 2, 100),
                    "timer": 60,
                    "scale": 1.0
                })
            
            elif event.key == pygame.K_SPACE and self.round_over:
                # Space to continue after round end
                if self.round_number < self.max_rounds and max(self.victories) < (self.max_rounds // 2 + 1):
                    self.round_number += 1
                    self._start_round()
                else:
                    # Game over - show results - import here to avoid circular import
                    from game.scenes.game_over_scene import GameOverScene
                    winner = 1 if self.victories[0] > self.victories[1] else 2
                    self.game_engine.change_scene(GameOverScene(self.game_engine, winner))
            
            # Weather toggle for testing (would be removed in production)
            elif event.key == pygame.K_w and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Cycle through weather types
                weather_types = [None, "rain", "snow", "sandstorm"]
                current_idx = 0
                if self.weather_system.weather_type in weather_types:
                    current_idx = weather_types.index(self.weather_system.weather_type)
                next_idx = (current_idx + 1) % len(weather_types)
                
                if weather_types[next_idx]:
                    self.weather_system.set_weather(weather_types[next_idx], 0.7)
                else:
                    self.weather_system.weather_type = None
                    self.weather_system.particles = []
        
        elif event.type == pygame.KEYUP:
            # Update key states for smooth movement
            if event.key in self.key_states:
                self.key_states[event.key] = False
                
                # Special handling for block release
                if event.key == pygame.K_s:
                    player1.stop_block()
                if not self.ai_enabled and event.key == pygame.K_DOWN:
                    player2.stop_block()
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Only update core gameplay if round is active
        if self.round_started and not self.round_over:
            self._update_gameplay(current_time)
        
        # Always update visual systems, even during intro/outro
        self._update_visual_systems(current_time)
        
        # Update announcements
        self._update_announcements()
        
        # Update hit effect timer
        if self.show_hit_effect:
            if current_time - self.hit_effect_time > 300:  # Show for 300ms
                self.show_hit_effect = False
    
    def _update_gameplay(self, current_time):
        """Update core gameplay elements."""
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        # Handle continuous key presses for smooth movement
        self._handle_key_states()
        
        # Update the remaining time
        elapsed_seconds = (current_time - self.round_start_time) // 1000
        self.remaining_time = max(0, self.round_time - elapsed_seconds)
        
        # Check if time is up
        if self.remaining_time <= 0:
            self._end_round()
            return
        
        # Update player states
        player1.update()
        player2.update()
        
        # Add footstep particles when players move
        if abs(player1.velocity[0]) > 0.5 and not player1.is_jumping and random.random() < 0.1:
            self.particle_system.add_footstep((player1.position[0], player1.position[1]))
            
        if abs(player2.velocity[0]) > 0.5 and not player2.is_jumping and random.random() < 0.1:
            self.particle_system.add_footstep((player2.position[0], player2.position[1]))
        
        # Check for collisions/attacks
        if player1.is_attacking and not player2.is_knocked_out:
            if self._check_hit(player1, player2):
                damage = player1.get_attack_damage()
                hit_successful = player2.take_damage(damage)
                
                if hit_successful:
                    # Hit connected
                    player1.successful_hit()  # Update combo
                    self.hit_counter += 1
                    self.combo_counter += 1
                    self.max_combo = max(self.max_combo, self.combo_counter)
                    
                    # Show hit effect with appropriate type
                    self._show_hit(player2.position, damage, player1.attack_type)
                    
                    # Add hit particles
                    self._add_hit_particles(player2.position, damage, player1.attack_type, 
                                          player1.facing_right)
                    
                    # Camera impact effect based on damage
                    impact_intensity = min(2.0, damage / 10)
                    self.camera_system.add_impact_effect(player2.position, impact_intensity)
                    
                    # Show combo announcement for good combos
                    if self.combo_counter >= 3:
                        self.announcements.append({
                            "text": f"{self.combo_counter}x COMBO!",
                            "color": (255, 220, 50),
                            "size": "medium",
                            "position": (self.game_engine.width // 2, 150),
                            "timer": 60,
                            "scale": 1.0
                        })
                else:
                    # Hit was blocked
                    self.combo_counter = 0  # Reset combo on block
                    self._show_block_effect(player2.position)
                    
                    # Small camera shake
                    self.camera_system.add_shake(1.0)
                
                # Check if knocked out
                if player2.health <= 0:
                    player2.knock_out()
                    self._show_knockout_effect(player2.position)
                    self._end_round()
        
        if player2.is_attacking and not player1.is_knocked_out:
            if self._check_hit(player2, player1):
                damage = player2.get_attack_damage()
                hit_successful = player1.take_damage(damage)
                
                if hit_successful:
                    # Hit connected
                    player2.successful_hit()  # Update combo
                    self.hit_counter += 1
                    
                    # Show hit effect with appropriate type
                    self._show_hit(player1.position, damage, player2.attack_type)
                    
                    # Add hit particles
                    self._add_hit_particles(player1.position, damage, player2.attack_type, 
                                          player2.facing_right)
                    
                    # Camera impact effect based on damage
                    impact_intensity = min(2.0, damage / 10)
                    self.camera_system.add_impact_effect(player1.position, impact_intensity)
                else:
                    # Hit was blocked
                    self._show_block_effect(player1.position)
                    
                    # Small camera shake
                    self.camera_system.add_shake(1.0)
                
                # Check if knocked out
                if player1.health <= 0:
                    player1.knock_out()
                    self._show_knockout_effect(player1.position)
                    self._end_round()
    
    def _update_visual_systems(self, current_time):
        """Update all visual effects systems."""
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        # Update weather effects
        if self.weather_system.weather_type:
            self.weather_system.update()
        
        # Update interactive background elements
        self.interactive_bg.update(player1.position, player2.position, current_time)
        
        # Update particle system
        self.particle_system.update()
        
        # Update camera system
        self.camera_system.update(player1.position, player2.position, self.round_started, self.round_over)
    
    def _update_announcements(self):
        """Update text announcements."""
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
    
    def _check_hit(self, attacker, defender):
        """Check if an attack hits with improved hitbox detection."""
        # Define hitboxes based on character state
        attacker_rect = pygame.Rect(
            attacker.position[0] - 20, 
            attacker.position[1] - 100,
            40, 100
        )
        
        defender_rect = pygame.Rect(
            defender.position[0] - 20, 
            defender.position[1] - 100,
            40, 100
        )
        
        # Create attack hitbox based on attack type and facing direction
        attack_rect = None
        attack_color = (255, 200, 0, 100)  # Default attack effect color
        
        if attacker.attack_type == "punch":
            # Punch has medium range
            if attacker.facing_right:
                attack_rect = pygame.Rect(
                    attacker.position[0] + 10,
                    attacker.position[1] - 60,
                    40, 40
                )
            else:
                attack_rect = pygame.Rect(
                    attacker.position[0] - 50,
                    attacker.position[1] - 60,
                    40, 40
                )
                
        elif attacker.attack_type == "kick":
            # Kick has longer range
            if attacker.facing_right:
                attack_rect = pygame.Rect(
                    attacker.position[0] + 10,
                    attacker.position[1] - 40,
                    60, 30
                )
            else:
                attack_rect = pygame.Rect(
                    attacker.position[0] - 70,
                    attacker.position[1] - 40,
                    60, 30
                )
                
        elif attacker.attack_type == "special":
            # Special has area effect
            radius = 70
            attack_rect = pygame.Rect(
                attacker.position[0] - radius,
                attacker.position[1] - radius,
                radius * 2, radius * 2
            )
            attack_color = (100, 200, 255, 100)  # Different color for special
        
        # Check if attack hitbox intersects with defender's body
        if attack_rect and attack_rect.colliderect(defender_rect):
            # If defender is blocking, check if they're facing the right way
            if defender.is_blocking:
                is_block_effective = (defender.facing_right and attacker.position[0] < defender.position[0]) or \
                                    (not defender.facing_right and attacker.position[0] > defender.position[0])
                # Still register a hit (for effects) but damage reduction happens in take_damage()
                return True
            return True
            
        return False
    
    def _show_hit(self, position, damage, hit_type):
        """Show an enhanced hit effect at the given position with type-specific visuals."""
        self.show_hit_effect = True
        self.hit_effect_time = pygame.time.get_ticks()
        self.hit_location = position
        self.hit_strength = damage  # Used for scaling hit effect
        self.hit_type = hit_type    # Type of hit for different visuals
    
    def _show_block_effect(self, position):
        """Show a block effect."""
        # Add block particles
        for i in range(10):
            angle = random.uniform(0, math.pi)  # Semicircle in front
            speed = random.uniform(1, 3)
            size = random.randint(3, 6)
            
            self.particle_system.particles.append({
                "type": "dust",
                "x": position[0],
                "y": position[1] - 50,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 1,  # Upward bias
                "color": (200, 200, 255),
                "size": size,
                "life": random.randint(10, 20),
                "alpha": 200,
                "fade_speed": random.uniform(5, 10),
                "gravity": False
            })
        
        # Add "BLOCK" announcement
        self.announcements.append({
            "text": "BLOCK!",
            "color": (100, 100, 255),
            "size": "small",
            "position": (position[0], position[1] - 100),
            "timer": 20,
            "scale": 1.0
        })
    
    def _show_knockout_effect(self, position):
        """Show a knockout effect."""
        # Add big screen shake
        self.camera_system.add_shake(15)
        
        # Add KO particles - stars and impact lines
        for i in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            size = random.randint(3, 8)
            
            self.particle_system.particles.append({
                "type": "explosion",
                "x": position[0],
                "y": position[1] - 50,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 2,  # Upward bias
                "color": (255, 255, 100),
                "size": size,
                "life": random.randint(30, 60),
                "alpha": 255,
                "fade_speed": random.uniform(2, 4),
                "gravity": True,
                "rotation": random.uniform(0, 360),
                "rotation_speed": random.uniform(-5, 5)
            })
        
        # Add explosion effect
        self.particle_system.add_explosion(position, color=(255, 200, 50), size=50, particle_count=30)
        
        # Add "K.O.!" announcement
        self.announcements.append({
            "text": "K.O.!",
            "color": (255, 50, 50),
            "size": "large",
            "position": (self.game_engine.width // 2, self.game_engine.height // 2),
            "timer": 120,
            "scale": 1.0
        })
        
        # Add dramatic camera effects
        self.camera_system.add_zoom_pulse(0.2, 60)
    
    def _add_hit_particles(self, position, damage, hit_type, facing_right):
        """Add particles based on hit type and damage."""
        num_particles = min(int(damage), 20)  # More particles for stronger hits
        
        # Determine direction based on facing
        dir_x = 1 if facing_right else -1
        
        if hit_type == "punch":
            # Simple impact particles
            self.particle_system.add_explosion(position, color=(255, 200, 100), size=damage * 0.8, particle_count=num_particles)
            
            # Add small sweat particles
            for i in range(num_particles // 2):
                angle = random.uniform(-0.5, 0.5) + (0 if facing_right else math.pi)
                speed = random.uniform(1, 3)
                size = random.randint(2, 4)
                
                self.particle_system.particles.append({
                    "type": "dust",
                    "x": position[0],
                    "y": position[1] - 50 + random.uniform(-20, 20),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed - 0.5,
                    "color": (220, 220, 255),
                    "size": size,
                    "life": random.randint(10, 20),
                    "alpha": 200,
                    "fade_speed": random.uniform(5, 10),
                    "gravity": False
                })
                
        elif hit_type == "kick":
            # More forceful particles
            self.particle_system.add_explosion(position, color=(255, 150, 50), size=damage, particle_count=num_particles)
            
            # Add energy trail
            self.particle_system.add_energy_trail(position, color=(255, 180, 50), 
                                              size=damage * 0.6, dir=(dir_x, 0), 
                                              particle_count=num_particles // 2)
                
        elif hit_type == "special":
            # Elemental effect particles based on character type
            char_class = self.game_engine.player1_character.__class__.__name__
            
            # Different effects based on character class
            if char_class == "Wizard":
                # Magical elemental particles
                color = (100, 200, 255)  # Blue for magic
                self.particle_system.add_explosion(position, color=color, size=damage * 1.2, particle_count=num_particles * 2)
                
                # Add additional magical energy
                for i in range(num_particles * 2):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(1, 5)
                    size = random.randint(4, 8)
                    
                    self.particle_system.particles.append({
                        "type": "energy",
                        "x": position[0] + random.uniform(-20, 20),
                        "y": position[1] - 50 + random.uniform(-20, 20),
                        "vx": math.cos(angle) * speed,
                        "vy": math.sin(angle) * speed - 1,  # Upward bias
                        "color": (100, 200, 255) if random.random() < 0.6 else (255, 255, 255),
                        "size": size,
                        "size_change": random.uniform(-0.1, 0.1),  # Shrink or grow
                        "life": random.randint(20, 40),
                        "alpha": 200,
                        "fade_speed": random.uniform(3, 6),
                        "gravity": False,
                        "pulse": random.uniform(0, math.pi)
                    })
                
            elif char_class == "Guardian":
                # Heavy impact particles
                color = (255, 220, 100)  # Gold for guardian
                self.particle_system.add_explosion(position, color=color, size=damage * 1.5, particle_count=num_particles * 2)
                
                # Add shockwave
                for radius in range(20, 60, 10):
                    wave_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    alpha = max(0, 150 - radius * 2)
                    pygame.draw.circle(wave_surf, (*color, alpha), (radius, radius), radius, 3)
                    screen_pos = self.camera_system.get_world_to_screen_coords(position)
                    screen_pos = (screen_pos[0] - radius, screen_pos[1] - 50 - radius)
                    self.game_engine.screen.blit(wave_surf, screen_pos)
                
            elif char_class == "Ninja":
                # Fast, sharp particles
                color = (200, 100, 255)  # Purple for ninja
                
                # Add shadow trail
                for i in range(5):
                    offset_x = -i * 15 * dir_x
                    alpha = max(0, 150 - i * 30)
                    
                    shadow_surf = pygame.Surface((40, 70), pygame.SRCALPHA)
                    shadow_color = (*color, alpha)
                    pygame.draw.ellipse(shadow_surf, shadow_color, (0, 0, 40, 70))
                    
                    screen_pos = self.camera_system.get_world_to_screen_coords(position)
                    screen_pos = (screen_pos[0] - 20 + offset_x, screen_pos[1] - 85)
                    self.game_engine.screen.blit(shadow_surf, screen_pos)
                
                # Add sharp particle slashes
                for i in range(num_particles):
                    angle = random.uniform(-0.5, 0.5) + (0 if facing_right else math.pi)
                    speed = random.uniform(3, 7)
                    size = random.randint(5, 10)
                    
                    self.particle_system.particles.append({
                        "type": "energy",
                        "x": position[0],
                        "y": position[1] - 50 + random.uniform(-20, 20),
                        "vx": math.cos(angle) * speed,
                        "vy": math.sin(angle) * speed,
                        "color": color,
                        "size": size,
                        "size_change": -0.2,  # Shrink quickly
                        "life": random.randint(10, 20),
                        "alpha": 230,
                        "fade_speed": random.uniform(8, 12),
                        "gravity": False
                    })
                
            elif char_class == "Samurai":
                # Slashing, fiery particles
                color = (255, 100, 50)  # Orange-red for samurai
                
                # Add slash effect
                slash_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                slash_angle = 45 if facing_right else 135
                slash_rect = pygame.Rect(0, 0, 100, 100)
                pygame.draw.arc(slash_surf, color, slash_rect, 
                              math.radians(slash_angle - 30), math.radians(slash_angle + 30), 
                              10)
                
                screen_pos = self.camera_system.get_world_to_screen_coords(position)
                screen_pos = (screen_pos[0] - 50, screen_pos[1] - 100)
                self.game_engine.screen.blit(slash_surf, screen_pos)
                
                # Add fire particles
                for i in range(num_particles * 2):
                    angle = random.uniform(-0.3, 0.3) + (0 if facing_right else math.pi)
                    speed = random.uniform(2, 6)
                    size = random.randint(4, 8)
                    
                    self.particle_system.particles.append({
                        "type": "explosion",
                        "x": position[0],
                        "y": position[1] - 50 + random.uniform(-10, 10),
                        "vx": math.cos(angle) * speed,
                        "vy": math.sin(angle) * speed - random.uniform(0, 2),
                        "color": (255, 100 + random.randint(0, 100), 0),
                        "size": size,
                        "life": random.randint(15, 30),
                        "alpha": 200,
                        "fade_speed": random.uniform(5, 10),
                        "gravity": True,
                        "rotation": random.uniform(0, 360),
                        "rotation_speed": random.uniform(-10, 10)
                    })
            
            else:
                # Generic special effect for other characters
                self.particle_system.add_explosion(position, color=(200, 200, 255), size=damage * 1.2, particle_count=num_particles * 2)
            
            # Add "SPECIAL!" announcement for big hits
            if damage > 15:
                self.announcements.append({
                    "text": "SPECIAL!",
                    "color": (100, 200, 255),
                    "size": "medium",
                    "position": (position[0], position[1] - 100),
                    "timer": 30,
                    "scale": 1.0
                })
    
    def _end_round(self):
        """End the current round."""
        self.round_over = True
        
        # Determine round winner
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        # Add winner announcement
        winner_text = ""
        winner_color = (255, 220, 50)
        
        if player1.health > player2.health:
            self.victories[0] += 1
            winner_text = "PLAYER 1 WINS!"
            winner_color = (100, 100, 255)
        elif player2.health > player1.health:
            self.victories[1] += 1
            winner_text = "PLAYER 2 WINS!" 
            winner_color = (255, 100, 100)
        else:
            # It's a tie, both get a point
            self.victories[0] += 1
            self.victories[1] += 1
            winner_text = "DRAW!"
            winner_color = (200, 200, 200)
        
        # Add round end announcement
        self.announcements.append({
            "text": winner_text,
            "color": winner_color,
            "size": "large",
            "position": (self.game_engine.width // 2, self.game_engine.height // 2),
            "timer": 180,
            "scale": 1.0
        })
        
        # Add continue prompt
        if self.round_number < self.max_rounds and max(self.victories) < (self.max_rounds // 2 + 1):
            continue_text = "Press SPACE for next round"
        else:
            continue_text = "Press SPACE to continue"
            
        self.announcements.append({
            "text": continue_text,
            "color": (200, 200, 200),
            "size": "small",
            "position": (self.game_engine.width // 2, self.game_engine.height // 2 + 80),
            "timer": 180,
            "delay": 60,  # Show after a delay
            "scale": 1.0
        })
        
        # Add victory confetti particles
        for i in range(100):
            x = random.randint(0, self.game_engine.width)
            y = -10  # Start above screen
            
            self.particle_system.particles.append({
                "type": "explosion",
                "x": x,
                "y": y,
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(1, 3),
                "color": winner_color if random.random() < 0.5 else (255, 220, 50),
                "size": random.randint(3, 6),
                "life": random.randint(120, 180),
                "alpha": 255,
                "fade_speed": random.uniform(1, 2),
                "gravity": True,
                "rotation": random.uniform(0, 360),
                "rotation_speed": random.uniform(-2, 2)
            })
            
        # Add dramatic camera effects
        self.camera_system.add_zoom_pulse(0.15, 90)
    
    def _handle_key_states(self):
        """Handle continuous key presses for smoother controls"""
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        # Player 1 controls
        if not player1.is_knocked_out:
            # Movement
            if self.key_states[pygame.K_a]:
                player1.move_left()
            elif self.key_states[pygame.K_d]:
                player1.move_right()
                
            # Jumping - only trigger once
            if self.key_states[pygame.K_w]:
                if not player1.is_jumping:
                    player1.jump()
                    self.key_states[pygame.K_w] = False  # Require key re-press
            
            # Blocking - continuous
            if self.key_states[pygame.K_s]:
                player1.block()
            
            # Attacks - only trigger once per press
            if self.key_states[pygame.K_g]:
                player1.punch()
                self.key_states[pygame.K_g] = False  # Require key re-press
            
            elif self.key_states[pygame.K_h]:
                player1.kick()
                self.key_states[pygame.K_h] = False  # Require key re-press
            
            elif self.key_states[pygame.K_j]:
                player1.special_move()
                self.key_states[pygame.K_j] = False  # Require key re-press
        
        # Player 2 controls - only if AI is disabled
        if not self.ai_enabled and not player2.is_knocked_out:
            # Movement
            if self.key_states[pygame.K_LEFT]:
                player2.move_left()
            elif self.key_states[pygame.K_RIGHT]:
                player2.move_right()
                
            # Jumping - only trigger once
            if self.key_states[pygame.K_UP]:
                if not player2.is_jumping:
                    player2.jump()
                    self.key_states[pygame.K_UP] = False  # Require key re-press
            
            # Blocking - continuous
            if self.key_states[pygame.K_DOWN]:
                player2.block()
            
            # Attacks - only trigger once per press
            if self.key_states[pygame.K_KP1]:
                player2.punch()
                self.key_states[pygame.K_KP1] = False  # Require key re-press
            
            elif self.key_states[pygame.K_KP2]:
                player2.kick()
                self.key_states[pygame.K_KP2] = False  # Require key re-press
            
            elif self.key_states[pygame.K_KP3]:
                player2.special_move()
                self.key_states[pygame.K_KP3] = False  # Require key re-press
    
    def render(self, screen):
        """Render the enhanced fight scene with all visual effects."""
        # Create a world surface that we'll apply camera effects to
        world_surface = pygame.Surface((self.game_engine.width, self.game_engine.height))
        
        # Get the background for the current stage
        stage = self.game_engine.current_stage
        bg_color = self.stage_backgrounds.get(stage, {"color": (0, 0, 0)})["color"]
        world_surface.fill(bg_color)
        
        # Draw stage background
        self._draw_stage(world_surface)
        
        # Draw weather effects (background layer)
        if self.weather_system.weather_type:
            self.weather_system.render(world_surface)
        
        # Draw interactive background elements
        self.interactive_bg.render(world_surface)
        
        # Draw the ground
        ground_rect = pygame.Rect(0, 450, self.game_engine.width, 150)
        pygame.draw.rect(world_surface, (60, 40, 20), ground_rect)
        
        # Draw players
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        player1.render(world_surface)
        player2.render(world_surface)
        
        # Draw hit effect
        if self.show_hit_effect:
            self._draw_hit_effect(world_surface)
        
        # Draw all particles
        self.particle_system.render(world_surface)
        
        # Apply camera transformations (shake, zoom, etc.)
        final_view = self.camera_system.apply_to_surface(world_surface)
        
        # Blit the transformed view to the screen
        screen.blit(final_view, (0, 0))
        
        # Draw UI elements (these aren't affected by camera)
        self._draw_ui(screen)
        
        # Draw announcements (these aren't affected by camera)
        self._draw_announcements(screen)
    
    def _draw_stage(self, screen):
        """Draw an enhanced stage background for the current stage."""
        stage = self.game_engine.current_stage
        
        if stage == "dojo":
            # Draw wooden wall with detailed texturing
            wall_color = (120, 80, 40)
            pygame.draw.rect(screen, wall_color, (0, 0, self.game_engine.width, 450))
            
            # Draw wall panels with wood grain effect
            panel_color = (140, 100, 50)
            for x in range(0, self.game_engine.width, 100):
                pygame.draw.rect(screen, panel_color, (x, 50, 80, 400))
                
                # Add wood grain lines
                darker_color = (120, 85, 40)
                for i in range(5):
                    line_x = x + 10 + i * 15
                    pygame.draw.line(screen, darker_color, (line_x, 50), (line_x, 450), 1)
            
            # Draw decorative elements
            # Banner
            banner_rect = pygame.Rect(200, 100, 400, 100)
            pygame.draw.rect(screen, (150, 20, 20), banner_rect)
            pygame.draw.rect(screen, (100, 10, 10), banner_rect, 2)
            
            # Kanji or symbol in center of banner
            symbol_rect = pygame.Rect(370, 130, 60, 40)
            pygame.draw.rect(screen, (0, 0, 0), symbol_rect)
            
            # Door
            door_rect = pygame.Rect(350, 220, 100, 230)
            pygame.draw.rect(screen, (20, 20, 20), door_rect)
            
        elif stage == "forest":
            # Sky with gradient
            sky_rect = pygame.Rect(0, 0, self.game_engine.width, 200)
            pygame.draw.rect(screen, (100, 150, 255), sky_rect)
            
            # Add sun
            pygame.draw.circle(screen, (255, 240, 200), (600, 80), 40)
            
            # Distant mountains
            mountain_color = (70, 100, 70)
            mountain_points = [
                (0, 200),
                (200, 120),
                (350, 180),
                (500, 100),
                (700, 150),
                (self.game_engine.width, 180),
                (self.game_engine.width, 200)
            ]
            pygame.draw.polygon(screen, mountain_color, mountain_points)
            
            # Ground
            ground_color = (50, 100, 50)
            pygame.draw.rect(screen, ground_color, (0, 200, self.game_engine.width, 250))
            
            # Add some grass details
            for x in range(0, self.game_engine.width, 30):
                grass_height = random.randint(5, 15)
                grass_color = (30, 120, 30)
                pygame.draw.rect(screen, grass_color, (x, 450 - grass_height, 10, grass_height))
            
        elif stage == "temple":
            # Sky with atmospheric perspective
            sky_color = (60, 60, 100)
            pygame.draw.rect(screen, sky_color, (0, 0, self.game_engine.width, 450))
            
            # Add some distant clouds
            for i in range(3):
                cloud_x = (i * 300 + pygame.time.get_ticks() // 100) % self.game_engine.width
                cloud_y = 100 + i * 30
                cloud_width = 100 + i * 50
                cloud_height = 30 + i * 10
                cloud_color = (200, 200, 220, 100)
                
                cloud_surf = pygame.Surface((cloud_width, cloud_height), pygame.SRCALPHA)
                pygame.draw.ellipse(cloud_surf, cloud_color, (0, 0, cloud_width, cloud_height))
                screen.blit(cloud_surf, (cloud_x - cloud_width // 2, cloud_y - cloud_height // 2))
            
            # Temple structure in background
            pygame.draw.rect(screen, (180, 180, 200), (150, 100, 500, 350))
            
            # Temple roof
            roof_points = [
                (100, 100),
                (700, 100),
                (600, 50),
                (200, 50)
            ]
            pygame.draw.polygon(screen, (100, 100, 120), roof_points)
            
            # Add some mystic energy effect at altar
            glow_radius = 50 + math.sin(pygame.time.get_ticks() * 0.002) * 10
            glow_alpha = 50 + int(math.sin(pygame.time.get_ticks() * 0.002) * 20)
            glow_surf = pygame.Surface((int(glow_radius * 2), int(glow_radius)), pygame.SRCALPHA)
            glow_color = (160, 120, 255, glow_alpha)
            pygame.draw.ellipse(glow_surf, glow_color, (0, 0, int(glow_radius * 2), int(glow_radius)))
            screen.blit(glow_surf, (400 - glow_radius, 400 - glow_radius // 2))
            
        elif stage == "arena":
            # Sandy background
            pygame.draw.rect(screen, (200, 180, 140), (0, 0, self.game_engine.width, 450))
            
            # Draw arena circle
            arena_center = (self.game_engine.width // 2, 450)
            arena_radius = 300
            pygame.draw.circle(screen, (180, 160, 120), arena_center, arena_radius)
            
            # Draw arena line markers
            pygame.draw.circle(screen, (160, 140, 100), arena_center, arena_radius - 20, 2)
            pygame.draw.circle(screen, (160, 140, 100), arena_center, arena_radius - 100, 2)
            
            # Draw center marking
            pygame.draw.circle(screen, (160, 140, 100), arena_center, 30, 2)
            
            # Draw pillars at corners of screen
            pillar_positions = [(50, 150), (750, 150), (50, 350), (750, 350)]
            for pos in pillar_positions:
                pygame.draw.rect(screen, (170, 150, 110), (pos[0] - 20, pos[1] - 100, 40, 200))
                # Pillar capital
                pygame.draw.rect(screen, (190, 170, 130), (pos[0] - 25, pos[1] - 110, 50, 10))
            
        elif stage == "volcano":
            # Dark sky with red tint
            sky_rect = pygame.Rect(0, 0, self.game_engine.width, 450)
            pygame.draw.rect(screen, (40, 20, 20), sky_rect)
            
            # Add dim sun through smoke
            sun_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(sun_surf, (255, 100, 50, 100), (40, 40), 40)
            screen.blit(sun_surf, (100, 80))
            
            # Distant volcano
            volcano_points = [
                (0, 450),
                (200, 200),
                (400, 300),
                (600, 150),
                (800, 450)
            ]
            pygame.draw.polygon(screen, (60, 30, 30), volcano_points)
            
            # Draw lava at top of volcano
            lava_radius = 30 + math.sin(pygame.time.get_ticks() * 0.001) * 5
            pygame.draw.circle(screen, (255, 100, 0), (600, 150), int(lava_radius))
            
            # Red glow over the scene
            glow_surf = pygame.Surface((self.game_engine.width, 450), pygame.SRCALPHA)
            glow_surf.fill((255, 0, 0, 10))
            screen.blit(glow_surf, (0, 0))
            
            # Add some floating ash particles
            for i in range(20):
                x = random.randint(0, self.game_engine.width)
                y = random.randint(50, 400)
                size = random.randint(1, 3)
                alpha = random.randint(50, 150)
                
                ash_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                ash_color = (150, 150, 150, alpha)
                pygame.draw.circle(ash_surf, ash_color, (size, size), size)
                screen.blit(ash_surf, (x, y))

    def _draw_hit_effect(self, screen):
            """Draw the hit effect with type-specific visuals."""
            # Scale hit effect based on damage
            hit_size = 20 + min(30, self.hit_strength)
            
            if self.hit_type == "punch":
                # Simple impact circles
                for i in range(3):  
                    size = hit_size - i * 5
                    if size <= 0:
                        continue
                    alpha = 200 - i * 60
                    hit_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    hit_color = (255, 200, 0, alpha)
                    pygame.draw.circle(hit_surf, hit_color, (size, size), size)
                    hit_rect = hit_surf.get_rect(center=self.hit_location)
                    screen.blit(hit_surf, hit_rect)
                    
                # Add "PUNCH!" text
                if self.hit_strength > 12:  # Only for strong hits
                    hit_text = self.game_engine.fonts['small'].render("PUNCH!", True, (255, 200, 0))
                    text_rect = hit_text.get_rect(center=(self.hit_location[0], self.hit_location[1] - 30))
                    screen.blit(hit_text, text_rect)
                
            elif self.hit_type == "kick":
                # More angular impact shape
                for i in range(2):
                    size = hit_size - i * 8
                    if size <= 0:
                        continue
                    alpha = 200 - i * 60
                    
                    # Create a starburst shape
                    hit_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                    center = (size * 1.5, size * 1.5)
                    hit_color = (255, 150, 0, alpha)
                    
                    points = []
                    for angle in range(0, 360, 45):  # 8-point star
                        rad = math.radians(angle)
                        # Outer point
                        x = center[0] + math.cos(rad) * size * 1.5
                        y = center[1] + math.sin(rad) * size * 1.5
                        points.append((x, y))
                        
                        # Inner point
                        rad = math.radians(angle + 22.5)
                        x = center[0] + math.cos(rad) * size * 0.8
                        y = center[1] + math.sin(rad) * size * 0.8
                        points.append((x, y))
                    
                    pygame.draw.polygon(hit_surf, hit_color, points)
                    hit_rect = hit_surf.get_rect(center=self.hit_location)
                    screen.blit(hit_surf, hit_rect)
                
                # Add "KICK!" text
                if self.hit_strength > 10:  # Only for strong hits
                    hit_text = self.game_engine.fonts['small'].render("KICK!", True, (255, 150, 0))
                    text_rect = hit_text.get_rect(center=(self.hit_location[0], self.hit_location[1] - 30))
                    screen.blit(hit_text, text_rect)
                
            elif self.hit_type == "special":
                # Energy explosion effect
                for i in range(4):
                    size = hit_size - i * 5
                    if size <= 0:
                        continue
                    alpha = 200 - i * 40
                    hit_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                    
                    # Different colors for special moves
                    colors = [
                        (100, 200, 255, alpha),  # Blue
                        (200, 100, 255, alpha),  # Purple
                        (100, 255, 200, alpha),  # Cyan
                        (255, 255, 100, alpha)   # Yellow
                    ]
                    hit_color = colors[i % len(colors)]
                    
                    # Ripple effect
                    pygame.draw.circle(hit_surf, hit_color, (size * 2, size * 2), size * (1.5 - i * 0.2))
                    hit_rect = hit_surf.get_rect(center=self.hit_location)
                    screen.blit(hit_surf, hit_rect)
                
                # Add "SPECIAL!" text
                if self.hit_strength > 15:  # Only for strong hits
                    hit_text = self.game_engine.fonts['medium'].render("SPECIAL!", True, (100, 200, 255))
                    text_rect = hit_text.get_rect(center=(self.hit_location[0], self.hit_location[1] - 40))
                    screen.blit(hit_text, text_rect)
            
            # Add impact lines for all hit types
            for i in range(8):
                angle = i * 45 + pygame.time.get_ticks() * 0.1
                length = hit_size + 10
                end_x = self.hit_location[0] + math.cos(math.radians(angle)) * length
                end_y = self.hit_location[1] + math.sin(math.radians(angle)) * length
                
                # Line color based on hit type
                if self.hit_type == "punch":
                    line_color = (255, 200, 0)
                elif self.hit_type == "kick":
                    line_color = (255, 150, 0)
                else:  # special
                    line_color = (100, 200, 255)
                    
                pygame.draw.line(screen, line_color, self.hit_location, (int(end_x), int(end_y)), 2)
        
    def _draw_announcements(self, screen):
        """Draw text announcements."""
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
                
            scaled_surf = pygame.transform.scale(text_surf, (scaled_width, scaled_height))
            text_rect = scaled_surf.get_rect(center=announcement["position"])
            
            # Add shadow for better visibility
            shadow_surf = font.render(announcement["text"], True, (0, 0, 0))
            shadow_scaled = pygame.transform.scale(shadow_surf, (scaled_width, scaled_height))
            shadow_rect = shadow_scaled.get_rect(center=(announcement["position"][0] + 2, announcement["position"][1] + 2))
            screen.blit(shadow_scaled, shadow_rect)
            
            # Draw the text
            screen.blit(scaled_surf, text_rect)
    
    def _draw_ui(self, screen):
        """Draw enhanced UI elements like health bars, timer, etc."""
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        # Draw health bars with stylized background
        # Player 1 health bar (left side)
        health_bg_rect1 = pygame.Rect(50, 30, 250, 20)
        health_border1 = pygame.Rect(45, 25, 260, 30)
        health_fill_rect1 = pygame.Rect(50, 30, int(250 * (player1.health / player1.max_health)), 20)
        
        # Draw glowing border based on health - ensure valid color values
        border_color = (
            max(0, min(255, int(255 * (1 - player1.health / player1.max_health)))),
            max(0, min(255, int(255 * (player1.health / player1.max_health)))),
            50
        )
        pygame.draw.rect(screen, border_color, health_border1, 3, border_radius=5)
        pygame.draw.rect(screen, (30, 30, 30), health_bg_rect1)
        
        # Health bar with gradient
        if player1.health > player1.max_health * 0.6:
            bar_color = (100, 255, 100)  # Green for high health
        elif player1.health > player1.max_health * 0.3:
            bar_color = (255, 255, 100)  # Yellow for medium health
        else:
            bar_color = (255, 100, 100)  # Red for low health
            
            # Flashing effect for critical health
            if player1.health < player1.max_health * 0.15 and pygame.time.get_ticks() % 500 < 250:
                bar_color = (255, 50, 50)
                
        pygame.draw.rect(screen, bar_color, health_fill_rect1, border_radius=3)
        
        # Player 2 health bar (right side)
        health_bg_rect2 = pygame.Rect(500, 30, 250, 20)
        health_border2 = pygame.Rect(495, 25, 260, 30) 
        health_fill_width = int(250 * (player2.health / player2.max_health))
        health_fill_rect2 = pygame.Rect(500 + 250 - health_fill_width, 30, health_fill_width, 20)
        
        # Draw glowing border based on health - ensure valid color values
        border_color2 = (
            max(0, min(255, int(255 * (1 - player2.health / player2.max_health)))),
            max(0, min(255, int(255 * (player2.health / player2.max_health)))),
            50
        )
        pygame.draw.rect(screen, border_color2, health_border2, 3, border_radius=5)
        pygame.draw.rect(screen, (30, 30, 30), health_bg_rect2)
        
        # Health bar with gradient
        if player2.health > player2.max_health * 0.6:
            bar_color = (100, 255, 100)
        elif player2.health > player2.max_health * 0.3:
            bar_color = (255, 255, 100)
        else:
            bar_color = (255, 100, 100)
            
            # Flashing effect for critical health
            if player2.health < player2.max_health * 0.15 and pygame.time.get_ticks() % 500 < 250:
                bar_color = (255, 50, 50)
                
        pygame.draw.rect(screen, bar_color, health_fill_rect2, border_radius=3)
        
        # Display numerical health
        health_text1 = f"{player1.health}/{player1.max_health}"
        health_surf1 = self.game_engine.fonts['small'].render(health_text1, True, (255, 255, 255))
        health_rect1 = health_surf1.get_rect(center=(175, 40))
        screen.blit(health_surf1, health_rect1)
        
        health_text2 = f"{player2.health}/{player2.max_health}"
        health_surf2 = self.game_engine.fonts['small'].render(health_text2, True, (255, 255, 255))
        health_rect2 = health_surf2.get_rect(center=(625, 40))
        screen.blit(health_surf2, health_rect2)
        
        # Player names above health bars
        p1_name = self.game_engine.player1_character.__class__.__name__.upper()
        p2_name = self.game_engine.player2_character.__class__.__name__.upper()
        
        p1_name_surf = self.game_engine.fonts['small'].render(p1_name, True, (220, 220, 255))
        p1_name_rect = p1_name_surf.get_rect(center=(175, 15))
        screen.blit(p1_name_surf, p1_name_rect)
        
        p2_name_surf = self.game_engine.fonts['small'].render(p2_name, True, (255, 220, 220))
        p2_name_rect = p2_name_surf.get_rect(center=(625, 15))
        screen.blit(p2_name_surf, p2_name_rect)
        
        # Time remaining with countdown effect
        time_color = (255, 255, 255)
        time_scale = 1.0
        
        if self.remaining_time < 10:
            time_color = (255, 50, 50)
            # Pulsing effect for low time
            if pygame.time.get_ticks() % 500 < 250:
                time_color = (255, 100, 100)
                time_scale = 1.1
                
        time_surf = self.game_engine.fonts['large'].render(str(self.remaining_time), True, time_color)
        time_scaled = pygame.transform.scale(time_surf, 
                                          (int(time_surf.get_width() * time_scale), 
                                           int(time_surf.get_height() * time_scale)))
        time_rect = time_scaled.get_rect(center=(self.game_engine.width // 2, 40))
        screen.blit(time_scaled, time_rect)
        
        # Round indicator with decorative elements
        round_text = f"ROUND {self.round_number}/{self.max_rounds}"
        round_surf = self.game_engine.fonts['small'].render(round_text, True, (200, 200, 50))
        round_rect = round_surf.get_rect(center=(self.game_engine.width // 2, 70))
        
        # Decorative lines
        line_length = round_surf.get_width() + 20
        pygame.draw.line(screen, (200, 200, 50), 
                       (self.game_engine.width // 2 - line_length//2, 80),
                       (self.game_engine.width // 2 + line_length//2, 80), 1)
        
        screen.blit(round_surf, round_rect)
        
        # Victory indicators (stars) with animation
        for i in range(self.victories[0]):
            star_x = 60 + i * 30
            star_y = 65
            self._draw_star(screen, star_x, star_y, (255, 220, 0))
        
        for i in range(self.victories[1]):
            star_x = 740 - i * 30
            star_y = 65
            self._draw_star(screen, star_x, star_y, (255, 220, 0))
        
        # AI indicator
        if self.ai_enabled:
            ai_text = f"AI: ON (LEVEL {self.ai_difficulty})"
            ai_color = (100, 255, 100)
        else:
            ai_text = "AI: OFF"
            ai_color = (255, 100, 100)
            
        ai_surf = self.game_engine.fonts['small'].render(ai_text, True, ai_color)
        ai_rect = ai_surf.get_rect(topright=(self.game_engine.width - 10, 10))
        screen.blit(ai_surf, ai_rect)
        
        # Stats display: hits, combo
        if self.round_started and not self.round_over:
            # Create semi-transparent background
            stats_surface = pygame.Surface((200, 40), pygame.SRCALPHA)
            stats_surface.fill((0, 0, 0, 128))
            screen.blit(stats_surface, (10, 550))
            
            hits_text = f"HITS: {self.hit_counter}"
            hits_surf = self.game_engine.fonts['small'].render(hits_text, True, (200, 200, 200))
            screen.blit(hits_surf, (20, 555))
            
            combo_text = f"MAX COMBO: {self.max_combo}x"
            combo_surf = self.game_engine.fonts['small'].render(combo_text, True, (255, 220, 50))
            screen.blit(combo_surf, (20, 575))
        
        # Controls help
        controls_text = "P1: WASD+GHJ  |  Toggle AI: T  |  AI Level: Y"
        controls_surf = self.game_engine.fonts['small'].render(controls_text, True, (180, 180, 180))
        controls_rect = controls_surf.get_rect(bottomleft=(10, self.game_engine.height - 10))
        screen.blit(controls_surf, controls_rect)
        
        # Show current character moves
        if self.round_started and not self.round_over:
            # Only show for the active player (player 1 or non-AI player 2)
            active_player = player1 if not self.ai_enabled else player1
            
            # Create semi-transparent background
            moves_surface = pygame.Surface((200, 40), pygame.SRCALPHA)
            moves_surface.fill((0, 0, 0, 128))
            screen.blit(moves_surface, (self.game_engine.width - 210, 550))
            
            char_type = active_player.__class__.__name__
            moves_text = f"{char_type} MOVES: G-Punch H-Kick J-Special"
            moves_surf = self.game_engine.fonts['small'].render(moves_text, True, (200, 220, 255))
            moves_rect = moves_surf.get_rect(bottomright=(self.game_engine.width - 10, self.game_engine.height - 10))
            screen.blit(moves_surf, moves_rect)
    
    def _draw_star(self, screen, x, y, color, size=12):
        """Draw an animated star shape for victory indicators."""
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.2 + 0.8
        adjusted_size = size * pulse
        
        points = []
        for i in range(10):
            angle = math.pi * 2 * i / 10
            # Alternate between outer and inner radius
            radius = adjusted_size if i % 2 == 0 else adjusted_size / 2
            px = x + math.sin(angle) * radius
            py = y - math.cos(angle) * radius  # Negative for y to flip
            points.append((px, py))
        
        # Add glow effect
        glow_surf = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
        glow_color = (*color, 50)
        pygame.draw.polygon(glow_surf, glow_color, [
            (p[0] - x + size*2, p[1] - y + size*2) for p in points
        ])
        screen.blit(glow_surf, (x - size*2, y - size*2))
        
        # Draw star
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 1)  # Black outline