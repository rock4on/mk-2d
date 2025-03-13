import pygame
import math
import random
from game.engine.scene import Scene
from game.scenes.fight_scene import FightScene

class StageSelectScene(Scene):
    """Stage selection scene."""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.stages = ["dojo", "forest", "temple", "arena", "volcano"]
        self.current_selection = 0
        self.background_color = (30, 30, 50)
        self.title_color = (220, 220, 50)
        self.selected_color = (255, 255, 0)
        self.unselected_color = (150, 150, 150)
        
        # Stage preview properties
        self.preview_size = 300
        self.preview_rect = pygame.Rect(
            self.game_engine.width // 2 - self.preview_size // 2,
            150,
            self.preview_size,
            self.preview_size // 2
        )
        
        # Animation and effects
        self.animation_timer = 0
        self.particles = []
        self.generate_particles()
    
    def generate_particles(self):
        """Generate background particles for visual effect."""
        self.particles = []
        
        for _ in range(50):
            particle = {
                'x': random.randint(0, self.game_engine.width),
                'y': random.randint(0, self.game_engine.height),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.2, 1.0),
                'color': (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255)
                )
            }
            self.particles.append(particle)
    
    def update_particles(self):
        """Update particle positions for animation."""
        for particle in self.particles:
            # Move particles upward
            particle['y'] -= particle['speed']
            
            # Wrap around screen
            if particle['y'] < 0:
                particle['y'] = self.game_engine.height
                particle['x'] = random.randint(0, self.game_engine.width)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.current_selection = (self.current_selection - 1) % len(self.stages)
            elif event.key == pygame.K_RIGHT:
                self.current_selection = (self.current_selection + 1) % len(self.stages)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_stage()
            elif event.key == pygame.K_ESCAPE:
                # Go back to character select
                from scenes.character_select_scene import CharacterSelectScene
                # Create a new instance but preserve player characters
                p1_char = self.game_engine.player1_character
                p2_char = self.game_engine.player2_character
                self.game_engine.change_scene(CharacterSelectScene(self.game_engine))
                self.game_engine.player1_character = p1_char
                self.game_engine.player2_character = p2_char
    
    def _select_stage(self):
        # Set the selected stage
        self.game_engine.current_stage = self.stages[self.current_selection]
        
        # Start the fight
        self.game_engine.change_scene(FightScene(self.game_engine))
    
    def update(self):
        self.animation_timer += 1
        self.update_particles()
    
    def render(self, screen):
        # Fill the background
        screen.fill(self.background_color)
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(
                screen, 
                particle['color'], 
                (int(particle['x']), int(particle['y'])), 
                particle['size']
            )
        
        # Draw the title
        title_font = self.game_engine.fonts['large']
        title_surf = title_font.render("SELECT STAGE", True, self.title_color)
        title_rect = title_surf.get_rect(center=(self.game_engine.width // 2, 70))
        
        # Add shadow
        shadow_surf = title_font.render("SELECT STAGE", True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(self.game_engine.width // 2 + 3, 73))
        screen.blit(shadow_surf, shadow_rect)
        screen.blit(title_surf, title_rect)
        
        # Draw stage preview
        self._draw_stage_preview(screen)
        
        # Draw stage selection carousel
        self._draw_stage_selector(screen)
        
        # Draw stage name
        stage_name = self.stages[self.current_selection].upper()
        name_font = self.game_engine.fonts['medium']
        name_surf = name_font.render(stage_name, True, self.selected_color)
        name_rect = name_surf.get_rect(center=(self.game_engine.width // 2, 350))
        screen.blit(name_surf, name_rect)
        
        # Draw instructions
        inst_font = self.game_engine.fonts['small']
        inst_text = "Arrow Keys: Navigate   Enter: Select   Esc: Back"
        inst_surf = inst_font.render(inst_text, True, (180, 180, 180))
        inst_rect = inst_surf.get_rect(center=(self.game_engine.width // 2, 500))
        screen.blit(inst_surf, inst_rect)
        
        # Draw fighter names as a reminder
        player1 = self.game_engine.player1_character.__class__.__name__
        player2 = self.game_engine.player2_character.__class__.__name__
        
        p1_surf = inst_font.render(f"Player 1: {player1}", True, (100, 100, 255))
        p1_rect = p1_surf.get_rect(bottomleft=(20, self.game_engine.height - 20))
        screen.blit(p1_surf, p1_rect)
        
        p2_surf = inst_font.render(f"Player 2: {player2}", True, (255, 100, 100))
        p2_rect = p2_surf.get_rect(bottomright=(self.game_engine.width - 20, self.game_engine.height - 20))
        screen.blit(p2_surf, p2_rect)
    
    def _draw_stage_preview(self, screen):
        """Draw a preview of the currently selected stage."""
        stage = self.stages[self.current_selection]
        
        # Base preview box
        pygame.draw.rect(screen, (0, 0, 0), self.preview_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.preview_rect, 2)
        
        # Fill with stage-specific preview
        inner_rect = self.preview_rect.inflate(-4, -4)
        
        if stage == "dojo":
            # Wooden floor and wall
            floor_rect = pygame.Rect(inner_rect.x, inner_rect.y + inner_rect.height * 0.7, 
                                   inner_rect.width, inner_rect.height * 0.3)
            wall_rect = pygame.Rect(inner_rect.x, inner_rect.y, 
                                  inner_rect.width, inner_rect.height * 0.7)
            
            pygame.draw.rect(screen, (120, 80, 40), wall_rect)
            pygame.draw.rect(screen, (140, 100, 60), floor_rect)
            
            # Wall decorations
            banner_rect = pygame.Rect(inner_rect.x + inner_rect.width * 0.3, inner_rect.y + inner_rect.height * 0.1,
                                    inner_rect.width * 0.4, inner_rect.height * 0.2)
            pygame.draw.rect(screen, (180, 30, 30), banner_rect)
            
            # Wood panels
            for x in range(int(inner_rect.x), int(inner_rect.x + inner_rect.width), 20):
                pygame.draw.line(screen, (100, 70, 30), 
                               (x, inner_rect.y), 
                               (x, inner_rect.y + inner_rect.height * 0.7),
                               1)
            
            # Floor boards
            for y in range(int(inner_rect.y + inner_rect.height * 0.7), int(inner_rect.y + inner_rect.height), 10):
                pygame.draw.line(screen, (100, 70, 30), 
                               (inner_rect.x, y), 
                               (inner_rect.x + inner_rect.width, y),
                               1)
        
        elif stage == "forest":
            # Sky
            sky_rect = pygame.Rect(inner_rect.x, inner_rect.y, 
                                 inner_rect.width, inner_rect.height * 0.6)
            pygame.draw.rect(screen, (100, 150, 255), sky_rect)
            
            # Ground
            ground_rect = pygame.Rect(inner_rect.x, inner_rect.y + inner_rect.height * 0.6, 
                                    inner_rect.width, inner_rect.height * 0.4)
            pygame.draw.rect(screen, (50, 120, 50), ground_rect)
            
            # Trees
            for x in range(int(inner_rect.x), int(inner_rect.x + inner_rect.width), 50):
                tree_height = random.randint(50, 100)
                tree_width = random.randint(10, 20)
                trunk_height = tree_height * 0.3
                
                # Tree trunk
                trunk_rect = pygame.Rect(x, inner_rect.y + inner_rect.height * 0.6 - trunk_height,
                                      tree_width // 3, trunk_height)
                pygame.draw.rect(screen, (100, 70, 40), trunk_rect)
                
                # Tree foliage
                foliage_rect = pygame.Rect(x - tree_width // 2, inner_rect.y + inner_rect.height * 0.6 - tree_height,
                                        tree_width, tree_height - trunk_height)
                pygame.draw.ellipse(screen, (30, 100, 30), foliage_rect)
            
            # Clouds
            for _ in range(3):
                cloud_x = random.randint(int(inner_rect.x), int(inner_rect.x + inner_rect.width))
                cloud_y = random.randint(int(inner_rect.y), int(inner_rect.y + inner_rect.height * 0.3))
                cloud_size = random.randint(20, 40)
                
                pygame.draw.circle(screen, (240, 240, 240), (cloud_x, cloud_y), cloud_size)
                pygame.draw.circle(screen, (240, 240, 240), (cloud_x + cloud_size * 0.8, cloud_y), cloud_size * 0.7)
                pygame.draw.circle(screen, (240, 240, 240), (cloud_x - cloud_size * 0.8, cloud_y), cloud_size * 0.6)
        
        elif stage == "temple":
            # Sky background
            sky_rect = pygame.Rect(inner_rect.x, inner_rect.y, 
                                 inner_rect.width, inner_rect.height)
            pygame.draw.rect(screen, (80, 80, 150), sky_rect)
            
            # Temple structure
            temple_rect = pygame.Rect(inner_rect.x + inner_rect.width * 0.2, inner_rect.y + inner_rect.height * 0.3,
                                    inner_rect.width * 0.6, inner_rect.height * 0.7)
            pygame.draw.rect(screen, (200, 200, 220), temple_rect)
            
            # Temple roof
            roof_points = [
                (inner_rect.x + inner_rect.width * 0.2, inner_rect.y + inner_rect.height * 0.3),
                (inner_rect.x + inner_rect.width * 0.8, inner_rect.y + inner_rect.height * 0.3),
                (inner_rect.x + inner_rect.width * 0.7, inner_rect.y + inner_rect.height * 0.1),
                (inner_rect.x + inner_rect.width * 0.3, inner_rect.y + inner_rect.height * 0.1)
            ]
            pygame.draw.polygon(screen, (120, 120, 150), roof_points)
            
            # Temple columns
            column_width = inner_rect.width * 0.08
            for i in range(5):
                x_pos = inner_rect.x + inner_rect.width * (0.25 + i * 0.125)
                column_rect = pygame.Rect(x_pos, inner_rect.y + inner_rect.height * 0.3,
                                       column_width, inner_rect.height * 0.7)
                pygame.draw.rect(screen, (230, 230, 250), column_rect)
            
            # Floor
            floor_rect = pygame.Rect(inner_rect.x, inner_rect.y + inner_rect.height * 0.9,
                                  inner_rect.width, inner_rect.height * 0.1)
            pygame.draw.rect(screen, (100, 100, 110), floor_rect)
        
        elif stage == "arena":
            # Sandy background
            pygame.draw.rect(screen, (200, 180, 140), inner_rect)
            
            # Colosseum structure - drawn as an ellipse
            colosseum_rect = inner_rect.inflate(-20, -40)
            pygame.draw.ellipse(screen, (180, 160, 120), colosseum_rect)
            
            # Fighting area in center
            arena_rect = pygame.Rect(
                inner_rect.x + inner_rect.width * 0.2,
                inner_rect.y + inner_rect.height * 0.2,
                inner_rect.width * 0.6,
                inner_rect.height * 0.6
            )
            pygame.draw.ellipse(screen, (200, 150, 100), arena_rect)
            
            # Draw audience as small dots
            for _ in range(100):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(inner_rect.width * 0.3, inner_rect.width * 0.45)
                center_x = inner_rect.x + inner_rect.width // 2
                center_y = inner_rect.y + inner_rect.height // 2
                
                dot_x = center_x + math.cos(angle) * distance
                dot_y = center_y + math.sin(angle) * distance * 0.6  # Squashed for perspective
                
                # Only draw dots around the edge (not in fighting area)
                if (dot_x - center_x)**2 + ((dot_y - center_y) / 0.6)**2 >= (inner_rect.width * 0.3)**2:
                    pygame.draw.circle(screen, (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150)), 
                                     (int(dot_x), int(dot_y)), 1)
            
            # Draw pillars around edge
            for i in range(8):
                angle = i * (2 * math.pi / 8)
                distance = inner_rect.width * 0.47
                center_x = inner_rect.x + inner_rect.width // 2
                center_y = inner_rect.y + inner_rect.height // 2
                
                pillar_x = center_x + math.cos(angle) * distance
                pillar_y = center_y + math.sin(angle) * distance * 0.6
                
                pillar_width = inner_rect.width * 0.05
                pillar_height = inner_rect.height * 0.3
                
                pygame.draw.rect(screen, (160, 140, 120), 
                              (pillar_x - pillar_width//2, pillar_y - pillar_height//2, 
                               pillar_width, pillar_height))
        
        elif stage == "volcano":
            # Sky with smoke
            sky_color = (50, 20, 20)
            pygame.draw.rect(screen, sky_color, inner_rect)
            
            # Add some smoke/clouds
            for _ in range(5):
                smoke_x = random.randint(int(inner_rect.x), int(inner_rect.x + inner_rect.width))
                smoke_y = random.randint(int(inner_rect.y), int(inner_rect.y + inner_rect.height * 0.4))
                smoke_size = random.randint(15, 30)
                smoke_color = (80, 80, 80, random.randint(100, 200))
                
                smoke_surf = pygame.Surface((smoke_size * 2, smoke_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surf, smoke_color, (smoke_size, smoke_size), smoke_size)
                screen.blit(smoke_surf, (smoke_x - smoke_size, smoke_y - smoke_size))
            
            # Volcano in background
            volcano_points = [
                (inner_rect.x + inner_rect.width * 0.3, inner_rect.y + inner_rect.height * 0.7),
                (inner_rect.x + inner_rect.width * 0.7, inner_rect.y + inner_rect.height * 0.7),
                (inner_rect.x + inner_rect.width * 0.55, inner_rect.y + inner_rect.height * 0.2),
                (inner_rect.x + inner_rect.width * 0.45, inner_rect.y + inner_rect.height * 0.2)
            ]
            pygame.draw.polygon(screen, (60, 30, 30), volcano_points)
            
            # Lava at top of volcano
            lava_rect = pygame.Rect(
                inner_rect.x + inner_rect.width * 0.45,
                inner_rect.y + inner_rect.height * 0.2,
                inner_rect.width * 0.1,
                inner_rect.height * 0.1
            )
            
            # Pulsing lava effect
            pulse = math.sin(self.animation_timer * 0.1) * 0.2 + 0.8
            lava_color = (
                int(255 * pulse),
                int(100 * pulse),
                0
            )
            pygame.draw.ellipse(screen, lava_color, lava_rect)
            
            # Lava ground
            ground_rect = pygame.Rect(
                inner_rect.x,
                inner_rect.y + inner_rect.height * 0.7,
                inner_rect.width,
                inner_rect.height * 0.3
            )
            pygame.draw.rect(screen, (70, 20, 10), ground_rect)
            
            # Lava cracks
            for _ in range(8):
                crack_x = random.randint(int(inner_rect.x), int(inner_rect.x + inner_rect.width))
                crack_y = random.randint(int(inner_rect.y + inner_rect.height * 0.75), 
                                      int(inner_rect.y + inner_rect.height * 0.95))
                crack_width = random.randint(5, 15)
                crack_height = random.randint(3, 8)
                
                # Pulsing lava
                crack_pulse = math.sin(self.animation_timer * 0.1 + random.random() * 2) * 0.3 + 0.7
                crack_color = (
                    int(255 * crack_pulse),
                    int(100 * crack_pulse),
                    0
                )
                
                pygame.draw.ellipse(screen, crack_color, 
                                 (crack_x - crack_width//2, crack_y - crack_height//2, 
                                  crack_width, crack_height))
        
        # Add transition effect between stages
        if self.animation_timer % 30 < 5:  # Flash effect when changing stages
            flash_surf = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, 50))
            screen.blit(flash_surf, inner_rect)
    
    def _draw_stage_selector(self, screen):
        """Draw the stage selection carousel."""
        # Draw navigation arrows
        arrow_color = (200, 200, 255)
        arrow_size = 20
        
        # Left arrow
        left_points = [
            (100, 350),
            (100 + arrow_size, 350 - arrow_size),
            (100 + arrow_size, 350 + arrow_size)
        ]
        pygame.draw.polygon(screen, arrow_color, left_points)
        
        # Right arrow
        right_points = [
            (700, 350),
            (700 - arrow_size, 350 - arrow_size),
            (700 - arrow_size, 350 + arrow_size)
        ]
        pygame.draw.polygon(screen, arrow_color, right_points)
        
        # Draw stage indicators (dots)
        for i in range(len(self.stages)):
            # Position dots evenly along the bottom
            x_pos = self.game_engine.width // 2 + (i - self.current_selection) * 30
            y_pos = 400
            
            # Current selection is larger and yellow
            if i == self.current_selection:
                color = self.selected_color
                size = 10
            else:
                color = self.unselected_color
                size = 6
            
            pygame.draw.circle(screen, color, (x_pos, y_pos), size)
        
        # Draw small previews of adjacent stages
        preview_width = 80
        preview_height = 40
        
        # Left preview (previous stage)
        left_idx = (self.current_selection - 1) % len(self.stages)
        left_preview_rect = pygame.Rect(150 - preview_width // 2, 350 - preview_height // 2, 
                                      preview_width, preview_height)
        pygame.draw.rect(screen, (80, 80, 80), left_preview_rect)
        pygame.draw.rect(screen, (150, 150, 150), left_preview_rect, 1)
        
        left_name = self.stages[left_idx].upper()
        left_name_surf = self.game_engine.fonts['small'].render(left_name, True, (150, 150, 150))
        left_name_rect = left_name_surf.get_rect(center=(150, 350))
        screen.blit(left_name_surf, left_name_rect)
        
        # Right preview (next stage)
        right_idx = (self.current_selection + 1) % len(self.stages)
        right_preview_rect = pygame.Rect(650 - preview_width // 2, 350 - preview_height // 2, 
                                      preview_width, preview_height)
        pygame.draw.rect(screen, (80, 80, 80), right_preview_rect)
        pygame.draw.rect(screen, (150, 150, 150), right_preview_rect, 1)
        
        right_name = self.stages[right_idx].upper()
        right_name_surf = self.game_engine.fonts['small'].render(right_name, True, (150, 150, 150))
        right_name_rect = right_name_surf.get_rect(center=(650, 350))
        screen.blit(right_name_surf, right_name_rect)