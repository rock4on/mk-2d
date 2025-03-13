import pygame
import math

class CombatManager:
    """Handles combat interactions between characters."""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
    
    def check_combat_interactions(self, player1, player2):
        """
        Check for combat interactions between two players.
        Returns a list of combat results (hits, blocks, knockouts).
        """
        results = []
        
        # First check for knockouts based on health (regardless of attacks)
        if player1.health <= 0 and not player1.is_knocked_out:
            player1.knock_out()
            results.append({
                "type": "knockout",
                "attacker": player2,
                "defender": player1
            })
            return results  # End round immediately
            
        if player2.health <= 0 and not player2.is_knocked_out:
            player2.knock_out()
            results.append({
                "type": "knockout",
                "attacker": player1,
                "defender": player2
            })
            return results  # End round immediately
        
        # Check player1 attacking player2
        if player1.is_attacking and not player2.is_knocked_out:
            if self._check_hit(player1, player2):
                damage = player1.get_attack_damage()
                hit_successful = player2.take_damage(damage)
                
                if hit_successful:
                    # Hit connected
                    player1.successful_hit()
                    results.append({
                        "type": "hit",
                        "attacker": player1,
                        "defender": player2,
                        "position": player2.position,
                        "damage": damage,
                        "attack_type": player1.attack_type,
                        "facing_right": player1.facing_right
                    })
                    
                    # Check if knocked out
                    if player2.health <= 0:
                        player2.knock_out()
                        results.append({
                            "type": "knockout",
                            "attacker": player1,
                            "defender": player2
                        })
                else:
                    # Hit was blocked
                    results.append({
                        "type": "block",
                        "attacker": player1,
                        "defender": player2,
                        "position": player2.position
                    })
        
        # Check player2 attacking player1
        if player2.is_attacking and not player1.is_knocked_out:
            if self._check_hit(player2, player1):
                damage = player2.get_attack_damage()
                hit_successful = player1.take_damage(damage)
                
                if hit_successful:
                    # Hit connected
                    player2.successful_hit()
                    results.append({
                        "type": "hit",
                        "attacker": player2,
                        "defender": player1,
                        "position": player1.position,
                        "damage": damage,
                        "attack_type": player2.attack_type,
                        "facing_right": player2.facing_right
                    })
                    
                    # Check if knocked out
                    if player1.health <= 0:
                        player1.knock_out()
                        results.append({
                            "type": "knockout",
                            "attacker": player2,
                            "defender": player1
                        })
                else:
                    # Hit was blocked
                    results.append({
                        "type": "block",
                        "attacker": player2,
                        "defender": player1,
                        "position": player1.position
                    })
        
        return results
    
    def _check_hit(self, attacker, defender):
        """Check if an attack hits with improved hitbox detection."""
        # Define hitboxes based on character state
        attacker_rect = pygame.Rect(
            attacker.position[0] - 20, 
            attacker.position[1] - 100,
            40, 100
        )
        
        defender_rect = pygame.Rect(
            defender.position[0] - 20, 
            defender.position[1] - 100,
            40, 100
        )
        
        # Create attack hitbox based on attack type and facing direction
        attack_rect = None
        
        if attacker.attack_type == "punch":
            # Punch has medium range
            if attacker.facing_right:
                attack_rect = pygame.Rect(
                    attacker.position[0] + 10,
                    attacker.position[1] - 60,
                    40, 40
                )
            else:
                attack_rect = pygame.Rect(
                    attacker.position[0] - 50,
                    attacker.position[1] - 60,
                    40, 40
                )
                
        elif attacker.attack_type == "kick":
            # Kick has longer range
            if attacker.facing_right:
                attack_rect = pygame.Rect(
                    attacker.position[0] + 10,
                    attacker.position[1] - 40,
                    60, 30
                )
            else:
                attack_rect = pygame.Rect(
                    attacker.position[0] - 70,
                    attacker.position[1] - 40,
                    60, 30
                )
                
        elif attacker.attack_type == "special":
            # Special has area effect
            radius = 70
            attack_rect = pygame.Rect(
                attacker.position[0] - radius,
                attacker.position[1] - radius,
                radius * 2, radius * 2
            )
        
        # Check if attack hitbox intersects with defender's body
        if attack_rect and attack_rect.colliderect(defender_rect):
            # If defender is blocking, check if they're facing the right way
            if defender.is_blocking:
                is_block_effective = (defender.facing_right and attacker.position[0] < defender.position[0]) or \
                                    (not defender.facing_right and attacker.position[0] > defender.position[0])
                # Still register a hit (for effects) but damage reduction happens in take_damage()
                return True
            return True
            
        return False