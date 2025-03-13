import pygame
import math
import random

class MenuScene:
    """Main menu scene with animated background that matches the fighting game theme."""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.options = ["FIGHT", "OPTIONS", "QUIT"]
        self.selected_option = 0
        self.background_color = (20, 20, 40)
        self.title_color = (255, 50, 50)
        self.option_color = (220, 220, 220)
        self.selected_color = (255, 200, 0)
        
        # Animation properties
        self.animation_timer = 0
        
        # Fighting stage background elements
        self.stage_elements = {
            'sky_color': (30, 30, 60),
            'ground_color': (60, 40, 20),
            'ground_height': 450,
        }
        
        # Create lightning flashes
        self.lightning = {
            'active': False,
            'timer': 0,
            'duration': 0,
            'next': random.randint(100, 300)
        }
        
        # Fighting character silhouettes for dynamic combat animations
        self.fighters = []
        self.generate_fighters()
        
        # Floating combat text effects (like "KO", "FIGHT", etc.)
        self.combat_texts = []
        
        # Fire and impact particles
        self.particles = []
        
        # Health bars for aesthetic
        self.health_bars = [
            {'x': 150, 'width': 200, 'health': 100, 'color': (100, 200, 100)},
            {'x': 450, 'width': 200, 'health': 100, 'color': (200, 100, 100)}
        ]
    
    def generate_fighters(self):
        """Generate fighter silhouettes for combat animations."""
        # Create two fighters facing each other
        fighter1 = {
            'x': 200,
            'y': 350,
            'width': 40,
            'height': 80,
            'color': (50, 100, 200),
            'facing_right': True,
            'state': 'idle',
            'frame': 0,
            'attack_cooldown': 0,
            'move_cooldown': 0
        }
        
        fighter2 = {
            'x': 600,
            'y': 350,
            'width': 40,
            'height': 80,
            'color': (200, 50, 50),
            'facing_right': False,
            'state': 'idle',
            'frame': 0,
            'attack_cooldown': 0,
            'move_cooldown': 0
        }
        
        self.fighters = [fighter1, fighter2]
    
    def add_combat_text(self, text, position, color, size=36, duration=60):
        """Add a floating combat text effect."""
        self.combat_texts.append({
            'text': text,
            'x': position[0],
            'y': position[1],
            'color': color,
            'size': size,
            'timer': 0,
            'duration': duration,
            'scale': 1.0
        })
    
    def add_impact_particles(self, position, color, count=10):
        """Add impact particles at the given position."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            size = random.uniform(2, 6)
            lifetime = random.randint(10, 30)
            
            self.particles.append({
                'x': position[0],
                'y': position[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 1,  # Upward bias
                'size': size,
                'color': color,
                'lifetime': lifetime,
                'type': 'impact'
            })
    
    def add_fire_particle(self, position, color):
        """Add a fire/energy particle effect."""
        direction = random.uniform(-0.5, 0.5)
        speed = random.uniform(0.5, 2)
        size = random.uniform(2, 8)
        lifetime = random.randint(20, 40)
        
        self.particles.append({
            'x': position[0],
            'y': position[1],
            'vx': direction,
            'vy': -speed,  # Upward
            'size': size,
            'color': color,
            'lifetime': lifetime,
            'type': 'fire'
        })
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                self._play_selection_sound()
                # Add impact particles for menu navigation
                menu_y = 250 + self.selected_option * 70
                self.add_impact_particles((self.game_engine.width // 2, menu_y), 
                                        (255, 200, 0), count=5)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                self._play_selection_sound()
                # Add impact particles for menu navigation
                menu_y = 250 + self.selected_option * 70
                self.add_impact_particles((self.game_engine.width // 2, menu_y), 
                                        (255, 200, 0), count=5)
            elif event.key == pygame.K_RETURN:
                self._play_confirm_sound()
                # Add a "FIGHT" text effect when selecting an option
                if self.options[self.selected_option] == "FIGHT":
                    self.add_combat_text("FIGHT!", 
                                       (self.game_engine.width // 2, self.game_engine.height // 2),
                                       (255, 50, 50), 
                                       size=72,
                                       duration=30)
                self._select_option()
    
    def _play_selection_sound(self):
        """Play a sound effect for menu navigation."""
        # Placeholder for sound effect - can be implemented when sound system is added
        pass
    
    def _play_confirm_sound(self):
        """Play a sound effect for menu selection."""
        # Placeholder for sound effect - can be implemented when sound system is added
        pass
    
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
        # Increment animation timer
        self.animation_timer += 1
        
        # Update fighter animations
        self._update_fighters()
        
        # Update particles
        self._update_particles()
        
        # Update combat text effects
        self._update_combat_texts()
        
        # Update lightning effect
        self._update_lightning()
        
        # Update health bars with some random fluctuation for visual effect
        for bar in self.health_bars:
            if random.random() < 0.01:  # Occasionally change health for visual effect
                change = random.randint(-10, 5)
                bar['health'] = max(10, min(100, bar['health'] + change))
                
                # If a big hit happens, add an impact effect and combat text
                if change < -5:
                    hit_x = bar['x'] + bar['width'] // 2
                    self.add_impact_particles((hit_x, 50), (255, 50, 50), count=8)
                    
                    # Randomly show combat text
                    if random.random() < 0.3:
                        texts = ["HIT!", "COMBO!", "CRITICAL!"]
                        self.add_combat_text(random.choice(texts), (hit_x, 80), 
                                           (255, 200, 50), size=32)
        
        # Occasionally add combat text effect for atmosphere
        if random.random() < 0.005:
            positions = [(200, 200), (600, 200), (400, 150)]
            texts = ["FIGHT!", "K.O.", "ROUND 1", "PERFECT", "COUNTER!"]
            colors = [(255, 50, 50), (50, 200, 255), (255, 200, 50)]
            
            self.add_combat_text(random.choice(texts), 
                               random.choice(positions),
                               random.choice(colors), 
                               size=random.randint(36, 48))
    
    def _update_fighters(self):
        """Update fighter animations and AI."""
        for fighter in self.fighters:
            # Decrement cooldowns
            if fighter['attack_cooldown'] > 0:
                fighter['attack_cooldown'] -= 1
            if fighter['move_cooldown'] > 0:
                fighter['move_cooldown'] -= 1
            
            # Advance animation frames
            fighter['frame'] += 0.2
            if fighter['frame'] >= 4:
                fighter['frame'] = 0
                
                # Return to idle after attack
                if fighter['state'] == 'attack' or fighter['state'] == 'hit':
                    fighter['state'] = 'idle'
            
            # Fighter AI behaviors
            if fighter['state'] == 'idle':
                # Occasionally decide to attack or move
                if random.random() < 0.02 and fighter['attack_cooldown'] <= 0:
                    fighter['state'] = 'attack'
                    fighter['frame'] = 0
                    fighter['attack_cooldown'] = 60
                    
                    # Determine attack target
                    for target in self.fighters:
                        if target != fighter:
                            # Check if in range
                            distance = abs(target['x'] - fighter['x'])
                            if distance < 100:
                                # Hit!
                                target['state'] = 'hit'
                                target['frame'] = 0
                                
                                # Add impact particles
                                hit_x = target['x']
                                hit_y = target['y'] - target['height'] // 2
                                self.add_impact_particles((hit_x, hit_y), (255, 200, 0), count=15)
                                
                                # Damage healthbar
                                for bar in self.health_bars:
                                    if (fighter['facing_right'] and bar['x'] > 400) or \
                                       (not fighter['facing_right'] and bar['x'] < 400):
                                        bar['health'] = max(10, bar['health'] - random.randint(5, 15))
                                        break
                                
                                # Add combat text
                                if random.random() < 0.3:
                                    texts = ["HIT!", "COMBO!", "CRITICAL!"]
                                    self.add_combat_text(random.choice(texts), (hit_x, hit_y - 50), 
                                                       (255, 200, 50), size=32)
                                break
                
                elif random.random() < 0.01 and fighter['move_cooldown'] <= 0:
                    # Move fighter
                    fighter['state'] = 'walk'
                    fighter['move_cooldown'] = 30
                    
                    # Decide move direction (usually toward other fighter)
                    other_x = 0
                    for target in self.fighters:
                        if target != fighter:
                            other_x = target['x']
                            break
                    
                    if other_x > fighter['x']:
                        fighter['facing_right'] = True
                        fighter['x'] += random.randint(20, 50)
                    else:
                        fighter['facing_right'] = False
                        fighter['x'] -= random.randint(20, 50)
                        
                    # Keep within screen bounds
                    fighter['x'] = max(100, min(700, fighter['x']))
            
            elif fighter['state'] == 'walk':
                # Continue walking
                if fighter['facing_right']:
                    fighter['x'] += 2
                else:
                    fighter['x'] -= 2
                    
                # Return to idle
                if random.random() < 0.1:
                    fighter['state'] = 'idle'
                    
                # Keep within screen bounds
                fighter['x'] = max(100, min(700, fighter['x']))
            
            # Add fire/energy particles occasionally
            if random.random() < 0.1:
                particle_x = fighter['x'] + random.randint(-10, 10)
                particle_y = fighter['y'] - fighter['height'] // 2
                
                if fighter['state'] == 'attack':
                    # More particles during attack
                    for _ in range(3):
                        self.add_fire_particle((particle_x, particle_y), (255, 100, 50))
                else:
                    self.add_fire_particle((particle_x, particle_y), (100, 100, 255))
    
    def _update_particles(self):
        """Update particle effects."""
        i = 0
        while i < len(self.particles):
            particle = self.particles[i]
            
            # Apply velocity
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Apply gravity to impact particles
            if particle['type'] == 'impact':
                particle['vy'] += 0.2
            
            # Decrease lifetime
            particle['lifetime'] -= 1
            
            # Remove expired particles
            if particle['lifetime'] <= 0:
                self.particles.pop(i)
            else:
                i += 1
    
    def _update_combat_texts(self):
        """Update floating combat text effects."""
        i = 0
        while i < len(self.combat_texts):
            text = self.combat_texts[i]
            
            # Increment timer
            text['timer'] += 1
            
            # Move text upward
            text['y'] -= 1
            
            # Scale effect
            progress = text['timer'] / text['duration']
            if progress < 0.2:
                # Scale up
                text['scale'] = min(2.0, 0.5 + progress * 7.5)
            else:
                # Scale down
                text['scale'] = max(0.5, 2.0 - (progress - 0.2) * 2.0)
            
            # Remove expired texts
            if text['timer'] >= text['duration']:
                self.combat_texts.pop(i)
            else:
                i += 1
    
    def _update_lightning(self):
        """Update lightning flash effect."""
        if self.lightning['active']:
            self.lightning['timer'] += 1
            if self.lightning['timer'] >= self.lightning['duration']:
                self.lightning['active'] = False
                self.lightning['next'] = random.randint(200, 500)
        else:
            self.lightning['next'] -= 1
            if self.lightning['next'] <= 0:
                self.lightning['active'] = True
                self.lightning['timer'] = 0
                self.lightning['duration'] = random.randint(3, 8)
    
    def render(self, screen):
        # Fill the background
        screen.fill(self.stage_elements['sky_color'])
        
        # Draw lightning flash
        if self.lightning['active']:
            lightning_overlay = pygame.Surface((self.game_engine.width, self.game_engine.height), pygame.SRCALPHA)
            alpha = 100 if self.lightning['timer'] < self.lightning['duration'] / 2 else \
                   100 - (self.lightning['timer'] - self.lightning['duration'] / 2) * (200 / self.lightning['duration'])
            lightning_overlay.fill((255, 255, 255, int(alpha)))
            screen.blit(lightning_overlay, (0, 0))
        
        # Draw distant mountains/buildings for background
        for i in range(5):
            height = random.randint(50, 150)
            width = random.randint(100, 300)
            x = i * 200 - 50
            y = self.stage_elements['ground_height'] - height
            
            # Randomize color slightly for variety
            color_offset = random.randint(-20, 20)
            color = (40 + color_offset, 40 + color_offset, 80 + color_offset)
            
            pygame.draw.rect(screen, color, (x, y, width, height))
        
        # Draw ground
        ground_rect = pygame.Rect(0, self.stage_elements['ground_height'], 
                                self.game_engine.width, 
                                self.game_engine.height - self.stage_elements['ground_height'])
        pygame.draw.rect(screen, self.stage_elements['ground_color'], ground_rect)
        
        # Draw ground details (lines)
        for y in range(self.stage_elements['ground_height'], self.game_engine.height, 20):
            line_color = (self.stage_elements['ground_color'][0] - 10,
                        self.stage_elements['ground_color'][1] - 10,
                        self.stage_elements['ground_color'][2] - 10)
            pygame.draw.line(screen, line_color, (0, y), (self.game_engine.width, y), 1)
        
        # Draw fighters
        for fighter in self.fighters:
            self._draw_fighter(screen, fighter)
        
        # Draw fire/energy particles
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / 40))
            if particle['type'] == 'fire':
                # Pulsating size for fire particles
                size = particle['size'] * (0.8 + math.sin(self.animation_timer * 0.2) * 0.2)
                
                # Create an alpha surface for the glow effect
                glow_surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
                glow_color = (*particle['color'], alpha)
                pygame.draw.circle(glow_surf, glow_color, (int(size), int(size)), int(size))
                
                screen.blit(glow_surf, (int(particle['x'] - size), int(particle['y'] - size)))
            else:
                # Impact particles
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), 
                                 int(particle['size']))
        
        # Draw title with combat-style animation
        self._draw_animated_title(screen)
        
        # Draw health bars (just for visual effect)
        for i, bar in enumerate(self.health_bars):
            # Background
            bar_bg_rect = pygame.Rect(bar['x'], 50, bar['width'], 20)
            pygame.draw.rect(screen, (50, 50, 50), bar_bg_rect)
            
            # Health fill
            fill_width = int(bar['width'] * (bar['health'] / 100))
            if i == 0:  # Left side
                fill_rect = pygame.Rect(bar['x'], 50, fill_width, 20)
            else:  # Right side (flipped)
                fill_rect = pygame.Rect(bar['x'] + bar['width'] - fill_width, 50, fill_width, 20)
            
            # Color based on health
            if bar['health'] > 70:
                color = (100, 200, 100)  # Green
            elif bar['health'] > 30:
                color = (200, 200, 100)  # Yellow
            else:
                color = (200, 100, 100)  # Red
            
            pygame.draw.rect(screen, color, fill_rect)
            pygame.draw.rect(screen, (200, 200, 200), bar_bg_rect, 2)  # Border
        
        # Draw player indicators above health bars
        p1_text = self.game_engine.fonts['small'].render("P1", True, (200, 200, 255))
        p2_text = self.game_engine.fonts['small'].render("P2", True, (255, 200, 200))
        screen.blit(p1_text, (self.health_bars[0]['x'] + 10, 30))
        screen.blit(p2_text, (self.health_bars[1]['x'] + self.health_bars[1]['width'] - 30, 30))
        
        # Draw menu options with battle-style effects
        self._draw_menu_options(screen)
        
        # Draw combat text effects
        for text in self.combat_texts:
            font = pygame.font.Font(None, int(text['size'] * text['scale']))
            text_surf = font.render(text['text'], True, text['color'])
            
            # Add shadow for better readability
            shadow_surf = font.render(text['text'], True, (0, 0, 0))
            shadow_rect = shadow_surf.get_rect(center=(text['x'] + 2, text['y'] + 2))
            screen.blit(shadow_surf, shadow_rect)
            
            # Main text
            text_rect = text_surf.get_rect(center=(text['x'], text['y']))
            screen.blit(text_surf, text_rect)
        
        # Draw footer with controls
        self._draw_footer(screen)
    
    def _draw_fighter(self, screen, fighter):
        """Draw a fighter silhouette with simple animations."""
        x, y = fighter['x'], fighter['y']
        width, height = fighter['width'], fighter['height']
        color = fighter['color']
        frame = int(fighter['frame'])
        
        # Base body position
        body_rect = pygame.Rect(x - width // 2, y - height, width, height)
        
        # Adjust based on animation state
        if fighter['state'] == 'idle':
            # Breathing animation
            body_offset_y = math.sin(self.animation_timer * 0.1) * 2
            body_rect.y += body_offset_y
            
        elif fighter['state'] == 'walk':
            # Walking animation
            leg_offset = math.sin(self.animation_timer * 0.2) * 5
            
        elif fighter['state'] == 'attack':
            # Attack animation - extend arm/leg
            if fighter['facing_right']:
                body_rect.x += frame * 3  # Lean into punch
            else:
                body_rect.x -= frame * 3  # Lean into punch
            
        elif fighter['state'] == 'hit':
            # Hit reaction
            knockback = 10 * (1 - frame / 4)
            if fighter['facing_right']:
                body_rect.x -= knockback
            else:
                body_rect.x += knockback
            
            # Flash red
            if frame < 2:
                color = (255, 100, 100)
        
        # Draw body
        pygame.draw.rect(screen, color, body_rect)
        
        # Draw head
        head_size = width * 0.75
        head_rect = pygame.Rect(
            x - head_size // 2,
            y - height - head_size,
            head_size, head_size
        )
        
        # Head follows body animation
        if fighter['state'] == 'idle':
            head_rect.y += math.sin(self.animation_timer * 0.1) * 2
        elif fighter['state'] == 'attack':
            if fighter['facing_right']:
                head_rect.x += frame * 2
            else:
                head_rect.x -= frame * 2
        elif fighter['state'] == 'hit':
            knockback = 8 * (1 - frame / 4)
            if fighter['facing_right']:
                head_rect.x -= knockback
            else:
                head_rect.x += knockback
        
        pygame.draw.rect(screen, color, head_rect)
        
        # Draw eyes
        eye_color = (255, 255, 255)
        eye_size = 5
        eye_offset_x = 7 if fighter['facing_right'] else -7
        
        if fighter['state'] != 'hit':  # Don't show eyes when hit
            pygame.draw.circle(screen, eye_color, 
                             (int(x + eye_offset_x), int(head_rect.centery)), 
                             eye_size)
        
        # Draw arms based on animation state
        arm_width = 10
        arm_length = 30
        
        if fighter['state'] == 'attack' and frame >= 1:
            # Extended punching arm
            punch_extend = min(50, frame * 20)
            arm_color = color
            
            if fighter['facing_right']:
                pygame.draw.rect(screen, arm_color, 
                               (int(x + width // 4), int(y - height * 0.7), 
                                int(punch_extend), arm_width))
                
                # Draw fist
                pygame.draw.circle(screen, arm_color, 
                                 (int(x + width // 4 + punch_extend), int(y - height * 0.7 + arm_width // 2)), 
                                 8)
            else:
                pygame.draw.rect(screen, arm_color, 
                               (int(x - width // 4 - punch_extend), int(y - height * 0.7), 
                                int(punch_extend), arm_width))
                
                # Draw fist
                pygame.draw.circle(screen, arm_color, 
                                 (int(x - width // 4 - punch_extend), int(y - height * 0.7 + arm_width // 2)), 
                                 8)
        else:
            # Regular arms
            arm_color = (
                int(color[0] * 0.9),
                int(color[1] * 0.9),
                int(color[2] * 0.9)
            )
            
            # Left arm
            left_arm_x = x - width // 2 - 5
            left_arm_y = y - height * 0.7
            
            # Right arm
            right_arm_x = x + width // 2 + 5
            right_arm_y = y - height * 0.7
            
            if fighter['state'] == 'walk':
                arm_swing = math.sin(self.animation_timer * 0.2) * 10
                left_arm_y += arm_swing
                right_arm_y -= arm_swing
            
            if fighter['facing_right']:
                pygame.draw.rect(screen, arm_color, 
                               (int(left_arm_x - arm_length), int(left_arm_y), 
                                arm_length, arm_width))
                
                pygame.draw.rect(screen, arm_color, 
                               (int(right_arm_x), int(right_arm_y), 
                                arm_length, arm_width))
            else:
                pygame.draw.rect(screen, arm_color, 
                               (int(left_arm_x), int(left_arm_y), 
                                arm_length, arm_width))
                
                pygame.draw.rect(screen, arm_color, 
                               (int(right_arm_x - arm_length), int(right_arm_y), 
                                arm_length, arm_width))
        
        # Draw legs
        leg_color = (
            int(color[0] * 0.8),
            int(color[1] * 0.8),
            int(color[2] * 0.8)
        )
        
        leg_width = width // 3
        leg_height = height // 3
        
        if fighter['state'] == 'walk':
            # Walking animation
            left_leg_offset = math.sin(self.animation_timer * 0.2) * 10
            right_leg_offset = -left_leg_offset
            
            pygame.draw.rect(screen, leg_color, 
                           (int(x - width // 3 - leg_width // 2), int(y - leg_height + left_leg_offset), 
                            leg_width, leg_height))
            
            pygame.draw.rect(screen, leg_color, 
                           (int(x + width // 3 - leg_width // 2), int(y - leg_height + right_leg_offset), 
                            leg_width, leg_height))
        else:
            # Standing legs
            pygame.draw.rect(screen, leg_color, 
                           (int(x - width // 3 - leg_width // 2), int(y - leg_height), 
                            leg_width, leg_height))
            
            pygame.draw.rect(screen, leg_color, 
                           (int(x + width // 3 - leg_width // 2), int(y - leg_height), 
                            leg_width, leg_height))
    
    def _draw_animated_title(self, screen):
        """Draw the title with animation effects."""
        title_font = self.game_engine.fonts['title']
        title_text = "PIXEL KOMBAT"
        
        # Title animation based on a combat heartbeat
        pulse = 1.0 + math.sin(self.animation_timer * 0.1) * 0.05
        
        # Lightning effect on title
        title_colors = [(255, 50, 50), (255, 70, 70)]
        title_color = title_colors[0]
        
        if self.lightning['active']:
            title_color = (255, 255, 200)
        
        # Create the text surface
        title_surf = title_font.render(title_text, True, title_color)
        
        # Scale the surface
        scaled_width = int(title_surf.get_width() * pulse)
        scaled_height = int(title_surf.get_height() * pulse)
        scaled_title = pygame.transform.scale(title_surf, (scaled_width, scaled_height))
        
        # Position at center
        title_rect = scaled_title.get_rect(center=(self.game_engine.width // 2, 100))
        
        # Add drop shadow
        shadow_surf = title_font.render(title_text, True, (80, 20, 20))
        shadow_surf = pygame.transform.scale(shadow_surf, (scaled_width, scaled_height))
        shadow_rect = shadow_surf.get_rect(center=(self.game_engine.width // 2 + 4, 104))
        
        screen.blit(shadow_surf, shadow_rect)
        screen.blit(scaled_title, title_rect)
        
        # Combat subtitle
        subtitle_text = "THE ULTIMATE FIGHTING GAME"
        subtitle_surf = self.game_engine.fonts['small'].render(subtitle_text, True, (200, 200, 200))
        subtitle_rect = subtitle_surf.get_rect(center=(self.game_engine.width // 2, title_rect.bottom + 10))
        screen.blit(subtitle_surf, subtitle_rect)
    
    def _draw_menu_options(self, screen):
        """Draw menu options with combat-style effects."""
        option_font = self.game_engine.fonts['large']
        
        for i, option in enumerate(self.options):
            # Determine if this option is selected
            is_selected = (i == self.selected_option)
            
            # Base position
            option_y = 250 + i * 70
            
            # Add a fighting stance animation to selected option
            y_offset = 0
            if is_selected:
                y_offset = math.sin(self.animation_timer * 0.1) * 5
                
                # Add energy particles around selected option
                if random.random() < 0.2:
                    particle_x = self.game_engine.width // 2 + random.randint(-100, 100)
                    particle_y = option_y + random.randint(-20, 20) + y_offset
                    self.add_fire_particle((particle_x, particle_y), (255, 200, 0))
            
            # Determine color and effects
            if is_selected:
                # Fighting game style pulsing effect
                pulse = math.sin(self.animation_timer * 0.2) * 0.2 + 1.0
                color = self.selected_color
            else:
                pulse = 1.0
                color = self.option_color
            
            # Create the text surface
            option_surf = option_font.render(option, True, color)
            
            # Scale the surface for pulse effect
            if is_selected:
                scaled_width = int(option_surf.get_width() * pulse)
                scaled_height = int(option_surf.get_height() * pulse)
                option_surf = pygame.transform.scale(option_surf, (scaled_width, scaled_height))
            
            # Position at center with offset
            option_rect = option_surf.get_rect(center=(self.game_engine.width // 2, option_y + y_offset))
            
            # Add shadow for better readability
            shadow_surf = option_font.render(option, True, (0, 0, 0))
            if is_selected:
                shadow_surf = pygame.transform.scale(shadow_surf, (scaled_width, scaled_height))
            shadow_rect = shadow_surf.get_rect(center=(self.game_engine.width // 2 + 3, option_y + y_offset + 3))
            
            screen.blit(shadow_surf, shadow_rect)
            screen.blit(option_surf, option_rect)
            
            # Draw selection indicator for highlighted option
            if is_selected:
                # Fighting game style indicator (combo input)
                input_text = "→ ↓ ↘ + PUNCH"
                input_surf = self.game_engine.fonts['small'].render(input_text, True, (200, 200, 50))
                input_rect = input_surf.get_rect(center=(self.game_engine.width // 2, option_y + 25 + y_offset))
                screen.blit(input_surf, input_rect)
                
                # Animated selector brackets
                bracket_pulse = abs(math.sin(self.animation_timer * 0.1))
                bracket_width = 15 + bracket_pulse * 5
                bracket_height = 40 + bracket_pulse * 10
                bracket_thickness = 3
                
                # Left bracket
                left_x = option_rect.left - 20 - bracket_pulse * 5
                pygame.draw.line(screen, self.selected_color, 
                               (left_x, option_y - bracket_height//2 + y_offset),
                               (left_x, option_y + bracket_height//2 + y_offset),
                               bracket_thickness)
                pygame.draw.line(screen, self.selected_color, 
                               (left_x, option_y - bracket_height//2 + y_offset),
                               (left_x + bracket_width, option_y - bracket_height//2 + y_offset),
                               bracket_thickness)
                pygame.draw.line(screen, self.selected_color, 
                               (left_x, option_y + bracket_height//2 + y_offset),
                               (left_x + bracket_width, option_y + bracket_height//2 + y_offset),
                               bracket_thickness)
                
                # Right bracket
                right_x = option_rect.right + 20 + bracket_pulse * 5
                pygame.draw.line(screen, self.selected_color, 
                               (right_x, option_y - bracket_height//2 + y_offset),
                               (right_x, option_y + bracket_height//2 + y_offset),
                               bracket_thickness)
                pygame.draw.line(screen, self.selected_color, 
                               (right_x, option_y - bracket_height//2 + y_offset),
                               (right_x - bracket_width, option_y - bracket_height//2 + y_offset),
                               bracket_thickness)
                pygame.draw.line(screen, self.selected_color, 
                               (right_x, option_y + bracket_height//2 + y_offset),
                               (right_x - bracket_width, option_y + bracket_height//2 + y_offset),
                               bracket_thickness)
    
    def _draw_footer(self, screen):
        """Draw footer with controls and game info."""
        # Draw control instructions at bottom
        controls_text = "ARROW KEYS: SELECT   ENTER: CONFIRM"
        controls_surf = self.game_engine.fonts['small'].render(controls_text, True, (180, 180, 180))
        controls_rect = controls_surf.get_rect(midbottom=(self.game_engine.width // 2, self.game_engine.height - 20))
        screen.blit(controls_surf, controls_rect)
        
        # Draw game version
        version_text = "v1.0"
        version_surf = self.game_engine.fonts['small'].render(version_text, True, (150, 150, 150))
        version_rect = version_surf.get_rect(bottomright=(self.game_engine.width - 20, self.game_engine.height - 20))
        screen.blit(version_surf, version_rect)
        
        # Round number (just for aesthetic)
        round_text = f"ROUND 1"
        round_surf = self.game_engine.fonts['small'].render(round_text, True, (200, 200, 50))
        round_rect = round_surf.get_rect(center=(self.game_engine.width // 2, 25))
        screen.blit(round_surf, round_rect)
        
        # Timer (just for aesthetic)
        time_text = "60"
        time_color = (255, 255, 255)
        # Blinking when time is getting low (less than 30)
        if int(self.animation_timer / 60) % 2 == 0:
            time_color = (255, 100, 100)
        time_surf = self.game_engine.fonts['medium'].render(time_text, True, time_color)
        time_rect = time_surf.get_rect(midtop=(self.game_engine.width // 2, 40))
        screen.blit(time_surf, time_rect)

