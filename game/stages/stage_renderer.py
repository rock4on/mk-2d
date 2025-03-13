import pygame
import math
import random
from game.stages.stage_data import STAGE_DATA

class StageRenderer:
    """Handles rendering of stage backgrounds."""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.width = game_engine.width
        self.height = game_engine.height
        
        # Time offset for animations
        self.time_offset = pygame.time.get_ticks()
    
    def get_stage_data(self, stage_name):
        """
        Get data for a specific stage.
        
        Args:
            stage_name: Name of the stage
            
        Returns:
            Dict with stage properties or default values if stage not found
        """
        return STAGE_DATA.get(stage_name, {
            "color": (0, 0, 0),
            "floor": 450,
            "gravity": 0.8,
            "weather": None
        })
    
    def render(self, screen, stage_name):
        """
        Render the stage background.
        
        Args:
            screen: Pygame surface to render to
            stage_name: Name of the stage to render
        """
        # Update time for animations
        current_time = pygame.time.get_ticks()
        time_delta = current_time - self.time_offset
        
        # Get the rendering method for this stage
        render_methods = {
            "dojo": self._render_dojo,
            "forest": self._render_forest,
            "temple": self._render_temple,
            "arena": self._render_arena,
            "volcano": self._render_volcano
        }
        
        # Call the appropriate render method or use default
        if stage_name in render_methods:
            render_methods[stage_name](screen, time_delta)
        else:
            # Default rendering for unknown stages
            self._render_default(screen, stage_name)
    
    def _render_default(self, screen, stage_name):
        """Default rendering for unknown stages."""
        # Get stage data (or default)
        stage_data = self.get_stage_data(stage_name)
        
        # Fill with background color
        screen.fill(stage_data.get("color", (0, 0, 0)))
        
        # Draw ground
        ground_rect = pygame.Rect(0, stage_data.get("floor", 450), self.width, 150)
        pygame.draw.rect(screen, (60, 40, 20), ground_rect)
    
    def _render_dojo(self, screen, time_delta):
        """Render dojo stage background."""
        # Draw wooden wall with detailed texturing
        wall_color = (120, 80, 40)
        pygame.draw.rect(screen, wall_color, (0, 0, self.width, 450))
        
        # Draw wall panels with wood grain effect
        panel_color = (140, 100, 50)
        for x in range(0, self.width, 100):
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
        
        # Ground
        ground_rect = pygame.Rect(0, 450, self.width, 150)
        pygame.draw.rect(screen, (60, 40, 20), ground_rect)
    
    def _render_forest(self, screen, time_delta):
        """Render forest stage background."""
        # Sky with gradient
        sky_rect = pygame.Rect(0, 0, self.width, 200)
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
            (self.width, 180),
            (self.width, 200)
        ]
        pygame.draw.polygon(screen, mountain_color, mountain_points)
        
        # Ground
        ground_color = (50, 100, 50)
        pygame.draw.rect(screen, ground_color, (0, 200, self.width, 250))
        
        # Add some grass details
        for x in range(0, self.width, 30):
            # Use time_delta to make grass sway slightly
            sway = math.sin((x + time_delta * 0.001) * 0.1) * 2
            grass_height = random.randint(5, 15)
            grass_color = (30, 120, 30)
            
            # Draw grass blade with sway
            grass_points = [
                (x, 450),
                (x + 10, 450),
                (x + 5 + sway, 450 - grass_height)
            ]
            pygame.draw.polygon(screen, grass_color, grass_points)
        
        # Draw ground
        ground_rect = pygame.Rect(0, 450, self.width, 150)
        pygame.draw.rect(screen, (60, 40, 20), ground_rect)
    
    def _render_temple(self, screen, time_delta):
        """Render temple stage background."""
        # Sky with atmospheric perspective
        sky_color = (60, 60, 100)
        pygame.draw.rect(screen, sky_color, (0, 0, self.width, 450))
        
        # Add some distant clouds
        for i in range(3):
            cloud_x = ((i * 300 + time_delta // 100) % self.width)
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
        glow_radius = 50 + math.sin(time_delta * 0.002) * 10
        glow_alpha = 50 + int(math.sin(time_delta * 0.002) * 20)
        glow_surf = pygame.Surface((int(glow_radius * 2), int(glow_radius)), pygame.SRCALPHA)
        glow_color = (160, 120, 255, glow_alpha)
        pygame.draw.ellipse(glow_surf, glow_color, (0, 0, int(glow_radius * 2), int(glow_radius)))
        screen.blit(glow_surf, (400 - glow_radius, 400 - glow_radius // 2))
        
        # Draw ground
        ground_rect = pygame.Rect(0, 450, self.width, 150)
        pygame.draw.rect(screen, (60, 40, 20), ground_rect)
    
    def _render_arena(self, screen, time_delta):
        """Render arena stage background."""
        # Sandy background
        pygame.draw.rect(screen, (200, 180, 140), (0, 0, self.width, 450))
        
        # Draw arena circle
        arena_center = (self.width // 2, 450)
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
        
        # Draw ground
        ground_rect = pygame.Rect(0, 450, self.width, 150)
        pygame.draw.rect(screen, (60, 40, 20), ground_rect)
    
    def _render_volcano(self, screen, time_delta):
        """Render volcano stage background."""
        # Dark sky with red tint
        sky_rect = pygame.Rect(0, 0, self.width, 450)
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
        lava_radius = 30 + math.sin(time_delta * 0.001) * 5
        pygame.draw.circle(screen, (255, 100, 0), (600, 150), int(lava_radius))
        
        # Red glow over the scene
        glow_surf = pygame.Surface((self.width, 450), pygame.SRCALPHA)
        glow_surf.fill((255, 0, 0, 10))
        screen.blit(glow_surf, (0, 0))
        
        # Add some floating ash particles
        for i in range(20):
            x = (i * 40 + time_delta // 50) % self.width
            y = ((i * 30 + time_delta // 30) % 400) + 50
            size = random.randint(1, 3)
            alpha = random.randint(50, 150)
            
            ash_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            ash_color = (150, 150, 150, alpha)
            pygame.draw.circle(ash_surf, ash_color, (size, size), size)
            screen.blit(ash_surf, (x, y))
        
        # Draw ground (dark volcanic rock)
        ground_rect = pygame.Rect(0, 450, self.width, 150)
        pygame.draw.rect(screen, (40, 30, 30), ground_rect)
