import pygame

class Scene:
    """Base class for all game scenes."""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
    
    def handle_event(self, event):
        """Handle pygame events."""
        pass
    
    def update(self):
        """Update scene state."""
        pass
    
    def render(self, screen):
        """Render the scene."""
        pass
    
    def enter(self):
        """Called when this scene becomes active."""
        pass
    
    def exit(self):
        """Called when this scene is no longer active."""
        pass