import pygame
from game.engine.scene import Scene

class MenuScene(Scene):
    """Main menu scene."""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.options = ["FIGHT", "OPTIONS", "QUIT"]
        self.selected_option = 0
        self.background_color = (20, 20, 40)
        self.title_color = (255, 50, 50)
        self.option_color = (220, 220, 220)
        self.selected_color = (255, 200, 0)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._select_option()
    
    def _select_option(self):
        if self.options[self.selected_option] == "FIGHT":
            # Go to character selection screen - import here to avoid circular import
            from game.scenes.character_select_scene import CharacterSelectScene
            self.game_engine.change_scene(CharacterSelectScene(self.game_engine))
        elif self.options[self.selected_option] == "OPTIONS":
            # Options not implemented yet
            pass
        elif self.options[self.selected_option] == "QUIT":
            # Quit the game
            self.game_engine.quit()
    
    def update(self):
        pass
    
    def render(self, screen):
        # Fill the background
        screen.fill(self.background_color)
        
        # Draw the title
        title_font = self.game_engine.fonts['title']
        title_surf = title_font.render("PIXEL KOMBAT", True, self.title_color)
        title_rect = title_surf.get_rect(center=(self.game_engine.width // 2, 100))
        screen.blit(title_surf, title_rect)
        
        # Draw the menu options
        option_font = self.game_engine.fonts['large']
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.option_color
            option_surf = option_font.render(option, True, color)
            option_rect = option_surf.get_rect(center=(self.game_engine.width // 2, 250 + i * 70))
            screen.blit(option_surf, option_rect)