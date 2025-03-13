import pygame
import random
import math
from game.engine.scene import Scene

class FightScene(Scene):
    """Main fighting scene."""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        # Stage backgrounds with different colors
        self.stage_backgrounds = {
            "dojo": (100, 50, 50),
            "forest": (40, 80, 40),
            "temple": (70, 70, 90)
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
        
        # Visual effects
        self.show_hit_effect = False
        self.hit_effect_time = 0
        self.hit_location = (0, 0)
        self.hit_strength = 0
        
        # Game modes
        self.ai_enabled = True  # By default, Player 2 is AI-controlled
        self.ai_difficulty = 2  # Medium difficulty
        
        # Set up player positions
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        player1.position = (200, 400)
        player2.position = (600, 400)
        player1.facing_right = True
        player2.facing_right = False
        
        # Enable AI for player 2 if AI mode is on
        if self.ai_enabled:
            player2.enable_ai(self.ai_difficulty, player1)
        
        # Keyboard state for smoother controls
        self.key_states = {
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
        
        # Start the round
        self._start_round()
    
    def _start_round(self):
        """Start a new round."""
        self.round_started = False
        self.round_over = False
        self.remaining_time = self.round_time
        
        # Reset player health
        self.game_engine.player1_character.health = 100
        self.game_engine.player2_character.health = 100
        
        # Reset player positions
        self.game_engine.player1_character.position = (200, 400)
        self.game_engine.player2_character.position = (600, 400)
        
        # Reset player states
        self.game_engine.player1_character.reset()
        self.game_engine.player2_character.reset()
        
        # Set up AI targeting
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        if self.ai_enabled:
            player2.enable_ai(self.ai_difficulty, player1)
        else:
            player2.disable_ai()
        
        # Start after a short delay
        pygame.time.set_timer(pygame.USEREVENT, 2000, 1)  # Trigger once after 2 seconds
    
    def handle_event(self, event):
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        if event.type == pygame.USEREVENT:
            self.round_started = True
            self.round_start_time = pygame.time.get_ticks()
            
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
            
            elif event.key == pygame.K_y and self.round_started and not self.round_over:
                # Cycle AI difficulty
                self.ai_difficulty = (self.ai_difficulty % 3) + 1
                if self.ai_enabled:
                    player2.enable_ai(self.ai_difficulty, player1)
            
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
        if not self.round_started or self.round_over:
            return
        
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        # Handle continuous key presses for smooth movement
        self._handle_key_states()
        
        # Update the remaining time
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.round_start_time) // 1000
        self.remaining_time = max(0, self.round_time - elapsed_seconds)
        
        # Check if time is up
        if self.remaining_time <= 0:
            self._end_round()
            return
        
        # Update player states
        player1.update()
        player2.update()
        
        # Check for collisions/attacks
        if player1.is_attacking and not player2.is_knocked_out:
            if self._check_hit(player1, player2):
                damage = player1.get_attack_damage()
                player2.take_damage(damage)
                player1.successful_hit()  # Update combo
                self._show_hit(player2.position, damage)
                
                # Check if knocked out
                if player2.health <= 0:
                    player2.knock_out()
                    self._end_round()
        
        if player2.is_attacking and not player1.is_knocked_out:
            if self._check_hit(player2, player1):
                damage = player2.get_attack_damage()
                player1.take_damage(damage)
                player2.successful_hit()  # Update combo
                self._show_hit(player1.position, damage)
                
                # Check if knocked out
                if player1.health <= 0:
                    player1.knock_out()
                    self._end_round()
        
        # Update hit effect
        if self.show_hit_effect:
            if current_time - self.hit_effect_time > 300:  # Show for 300ms
                self.show_hit_effect = False
    
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
    
    def _check_hit(self, attacker, defender):
        """Check if an attack hits."""
        # Basic hitbox for character body
        attacker_rect = pygame.Rect(
            attacker.position[0] - 20, 
            attacker.position[1] - 50,
            40, 100
        )
        
        defender_rect = pygame.Rect(
            defender.position[0] - 20, 
            defender.position[1] - 50,
            40, 100
        )
        
        # Create attack hitbox based on attack type and facing direction
        attack_rect = None
        
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
    
    def _show_hit(self, position, damage):
        """Show a hit effect at the given position."""
        self.show_hit_effect = True
        self.hit_effect_time = pygame.time.get_ticks()
        self.hit_location = position
        self.hit_strength = damage  # Used for scaling hit effect
    
    def _end_round(self):
        """End the current round."""
        self.round_over = True
        
        # Determine round winner
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        if player1.health > player2.health:
            self.victories[0] += 1
        elif player2.health > player1.health:
            self.victories[1] += 1
        else:
            # It's a tie, both get a point
            self.victories[0] += 1
            self.victories[1] += 1
    
    def render(self, screen):
        # Get the background for the current stage
        bg_color = self.stage_backgrounds.get(self.game_engine.current_stage, (0, 0, 0))
        screen.fill(bg_color)
        
        # Draw a simple stage background with parallax effect
        self._draw_stage(screen)
        
        # Draw the ground
        ground_rect = pygame.Rect(0, 450, self.game_engine.width, 150)
        pygame.draw.rect(screen, (60, 40, 20), ground_rect)
        
        # Draw players
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        player1.render(screen)
        player2.render(screen)
        
        # Draw hit effect
        if self.show_hit_effect:
            # Scale hit effect based on damage
            hit_size = 20 + min(30, self.hit_strength)
            for i in range(3):  # Multiple concentric circles
                size = hit_size - i * 5
                if size <= 0:
                    continue
                alpha = 200 - i * 60
                hit_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(hit_surf, (255, 200, 0, alpha), (size, size), size)
                hit_rect = hit_surf.get_rect(center=self.hit_location)
                screen.blit(hit_surf, hit_rect)
            
            # Add impact lines
            for i in range(8):
                angle = i * 45 + pygame.time.get_ticks() * 0.1
                length = hit_size + 10
                end_x = self.hit_location[0] + math.cos(math.radians(angle)) * length
                end_y = self.hit_location[1] + math.sin(math.radians(angle)) * length
                pygame.draw.line(screen, (255, 255, 0), self.hit_location, (int(end_x), int(end_y)), 2)
        
        # Draw UI elements
        self._draw_ui(screen)
        
        # Draw round start/end messages
        if not self.round_started:
            self._draw_round_start(screen)
        elif self.round_over:
            self._draw_round_end(screen)
    
    def _draw_stage(self, screen):
        """Draw a simple parallax background for the stage."""
        stage = self.game_engine.current_stage
        
        if stage == "dojo":
            # Draw wooden wall
            wall_color = (120, 80, 40)
            pygame.draw.rect(screen, wall_color, (0, 0, self.game_engine.width, 450))
            
            # Draw wall panels
            panel_color = (140, 100, 50)
            for x in range(0, self.game_engine.width, 100):
                pygame.draw.rect(screen, panel_color, (x, 50, 80, 400))
                
            # Draw some distant decorations
            pygame.draw.rect(screen, (150, 20, 20), (200, 100, 400, 100))  # Banner
            pygame.draw.rect(screen, (20, 20, 20), (350, 220, 100, 230))  # Door
            
        elif stage == "forest":
            # Sky
            pygame.draw.rect(screen, (100, 150, 255), (0, 0, self.game_engine.width, 200))
            
            # Distant trees
            tree_color = (20, 60, 20)
            for x in range(-50, self.game_engine.width, 100):
                tree_height = random.randint(100, 200)
                tree_width = random.randint(50, 80)
                pygame.draw.rect(screen, tree_color, (x, 200 - tree_height, tree_width, tree_height))
                
            # Ground
            ground_color = (50, 100, 50)
            pygame.draw.rect(screen, ground_color, (0, 200, self.game_engine.width, 250))
            
        elif stage == "temple":
            # Sky
            sky_color = (60, 60, 100)
            pygame.draw.rect(screen, sky_color, (0, 0, self.game_engine.width, 450))
            
            # Temple structure
            temple_color = (180, 180, 200)
            pygame.draw.rect(screen, temple_color, (150, 100, 500, 350))
            
            # Temple columns
            column_color = (200, 200, 220)
            for x in range(200, 600, 100):
                pygame.draw.rect(screen, column_color, (x, 100, 30, 350))
                
            # Temple roof
            roof_points = [
                (100, 100),
                (700, 100),
                (600, 50),
                (200, 50)
            ]
            pygame.draw.polygon(screen, (100, 100, 120), roof_points)
        
        # Ground shadow
        shadow_surf = pygame.Surface((self.game_engine.width, 20), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 100))
        screen.blit(shadow_surf, (0, 450))
    
    def _draw_round_start(self, screen):
        """Draw the round start announcement."""
        # Semitransparent background
        overlay = pygame.Surface((self.game_engine.width, self.game_engine.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Main round text
        font_large = self.game_engine.fonts['large']
        round_text = f"ROUND {self.round_number}"
        
        # Shadow
        shadow_surf = font_large.render(round_text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(self.game_engine.width // 2 + 3, self.game_engine.height // 2 + 3))
        screen.blit(shadow_surf, shadow_rect)
        
        # Main text with glow effect
        text_surf = font_large.render(round_text, True, (255, 220, 50))
        text_rect = text_surf.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2))
        screen.blit(text_surf, text_rect)
        
        # Fighter names
        player1 = self.game_engine.player1_character.__class__.__name__
        player2 = self.game_engine.player2_character.__class__.__name__
        vs_text = f"{player1} VS {player2}"
        
        vs_surf = self.game_engine.fonts['medium'].render(vs_text, True, (255, 255, 255))
        vs_rect = vs_surf.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2 + 50))
        screen.blit(vs_surf, vs_rect)
    
    def _draw_round_end(self, screen):
        """Draw the round end announcement."""
        # Determine winner
        winner_text = ""
        if self.victories[0] > self.victories[1]:
            winner_text = "PLAYER 1 WINS!"
            color = (100, 100, 255)
        elif self.victories[1] > self.victories[0]:
            winner_text = "PLAYER 2 WINS!"
            color = (255, 100, 100)
        else:
            winner_text = "DRAW!"
            color = (200, 200, 200)
        
        # Semitransparent background
        overlay = pygame.Surface((self.game_engine.width, self.game_engine.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Animate the text
        scale = 1.0 + math.sin(pygame.time.get_ticks() * 0.005) * 0.1
        font_large = self.game_engine.fonts['large']
        
        # Shadow
        shadow_surf = font_large.render(winner_text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(self.game_engine.width // 2 + 3, self.game_engine.height // 2 + 3))
        screen.blit(shadow_surf, shadow_rect)
        
        # Main text with glow
        text_surf = font_large.render(winner_text, True, color)
        text_rect = text_surf.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2))
        
        # Scale for pulsing effect
        scaled_width = int(text_surf.get_width() * scale)
        scaled_height = int(text_surf.get_height() * scale)
        scaled_surf = pygame.transform.scale(text_surf, (scaled_width, scaled_height))
        scaled_rect = scaled_surf.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2))
        
        screen.blit(scaled_surf, scaled_rect)
        
        # Continue text
        if self.round_number < self.max_rounds and max(self.victories) < (self.max_rounds // 2 + 1):
            continue_text = "Press SPACE for next round"
        else:
            continue_text = "Press SPACE to continue"
            
        continue_surf = self.game_engine.fonts['small'].render(continue_text, True, (200, 200, 200))
        continue_rect = continue_surf.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2 + 80))
        screen.blit(continue_surf, continue_rect)
        
        # Show final score
        score_text = f"Score: {self.victories[0]} - {self.victories[1]}"
        score_surf = self.game_engine.fonts['medium'].render(score_text, True, (220, 220, 255))
        score_rect = score_surf.get_rect(center=(self.game_engine.width // 2, self.game_engine.height // 2 + 120))
        screen.blit(score_surf, score_rect)
    
    def _draw_ui(self, screen):
        """Draw UI elements like health bars, timer, etc."""
        player1 = self.game_engine.player1_character
        player2 = self.game_engine.player2_character
        
        # Draw health bars with stylized background
        # Player 1 health bar (left side)
        health_bg_rect1 = pygame.Rect(50, 30, 250, 20)
        health_border1 = pygame.Rect(45, 25, 260, 30)
        health_fill_rect1 = pygame.Rect(50, 30, int(250 * (player1.health / 100)), 20)
        
        # Draw glowing border based on health
        border_color = (
            int(255 * (1 - player1.health / 100)),
            int(255 * (player1.health / 100)),
            50
        )
        pygame.draw.rect(screen, border_color, health_border1, 3, border_radius=5)
        pygame.draw.rect(screen, (30, 30, 30), health_bg_rect1)
        
        # Health bar with gradient
        if player1.health > 60:
            bar_color = (100, 255, 100)  # Green for high health
        elif player1.health > 30:
            bar_color = (255, 255, 100)  # Yellow for medium health
        else:
            bar_color = (255, 100, 100)  # Red for low health
            
            # Flashing effect for critical health
            if player1.health < 15 and pygame.time.get_ticks() % 500 < 250:
                bar_color = (255, 50, 50)
                
        pygame.draw.rect(screen, bar_color, health_fill_rect1, border_radius=3)
        
        # Player 2 health bar (right side)
        health_bg_rect2 = pygame.Rect(500, 30, 250, 20)
        health_border2 = pygame.Rect(495, 25, 260, 30) 
        health_fill_rect2 = pygame.Rect(500 + 250 - int(250 * (player2.health / 100)), 30, int(250 * (player2.health / 100)), 20)
        
        # Draw glowing border based on health
        border_color2 = (
            int(255 * (1 - player2.health / 100)),
            int(255 * (player2.health / 100)),
            50
        )
        pygame.draw.rect(screen, border_color2, health_border2, 3, border_radius=5)
        pygame.draw.rect(screen, (30, 30, 30), health_bg_rect2)
        
        # Health bar with gradient
        if player2.health > 60:
            bar_color = (100, 255, 100)
        elif player2.health > 30:
            bar_color = (255, 255, 100)
        else:
            bar_color = (255, 100, 100)
            
            # Flashing effect for critical health
            if player2.health < 15 and pygame.time.get_ticks() % 500 < 250:
                bar_color = (255, 50, 50)
                
        pygame.draw.rect(screen, bar_color, health_fill_rect2, border_radius=3)
        
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
        if self.remaining_time < 10:
            time_color = (255, 50, 50)
            
            # Pulsing effect for low time
            if pygame.time.get_ticks() % 500 < 250:
                time_color = (255, 100, 100)
                
        time_surf = self.game_engine.fonts['large'].render(str(self.remaining_time), True, time_color)
        time_rect = time_surf.get_rect(center=(self.game_engine.width // 2, 40))
        screen.blit(time_surf, time_rect)
        
        # Round indicator
        round_text = f"ROUND {self.round_number}/{self.max_rounds}"
        round_surf = self.game_engine.fonts['small'].render(round_text, True, (200, 200, 50))
        round_rect = round_surf.get_rect(center=(self.game_engine.width // 2, 70))
        screen.blit(round_surf, round_rect)
        
        # Victory indicators (stars)
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
            ai_surf = self.game_engine.fonts['small'].render(ai_text, True, (200, 255, 200))
        else:
            ai_text = "AI: OFF"
            ai_surf = self.game_engine.fonts['small'].render(ai_text, True, (255, 200, 200))
            
        ai_rect = ai_surf.get_rect(topright=(self.game_engine.width - 10, 10))
        screen.blit(ai_surf, ai_rect)
        
        # Controls help
        controls_text = "P1: WASD+GHJ  |  Toggle AI: T  |  AI Level: Y"
        controls_surf = self.game_engine.fonts['small'].render(controls_text, True, (180, 180, 180))
        controls_rect = controls_surf.get_rect(bottomleft=(10, self.game_engine.height - 10))
        screen.blit(controls_surf, controls_rect)
    
    def _draw_star(self, screen, x, y, color, size=12):
        """Draw a simple star shape."""
        points = []
        for i in range(10):
            angle = math.pi * 2 * i / 10
            # Alternate between outer and inner radius
            radius = size if i % 2 == 0 else size / 2
            px = x + math.sin(angle) * radius
            py = y - math.cos(angle) * radius  # Negative for y to flip
            points.append((px, py))
        
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 1)  # Black outline