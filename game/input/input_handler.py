import pygame

class InputHandler:
    """Handles player input for combat and movement."""
    
    def __init__(self):
        # Keyboard state for smoother controls
        self.key_states = {
            # Player 1 controls
            pygame.K_a: False,  # Left
            pygame.K_d: False,  # Right
            pygame.K_w: False,  # Jump
            pygame.K_s: False,  # Block
            pygame.K_g: False,  # Punch
            pygame.K_h: False,  # Kick
            pygame.K_j: False,  # Special
            
            # Player 2 controls (only used if AI is disabled)
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_KP1: False,
            pygame.K_KP2: False,
            pygame.K_KP3: False,
        }
    
    def handle_event(self, event):
        """
        Update key states based on pygame events.
        
        Args:
            event: pygame event object
        """
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_states:
                self.key_states[event.key] = True
        
        elif event.type == pygame.KEYUP:
            if event.key in self.key_states:
                self.key_states[event.key] = False
                
                # Special handling for block release
                if event.key == pygame.K_s:
                    # This will be handled in process_input
                    pass
                if event.key == pygame.K_DOWN:
                    # This will be handled in process_input
                    pass
    
    def process_input(self, player1, player2, ai_enabled):
        """
        Process key states to control players.
        
        Args:
            player1: Player 1 character
            player2: Player 2 character
            ai_enabled: Whether player 2 is AI-controlled
        """
        # Player 1 controls
        if not player1.is_knocked_out:
            # Movement
            if self.key_states[pygame.K_a]:
                player1.move_left()
            elif self.key_states[pygame.K_d]:
                player1.move_right()
                
            # Jumping - only trigger once
            if self.key_states[pygame.K_w]:
                if not player1.is_jumping:
                    player1.jump()
                    self.key_states[pygame.K_w] = False  # Require key re-press
            
            # Blocking - continuous
            if self.key_states[pygame.K_s]:
                player1.block()
            else:
                player1.stop_block()
            
            # Attacks - only trigger once per press
            if self.key_states[pygame.K_g]:
                player1.punch()
                self.key_states[pygame.K_g] = False  # Require key re-press
            
            elif self.key_states[pygame.K_h]:
                player1.kick()
                self.key_states[pygame.K_h] = False  # Require key re-press
            
            elif self.key_states[pygame.K_j]:
                player1.special_move()
                self.key_states[pygame.K_j] = False  # Require key re-press
        
        # Player 2 controls - only if AI is disabled
        if not ai_enabled and not player2.is_knocked_out:
            # Movement
            if self.key_states[pygame.K_LEFT]:
                player2.move_left()
            elif self.key_states[pygame.K_RIGHT]:
                player2.move_right()
                
            # Jumping - only trigger once
            if self.key_states[pygame.K_UP]:
                if not player2.is_jumping:
                    player2.jump()
                    self.key_states[pygame.K_UP] = False  # Require key re-press
            
            # Blocking - continuous
            if self.key_states[pygame.K_DOWN]:
                player2.block()
            else:
                player2.stop_block()
            
            # Attacks - only trigger once per press
            if self.key_states[pygame.K_KP1]:
                player2.punch()
                self.key_states[pygame.K_KP1] = False  # Require key re-press
            
            elif self.key_states[pygame.K_KP2]:
                player2.kick()
                self.key_states[pygame.K_KP2] = False  # Require key re-press
            
            elif self.key_states[pygame.K_KP3]:
                player2.special_move()
                self.key_states[pygame.K_KP3] = False  # Require key re-press
