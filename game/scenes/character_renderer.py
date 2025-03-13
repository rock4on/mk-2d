import pygame
import math
import random
from typing import Dict, List, Tuple, Optional

class CharacterRenderer:
    """
    Centralized rendering system for all character types.
    This class handles the visual representation of characters for both
    previews in character selection and for rendering in-game.
    """
    
    def __init__(self, game_engine):
        """
        Initialize the character renderer.
        
        Args:
            game_engine: Reference to the game engine
        """
        self.game_engine = game_engine
        self.animation_timer = 0
        
        # Color schemes for different character types and players
        self.color_schemes = {
            "NINJA": {
                "player1": {
                    "body": (50, 50, 150),
                    "accent": (200, 50, 50),
                    "weapon": (150, 150, 150)
                },
                "player2": {
                    "body": (150, 50, 50),
                    "accent": (50, 50, 200),
                    "weapon": (150, 150, 150)
                }
            },
            "SAMURAI": {
                "player1": {
                    "body": (70, 50, 150),
                    "armor": (100, 100, 180),
                    "weapon": (100, 100, 100)
                },
                "player2": {
                    "body": (150, 50, 70),
                    "armor": (180, 100, 100),
                    "weapon": (100, 100, 100)
                }
            },
            "WIZARD": {
                "player1": {
                    "body": (70, 20, 120),
                    "hat": (40, 0, 80),
                    "staff": (120, 80, 0),
                    "orb": (50, 100, 255)
                },
                "player2": {
                    "body": (120, 20, 70),
                    "hat": (80, 0, 40),
                    "staff": (120, 80, 0),
                    "orb": (50, 100, 255)
                }
            },
            "GUARDIAN": {
                "player1": {
                    "body": (50, 100, 50),
                    "armor": (100, 150, 100),
                    "shield": (220, 220, 100),
                    "weapon": (150, 150, 150)
                },
                "player2": {
                    "body": (100, 50, 50),
                    "armor": (150, 100, 100),
                    "shield": (220, 220, 100),
                    "weapon": (150, 150, 150)
                }
            }
        }
        
        # Define the render methods for each character type
        self.render_methods = {
            "NINJA": self._render_ninja,
            "SAMURAI": self._render_samurai,
            "WIZARD": self._render_wizard,
            "GUARDIAN": self._render_guardian
        }
        
        # Define preview methods for each character type in selection screen
        self.preview_methods = {
            "NINJA": self._preview_ninja,
            "SAMURAI": self._preview_samurai,
            "WIZARD": self._preview_wizard,
            "GUARDIAN": self._preview_guardian
        }
    
    def update(self):
        """Update animations."""
        self.animation_timer += 1
    
    def render_character(self, screen, character, position, is_player1=True, animation_state="idle"):
        """
        Render a character at the given position with specified animation state.
        
        Args:
            screen: Pygame surface to render to
            character: Character instance
            position: (x, y) position
            is_player1: Whether this is player 1's character
            animation_state: Current animation state
        """
        character_type = character.__class__.__name__.upper()
        
        # Get the appropriate render method
        render_method = self.render_methods.get(character_type, self._render_default)
        
        # Call the render method
        render_method(screen, character, position, is_player1, animation_state)
    
    def render_preview(self, screen, character_type, rect, is_player1=True):
        """
        Render a character preview in the selection screen.
        
        Args:
            screen: Pygame surface to render to
            character_type: String name of character type
            rect: Rect area to draw the preview in
            is_player1: Whether this is player 1's character
        """
        # Center position with small bounce animation
        x = rect.centerx
        y = rect.centery + 30  # Slightly lower to show full character
        bounce = math.sin(self.animation_timer * 0.1) * 5
        y += bounce
        
        # Get the appropriate preview method
        preview_method = self.preview_methods.get(character_type, self._preview_default)
        
        # Call the preview method
        preview_method(screen, x, y, is_player1)
    
    def _get_colors(self, character_type, is_player1):
        """Get the color scheme for a character."""
        player_key = "player1" if is_player1 else "player2"
        
        # Default colors as fallback
        default_colors = {
            "body": (100, 100, 150) if is_player1 else (150, 100, 100),
            "accent": (50, 50, 150) if is_player1 else (150, 50, 50),
            "weapon": (150, 150, 150)
        }
        
        # Get character-specific color scheme or use default
        if character_type in self.color_schemes and player_key in self.color_schemes[character_type]:
            return self.color_schemes[character_type][player_key]
        else:
            return default_colors
    
    #
    # Character Preview Methods for Selection Screen
    #
    
    def _preview_ninja(self, screen, x, y, is_player1):
        """Draw ninja character preview."""
        colors = self._get_colors("NINJA", is_player1)
        
        # Body
        pygame.draw.rect(screen, colors["body"], (x-15, y-50, 30, 50))
        # Head
        pygame.draw.circle(screen, colors["body"], (x, y-65), 15)
        # Eyes
        eye_x = x + 5 if is_player1 else x - 5
        pygame.draw.circle(screen, (255, 255, 255), (eye_x, y-65), 5)
        pygame.draw.circle(screen, (0, 0, 0), (eye_x, y-65), 2)
        # Ninja band
        pygame.draw.rect(screen, (0, 0, 0), (x-15, y-72, 30, 5))
        # Sword on back
        if is_player1:
            pygame.draw.rect(screen, colors["weapon"], (x+15, y-60, 5, 40))
        else:
            pygame.draw.rect(screen, colors["weapon"], (x-20, y-60, 5, 40))
        
        # Ninja scarf
        scarf_color = colors["accent"]
        scarf_points = []
        
        if is_player1:
            wind_effect = math.sin(self.animation_timer * 0.1) * 5
            scarf_points = [
                (x - 5, y - 75),
                (x - 15, y - 75),
                (x - 25, y - 65 + wind_effect),
                (x - 20, y - 60 + wind_effect),
                (x - 10, y - 70)
            ]
        else:
            wind_effect = math.sin(self.animation_timer * 0.1) * 5
            scarf_points = [
                (x + 5, y - 75),
                (x + 15, y - 75),
                (x + 25, y - 65 + wind_effect),
                (x + 20, y - 60 + wind_effect),
                (x + 10, y - 70)
            ]
        
        if len(scarf_points) > 2:  # Need at least 3 points for a polygon
            pygame.draw.polygon(screen, scarf_color, scarf_points)
    
    def _preview_samurai(self, screen, x, y, is_player1):
        """Draw samurai character preview."""
        colors = self._get_colors("SAMURAI", is_player1)
        
        # Body with armor
        pygame.draw.rect(screen, colors["body"], (x-20, y-50, 40, 50))
        # Armor plates
        pygame.draw.rect(screen, colors["armor"], (x-20, y-50, 40, 15))
        pygame.draw.rect(screen, colors["armor"], (x-20, y-25, 40, 10))
        # Head with helmet
        pygame.draw.circle(screen, colors["body"], (x, y-65), 15)
        # Helmet
        helmet_points = [(x-15, y-65), (x+15, y-65), (x, y-85)]
        pygame.draw.polygon(screen, colors["armor"], helmet_points)
        # Face mask
        pygame.draw.rect(screen, (50, 50, 50), (x-10, y-70, 20, 10))
        # Sword
        if is_player1:
            pygame.draw.rect(screen, colors["weapon"], (x+20, y-70, 5, 70))
        else:
            pygame.draw.rect(screen, colors["weapon"], (x-25, y-70, 5, 70))
    
    def _preview_wizard(self, screen, x, y, is_player1):
        """Draw wizard character preview."""
        colors = self._get_colors("WIZARD", is_player1)
        
        # Body
        pygame.draw.rect(screen, colors["body"], (x-20, y-50, 40, 50))
        # Head
        pygame.draw.circle(screen, colors["body"], (x, y-65), 15)
        # Wizard hat
        hat_points = [(x, y-95), (x-20, y-75), (x+20, y-75)]
        pygame.draw.polygon(screen, colors["hat"], hat_points)
        pygame.draw.rect(screen, colors["hat"], (x-25, y-75, 50, 5))
        # Eyes
        eye_x = x + 5 if is_player1 else x - 5
        pygame.draw.circle(screen, (255, 255, 255), (eye_x, y-65), 5)
        pygame.draw.circle(screen, (0, 0, 255), (eye_x, y-65), 2)
        # Staff
        if is_player1:
            pygame.draw.rect(screen, colors["staff"], (x+20, y-80, 5, 80))
            pygame.draw.circle(screen, colors["orb"], (x+22, y-80), 10)
        else:
            pygame.draw.rect(screen, colors["staff"], (x-25, y-80, 5, 80))
            pygame.draw.circle(screen, colors["orb"], (x-22, y-80), 10)
        
        # Magic particles
        for i in range(5):
            angle = (self.animation_timer * 0.1 + i * 1.2) % 6.28
            dist = 15 + math.sin(self.animation_timer * 0.05 + i) * 5
            px = x + math.cos(angle) * dist
            py = y - 90 + math.sin(angle) * dist * 0.5
            particle_color = (100 + i * 30, 100, 255 - i * 30)
            pygame.draw.circle(screen, particle_color, (int(px), int(py)), 2 + i % 2)
    
    def _preview_guardian(self, screen, x, y, is_player1):
        """Draw guardian character preview."""
        colors = self._get_colors("GUARDIAN", is_player1)
        
        # Body (wider)
        pygame.draw.rect(screen, colors["body"], (x-25, y-50, 50, 50))
        # Armor plates
        pygame.draw.rect(screen, colors["armor"], (x-25, y-50, 50, 15))
        pygame.draw.rect(screen, colors["armor"], (x-20, y-30, 40, 20))
        # Head with helmet
        pygame.draw.circle(screen, colors["body"], (x, y-65), 15)
        # Helmet
        pygame.draw.rect(screen, colors["armor"], (x-18, y-80, 36, 30), border_radius=5)
        # Visor
        pygame.draw.rect(screen, (50, 50, 50), (x-15, y-70, 30, 10))
        # Shoulder guards
        pygame.draw.circle(screen, colors["armor"], (x-25, y-45), 8)
        pygame.draw.circle(screen, colors["armor"], (x+25, y-45), 8)
        # Weapon (hammer or shield)
        if is_player1:
            # Shield
            pygame.draw.rect(screen, colors["shield"], (x-40, y-60, 20, 40), border_radius=5)
            # Hammer on back
            pygame.draw.rect(screen, (100, 70, 40), (x+25, y-70, 5, 60))
            pygame.draw.rect(screen, colors["weapon"], (x+15, y-70, 25, 15))
        else:
            # Shield
            pygame.draw.rect(screen, colors["shield"], (x+20, y-60, 20, 40), border_radius=5)
            # Hammer on back
            pygame.draw.rect(screen, (100, 70, 40), (x-30, y-70, 5, 60))
            pygame.draw.rect(screen, colors["weapon"], (x-40, y-70, 25, 15))
    
    def _preview_default(self, screen, x, y, is_player1):
        """Draw default character preview for any unknown characters."""
        colors = self._get_colors("DEFAULT", is_player1)
        
        # Simple body
        pygame.draw.rect(screen, colors["body"], (x-20, y-50, 40, 50))
        # Head
        pygame.draw.circle(screen, colors["body"], (x, y-65), 15)
        # Eyes
        eye_x = x + 5 if is_player1 else x - 5
        pygame.draw.circle(screen, (255, 255, 255), (eye_x, y-65), 5)
        pygame.draw.circle(screen, (0, 0, 0), (eye_x, y-65), 2)
        # Question mark to indicate unknown
        text = self.game_engine.fonts['small'].render("?", True, (255, 255, 255))
        text_rect = text.get_rect(center=(x, y-30))
        screen.blit(text, text_rect)
    
    #
    # Full Character Rendering Methods for Game
    #
    
    def _render_ninja(self, screen, character, position, is_player1, animation_state):
        """Render ninja character during gameplay."""
        # Delegate to the character's own render method for now
        # In a full implementation, this would contain the rendering logic
        character.render(screen)
    
    def _render_samurai(self, screen, character, position, is_player1, animation_state):
        """Render samurai character during gameplay."""
        character.render(screen)
    
    def _render_wizard(self, screen, character, position, is_player1, animation_state):
        """Render wizard character during gameplay."""
        character.render(screen)
    
    def _render_guardian(self, screen, character, position, is_player1, animation_state):
        """Render guardian character during gameplay."""
        character.render(screen)
    
    def _render_default(self, screen, character, position, is_player1, animation_state):
        """Render default character during gameplay."""
        character.render(screen)