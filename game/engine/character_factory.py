import importlib
import inspect
from typing import Dict, List, Type, Tuple

from game.engine.character import Character
from game.characters.ninja import Ninja
from game.characters.samurai import Samurai
from game.characters.wizard import Wizard
from game.characters.guardian import Guardian
from game.characters.monk import Monk
from game.characters.pirate import Pirate

class CharacterFactory:
    """
    Factory class for creating character instances and managing character information.
    This provides a centralized way to handle character creation and metadata.
    """
    
    def __init__(self):
        """Initialize the character factory with all available character classes."""
        # Dictionary mapping character names to their classes
        self.character_classes: Dict[str, Type[Character]] = {}
        
        # Dictionary storing character stats and information
        self.character_stats: Dict[str, Dict] = {}
        
        # Auto-discover characters from the game.characters package
        self._discover_characters()
    
    def _discover_characters(self):
        """
        Automatically discover and register all character classes.
        This approach allows new characters to be added with minimal code changes.
        """
        # Explicitly register known characters
        # In a full implementation, this could scan the characters directory dynamically
        character_classes = [Ninja, Samurai, Wizard, Guardian, Monk,Pirate]
        
        for char_class in character_classes:
            char_name = char_class.__name__.upper()
            self.character_classes[char_name] = char_class
            
            # Extract character stats from class attributes
            self._register_character_stats(char_name, char_class)
    
    def _register_character_stats(self, char_name: str, char_class: Type[Character]):
        """
        Register character stats based on class attributes.
        This extracts information directly from the character class.
        
        Args:
            char_name: The uppercase name of the character
            char_class: The character class
        """
        # Create a temporary instance to get actual attribute values
        temp_instance = char_class()
        
        # Extract key stats
        self.character_stats[char_name] = {
            "health": temp_instance.max_health,
            "speed": temp_instance.move_speed,
            "attack": temp_instance.attack_damage,
            "special": self._get_special_name(char_class)
        }
    
    def _get_special_name(self, char_class: Type[Character]) -> str:
        """
        Get a human-readable name for the character's special ability.
        
        Args:
            char_class: The character class
        
        Returns:
            A string describing the special ability
        """
        # Map character classes to their special abilities
        special_names = {
            "Ninja": "Teleport",
            "Samurai": "Rage Mode",
            "Wizard": "Ice Storm",
            "Guardian": "Counter",
            "Monk" : "Meditate",
            "Pirate" : "Shoot"
        }
        
        return special_names.get(char_class.__name__, "Special Attack")
    
    def get_character_names(self) -> List[str]:
        """
        Get a list of all available character names.
        
        Returns:
            List of character names (uppercase)
        """
        return list(self.character_classes.keys())
    
    def get_character_stats(self, char_name: str) -> Dict:
        """
        Get character stats for a specific character.
        
        Args:
            char_name: The uppercase name of the character
            
        Returns:
            Dictionary of character stats
        """
        return self.character_stats.get(char_name, {})
    
    def create_character(self, char_name: str, is_player1: bool = True) -> Character:
        """
        Create a new character instance.
        
        Args:
            char_name: The uppercase name of the character
            is_player1: Whether this is player 1's character (True) or player 2's (False)
            
        Returns:
            A new character instance
            
        Raises:
            ValueError: If the character name is not recognized
        """
        if char_name not in self.character_classes:
            raise ValueError(f"Unknown character: {char_name}")
        
        char_class = self.character_classes[char_name]
        return char_class(is_player1=is_player1)
    
    def apply_health_scaling(self, character: Character, scaling_type: str):
        """
        Apply health scaling to a character based on the scaling type.
        
        Args:
            character: The character instance to modify
            scaling_type: The type of scaling to apply (STANDARD, DOUBLE, HALF, RANDOM)
        """
        if scaling_type == "DOUBLE":
            character.health *= 2
            character.max_health *= 2
        elif scaling_type == "HALF":
            character.health = int(character.health / 2)
            character.max_health = int(character.max_health / 2)
        elif scaling_type == "RANDOM":
            import random
            scale = random.uniform(0.5, 2.0)
            character.health = int(character.health * scale)
            character.max_health = int(character.max_health * scale)
        # For STANDARD, no changes needed