import pygame
import random
import math
from game.engine.scene import Scene
from game.characters.ninja import Ninja
from game.characters.samurai import Samurai
from game.characters.wizard import Wizard
from game.characters.guardian import Guardian

class CharacterSelectScene(Scene):
    """Character selection scene."""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.characters = ["NINJA", "SAMURAI", "WIZARD", "GUARDIAN"]
        self.player1_selection = 0
        self.player2_selection = 1
        self.active_player = 0  # 0 for player 1, 1 for player 2
        self.selection_confirmed = [False, False]
        self.background_color = (40, 20, 60)
        self.title_color = (220, 220, 50)
        self.player_colors = [(50, 100, 255), (255, 50, 50)]
        self.selected_color = (255, 255, 0)
        self.unselected_color = (150, 150, 150)
        
        # Character stats for display
        self.character_stats = {
            "NINJA": {"health": 100, "speed": 8, "attack": 10, "special": "Teleport"},
            "SAMURAI": {"health": 120, "speed": 6, "attack": 15, "special": "Rage Mode"},
            "WIZARD": {"health": 80, "speed": 4, "attack": 7, "special": "Ice Storm"},
            "GUARDIAN": {"health": 150, "speed": 3, "attack": 12, "special": "Counter"}
        }
        
        # Health scaling options
        self.health_options = ["STANDARD", "DOUBLE", "HALF", "RANDOM"]
        self.health_scaling = 0  # Index of selected option
        
        # Animation timer for effects
        self.animation_timer = 0
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.selection_confirmed[self.active_player]:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    if self.active_player == 0:
                        self.player1_selection = (self.player1_selection - 1) % len(self.characters)
                    else:
                        self.player2_selection = (self.player2_selection - 1) % len(self.characters)
                
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.active_player == 0:
                        self.player1_selection = (self.player1_selection + 1) % len(self.characters)
                    else:
                        self.player2_selection = (self.player2_selection + 1) % len(self.characters)
                
                elif event.key in (pygame.K_UP, pygame.K_w):
                    # Only allow player 1 to change health options
                    if self.active_player == 0:
                        self.health_scaling = (self.health_scaling - 1) % len(self.health_options)
                
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    # Only allow player 1 to change health options
                    if self.active_player == 0:
                        self.health_scaling = (self.health_scaling + 1) % len(self.health_options)
                
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.selection_confirmed[self.active_player] = True
                    
                    # If both players confirmed, proceed to stage selection
                    if all(self.selection_confirmed):
                        self._create_characters()
                    else:
                        # Switch to the other player
                        self.active_player = 1 if self.active_player == 0 else 0
    
    def _create_characters(self):
        # Create character instances based on selections
        if self.characters[self.player1_selection] == "NINJA":
            self.game_engine.player1_character = Ninja(is_player1=True)
        elif self.characters[self.player1_selection] == "SAMURAI":
            self.game_engine.player1_character = Samurai(is_player1=True)
        elif self.characters[self.player1_selection] == "WIZARD":
            self.game_engine.player1_character = Wizard(is_player1=True)
        elif self.characters[self.player1_selection] == "GUARDIAN":
            self.game_engine.player1_character = Guardian(is_player1=True)
        
        if self.characters[self.player2_selection] == "NINJA":
            self.game_engine.player2_character = Ninja(is_player1=False)
        elif self.characters[self.player2_selection] == "SAMURAI":
            self.game_engine.player2_character = Samurai(is_player1=False)
        elif self.characters[self.player2_selection] == "WIZARD":
            self.game_engine.player2_character = Wizard(is_player1=False)
        elif self.characters[self.player2_selection] == "GUARDIAN":
            self.game_engine.player2_character = Guardian(is_player1=False)
        
        # Apply health scaling
        self._apply_health_scaling()
        
        # Change to the stage select scene
        from game.scenes.stage_select_scene import StageSelectScene
        self.game_engine.change_scene(StageSelectScene(self.game_engine))
    
    def _apply_health_scaling(self):
        # Apply health scaling based on selected option
        p1 = self.game_engine.player1_character
        p2 = self.game_engine.player2_character
        
        if self.health_options[self.health_scaling] == "DOUBLE":
            p1.health *= 2
            p1.max_health *= 2
            p2.health *= 2
            p2.max_health *= 2
        elif self.health_options[self.health_scaling] == "HALF":
            p1.health = int(p1.health / 2)
            p1.max_health = int(p1.max_health / 2)
            p2.health = int(p2.health / 2)
            p2.max_health = int(p2.max_health / 2)
        elif self.health_options[self.health_scaling] == "RANDOM":
            # Random scaling between 0.5x and 2x
            p1_scale = random.uniform(0.5, 2.0)
            p2_scale = random.uniform(0.5, 2.0)
            p1.health = int(p1.health * p1_scale)
            p1.max_health = int(p1.max_health * p1_scale)
            p2.health = int(p2.health * p2_scale)
            p2.max_health = int(p2.max_health * p2_scale)
    
    def update(self):
        self.animation_timer += 1
    
    def render(self, screen):
        # Fill the background
        screen.fill(self.background_color)
        
        # Draw background effects - simple particle system
        for i in range(20):
            particle_x = (self.animation_timer * (i + 1) % self.game_engine.width)
            particle_y = (i * 30 + self.animation_timer // 2) % self.game_engine.height
            particle_size = 2 + math.sin(self.animation_timer * 0.05 + i) * 1
            particle_color = (
                60 + i * 5,
                20 + i * 2,
                80 + i * 5
            )
            pygame.draw.circle(screen, particle_color, (int(particle_x), int(particle_y)), int(particle_size))
        
        # Draw the title
        title_font = self.game_engine.fonts['large']
        title_surf = title_font.render("SELECT YOUR FIGHTER", True, self.title_color)
        title_rect = title_surf.get_rect(center=(self.game_engine.width // 2, 60))
        screen.blit(title_surf, title_rect)
        
        # Draw health scaling options
        health_text = f"HEALTH: {self.health_options[self.health_scaling]}"
        health_color = (220, 180, 80) if self.active_player == 0 else (150, 150, 150)
        health_surf = self.game_engine.fonts['small'].render(health_text, True, health_color)
        health_rect = health_surf.get_rect(center=(self.game_engine.width // 2, 100))
        screen.blit(health_surf, health_rect)
        
        # Draw the character options
        char_font = self.game_engine.fonts['medium']
        
        # Draw player 1 selection
        p1_text = f"PLAYER 1: {self.characters[self.player1_selection]}"
        p1_color = self.player_colors[0] if self.active_player == 0 else self.unselected_color
        p1_surf = char_font.render(p1_text, True, p1_color)
        p1_rect = p1_surf.get_rect(center=(self.game_engine.width // 4, 150))
        screen.blit(p1_surf, p1_rect)
        
        # Draw player 2 selection
        p2_text = f"PLAYER 2: {self.characters[self.player2_selection]}"
        p2_color = self.player_colors[1] if self.active_player == 1 else self.unselected_color
        p2_surf = char_font.render(p2_text, True, p2_color)
        p2_rect = p2_surf.get_rect(center=(3 * self.game_engine.width // 4, 150))
        screen.blit(p2_surf, p2_rect)
        
        # Draw character previews
        preview_size = 150
        p1_preview_rect = pygame.Rect(
            self.game_engine.width // 4 - preview_size // 2,
            220,
            preview_size, preview_size
        )
        p2_preview_rect = pygame.Rect(
            3 * self.game_engine.width // 4 - preview_size // 2,
            220,
            preview_size, preview_size
        )
        
        # Draw character preview backgrounds
        pygame.draw.rect(screen, (30, 15, 45), p1_preview_rect)
        pygame.draw.rect(screen, (30, 15, 45), p2_preview_rect)
        pygame.draw.rect(screen, self.player_colors[0], p1_preview_rect, 2)
        pygame.draw.rect(screen, self.player_colors[1], p2_preview_rect, 2)
        
        # Draw character previews
        self._draw_character_preview(screen, self.characters[self.player1_selection], p1_preview_rect, True)
        self._draw_character_preview(screen, self.characters[self.player2_selection], p2_preview_rect, False)
        
        # Draw character stats
        self._draw_character_stats(screen, self.characters[self.player1_selection], 
                                 self.game_engine.width // 4, 400, self.player_colors[0])
        self._draw_character_stats(screen, self.characters[self.player2_selection], 
                                 3 * self.game_engine.width // 4, 400, self.player_colors[1])
        
        # Draw navigation hints
        if self.active_player == 0 and not self.selection_confirmed[0]:
            # Show vertical arrows for health options
            arrow_color = (200, 180, 80)
            pygame.draw.polygon(screen, arrow_color, [
                (self.game_engine.width // 2, 85),
                (self.game_engine.width // 2 - 5, 92),
                (self.game_engine.width // 2 + 5, 92)
            ])
            pygame.draw.polygon(screen, arrow_color, [
                (self.game_engine.width // 2, 115),
                (self.game_engine.width // 2 - 5, 108),
                (self.game_engine.width // 2 + 5, 108)
            ])
        
        # Draw character selection navigation
        p1_left_right = not self.selection_confirmed[0] and self.active_player == 0
        p2_left_right = not self.selection_confirmed[1] and self.active_player == 1
        
        if p1_left_right:
            # Left arrow for player 1
            pygame.draw.polygon(screen, self.player_colors[0], [
                (self.game_engine.width // 4 - 60, 150),
                (self.game_engine.width // 4 - 50, 140),
                (self.game_engine.width // 4 - 50, 160)
            ])
            # Right arrow for player 1
            pygame.draw.polygon(screen, self.player_colors[0], [
                (self.game_engine.width // 4 + 60, 150),
                (self.game_engine.width // 4 + 50, 140),
                (self.game_engine.width // 4 + 50, 160)
            ])
        
        if p2_left_right:
            # Left arrow for player 2
            pygame.draw.polygon(screen, self.player_colors[1], [
                (3 * self.game_engine.width // 4 - 60, 150),
                (3 * self.game_engine.width // 4 - 50, 140),
                (3 * self.game_engine.width // 4 - 50, 160)
            ])
            # Right arrow for player 2
            pygame.draw.polygon(screen, self.player_colors[1], [
                (3 * self.game_engine.width // 4 + 60, 150),
                (3 * self.game_engine.width // 4 + 50, 140),
                (3 * self.game_engine.width // 4 + 50, 160)
            ])
        
        # Draw instructions
        if all(self.selection_confirmed):
            instructions = "LOADING STAGE SELECT..."
        else:
            current_player = "PLAYER 1" if self.active_player == 0 else "PLAYER 2"
            instructions = f"{current_player}: PRESS ENTER TO CONFIRM"
        
        inst_surf = self.game_engine.fonts['small'].render(instructions, True, (200, 200, 200))
        inst_rect = inst_surf.get_rect(center=(self.game_engine.width // 2, 500))
        screen.blit(inst_surf, inst_rect)
        
        # Draw controls hint
        controls_text = "Move: Arrows/WASD   Confirm: Enter/Space"
        controls_surf = self.game_engine.fonts['small'].render(controls_text, True, (150, 150, 150))
        controls_rect = controls_surf.get_rect(center=(self.game_engine.width // 2, 530))
        screen.blit(controls_surf, controls_rect)
    
    def _draw_character_preview(self, screen, character, rect, is_player1):
        # Draw a simple preview of the character
        x = rect.centerx
        y = rect.centery + 30  # Slightly lower to show full character
        
        # Simple animated bounce effect
        bounce = math.sin(self.animation_timer * 0.1) * 5
        y += bounce
        
        if character == "NINJA":
            # Draw ninja
            body_color = (50, 50, 150) if is_player1 else (150, 50, 50)
            
            # Body
            pygame.draw.rect(screen, body_color, (x-15, y-50, 30, 50))
            # Head
            pygame.draw.circle(screen, body_color, (x, y-65), 15)
            # Eyes
            eye_x = x + 5 if is_player1 else x - 5
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, y-65), 5)
            pygame.draw.circle(screen, (0, 0, 0), (eye_x, y-65), 2)
            # Ninja band
            pygame.draw.rect(screen, (0, 0, 0), (x-15, y-72, 30, 5))
            # Sword on back
            if is_player1:
                pygame.draw.rect(screen, (150, 150, 150), (x+15, y-60, 5, 40))
            else:
                pygame.draw.rect(screen, (150, 150, 150), (x-20, y-60, 5, 40))
        
        elif character == "SAMURAI":
            # Draw samurai
            body_color = (70, 50, 150) if is_player1 else (150, 50, 70)
            
            # Body with armor
            pygame.draw.rect(screen, body_color, (x-20, y-50, 40, 50))
            # Armor plates
            armor_color = (100, 100, 180) if is_player1 else (180, 100, 100)
            pygame.draw.rect(screen, armor_color, (x-20, y-50, 40, 15))
            pygame.draw.rect(screen, armor_color, (x-20, y-25, 40, 10))
            # Head with helmet
            pygame.draw.circle(screen, body_color, (x, y-65), 15)
            # Helmet
            helmet_points = [(x-15, y-65), (x+15, y-65), (x, y-85)]
            pygame.draw.polygon(screen, armor_color, helmet_points)
            # Face mask
            pygame.draw.rect(screen, (50, 50, 50), (x-10, y-70, 20, 10))
            # Sword
            if is_player1:
                pygame.draw.rect(screen, (100, 100, 100), (x+20, y-70, 5, 70))
            else:
                pygame.draw.rect(screen, (100, 100, 100), (x-25, y-70, 5, 70))
        
        elif character == "WIZARD":
            # Draw wizard
            body_color = (70, 20, 120) if is_player1 else (120, 20, 70)
            
            # Body
            pygame.draw.rect(screen, body_color, (x-20, y-50, 40, 50))
            # Head
            pygame.draw.circle(screen, body_color, (x, y-65), 15)
            # Wizard hat
            hat_color = (40, 0, 80) if is_player1 else (80, 0, 40)
            hat_points = [(x, y-95), (x-20, y-75), (x+20, y-75)]
            pygame.draw.polygon(screen, hat_color, hat_points)
            pygame.draw.rect(screen, hat_color, (x-25, y-75, 50, 5))
            # Eyes
            eye_x = x + 5 if is_player1 else x - 5
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, y-65), 5)
            pygame.draw.circle(screen, (0, 0, 255), (eye_x, y-65), 2)
            # Staff
            staff_color = (120, 80, 0)
            orb_color = (50, 100, 255)
            if is_player1:
                pygame.draw.rect(screen, staff_color, (x+20, y-80, 5, 80))
                pygame.draw.circle(screen, orb_color, (x+22, y-80), 10)
            else:
                pygame.draw.rect(screen, staff_color, (x-25, y-80, 5, 80))
                pygame.draw.circle(screen, orb_color, (x-22, y-80), 10)
            
            # Magic particles
            for i in range(5):
                angle = (self.animation_timer * 0.1 + i * 1.2) % 6.28
                dist = 15 + math.sin(self.animation_timer * 0.05 + i) * 5
                px = x + math.cos(angle) * dist
                py = y - 90 + math.sin(angle) * dist * 0.5
                particle_color = (100 + i * 30, 100, 255 - i * 30)
                pygame.draw.circle(screen, particle_color, (int(px), int(py)), 2 + i % 2)
        
        elif character == "GUARDIAN":
            # Draw guardian
            body_color = (50, 100, 50) if is_player1 else (100, 50, 50)
            armor_color = (100, 150, 100) if is_player1 else (150, 100, 100)
            
            # Body (wider)
            pygame.draw.rect(screen, body_color, (x-25, y-50, 50, 50))
            # Armor plates
            pygame.draw.rect(screen, armor_color, (x-25, y-50, 50, 15))
            pygame.draw.rect(screen, armor_color, (x-20, y-30, 40, 20))
            # Head with helmet
            pygame.draw.circle(screen, body_color, (x, y-65), 15)
            # Helmet
            pygame.draw.rect(screen, armor_color, (x-18, y-80, 36, 30), border_radius=5)
            # Visor
            pygame.draw.rect(screen, (50, 50, 50), (x-15, y-70, 30, 10))
            # Shoulder guards
            pygame.draw.circle(screen, armor_color, (x-25, y-45), 8)
            pygame.draw.circle(screen, armor_color, (x+25, y-45), 8)
            # Weapon (hammer or shield)
            if is_player1:
                # Shield
                pygame.draw.rect(screen, (220, 220, 100), (x-40, y-60, 20, 40), border_radius=5)
                # Hammer on back
                pygame.draw.rect(screen, (100, 70, 40), (x+25, y-70, 5, 60))
                pygame.draw.rect(screen, (150, 150, 150), (x+15, y-70, 25, 15))
            else:
                # Shield
                pygame.draw.rect(screen, (220, 220, 100), (x+20, y-60, 20, 40), border_radius=5)
                # Hammer on back
                pygame.draw.rect(screen, (100, 70, 40), (x-30, y-70, 5, 60))
                pygame.draw.rect(screen, (150, 150, 150), (x-40, y-70, 25, 15))
    
    def _draw_character_stats(self, screen, character, x, y, color):
        """Draw the character stats below the preview."""
        stats = self.character_stats[character]
        
        # Background panel
        panel_width = 200
        panel_height = 80
        panel_rect = pygame.Rect(x - panel_width//2, y, panel_width, panel_height)
        pygame.draw.rect(screen, (30, 15, 45), panel_rect)
        pygame.draw.rect(screen, color, panel_rect, 1)
        
        # Draw character name
        name_surf = self.game_engine.fonts['medium'].render(character, True, color)
        name_rect = name_surf.get_rect(midtop=(x, y + 5))
        screen.blit(name_surf, name_rect)
        
        # Draw stats
        small_font = self.game_engine.fonts['small']
        
        # Health stat
        health_text = f"HEALTH: {stats['health']}"
        health_surf = small_font.render(health_text, True, (200, 200, 200))
        health_rect = health_surf.get_rect(topleft=(x - panel_width//2 + 10, y + 30))
        screen.blit(health_surf, health_rect)
        
        # Speed stat
        speed_text = f"SPEED: {stats['speed']}"
        speed_surf = small_font.render(speed_text, True, (200, 200, 200))
        speed_rect = speed_surf.get_rect(topleft=(x - panel_width//2 + 10, y + 45))
        screen.blit(speed_surf, speed_rect)
        
        # Attack stat
        attack_text = f"ATTACK: {stats['attack']}"
        attack_surf = small_font.render(attack_text, True, (200, 200, 200))
        attack_rect = attack_surf.get_rect(topleft=(x - panel_width//2 + 10, y + 60))
        screen.blit(attack_surf, attack_rect)
        
        # Special ability
        special_text = f"SPECIAL: {stats['special']}"
        special_surf = small_font.render(special_text, True, (220, 180, 80))
        special_rect = special_surf.get_rect(bottomright=(x + panel_width//2 - 10, y + panel_height - 10))
        screen.blit(special_surf, special_rect)