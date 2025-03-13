import pygame
import random
import math

class EnhancedParticleSystem:
    """An improved particle system with more complex behaviors."""
    
    def __init__(self):
        self.particles = []
        
    def add_particle(self, particle):
        """Add a particle to the system."""
        self.particles.append(particle)
        
    def add_explosion(self, pos, color=(255, 100, 0), size=30, particle_count=20):
        """Add an explosion effect at the given position."""
        for _ in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            self.particles.append({
                "type": "explosion",
                "x": pos[0],
                "y": pos[1],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "gravity": 0.1,
                "size": random.uniform(size * 0.2, size * 0.5),
                "color": color,
                "alpha": 255,
                "fade_speed": random.uniform(3, 7),
                "life": random.randint(20, 40),
                "rotation": random.uniform(0, 360),
                "rotation_speed": random.uniform(-5, 5)
            })
            
    def add_smoke(self, pos, color=(100, 100, 100), size=15, particle_count=10):
        """Add a smoke effect at the given position."""
        for _ in range(particle_count):
            angle = random.uniform(-math.pi/2 - 0.5, -math.pi/2 + 0.5)  # Mostly upward
            speed = random.uniform(0.5, 2)
            self.particles.append({
                "type": "smoke",
                "x": pos[0] + random.uniform(-10, 10),
                "y": pos[1] + random.uniform(-5, 5),
                "vx": math.cos(angle) * speed + random.uniform(-0.3, 0.3),
                "vy": math.sin(angle) * speed,
                "size": random.uniform(size * 0.5, size),
                "size_change": random.uniform(0.1, 0.3),  # Grows over time
                "max_size": size * 2,
                "color": color,
                "alpha": random.uniform(150, 200),
                "fade_speed": random.uniform(1, 3),
                "life": random.randint(30, 60)
            })
            
    def add_energy_trail(self, pos, color=(100, 200, 255), size=10, dir=(1, 0), particle_count=5):
        """Add an energy trail effect at the given position."""
        for _ in range(particle_count):
            # Direction perpendicular to movement
            perp_dir = (-dir[1], dir[0])
            
            offset_x = perp_dir[0] * random.uniform(-size/2, size/2)
            offset_y = perp_dir[1] * random.uniform(-size/2, size/2)
            
            self.particles.append({
                "type": "energy",
                "x": pos[0] + offset_x,
                "y": pos[1] + offset_y,
                "vx": -dir[0] * random.uniform(0.5, 2) + random.uniform(-0.3, 0.3),
                "vy": -dir[1] * random.uniform(0.5, 2) + random.uniform(-0.3, 0.3),
                "size": random.uniform(size * 0.3, size * 0.7),
                "size_change": random.uniform(-0.1, -0.05),  # Shrinks over time
                "color": color,
                "alpha": random.uniform(150, 255),
                "fade_speed": random.uniform(3, 7),
                "life": random.randint(10, 30),
                "pulse": random.uniform(0, math.pi)  # For pulsing effect
            })
            
    def add_footstep(self, pos, color=(120, 100, 80), size=8):
        """Add a footstep dust effect."""
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.3, 1.2)
            self.particles.append({
                "type": "dust",
                "x": pos[0] + random.uniform(-5, 5),
                "y": pos[1] + random.uniform(-2, 2),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 0.5,  # Slight upward bias
                "size": random.uniform(size * 0.5, size),
                "color": color,
                "alpha": random.uniform(100, 180),
                "fade_speed": random.uniform(3, 8),
                "life": random.randint(10, 25)
            })
            
    def add_blood(self, pos, dir, amount=10):
        """Add blood splatter effect (optional - can be disabled for younger audiences)."""
        for _ in range(amount):
            angle = math.atan2(dir[1], dir[0]) + random.uniform(-1, 1)
            speed = random.uniform(1, 3)
            size = random.uniform(2, 5)
            
            self.particles.append({
                "type": "blood",
                "x": pos[0],
                "y": pos[1],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - random.uniform(0, 1),  # Some upward motion
                "gravity": 0.15,
                "size": size,
                "color": (150, 0, 0),
                "alpha": 200,
                "fade_speed": random.uniform(1, 3),
                "life": random.randint(20, 60),
                "ground_y": 450,  # Floor height
                "landed": False,
                "splat_size": size * 1.5
            })
            
    def update(self):
        """Update all particles."""
        i = 0
        while i < len(self.particles):
            p = self.particles[i]
            
            # Update position
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            
            # Apply type-specific updates
            if p["type"] == "explosion":
                # Apply gravity
                p["vy"] += p.get("gravity", 0)
                
                # Update rotation
                if "rotation" in p:
                    p["rotation"] += p.get("rotation_speed", 0)
                
            elif p["type"] == "smoke":
                # Smoke grows over time
                if "size_change" in p:
                    p["size"] += p["size_change"]
                    if "max_size" in p and p["size"] > p["max_size"]:
                        p["size"] = p["max_size"]
                
                # Smoke slows down
                p["vx"] *= 0.98
                p["vy"] *= 0.98
                
            elif p["type"] == "energy":
                # Energy particles pulse
                if "pulse" in p:
                    p["pulse"] += 0.1
                    pulse_factor = (math.sin(p["pulse"]) * 0.3 + 0.7)
                    p["alpha"] = min(255, p["alpha"] * pulse_factor)
                
                # Update size
                if "size_change" in p:
                    p["size"] += p["size_change"]
                    if p["size"] <= 0:
                        p["life"] = 0  # Remove if size becomes zero
                        
            elif p["type"] == "blood" and not p.get("landed", False):
                # Apply gravity
                p["vy"] += p.get("gravity", 0)
                
                # Check for landing on ground
                if p["y"] >= p.get("ground_y", 450):
                    p["y"] = p.get("ground_y", 450)
                    p["vx"] = 0
                    p["vy"] = 0
                    p["landed"] = True
                    p["fade_speed"] /= 3  # Slower fade when on ground
                    p["size"] = p.get("splat_size", p["size"])
            
            # Update life and alpha
            p["life"] -= 1
            p["alpha"] = max(0, p["alpha"] - p.get("fade_speed", 5))
            
            # Remove dead particles
            if p["life"] <= 0 or p["alpha"] <= 0:
                self.particles.pop(i)
            else:
                i += 1
                
    def render(self, screen):
        """Render all particles."""
        for p in sorted(self.particles, key=lambda x: x["size"]):  # Sort for better layering
            # Create surface for this particle
            size = max(1, int(p["size"] * 2))
            particle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            
            if p["type"] == "explosion":
                # Draw as a circle or polygon
                if random.random() < 0.3:  # Some particles are polygons for variety
                    points = []
                    sides = random.randint(3, 5)
                    for i in range(sides):
                        angle = i * (2 * math.pi / sides) + p.get("rotation", 0)
                        x = size // 2 + math.cos(angle) * p["size"]
                        y = size // 2 + math.sin(angle) * p["size"]
                        points.append((x, y))
                    pygame.draw.polygon(particle_surf, (*p["color"], int(p["alpha"])), points)
                else:
                    # Circle with glow
                    pygame.draw.circle(particle_surf, (*p["color"], int(p["alpha"] * 0.5)), 
                                     (size // 2, size // 2), p["size"] * 1.2)
                    pygame.draw.circle(particle_surf, (*p["color"], int(p["alpha"])), 
                                     (size // 2, size // 2), p["size"])
            
            elif p["type"] == "smoke":
                # Draw as a soft circle
                pygame.draw.circle(particle_surf, (*p["color"], int(p["alpha"])), 
                                 (size // 2, size // 2), p["size"])
            
            elif p["type"] == "energy":
                # Draw as a glowing circle
                pygame.draw.circle(particle_surf, (*p["color"], int(p["alpha"] * 0.7)), 
                                 (size // 2, size // 2), p["size"] * 1.5)
                pygame.draw.circle(particle_surf, (*p["color"], int(p["alpha"])), 
                                 (size // 2, size // 2), p["size"])
                
                # Add center highlight
                highlight_size = max(1, int(p["size"] * 0.5))
                pygame.draw.circle(particle_surf, (255, 255, 255, int(p["alpha"])), 
                                 (size // 2, size // 2), highlight_size)
            
            elif p["type"] == "dust":
                # Draw as a soft circle
                pygame.draw.circle(particle_surf, (*p["color"], int(p["alpha"])), 
                                 (size // 2, size // 2), p["size"])
                
            elif p["type"] == "blood":
                if p.get("landed", False):
                    # Draw as a splat on the ground
                    pygame.draw.ellipse(particle_surf, (*p["color"], int(p["alpha"])), 
                                      (0, size//2, size, size//2))
                else:
                    # Draw as a droplet
                    pygame.draw.circle(particle_surf, (*p["color"], int(p["alpha"])), 
                                     (size // 2, size // 2), p["size"])
            
            # Draw the particle
            screen.blit(particle_surf, (int(p["x"] - size // 2), int(p["y"] - size // 2)))