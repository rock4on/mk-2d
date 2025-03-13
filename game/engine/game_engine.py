import pygame
import sys

class GameEngine:
    def __init__(self, width, height, title):
        """Initialize the game engine."""
        self.width = width
        self.height = height
        self.title = title
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_scene = None
        self.fps = 60
        
        # Game states
        self.player1_character = None
        self.player2_character = None
        self.current_stage = None
        
        # Global resources
        self.fonts = {}
        self.sounds = {}
        
        # Initialize resources
        self._init_resources()
    
    def _init_resources(self):
        """Initialize fonts and other resources."""
        pygame.font.init()
        self.fonts['small'] = pygame.font.Font(None, 24)
        self.fonts['medium'] = pygame.font.Font(None, 36)
        self.fonts['large'] = pygame.font.Font(None, 48)
        self.fonts['title'] = pygame.font.Font(None, 72)
    
    def change_scene(self, scene):
        """Change the current scene."""
        self.current_scene = scene
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Let the current scene handle the event
            if self.current_scene:
                self.current_scene.handle_event(event)
    
    def update(self):
        """Update game state."""
        if self.current_scene:
            self.current_scene.update()
    
    def render(self):
        """Render the current scene."""
        if self.current_scene:
            self.current_scene.render(self.screen)
        pygame.display.flip()
    
    def run(self):
        """Run the main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
    
    def quit(self):
        """Quit the game."""
        self.running = False