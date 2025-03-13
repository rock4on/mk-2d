import pygame
import math
from game.engine.scene import Scene

class GameOverScene(Scene):
    """Game over scene showing the winner."""
    
    def __init__(self, game_engine, winner):
        super().__init__(game_engine)
        self.winner = winner  # 1 or 2 for player number
        self.background_color = (20, 20, 30)
        self.timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # Return to the main menu - import here to avoid circular import
                from game.scenes.menu_scene import MenuScene
                self.game_engine.change_scene(MenuScene(self.game_engine))
    
    def update(self):
        self.timer += 1
    
    def render(self, screen):
        # Fill background
        screen.fill(self.background_color)
        
        # Create a pulsing effect for the text
        pulse = abs(math.sin(self.timer * 0.05)) * 30 + 225
        
        # Draw winner text
        title_font = self.game_engine.fonts['title']
        title_text = f"PLAYER {self.winner} WINS!"
        title_color = (pulse, pulse, 50) if self.winner == 1 else (pulse, 50, 50)
        title_surf = title_font.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(center=(self.game_engine.width // 2, 200))
        
        # Add a shadow effect
        shadow_surf = title_font.render(title_text, True, (40, 40, 40))
        shadow_rect = shadow_surf.get_rect(center=(self.game_engine.width // 2 + 4, 204))
        screen.blit(shadow_surf, shadow_rect)
        screen.blit(title_surf, title_rect)
        
        # Draw continue text
        if self.timer > 60:  # Wait a bit before showing this
            continue_font = self.game_engine.fonts['medium']
            continue_text = "Press ENTER to continue"
            continue_surf = continue_font.render(continue_text, True, (200, 200, 200))
            continue_rect = continue_surf.get_rect(center=(self.game_engine.width // 2, 400))
            screen.blit(continue_surf, continue_rect)