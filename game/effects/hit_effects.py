import pygame
import math
import random

class HitEffects:
    """Handles visual effects for hits, blocks, and other combat interactions."""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.show_hit_effect = False
        self.hit_effect_time = 0
        self.hit_location = (0, 0)
        self.hit_strength = 0
        self.hit_type = ""  # Type of hit (punch, kick, special)
    
    def update(self):
        """Update hit effect timers."""
        current_time = pygame.time.get_ticks()
        if self.show_hit_effect:
            if current_time - self.hit_effect_time > 300:  # Show for 300ms
                self.show_hit_effect = False
    
    def render(self, screen):
        """Render active hit effects."""
        if self.show_hit_effect:
            self._draw_hit_effect(screen)
    
    def show_hit(self, position, damage, hit_type):
        """
        Show a hit effect at the given position.
        
        Args:
            position: (x, y) position for the hit effect
            damage: Amount of damage dealt
            hit_type: Type of attack ("punch", "kick", "special")
        """
        self.show_hit_effect = True
        self.hit_effect_time = pygame.time.get_ticks()
        self.hit_location = position
        self.hit_strength = damage
        self.hit_type = hit_type
    
    def show_block_effect(self, particle_system, position):
        """
        Show a block effect.
        
        Args:
            particle_system: Particle system to add block particles to
            position: (x, y) position for the block effect
        """
        # Add block particles
        for i in range(10):
            angle = random.uniform(0, math.pi)  # Semicircle in front
            speed = random.uniform(1, 3)
            size = random.randint(3, 6)
            
            particle_system.particles.append({
                "type": "dust",
                "x": position[0],
                "y": position[1] - 50,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 1,  # Upward bias
                "color": (200, 200, 255),
                "size": size,
                "life": random.randint(10, 20),
                "alpha": 200,
                "fade_speed": random.uniform(5, 10),
                "gravity": False
            })
    
    def show_knockout_effect(self, particle_system, position, camera_system):
        """
        Show a knockout effect.
        
        Args:
            particle_system: Particle system to add KO particles to
            position: (x, y) position for the KO effect
            camera_system: Camera system to add shake/zoom effects
        """
        # Add big screen shake
        camera_system.add_shake(15)
        
        # Add KO particles - stars and impact lines
        for i in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            size = random.randint(3, 8)
            
            particle_system.particles.append({
                "type": "explosion",
                "x": position[0],
                "y": position[1] - 50,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 2,  # Upward bias
                "color": (255, 255, 100),
                "size": size,
                "life": random.randint(30, 60),
                "alpha": 255,
                "fade_speed": random.uniform(2, 4),
                "gravity": True,
                "rotation": random.uniform(0, 360),
                "rotation_speed": random.uniform(-5, 5)
            })
        
        # Add explosion effect
        particle_system.add_explosion(position, color=(255, 200, 50), size=50, particle_count=30)
        
        # Add dramatic camera effects
        camera_system.add_zoom_pulse(0.2, 60)
    
    def add_hit_particles(self, particle_system, position, damage, hit_type, facing_right, char_class):
        """
        Add particles based on hit type and damage.
        
        Args:
            particle_system: Particle system to add hit particles to
            position: (x, y) position for the particles
            damage: Amount of damage dealt
            hit_type: Type of attack ("punch", "kick", "special")
            facing_right: Direction the attacker is facing
            char_class: Character class name of the attacker
        """
        num_particles = min(int(damage), 20)  # More particles for stronger hits
        
        # Determine direction based on facing
        dir_x = 1 if facing_right else -1
        
        if hit_type == "punch":
            # Simple impact particles
            particle_system.add_explosion(position, color=(255, 200, 100), size=damage * 0.8, particle_count=num_particles)
            
            # Add small sweat particles
            for i in range(num_particles // 2):
                angle = random.uniform(-0.5, 0.5) + (0 if facing_right else math.pi)
                speed = random.uniform(1, 3)
                size = random.randint(2, 4)
                
                particle_system.particles.append({
                    "type": "dust",
                    "x": position[0],
                    "y": position[1] - 50 + random.uniform(-20, 20),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed - 0.5,
                    "color": (220, 220, 255),
                    "size": size,
                    "life": random.randint(10, 20),
                    "alpha": 200,
                    "fade_speed": random.uniform(5, 10),
                    "gravity": False
                })
                
        elif hit_type == "kick":
            # More forceful particles
            particle_system.add_explosion(position, color=(255, 150, 50), size=damage, particle_count=num_particles)
            
            # Add energy trail
            particle_system.add_energy_trail(position, color=(255, 180, 50), 
                                         size=damage * 0.6, dir=(dir_x, 0), 
                                         particle_count=num_particles // 2)
                
        elif hit_type == "special":
            # Character-specific special attack particles
            if char_class == "Wizard":
                self._add_wizard_special_particles(particle_system, position, damage, num_particles)
            elif char_class == "Guardian":
                self._add_guardian_special_particles(particle_system, position, damage, num_particles)
            elif char_class == "Ninja":
                self._add_ninja_special_particles(particle_system, position, damage, num_particles, facing_right, dir_x)
            elif char_class == "Samurai":
                self._add_samurai_special_particles(particle_system, position, damage, num_particles, facing_right)
            else:
                # Generic special effect
                particle_system.add_explosion(position, color=(200, 200, 255), size=damage * 1.2, particle_count=num_particles * 2)
    
    def _add_wizard_special_particles(self, particle_system, position, damage, num_particles):
        """Add wizard-specific special attack particles."""
        # Magical elemental particles
        color = (100, 200, 255)  # Blue for magic
        particle_system.add_explosion(position, color=color, size=damage * 1.2, particle_count=num_particles * 2)
        
        # Add additional magical energy
        for i in range(num_particles * 2):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            size = random.randint(4, 8)
            
            particle_system.particles.append({
                "type": "energy",
                "x": position[0] + random.uniform(-20, 20),
                "y": position[1] - 50 + random.uniform(-20, 20),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 1,  # Upward bias
                "color": (100, 200, 255) if random.random() < 0.6 else (255, 255, 255),
                "size": size,
                "size_change": random.uniform(-0.1, 0.1),  # Shrink or grow
                "life": random.randint(20, 40),
                "alpha": 200,
                "fade_speed": random.uniform(3, 6),
                "gravity": False,
                "pulse": random.uniform(0, math.pi)
            })
    
    def _add_guardian_special_particles(self, particle_system, position, damage, num_particles):
        """Add guardian-specific special attack particles."""
        # Heavy impact particles
        color = (255, 220, 100)  # Gold for guardian
        particle_system.add_explosion(position, color=color, size=damage * 1.5, particle_count=num_particles * 2)
    
    def _add_ninja_special_particles(self, particle_system, position, damage, num_particles, facing_right, dir_x):
        """Add ninja-specific special attack particles."""
        # Fast, sharp particles
        color = (200, 100, 255)  # Purple for ninja
        
        # Add sharp particle slashes
        for i in range(num_particles):
            angle = random.uniform(-0.5, 0.5) + (0 if facing_right else math.pi)
            speed = random.uniform(3, 7)
            size = random.randint(5, 10)
            
            particle_system.particles.append({
                "type": "energy",
                "x": position[0],
                "y": position[1] - 50 + random.uniform(-20, 20),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": color,
                "size": size,
                "size_change": -0.2,  # Shrink quickly
                "life": random.randint(10, 20),
                "alpha": 230,
                "fade_speed": random.uniform(8, 12),
                "gravity": False
            })
    
    def _add_samurai_special_particles(self, particle_system, position, damage, num_particles, facing_right):
        """Add samurai-specific special attack particles."""
        # Slashing, fiery particles
        color = (255, 100, 50)  # Orange-red for samurai
        
        # Add fire particles
        for i in range(num_particles * 2):
            angle = random.uniform(-0.3, 0.3) + (0 if facing_right else math.pi)
            speed = random.uniform(2, 6)
            size = random.randint(4, 8)
            
            particle_system.particles.append({
                "type": "explosion",
                "x": position[0],
                "y": position[1] - 50 + random.uniform(-10, 10),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - random.uniform(0, 2),
                "color": (255, 100 + random.randint(0, 100), 0),
                "size": size,
                "life": random.randint(15, 30),
                "alpha": 200,
                "fade_speed": random.uniform(5, 10),
                "gravity": True,
                "rotation": random.uniform(0, 360),
                "rotation_speed": random.uniform(-10, 10)
            })
    
    def _draw_hit_effect(self, screen):
        """Draw the hit effect with type-specific visuals."""
        # Scale hit effect based on damage
        hit_size = 20 + min(30, self.hit_strength)
        
        if self.hit_type == "punch":
            # Simple impact circles
            for i in range(3):  
                size = hit_size - i * 5
                if size <= 0:
                    continue
                alpha = 200 - i * 60
                hit_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                hit_color = (255, 200, 0, alpha)
                pygame.draw.circle(hit_surf, hit_color, (size, size), size)
                hit_rect = hit_surf.get_rect(center=self.hit_location)
                screen.blit(hit_surf, hit_rect)
                
            # Add "PUNCH!" text
            if self.hit_strength > 12:  # Only for strong hits
                hit_text = self.game_engine.fonts['small'].render("PUNCH!", True, (255, 200, 0))
                text_rect = hit_text.get_rect(center=(self.hit_location[0], self.hit_location[1] - 30))
                screen.blit(hit_text, text_rect)
            
        elif self.hit_type == "kick":
            # More angular impact shape
            for i in range(2):
                size = hit_size - i * 8
                if size <= 0:
                    continue
                alpha = 200 - i * 60
                
                # Create a starburst shape
                hit_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                center = (size * 1.5, size * 1.5)
                hit_color = (255, 150, 0, alpha)
                
                points = []
                for angle in range(0, 360, 45):  # 8-point star
                    rad = math.radians(angle)
                    # Outer point
                    x = center[0] + math.cos(rad) * size * 1.5
                    y = center[1] + math.sin(rad) * size * 1.5
                    points.append((x, y))
                    
                    # Inner point
                    rad = math.radians(angle + 22.5)
                    x = center[0] + math.cos(rad) * size * 0.8
                    y = center[1] + math.sin(rad) * size * 0.8
                    points.append((x, y))
                
                pygame.draw.polygon(hit_surf, hit_color, points)
                hit_rect = hit_surf.get_rect(center=self.hit_location)
                screen.blit(hit_surf, hit_rect)
            
            # Add "KICK!" text
            if self.hit_strength > 10:  # Only for strong hits
                hit_text = self.game_engine.fonts['small'].render("KICK!", True, (255, 150, 0))
                text_rect = hit_text.get_rect(center=(self.hit_location[0], self.hit_location[1] - 30))
                screen.blit(hit_text, text_rect)
            
        elif self.hit_type == "special":
            # Energy explosion effect
            for i in range(4):
                size = hit_size - i * 5
                if size <= 0:
                    continue
                alpha = 200 - i * 40
                hit_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                
                # Different colors for special moves
                colors = [
                    (100, 200, 255, alpha),  # Blue
                    (200, 100, 255, alpha),  # Purple
                    (100, 255, 200, alpha),  # Cyan
                    (255, 255, 100, alpha)   # Yellow
                ]
                hit_color = colors[i % len(colors)]
                
                # Ripple effect
                pygame.draw.circle(hit_surf, hit_color, (size * 2, size * 2), size * (1.5 - i * 0.2))
                hit_rect = hit_surf.get_rect(center=self.hit_location)
                screen.blit(hit_surf, hit_rect)
            
            # Add "SPECIAL!" text
            if self.hit_strength > 15:  # Only for strong hits
                hit_text = self.game_engine.fonts['medium'].render("SPECIAL!", True, (100, 200, 255))
                text_rect = hit_text.get_rect(center=(self.hit_location[0], self.hit_location[1] - 40))
                screen.blit(hit_text, text_rect)
        
        # Add impact lines for all hit types
        for i in range(8):
            angle = i * 45 + pygame.time.get_ticks() * 0.1
            length = hit_size + 10
            end_x = self.hit_location[0] + math.cos(math.radians(angle)) * length
            end_y = self.hit_location[1] + math.sin(math.radians(angle)) * length
            
            # Line color based on hit type
            if self.hit_type == "punch":
                line_color = (255, 200, 0)
            elif self.hit_type == "kick":
                line_color = (255, 150, 0)
            else:  # special
                line_color = (100, 200, 255)
                
            pygame.draw.line(screen, line_color, self.hit_location, (int(end_x), int(end_y)), 2)
