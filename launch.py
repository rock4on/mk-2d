#!/usr/bin/env python3
"""
Game Launcher - Choose which game to run
"""
import os
import sys
import pygame

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND = (20, 20, 40)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Launcher")
clock = pygame.time.Clock()

def draw_button(text, rect, color, hover_color, is_hover=False):
    """Draw a button with text"""
    pygame.draw.rect(screen, hover_color if is_hover else color, rect, 0, 10)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2, 10)
    
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def main():
    running = True
    
    # Define buttons
    basic_sand_button = pygame.Rect(250, 150, 300, 80)
    enhanced_sand_button = pygame.Rect(250, 250, 300, 80)
    fight_button = pygame.Rect(250, 350, 300, 80)
    
    # Button states
    hover_basic = False
    hover_enhanced = False
    hover_fight = False
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is hovering over buttons
        hover_basic = basic_sand_button.collidepoint(mouse_pos)
        hover_enhanced = enhanced_sand_button.collidepoint(mouse_pos)
        hover_fight = fight_button.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if hover_basic:
                        # Run the basic sand simulator
                        pygame.quit()
                        print("Starting Basic Sand Simulator...")
                        os.system("python3 main.py")
                        return
                    elif hover_enhanced:
                        # Run the enhanced sand simulator
                        pygame.quit()
                        print("Starting Enhanced Sand Simulator...")
                        os.system("python3 enhanced_sand.py")
                        return
                    elif hover_fight:
                        # Run the fighting game
                        pygame.quit()
                        print("Starting Pixel Kombat...")
                        os.system("python3 run_game.py")
                        return
        
        # Draw the screen
        screen.fill(BACKGROUND)
        
        # Draw title
        font_title = pygame.font.Font(None, 64)
        title_text = "Choose a Game"
        title_surf = font_title.render(title_text, True, (255, 220, 100))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 80))
        screen.blit(title_surf, title_rect)
        
        # Draw buttons
        draw_button("Basic Sand", basic_sand_button, (50, 100, 150), (70, 130, 200), hover_basic)
        draw_button("Enhanced Sand", enhanced_sand_button, (150, 100, 50), (200, 130, 70), hover_enhanced)
        draw_button("Pixel Kombat", fight_button, (150, 50, 50), (200, 70, 70), hover_fight)
        
        # Draw help text
        font_small = pygame.font.Font(None, 24)
        help_text = "Click on a game to launch it"
        help_surf = font_small.render(help_text, True, (200, 200, 200))
        help_rect = help_surf.get_rect(center=(WIDTH // 2, 460))
        screen.blit(help_surf, help_rect)
        
        # Draw game descriptions
        desc_texts = [
            "Simple 2D sand falling simulation",
            "Advanced sand with water and depth layers",
            "2D fighting game like Mortal Kombat"
        ]
        
        for i, text in enumerate(desc_texts):
            desc_surf = font_small.render(text, True, (180, 180, 180))
            desc_rect = desc_surf.get_rect(center=(WIDTH // 2, 190 + i * 100))
            screen.blit(desc_surf, desc_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()