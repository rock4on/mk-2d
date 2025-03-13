import pygame
import random
import math

class WeatherSystem:
    """A system to add dynamic weather effects to stages."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.weather_type = None
        self.particles = []
        self.timer = 0
        self.lightning_active = False
        self.lightning_timer = 0
        self.lightning_pos = (0, 0)
        self.lightning_size = (0, 0)
        
    def set_weather(self, weather_type, intensity=0.5):
        """Set the current weather type and intensity."""
        self.weather_type = weather_type
        self.intensity = min(1.0, max(0.1, intensity))
        self.particles = []
        
        # Generate initial particles
        if weather_type == "rain":
            self.generate_rain()
        elif weather_type == "snow":
            self.generate_snow()
        elif weather_type == "sandstorm":
            self.generate_sand()
            
    def update(self):
        """Update weather particles and effects."""
        self.timer += 1
        
        # Update existing particles
        self.update_particles()
        
        # Add new particles based on intensity
        if self.weather_type == "rain":
            if random.random() < self.intensity * 0.3:
                self.generate_rain(5)
        elif self.weather_type == "snow":
            if random.random() < self.intensity * 0.1:
                self.generate_snow(2)
        elif self.weather_type == "sandstorm":
            if random.random() < self.intensity * 0.2:
                self.generate_sand(3)
        
        # Update lightning effect
        if self.lightning_active:
            self.lightning_timer -= 1
            if self.lightning_timer <= 0:
                self.lightning_active = False
        
        # Random lightning for rain
        if self.weather_type == "rain" and random.random() < 0.005 * self.intensity:
            self.create_lightning()
            
    def update_particles(self):
        """Update all weather particles."""
        # Update and remove particles that are off-screen
        i = 0
        while i < len(self.particles):
            p = self.particles[i]
            
            # Update position
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            
            # Apply physics based on type
            if p["type"] == "rain":
                # Rain accelerates
                p["vy"] += 0.1
            elif p["type"] == "snow":
                # Snow drifts and falls slowly
                p["vx"] += random.uniform(-0.05, 0.05)
                p["vx"] = max(-1, min(1, p["vx"]))  # Limit horizontal speed
                
                # Snow sometimes swirls upward briefly
                if random.random() < 0.01:
                    p["vy"] -= random.uniform(0, 0.3)
                p["vy"] = min(p["vy"] + 0.01, 0.7)  # Limit fall speed
            elif p["type"] == "sand":
                # Sand gets pushed by wind in gusts
                if random.random() < 0.05:
                    p["vx"] = random.uniform(-3, -1) * self.intensity
                
            # Remove if offscreen
            if (p["x"] < -20 or p["x"] > self.width + 20 or 
                p["y"] < -20 or p["y"] > self.height + 20):
                self.particles.pop(i)
            else:
                i += 1
    
    def generate_rain(self, count=20):
        """Generate rain particles."""
        for _ in range(count):
            self.particles.append({
                "type": "rain",
                "x": random.uniform(-10, self.width + 10),
                "y": random.uniform(-20, 0),
                "vx": random.uniform(-1, -0.5) * self.intensity,
                "vy": random.uniform(5, 9) * self.intensity,
                "length": random.uniform(5, 15) * self.intensity,
                "color": (200, 230, 255)
            })
    
    def generate_snow(self, count=10):
        """Generate snow particles."""
        for _ in range(count):
            size = random.uniform(2, 4) * self.intensity
            self.particles.append({
                "type": "snow",
                "x": random.uniform(-10, self.width + 10),
                "y": random.uniform(-20, 0),
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(0.3, 0.7) * self.intensity,
                "size": size,
                "alpha": random.uniform(150, 230),
                "color": (250, 250, 255)
            })
    
    def generate_sand(self, count=15):
        """Generate sand/dust particles."""
        for _ in range(count):
            size = random.uniform(1, 3) * self.intensity
            alpha = random.uniform(100, 200)
            self.particles.append({
                "type": "sand",
                "x": random.uniform(self.width, self.width + 50),
                "y": random.uniform(100, 400),
                "vx": random.uniform(-2, -1) * self.intensity,
                "vy": random.uniform(-0.5, 0.5),
                "size": size,
                "alpha": alpha,
                "color": (230, 210, 160)
            })
    
    def create_lightning(self):
        """Create a lightning flash effect."""
        self.lightning_active = True
        self.lightning_timer = random.randint(3, 8)
        self.lightning_pos = (random.uniform(100, self.width - 100), 0)
        self.lightning_size = (random.uniform(50, 150), random.uniform(100, 300))
        
    def render(self, screen):
        """Render all weather effects."""
        # Draw lightning first (as a background effect)
        if self.lightning_active:
            flash_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, min(100, self.lightning_timer * 30)))
            screen.blit(flash_surf, (0, 0))
            
            # Draw actual lightning bolt
            self.draw_lightning_bolt(screen, 
                                   self.lightning_pos, 
                                   (self.lightning_pos[0] + random.uniform(-30, 30), 
                                    self.height - random.uniform(50, 150)))
        
        # Draw all particles
        for p in self.particles:
            if p["type"] == "rain":
                # Draw as a line
                end_x = p["x"] - p["vx"] * (p["length"] / p["vy"])
                end_y = p["y"] - p["vy"] * (p["length"] / p["vy"])
                pygame.draw.line(screen, p["color"], (p["x"], p["y"]), (end_x, end_y), 1)
            
            elif p["type"] == "snow":
                # Draw as a small semi-transparent circle
                snow_surf = pygame.Surface((int(p["size"] * 2), int(p["size"] * 2)), pygame.SRCALPHA)
                pygame.draw.circle(snow_surf, (*p["color"], int(p["alpha"])), 
                                 (int(p["size"]), int(p["size"])), int(p["size"]))
                screen.blit(snow_surf, (int(p["x"] - p["size"]), int(p["y"] - p["size"])))
            
            elif p["type"] == "sand":
                # Draw as tiny semi-transparent particles
                sand_surf = pygame.Surface((int(p["size"] * 2), int(p["size"] * 2)), pygame.SRCALPHA)
                pygame.draw.circle(sand_surf, (*p["color"], int(p["alpha"])), 
                                 (int(p["size"]), int(p["size"])), int(p["size"]))
                screen.blit(sand_surf, (int(p["x"] - p["size"]), int(p["y"] - p["size"])))
    
    def draw_lightning_bolt(self, screen, start_pos, end_pos):
        """Draw a lightning bolt between two points."""
        points = [start_pos]
        
        # Generate a jagged path
        current = pygame.Vector2(start_pos)
        target = pygame.Vector2(end_pos)
        direction = target - current
        distance = direction.length()
        direction.normalize_ip()
        
        # Create segments
        segment_length = distance / random.randint(3, 7)
        while current.distance_to(target) > segment_length:
            # Move toward target
            current += direction * segment_length
            
            # Add randomness to path
            perpendicular = pygame.Vector2(-direction.y, direction.x)
            current += perpendicular * random.uniform(-30, 30)
            
            points.append((current.x, current.y))
        
        # Add final point
        points.append(end_pos)
        
        # Draw main bolt
        pygame.draw.lines(screen, (200, 200, 255), False, points, 3)
        
        # Draw glow effect
        for i in range(2):
            glow_points = []
            for p in points:
                # Add slight randomness to glow points
                glow_x = p[0] + random.uniform(-2, 2)
                glow_y = p[1] + random.uniform(-2, 2)
                glow_points.append((glow_x, glow_y))
                
            glow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.lines(glow_surf, (200, 200, 255, 50), False, glow_points, 8 - i*3)
            screen.blit(glow_surf, (0, 0))
            
        # Add branches with some probability
        for i in range(1, len(points) - 1):
            if random.random() < 0.4:
                # Create a branch
                branch_start = points[i]
                direction = pygame.Vector2(direction)
                
                # Random branch direction
                branch_dir = pygame.Vector2(direction)
                branch_dir.rotate_ip(random.uniform(30, 150) * (1 if random.random() < 0.5 else -1))
                
                # Branch end point
                branch_length = random.uniform(30, 80)
                branch_end = (
                    branch_start[0] + branch_dir.x * branch_length,
                    branch_start[1] + branch_dir.y * branch_length
                )
                
                # Draw simplified branch
                branch_points = self.generate_branch_points(branch_start, branch_end)
                pygame.draw.lines(screen, (200, 200, 255), False, branch_points, 2)
    
    def generate_branch_points(self, start, end):
        """Generate points for a lightning branch."""
        points = [start]
        
        # Create 2-3 segments
        segments = random.randint(2, 3)
        for i in range(1, segments):
            # Interpolate position
            t = i / segments
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            
            # Add randomness
            x += random.uniform(-10, 10)
            y += random.uniform(-10, 10)
            
            points.append((x, y))
            
        points.append(end)
        return points