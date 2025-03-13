import pygame
import random
import math
from game.engine.scene import Scene
from game.stages.stage_renderer import StageRenderer
from game.scenes.fight_ui_renderer import FightUIRenderer
from game.combat.combat_manager import CombatManager
from game.combat.announcement_system import AnnouncementSystem
from game.effects.hit_effects import HitEffects
from game.effects.camera_system import CameraSystem
from game.effects.particle_system import EnhancedParticleSystem
from game.effects.weather_system import WeatherSystem
from game.effects.interactive_background import InteractiveBackground
from game.input.input_handler import InputHandler

class FightScene(Scene):
    """Main fighting scene that coordinates all aspects of gameplay."""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        
        # Initialize subsystems
        self.stage_renderer = StageRenderer(game_engine)
        self.ui_renderer = FightUIRenderer(game_engine)
        self.combat_manager = CombatManager(game_engine)
        self.announcement_system = AnnouncementSystem(game_engine)
        self.hit_effects = HitEffects(game_engine)
        self.input_handler = InputHandler()
        
        # Visual effects systems
        self.particle_system = EnhancedParticleSystem()
        self.weather_system = WeatherSystem(self.game_engine.width, self.game_engine.height)
        self.interactive_bg = InteractiveBackground(self.game_engine.width, self.game_engine.height)
        self.camera_system = CameraSystem(self.game_engine.width, self.game_engine.height, 
                                        self.game_engine.width, self.game_engine.height)
        
        # Round settings
        self.round_time = 60  # 60 seconds per round
        self.remaining_time = self.round_time
        self.round_started = False
        self.round_over = False
        self.round_start_time = 0
        self.round_number = 1
        self.max_rounds = 3
        self.victories = [0, 0]  # Player 1 and Player 2 victories
        
        # Match state
        self.match_over = False
        self.match_winner = None
        
        # Game modes
        self.ai_enabled = True  # By default, Player 2 is AI-controlled
        self.ai_difficulty = 2  # Medium difficulty
        
        # Combat stats
        self.hit_counter = 0
        self.combo_counter = 0
        self.max_combo = 0
        
        # Setup players
        self._setup_players()
        
        # Start the round
        self._start_round()
    
    def _setup_players(self):
        """Set up initial player positions and properties."""
        # Set up player positions
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        player1.position = (200, 400)
        player2.position = (600, 400)
        player1.facing_right = True
        player2.facing_right = False
        
        # Set floor height and gravity based on stage
        stage_data = self.stage_renderer.get_stage_data(self.game_engine.current_stage)
        floor_height = stage_data.get("floor", 450)
        gravity = stage_data.get("gravity", 0.8)
        
        player1.floor_height = floor_height
        player2.floor_height = floor_height
        player1.gravity = gravity
        player2.gravity = gravity
        
        # Enable AI for player 2 if AI mode is on
        if self.ai_enabled:
            player2.enable_ai(self.ai_difficulty, player1)
        
        # Set up weather for the current stage
        weather_type = stage_data.get("weather")
        if weather_type:
            self.weather_system.set_weather(weather_type, 0.7)
        
        # Generate interactive background elements
        self.interactive_bg.generate_elements(self.game_engine.current_stage)
    
    def _start_round(self):
        """Start a new round."""
        self.round_started = False
        self.round_over = False
        self.remaining_time = self.round_time
        
        # Get stage info
        stage_data = self.stage_renderer.get_stage_data(self.game_engine.current_stage)
        floor_height = stage_data.get("floor", 450)
        gravity = stage_data.get("gravity", 0.8)
        
        # Reset player health and positions
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        player1.health = player1.max_health
        player2.health = player2.max_health
        
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
        
        # Reset subsystems
        self.particle_system = EnhancedParticleSystem()
        self.announcement_system.clear()
        
        # Reset camera
        self.camera_system = CameraSystem(self.game_engine.width, self.game_engine.height, 
                                        self.game_engine.width, self.game_engine.height)
        
        # Add round announcements
        self.announcement_system.add_announcement(
            f"ROUND {self.round_number}",
            color=(255, 220, 50),
            size="large",
            position=(self.game_engine.width // 2, self.game_engine.height // 2),
            timer=120
        )
        
        self.announcement_system.add_announcement(
            "FIGHT!",
            color=(255, 50, 50),
            size="large",
            position=(self.game_engine.width // 2, self.game_engine.height // 2 + 60),
            timer=30,
            delay=60
        )
        
        # Set up weather for the current stage
        weather_type = stage_data.get("weather")
        if weather_type:
            self.weather_system.set_weather(weather_type, 0.7)
        
        # Generate fresh interactive background elements
        self.interactive_bg.generate_elements(self.game_engine.current_stage)
        
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
            
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            # First update the input handler's key states
            self.input_handler.handle_event(event)
            
            # Handle other special key events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t and self.round_started and not self.round_over:
                    # Toggle AI on/off for player 2
                    self.ai_enabled = not self.ai_enabled
                    if self.ai_enabled:
                        player2.enable_ai(self.ai_difficulty, player1)
                    else:
                        player2.disable_ai()
                    
                    # Show AI toggle announcement
                    self.announcement_system.add_announcement(
                        f"AI: {'ON' if self.ai_enabled else 'OFF'}",
                        color=(100, 255, 100) if self.ai_enabled else (255, 100, 100),
                        size="medium",
                        position=(self.game_engine.width // 2, 100),
                        timer=60
                    )
                
                elif event.key == pygame.K_y and self.round_started and not self.round_over:
                    # Cycle AI difficulty
                    self.ai_difficulty = (self.ai_difficulty % 3) + 1
                    if self.ai_enabled:
                        player2.enable_ai(self.ai_difficulty, player1)
                    
                    # Show AI difficulty announcement
                    self.announcement_system.add_announcement(
                        f"AI DIFFICULTY: {self.ai_difficulty}",
                        color=(100, 200, 100),
                        size="medium",
                        position=(self.game_engine.width // 2, 100),
                        timer=60
                    )
                
                elif event.key == pygame.K_SPACE and self.round_over:
                    # Space to continue after round end
                    if not self.match_over:
                        # Continue to next round
                        self.round_number += 1
                        self._start_round()
                    else:
                        # Game over - show results - import here to avoid circular import
                        from game.scenes.game_over_scene import GameOverScene
                        # Use the match_winner already determined in _end_round
                        self.game_engine.change_scene(GameOverScene(self.game_engine, self.match_winner))
                
                # Toggle weather (developer feature)
                elif event.key == pygame.K_w and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self._cycle_weather()
    
    def _cycle_weather(self):
        """Cycle through weather types (developer feature)."""
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
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Only update core gameplay if round is active
        if self.round_started and not self.round_over:
            self._update_gameplay(current_time)
        
        # Always update visual systems, even during intro/outro
        self._update_visual_systems(current_time)
        
        # Update announcements
        self.announcement_system.update()
    
    def _update_gameplay(self, current_time):
        """Update core gameplay elements."""
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        # Handle player input
        self.input_handler.process_input(player1, player2, self.ai_enabled)
        
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
        
        # Check for combat interactions using combat manager
        hit_results = self.combat_manager.check_combat_interactions(player1, player2)
        
        for result in hit_results:
            if result["type"] == "hit":
                # Handle hit
                self.hit_counter += 1
                self.combo_counter += 1 if result["attacker"] == player1 else 0  # Only track player 1 combos
                self.max_combo = max(self.max_combo, self.combo_counter)
                
                # Visual effects for hit
                self.hit_effects.show_hit(result["position"], result["damage"], result["attack_type"])
                
                # Add hit particles
                self.hit_effects.add_hit_particles(self.particle_system, 
                                                result["position"], 
                                                result["damage"], 
                                                result["attack_type"], 
                                                result["facing_right"],
                                                result["attacker"].__class__.__name__)
                
                # Camera impact effect based on damage
                impact_intensity = min(2.0, result["damage"] / 10)
                self.camera_system.add_impact_effect(result["position"], impact_intensity)
                
                # Show combo announcement for good combos
                if self.combo_counter >= 3:
                    self.announcement_system.add_announcement(
                        f"{self.combo_counter}x COMBO!",
                        color=(255, 220, 50),
                        size="medium",
                        position=(self.game_engine.width // 2, 150),
                        timer=60
                    )
                    
            elif result["type"] == "block":
                # Handle block
                self.combo_counter = 0  # Reset combo on block
                self.hit_effects.show_block_effect(self.particle_system, result["position"])
                self.announcement_system.add_announcement(
                    "BLOCK!",
                    color=(100, 100, 255),
                    size="small",
                    position=(result["position"][0], result["position"][1] - 100),
                    timer=20
                )
                
                # Small camera shake
                self.camera_system.add_shake(1.0)
                
            elif result["type"] == "knockout":
                # Handle knockout
                defender = result["defender"]
                self.hit_effects.show_knockout_effect(self.particle_system, 
                                                   defender.position, 
                                                   self.camera_system)
                self.announcement_system.add_announcement(
                    "K.O.!",
                    color=(255, 50, 50),
                    size="large",
                    position=(self.game_engine.width // 2, self.game_engine.height // 2),
                    timer=120
                )
                
                defender.knock_out()
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
        
        # Update hit effects
        self.hit_effects.update()
    
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
        self.announcement_system.add_announcement(
            winner_text,
            color=winner_color,
            size="large",
            position=(self.game_engine.width // 2, self.game_engine.height // 2),
            timer=180
        )
        
        # Check if the match is over (someone has majority of victories needed)
        match_over = False
        winner = None
        victory_threshold = self.max_rounds // 2 + 1
        
        if self.victories[0] >= victory_threshold:
            match_over = True
            winner = 1
        elif self.victories[1] >= victory_threshold:
            match_over = True
            winner = 2
        elif self.round_number >= self.max_rounds:
            # All rounds played, determine winner by number of victories
            match_over = True
            if self.victories[0] > self.victories[1]:
                winner = 1
            elif self.victories[1] > self.victories[0]:
                winner = 2
            else:
                # True tie after all rounds
                winner = 0
                
        # Add final match result if match is over
        if match_over:
            result_text = "MATCH COMPLETE"
            if winner > 0:
                result_text = f"PLAYER {winner} WINS THE MATCH!"
            else:
                result_text = "MATCH ENDS IN A DRAW!"
                
            # Show match result with delay
            self.announcement_system.add_announcement(
                result_text,
                color=(255, 220, 50),
                size="large",
                position=(self.game_engine.width // 2, self.game_engine.height // 2 + 40),
                timer=180,
                delay=90
            )
        
        # Add continue prompt
        if not match_over:
            continue_text = "Press SPACE for next round"
        else:
            continue_text = "Press SPACE to continue"
            
        self.announcement_system.add_announcement(
            continue_text,
            color=(200, 200, 200),
            size="small",
            position=(self.game_engine.width // 2, self.game_engine.height // 2 + 80),
            timer=180,
            delay=60
        )
        
        # Store the match winner for use in handle_event
        self.match_winner = winner if match_over else None
        self.match_over = match_over
        
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
    
    def render(self, screen):
        """Render the fight scene with all visual effects."""
        # Create a world surface that we'll apply camera effects to
        world_surface = pygame.Surface((self.game_engine.width, self.game_engine.height))
        
        # Render stage
        self.stage_renderer.render(world_surface, self.game_engine.current_stage)
        
        # Draw weather effects (background layer)
        if self.weather_system.weather_type:
            self.weather_system.render(world_surface)
        
        # Draw interactive background elements
        self.interactive_bg.render(world_surface)
        
        # Draw players
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        player1.render(world_surface)
        player2.render(world_surface)
        
        # Draw hit effects
        self.hit_effects.render(world_surface)
        
        # Draw all particles
        self.particle_system.render(world_surface)
        
        # Apply camera transformations (shake, zoom, etc.)
        final_view = self.camera_system.apply_to_surface(world_surface)
        
        # Blit the transformed view to the screen
        screen.blit(final_view, (0, 0))
        
        # Draw UI elements (these aren't affected by camera)
        self.ui_renderer.render(screen, 
                              player1, player2, 
                              self.remaining_time, 
                              self.round_number, self.max_rounds,
                              self.victories, 
                              self.hit_counter, self.max_combo,
                              self.ai_enabled, self.ai_difficulty,
                              self.round_started, self.round_over)
        
        # Draw announcements
        self.announcement_system.render(screen)