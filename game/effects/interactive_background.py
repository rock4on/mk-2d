import pygame
import random
import math

class InteractiveBackground:
    """Background elements that react to character actions."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.elements = []
        self.grass_elements = []
        self.interacted_elements = set()  # Track which elements have been interacted with
        
    def generate_elements(self, stage):
        """Generate interactive elements based on stage."""
        self.elements = []
        self.grass_elements = []
        self.interacted_elements = set()
        
        if stage == "forest":
            # Add tall grass patches that sway
            for i in range(30):
                x = random.randint(0, self.width)
                height = random.randint(10, 25)
                self.grass_elements.append({
                    "x": x,
                    "y": 450,  # On the ground
                    "width": random.randint(20, 40),
                    "height": height,
                    "color": (30, 100, 30),
                    "original_height": height,
                    "sway_offset": random.uniform(0, math.pi),
                    "sway_speed": random.uniform(0.05, 0.1),
                    "sway": 0,  # Initialize sway property
                    "blades": [random.uniform(0.2, 0.8) for _ in range(random.randint(3, 7))]
                })
            
            # Add breakable branches
            for i in range(5):
                x = random.randint(50, self.width - 50)
                y = random.randint(400, 440)
                self.elements.append({
                    "type": "branch",
                    "x": x,
                    "y": y,
                    "width": random.randint(30, 60),
                    "height": random.randint(5, 10),
                    "angle": random.uniform(-0.2, 0.2),
                    "color": (120, 80, 40),
                    "health": 30,
                    "breaking_threshold": 10,
                    "broken": False,
                    "broken_pieces": []
                })
                
        elif stage == "dojo":
            # Add breakable wooden panels
            for i in range(3):
                x = random.randint(150, self.width - 150)
                y = 400
                self.elements.append({
                    "type": "panel",
                    "x": x,
                    "y": y,
                    "width": 40,
                    "height": 70,
                    "color": (160, 120, 80),
                    "health": 50,
                    "breaking_threshold": 20,
                    "broken": False,
                    "broken_pieces": []
                })
                
            # Add candles that can be knocked over
            for i in range(5):
                x = random.randint(50, self.width - 50)
                self.elements.append({
                    "type": "candle",
                    "x": x,
                    "y": 450,
                    "width": 5,
                    "height": 15,
                    "color": (230, 230, 200),
                    "flame_size": random.uniform(5, 8),
                    "flame_flicker": 0,
                    "tipped": False,
                    "tip_angle": 0,
                    "tip_speed": 0
                })
                
        elif stage == "temple":
            # Add vases that can be broken
            for i in range(4):
                x = random.randint(100, self.width - 100)
                self.elements.append({
                    "type": "vase",
                    "x": x,
                    "y": 430,
                    "width": 20,
                    "height": 30,
                    "color": (180, 160, 200),
                    "pattern_color": (140, 120, 160),
                    "health": 20,
                    "breaking_threshold": 10,
                    "broken": False,
                    "broken_pieces": []
                })
                
        elif stage == "arena":
            # Add sand patches that kick up dust
            for i in range(20):
                x = random.randint(0, self.width)
                radius = random.randint(20, 40)
                self.elements.append({
                    "type": "sand_patch",
                    "x": x,
                    "y": 450,
                    "radius": radius,
                    "color": (210, 190, 150),
                    "dust_particles": []
                })
                
        elif stage == "volcano":
            # Add lava cracks that spurt when stepped on
            for i in range(5):
                x = random.randint(100, self.width - 100)
                width = random.randint(20, 40)
                self.elements.append({
                    "type": "lava_crack",
                    "x": x,
                    "y": 450,
                    "width": width,
                    "height": 10,
                    "color": (200, 50, 0),
                    "glow_intensity": random.uniform(0.6, 1.0),
                    "particles": [],
                    "last_trigger": 0,
                    "cooldown": random.randint(60, 120)
                })
    
    def update(self, player1_pos, player2_pos, current_time):
        """Update interactive elements based on player positions."""
        # Update grass elements
        for grass in self.grass_elements:
            # Natural swaying
            grass["sway_offset"] += grass["sway_speed"]
            sway = math.sin(current_time * 0.01 + grass["sway_offset"]) * 2
            
            # Check if players are near grass
            p1_dist = abs(player1_pos[0] - grass["x"])
            p2_dist = abs(player2_pos[0] - grass["x"])
            
            # Grass bends if players are nearby
            bend = 0
            if p1_dist < grass["width"] // 2 + 20:
                # Bend away from player
                direction = 1 if player1_pos[0] > grass["x"] else -1
                bend = -direction * max(0, (grass["width"] // 2 + 20 - p1_dist) * 0.2)
            
            if p2_dist < grass["width"] // 2 + 20:
                # Bend away from player
                direction = 1 if player2_pos[0] > grass["x"] else -1
                bend_p2 = -direction * max(0, (grass["width"] // 2 + 20 - p2_dist) * 0.2)
                # Take the stronger bend
                bend = bend_p2 if abs(bend_p2) > abs(bend) else bend
                
            # Apply bend and sway
            grass["sway"] = sway + bend
        
        # Update other interactive elements
        for element in self.elements:
            if element["type"] == "branch" and not element["broken"]:
                # Check if players are hitting the branch
                self._check_player_collision(element, player1_pos, player2_pos)
                
                # Branch breaks if health is below threshold
                if element["health"] <= element["breaking_threshold"] and not element["broken"]:
                    element["broken"] = True
                    
                    # Create broken pieces
                    pieces = random.randint(3, 5)
                    width_per_piece = element["width"] / pieces
                    for i in range(pieces):
                        # Create a piece of the branch
                        piece_x = element["x"] + i * width_per_piece
                        piece_y = element["y"]
                        
                        # Add random velocity
                        vx = random.uniform(-2, 2)
                        vy = random.uniform(-5, -2)
                        
                        element["broken_pieces"].append({
                            "x": piece_x,
                            "y": piece_y,
                            "width": width_per_piece * 0.8,
                            "height": element["height"],
                            "angle": element["angle"],
                            "rotation": random.uniform(-0.1, 0.1),
                            "vx": vx,
                            "vy": vy,
                            "gravity": 0.2
                        })
                
                # Update broken pieces
                i = 0
                while i < len(element["broken_pieces"]):
                    piece = element["broken_pieces"][i]
                    
                    # Apply physics
                    piece["x"] += piece["vx"]
                    piece["y"] += piece["vy"]
                    piece["vy"] += piece["gravity"]
                    piece["angle"] += piece["rotation"]
                    
                    # Remove pieces that fall off screen
                    if piece["y"] > self.height:
                        element["broken_pieces"].pop(i)
                    else:
                        i += 1
            
            elif element["type"] == "panel" and not element["broken"]:
                # Check if players are hitting the panel
                self._check_player_collision(element, player1_pos, player2_pos)
                
                # Panel breaks if health is below threshold
                if element["health"] <= element["breaking_threshold"] and not element["broken"]:
                    element["broken"] = True
                    
                    # Create broken pieces
                    for _ in range(random.randint(5, 8)):
                        # Random piece properties
                        piece_width = random.uniform(5, 15)
                        piece_height = random.uniform(5, 15)
                        piece_x = element["x"] + random.uniform(-element["width"]/2, element["width"]/2)
                        piece_y = element["y"] + random.uniform(-element["height"]/2, element["height"]/2)
                        
                        # Add random velocity
                        center_x = element["x"] + element["width"] / 2
                        center_y = element["y"] + element["height"] / 2
                        
                        # Direction away from center
                        dir_x = piece_x - center_x
                        dir_y = piece_y - center_y
                        
                        # Normalize and scale for velocity
                        length = max(0.1, math.sqrt(dir_x*dir_x + dir_y*dir_y))
                        dir_x /= length
                        dir_y /= length
                        
                        vx = dir_x * random.uniform(2, 5)
                        vy = dir_y * random.uniform(2, 5) - random.uniform(1, 3)  # Add upward component
                        
                        element["broken_pieces"].append({
                            "x": piece_x,
                            "y": piece_y,
                            "width": piece_width,
                            "height": piece_height,
                            "angle": random.uniform(0, math.pi * 2),
                            "rotation": random.uniform(-0.2, 0.2),
                            "vx": vx,
                            "vy": vy,
                            "gravity": 0.2
                        })
                
                # Update broken pieces
                i = 0
                while i < len(element["broken_pieces"]):
                    piece = element["broken_pieces"][i]
                    
                    # Apply physics
                    piece["x"] += piece["vx"]
                    piece["y"] += piece["vy"]
                    piece["vy"] += piece["gravity"]
                    piece["angle"] += piece["rotation"]
                    
                    # Slow down
                    piece["vx"] *= 0.98
                    piece["vy"] *= 0.98
                    
                    # Remove pieces that fall off screen or stop moving
                    if piece["y"] > self.height or (abs(piece["vx"]) < 0.1 and abs(piece["vy"]) < 0.1 and piece["y"] > 445):
                        element["broken_pieces"].pop(i)
                    else:
                        i += 1
            
            elif element["type"] == "candle":
                # Update flame flicker
                element["flame_flicker"] = math.sin(current_time * 0.1) * 0.5 + 0.5
                
                # Check if players are near the candle
                p1_dist = math.sqrt((player1_pos[0] - element["x"])**2 + (player1_pos[1] - element["y"])**2)
                p2_dist = math.sqrt((player2_pos[0] - element["x"])**2 + (player2_pos[1] - element["y"])**2)
                
                # Candle tips if player is close and moving fast
                if (p1_dist < 30 and abs(player1_pos[0] - element["x"]) < 20) or \
                   (p2_dist < 30 and abs(player2_pos[0] - element["x"]) < 20):
                    
                    if not element["tipped"]:
                        # Determine which direction to tip
                        if p1_dist < p2_dist:
                            tip_dir = 1 if player1_pos[0] > element["x"] else -1
                        else:
                            tip_dir = 1 if player2_pos[0] > element["x"] else -1
                        
                        element["tipped"] = True
                        element["tip_speed"] = tip_dir * 0.05
                
                # Update tipping animation
                if element["tipped"]:
                    element["tip_angle"] += element["tip_speed"]
                    
                    # Cap the angle
                    max_angle = math.pi / 2
                    element["tip_angle"] = max(-max_angle, min(max_angle, element["tip_angle"]))
                    
                    # If candle is horizontal, stop tipping
                    if abs(element["tip_angle"]) >= max_angle * 0.95:
                        element["tip_speed"] = 0
            
            elif element["type"] == "vase" and not element["broken"]:
                # Check if players are hitting the vase
                self._check_player_collision(element, player1_pos, player2_pos)
                
                # Vase breaks if health is below threshold
                if element["health"] <= element["breaking_threshold"] and not element["broken"]:
                    element["broken"] = True
                    
                    # Create broken pieces in a circular pattern
                    pieces = random.randint(6, 10)
                    for i in range(pieces):
                        angle = i * (2 * math.pi / pieces)
                        
                        # Add random velocity in that direction
                        speed = random.uniform(3, 6)
                        vx = math.cos(angle) * speed
                        vy = math.sin(angle) * speed - random.uniform(1, 4)  # Add upward component
                        
                        element["broken_pieces"].append({
                            "x": element["x"] + element["width"] / 2,
                            "y": element["y"] + element["height"] / 2,
                            "width": random.uniform(3, 8),
                            "height": random.uniform(3, 8),
                            "angle": random.uniform(0, math.pi * 2),
                            "rotation": random.uniform(-0.3, 0.3),
                            "vx": vx,
                            "vy": vy,
                            "gravity": 0.2,
                            "color": element["color"] if random.random() < 0.7 else element["pattern_color"]
                        })
                
                # Update broken pieces
                i = 0
                while i < len(element["broken_pieces"]):
                    piece = element["broken_pieces"][i]
                    
                    # Apply physics
                    piece["x"] += piece["vx"]
                    piece["y"] += piece["vy"]
                    piece["vy"] += piece["gravity"]
                    piece["angle"] += piece["rotation"]
                    
                    # Add friction when on ground
                    if piece["y"] > 445:
                        piece["y"] = 445
                        piece["vy"] *= -0.3  # Bounce with energy loss
                        piece["vx"] *= 0.8   # Friction
                    
                    # Remove pieces that stop moving or go off screen
                    if piece["y"] > self.height or (abs(piece["vx"]) < 0.1 and abs(piece["vy"]) < 0.1 and piece["y"] >= 445):
                        element["broken_pieces"].pop(i)
                    else:
                        i += 1
            
            elif element["type"] == "sand_patch":
                # Check if players are on the sand patch
                p1_on_sand = math.sqrt((player1_pos[0] - element["x"])**2) < element["radius"]
                p2_on_sand = math.sqrt((player2_pos[0] - element["x"])**2) < element["radius"]
                
                # Create dust particles when players move on sand
                if p1_on_sand and random.random() < 0.1:
                    # Add dust particles at player's feet
                    for _ in range(random.randint(1, 3)):
                        element["dust_particles"].append({
                            "x": player1_pos[0] + random.uniform(-10, 10),
                            "y": 450, 
                            "vx": random.uniform(-0.5, 0.5),
                            "vy": random.uniform(-1, -0.2),
                            "size": random.uniform(1, 3),
                            "alpha": random.uniform(100, 150),
                            "fade_speed": random.uniform(1, 3),
                            "life": random.randint(20, 40)
                        })
                
                if p2_on_sand and random.random() < 0.1:
                    # Add dust particles at player's feet
                    for _ in range(random.randint(1, 3)):
                        element["dust_particles"].append({
                            "x": player2_pos[0] + random.uniform(-10, 10),
                            "y": 450, 
                            "vx": random.uniform(-0.5, 0.5),
                            "vy": random.uniform(-1, -0.2),
                            "size": random.uniform(1, 3),
                            "alpha": random.uniform(100, 150),
                            "fade_speed": random.uniform(1, 3),
                            "life": random.randint(20, 40)
                        })
                
                # Update dust particles
                i = 0
                while i < len(element["dust_particles"]):
                    dust = element["dust_particles"][i]
                    
                    # Update position
                    dust["x"] += dust["vx"]
                    dust["y"] += dust["vy"]
                    
                    # Slow down
                    dust["vx"] *= 0.98
                    dust["vy"] *= 0.98
                    
                    # Update lifetime and alpha
                    dust["life"] -= 1
                    dust["alpha"] = max(0, dust["alpha"] - dust["fade_speed"])
                    
                    # Remove dead particles
                    if dust["life"] <= 0 or dust["alpha"] <= 0:
                        element["dust_particles"].pop(i)
                    else:
                        i += 1
            
            elif element["type"] == "lava_crack":
                # Update glow pulsing
                element["glow_intensity"] = 0.6 + math.sin(current_time * 0.05) * 0.2
                
                # Check if players are near the lava crack
                p1_near = abs(player1_pos[0] - element["x"]) < element["width"] / 2 + 10
                p2_near = abs(player2_pos[0] - element["x"]) < element["width"] / 2 + 10
                
                # Create lava spurt if player steps on crack and cooldown is over
                if (p1_near or p2_near) and current_time - element["last_trigger"] > element["cooldown"]:
                    element["last_trigger"] = current_time
                    
                    # Add lava particles for spurt
                    for _ in range(random.randint(5, 10)):
                        angle = random.uniform(-math.pi/3, math.pi/3) - math.pi/2  # Mostly upward
                        speed = random.uniform(3, 7)
                        size = random.uniform(2, 5)
                        
                        element["particles"].append({
                            "x": element["x"] + random.uniform(-element["width"]/4, element["width"]/4),
                            "y": element["y"], 
                            "vx": math.cos(angle) * speed,
                            "vy": math.sin(angle) * speed,
                            "size": size,
                            "color": (255, 100 + random.randint(0, 100), 0),
                            "alpha": 255,
                            "fade_speed": random.uniform(2, 5),
                            "life": random.randint(30, 60),
                            "gravity": 0.15
                        })
                
                # Update lava particles
                i = 0
                while i < len(element["particles"]):
                    particle = element["particles"][i]
                    
                    # Update position
                    particle["x"] += particle["vx"]
                    particle["y"] += particle["vy"]
                    
                    # Apply gravity
                    particle["vy"] += particle["gravity"]
                    
                    # Update lifetime and alpha
                    particle["life"] -= 1
                    particle["alpha"] = max(0, particle["alpha"] - particle["fade_speed"])
                    
                    # Remove dead particles or those that hit the ground
                    if particle["life"] <= 0 or particle["alpha"] <= 0 or particle["y"] >= 450:
                        element["particles"].pop(i)
                    else:
                        i += 1

    def _check_player_collision(self, element, player1_pos, player2_pos):
        """Check if players are hitting an element and damage it if so."""
        # Define the element's rectangle
        element_rect = pygame.Rect(
            element["x"], 
            element["y"],
            element["width"],
            element["height"]
        )
        
        # Check if player 1 is attacking this element
        p1_rect = pygame.Rect(player1_pos[0] - 30, player1_pos[1] - 100, 60, 100)
        if p1_rect.colliderect(element_rect) and element["type"] not in self.interacted_elements:
            # Only damage if player is attacking
            # This would need to be integrated with your actual attack detection
            if random.random() < 0.1:  # Simplified check, replace with actual attack logic
                element["health"] -= random.randint(5, 15)
                self.interacted_elements.add(element["type"])
                
        # Check if player 2 is attacking this element
        p2_rect = pygame.Rect(player2_pos[0] - 30, player2_pos[1] - 100, 60, 100)
        if p2_rect.colliderect(element_rect) and element["type"] not in self.interacted_elements:
            # Only damage if player is attacking
            if random.random() < 0.1:  # Simplified check, replace with actual attack logic
                element["health"] -= random.randint(5, 15)
                self.interacted_elements.add(element["type"])
    
    def render(self, screen):
        """Render all interactive background elements."""
        # Render grass elements
        for grass in self.grass_elements:
            # Draw each blade of grass
            for i, blade_pos in enumerate(grass["blades"]):
                blade_x = grass["x"] - grass["width"] // 2 + int(blade_pos * grass["width"])
                blade_height = grass["original_height"] * (0.8 + blade_pos * 0.4)  # Vary height a bit
                
                # Apply sway to each blade
                sway_offset = grass["sway"] * blade_height * 0.05
                
                # Draw a blade (simple line for now)
                blade_points = [
                    (blade_x, grass["y"]),
                    (blade_x + sway_offset, grass["y"] - blade_height)
                ]
                pygame.draw.line(screen, grass["color"], blade_points[0], blade_points[1], 2)
        
        # Render other interactive elements
        for element in self.elements:
            if element["type"] == "branch":
                if not element["broken"]:
                    # Draw intact branch
                    branch_surf = pygame.Surface((int(element["width"]), int(element["height"])), pygame.SRCALPHA)
                    pygame.draw.rect(branch_surf, element["color"], (0, 0, int(element["width"]), int(element["height"])))
                    
                    # Rotate branch
                    rotated = pygame.transform.rotate(branch_surf, math.degrees(element["angle"]))
                    rotated_rect = rotated.get_rect(center=(element["x"] + element["width"]//2, element["y"] + element["height"]//2))
                    screen.blit(rotated, rotated_rect)
                else:
                    # Draw broken pieces
                    for piece in element["broken_pieces"]:
                        piece_surf = pygame.Surface((int(piece["width"]), int(piece["height"])), pygame.SRCALPHA)
                        pygame.draw.rect(piece_surf, element["color"], (0, 0, int(piece["width"]), int(piece["height"])))
                        
                        # Rotate piece
                        rotated = pygame.transform.rotate(piece_surf, math.degrees(piece["angle"]))
                        rotated_rect = rotated.get_rect(center=(piece["x"] + piece["width"]//2, piece["y"] + piece["height"]//2))
                        screen.blit(rotated, rotated_rect)
            
            elif element["type"] == "panel":
                if not element["broken"]:
                    # Draw wooden panel
                    pygame.draw.rect(screen, element["color"], 
                                   (element["x"], element["y"], element["width"], element["height"]))
                    
                    # Add wood grain details
                    grain_color = (element["color"][0] - 20, element["color"][1] - 20, element["color"][2] - 20)
                    for i in range(3):
                        pygame.draw.line(screen, grain_color, 
                                       (element["x"], element["y"] + i * element["height"]//3), 
                                       (element["x"] + element["width"], element["y"] + i * element["height"]//3),
                                       1)
                else:
                    # Draw broken pieces
                    for piece in element["broken_pieces"]:
                        piece_surf = pygame.Surface((int(piece["width"]), int(piece["height"])), pygame.SRCALPHA)
                        pygame.draw.rect(piece_surf, element["color"], (0, 0, int(piece["width"]), int(piece["height"])))
                        
                        # Rotate piece
                        rotated = pygame.transform.rotate(piece_surf, math.degrees(piece["angle"]))
                        rotated_rect = rotated.get_rect(center=(piece["x"] + piece["width"]//2, piece["y"] + piece["height"]//2))
                        screen.blit(rotated, rotated_rect)
            
            elif element["type"] == "candle":
                # Get candle position taking into account tipping
                tip_x = element["x"] + math.sin(element["tip_angle"]) * element["height"] / 2
                tip_y = element["y"] - math.cos(element["tip_angle"]) * element["height"] / 2
                
                # Draw candle body
                candle_surf = pygame.Surface((int(element["width"]), int(element["height"])), pygame.SRCALPHA)
                pygame.draw.rect(candle_surf, element["color"], (0, 0, int(element["width"]), int(element["height"])))
                
                # Rotate candle
                rotated = pygame.transform.rotate(candle_surf, math.degrees(element["tip_angle"]))
                rotated_rect = rotated.get_rect(center=(element["x"], element["y"] - element["height"]//2))
                screen.blit(rotated, rotated_rect)
                
                # Draw flame if candle is not tipped too much
                if abs(element["tip_angle"]) < math.pi / 3:
                    # Flame position adjusted for tipping
                    flame_x = tip_x
                    flame_y = tip_y - 5
                    
                    # Draw flickering flame
                    flame_size = element["flame_size"] * (0.8 + element["flame_flicker"] * 0.4)
                    
                    # Flame outer glow
                    glow_surf = pygame.Surface((int(flame_size * 4), int(flame_size * 4)), pygame.SRCALPHA)
                    glow_color = (255, 200, 100, 50)
                    pygame.draw.ellipse(glow_surf, glow_color, (0, 0, int(flame_size * 4), int(flame_size * 4)))
                    glow_rect = glow_surf.get_rect(center=(flame_x, flame_y))
                    screen.blit(glow_surf, glow_rect)
                    
                    # Flame base
                    pygame.draw.circle(screen, (255, 200, 50), (int(flame_x), int(flame_y)), int(flame_size))
                    
                    # Flame inner core
                    pygame.draw.circle(screen, (255, 255, 200), (int(flame_x), int(flame_y) - int(flame_size * 0.3)), int(flame_size * 0.5))
            
            elif element["type"] == "vase":
                if not element["broken"]:
                    # Draw vase body
                    pygame.draw.ellipse(screen, element["color"], 
                                      (element["x"], element["y"], element["width"], element["height"]))
                    
                    # Draw decorative pattern
                    pattern_rect = pygame.Rect(element["x"] + 3, element["y"] + 5, element["width"] - 6, element["height"] - 10)
                    pygame.draw.ellipse(screen, element["pattern_color"], pattern_rect)
                else:
# Draw broken pieces
                    for piece in element["broken_pieces"]:
                        piece_surf = pygame.Surface((int(piece["width"] * 2), int(piece["height"] * 2)), pygame.SRCALPHA)
                        pygame.draw.ellipse(piece_surf, piece["color"], 
                                          (0, 0, int(piece["width"] * 2), int(piece["height"] * 2)))
                        
                        # Rotate piece
                        rotated = pygame.transform.rotate(piece_surf, math.degrees(piece["angle"]))
                        rotated_rect = rotated.get_rect(center=(piece["x"], piece["y"]))
                        screen.blit(rotated, rotated_rect)
            
            elif element["type"] == "sand_patch":
                # Draw sand patch
                pygame.draw.circle(screen, element["color"], (int(element["x"]), int(element["y"])), int(element["radius"]))
                
                # Draw dust particles
                for dust in element["dust_particles"]:
                    dust_surf = pygame.Surface((int(dust["size"] * 2), int(dust["size"] * 2)), pygame.SRCALPHA)
                    dust_color = (*element["color"], int(dust["alpha"]))
                    pygame.draw.circle(dust_surf, dust_color, 
                                     (int(dust["size"]), int(dust["size"])), int(dust["size"]))
                    screen.blit(dust_surf, (int(dust["x"] - dust["size"]), int(dust["y"] - dust["size"])))
            
            elif element["type"] == "lava_crack":
                # Draw lava crack
                pygame.draw.ellipse(screen, element["color"], 
                                  (element["x"] - element["width"]//2, element["y"] - element["height"]//2, 
                                   element["width"], element["height"]))
                
                # Add glow effect
                glow_surf = pygame.Surface((int(element["width"] * 1.5), int(element["height"] * 3)), pygame.SRCALPHA)
                glow_color = (255, 150, 0, int(50 * element["glow_intensity"]))
                pygame.draw.ellipse(glow_surf, glow_color, 
                                  (0, 0, int(element["width"] * 1.5), int(element["height"] * 3)))
                screen.blit(glow_surf, (int(element["x"] - element["width"] * 0.75), 
                                     int(element["y"] - element["height"] * 1.5)))
                
                # Draw lava particles
                for particle in element["particles"]:
                    particle_surf = pygame.Surface((int(particle["size"] * 2), int(particle["size"] * 2)), pygame.SRCALPHA)
                    particle_color = (*particle["color"], int(particle["alpha"]))
                    pygame.draw.circle(particle_surf, particle_color, 
                                     (int(particle["size"]), int(particle["size"])), int(particle["size"]))
                    screen.blit(particle_surf, (int(particle["x"] - particle["size"]), int(particle["y"] - particle["size"])))