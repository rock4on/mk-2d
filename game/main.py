import pygame
import sys
from game.engine.game_engine import GameEngine
from game.scenes.menu_scene import MenuScene

# Initialize pygame
pygame.init()

def main():
    # Initialize the game engine
    game_engine = GameEngine(800, 600, "Pixel Kombat")
    
    # Set the starting scene
    menu_scene = MenuScene(game_engine)
    game_engine.change_scene(menu_scene)
    
    # Run the game loop
    game_engine.run()
    
    # Clean up
    pygame.quit()
    sys.exit()

# Run the game if this file is executed directly
if __name__ == "__main__":
    main()