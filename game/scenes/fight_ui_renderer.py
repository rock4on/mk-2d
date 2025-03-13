import pygame
import math

class FightUIRenderer:
    """Handles rendering UI elements for the fight scene."""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
    
    def render(self, screen, player1, player2, remaining_time, 
               round_number, max_rounds, victories, hit_counter, max_combo,
               ai_enabled, ai_difficulty, round_started, round_over):
        """Render all UI elements for the fight scene."""
        # Draw health bars
        self._draw_health_bars(screen, player1, player2)
        
        # Draw time remaining
        self._draw_timer(screen, remaining_time)
        
        # Draw round indicator and victory stars
        self._draw_round_indicator(screen, round_number, max_rounds, victories)
        
        # Draw AI state
        self._draw_ai_indicator(screen, ai_enabled, ai_difficulty)
        
        # Draw combat stats
        if round_started and not round_over:
            self._draw_stats(screen, hit_counter, max_combo)
        
        # Draw controls help
        self._draw_controls_help(screen)
        
        # Draw character moves info
        if round_started and not round_over:
            self._draw_moves_info(screen, player1)
    
    def _draw_health_bars(self, screen, player1, player2):
        """Draw stylized health bars for both players."""
        # Create backdrop for health bars
        top_panel = pygame.Surface((self.game_engine.width, 80), pygame.SRCALPHA)
        top_panel.fill((0, 0, 0, 150))
        screen.blit(top_panel, (0, 0))
        
        # Calculate actual health percentages
        p1_health_percent = max(0, min(1.0, player1.health / player1.max_health))
        p2_health_percent = max(0, min(1.0, player2.health / player2.max_health))
        
        # Player 1 health bar (left side)
        health_bg_rect1 = pygame.Rect(50, 30, 250, 20)
        health_border1 = pygame.Rect(45, 25, 260, 30)
        health_fill_rect1 = pygame.Rect(50, 30, int(250 * p1_health_percent), 20)
        
        # Draw glowing border based on health
        border_color = (
            max(0, min(255, int(255 * (1 - p1_health_percent)))),
            max(0, min(255, int(255 * p1_health_percent))),
            50
        )
        
        # Draw bar shadows (3D effect)
        shadow_offset = 2
        shadow_rect1 = pygame.Rect(
            health_border1.x + shadow_offset, 
            health_border1.y + shadow_offset,
            health_border1.width,
            health_border1.height
        )
        pygame.draw.rect(screen, (10, 10, 10, 150), shadow_rect1, 3, border_radius=5)
        
        # Draw border and background
        pygame.draw.rect(screen, border_color, health_border1, 3, border_radius=5)
        pygame.draw.rect(screen, (30, 30, 30), health_bg_rect1, border_radius=3)
        
        # Health bar with gradient effect
        health_percent = p1_health_percent
        
        # Create gradient colors
        if health_percent > 0.6:
            gradient_start = (50, 200, 50)  # Dark green
            gradient_end = (150, 255, 150)  # Light green
        elif health_percent > 0.3:
            gradient_start = (200, 200, 50)  # Dark yellow
            gradient_end = (255, 255, 150)  # Light yellow
        else:
            gradient_start = (200, 50, 50)  # Dark red
            gradient_end = (255, 150, 150)  # Light red
            
            # Flashing effect for critical health
            if player1.health < player1.max_health * 0.15 and pygame.time.get_ticks() % 500 < 250:
                gradient_start = (255, 0, 0)
                gradient_end = (255, 100, 100)
        
        # Draw gradient health bar
        bar_width = int(250 * health_percent)
        if bar_width > 0:
            for i in range(bar_width):
                progress = i / 250  # Position along bar (0 to 1)
                color = (
                    max(0, min(255, int(gradient_start[0] + (gradient_end[0] - gradient_start[0]) * progress))),
                    max(0, min(255, int(gradient_start[1] + (gradient_end[1] - gradient_start[1]) * progress))),
                    max(0, min(255, int(gradient_start[2] + (gradient_end[2] - gradient_start[2]) * progress)))
                )
                pygame.draw.line(screen, color, (50 + i, 30), (50 + i, 49))
        
        # Add highlights to bar
        if bar_width > 5:
            highlight_rect = pygame.Rect(50, 30, bar_width, 5)
            pygame.draw.rect(screen, (255, 255, 255, 70), highlight_rect, border_radius=2)
        
        # Player 2 health bar (right side)
        health_bg_rect2 = pygame.Rect(500, 30, 250, 20)
        health_border2 = pygame.Rect(495, 25, 260, 30) 
        health_fill_width = int(250 * p2_health_percent)
        health_fill_rect2 = pygame.Rect(500 + 250 - health_fill_width, 30, health_fill_width, 20)
        
        # Draw shadow for 3D effect
        shadow_rect2 = pygame.Rect(
            health_border2.x + shadow_offset, 
            health_border2.y + shadow_offset,
            health_border2.width,
            health_border2.height
        )
        pygame.draw.rect(screen, (10, 10, 10, 150), shadow_rect2, 3, border_radius=5)
        
        # Draw glowing border based on health
        border_color2 = (
            max(0, min(255, int(255 * (1 - p2_health_percent)))),
            max(0, min(255, int(255 * p2_health_percent))),
            50
        )
        pygame.draw.rect(screen, border_color2, health_border2, 3, border_radius=5)
        pygame.draw.rect(screen, (30, 30, 30), health_bg_rect2, border_radius=3)
        
        # Health bar with gradient
        health_percent2 = p2_health_percent
        
        # Create gradient colors
        if health_percent2 > 0.6:
            gradient_start = (50, 200, 50)  # Dark green
            gradient_end = (150, 255, 150)  # Light green
        elif health_percent2 > 0.3:
            gradient_start = (200, 200, 50)  # Dark yellow
            gradient_end = (255, 255, 150)  # Light yellow
        else:
            gradient_start = (200, 50, 50)  # Dark red
            gradient_end = (255, 150, 150)  # Light red
            
            # Flashing effect for critical health
            if player2.health < player2.max_health * 0.15 and pygame.time.get_ticks() % 500 < 250:
                gradient_start = (255, 0, 0)
                gradient_end = (255, 100, 100)
        
        # Draw gradient health bar (right to left for player 2)
        if health_fill_width > 0:
            for i in range(health_fill_width):
                progress = 1 - (i / 250)  # Reversed for player 2
                color = (
                    max(0, min(255, int(gradient_start[0] + (gradient_end[0] - gradient_start[0]) * progress))),
                    max(0, min(255, int(gradient_start[1] + (gradient_end[1] - gradient_start[1]) * progress))),
                    max(0, min(255, int(gradient_start[2] + (gradient_end[2] - gradient_start[2]) * progress)))
                )
                x_pos = 750 - i
                pygame.draw.line(screen, color, (x_pos, 30), (x_pos, 49))
        
        # Add highlights to bar
        if health_fill_width > 5:
            highlight_rect = pygame.Rect(750 - health_fill_width, 30, health_fill_width, 5)
            pygame.draw.rect(screen, (255, 255, 255, 70), highlight_rect, border_radius=2)
        
        # Display numerical health with shadow effect
        # Make sure to clamp health to 0 for display purposes
        display_health1 = max(0, player1.health)
        display_health2 = max(0, player2.health)
        
        health_text1 = f"{display_health1}/{player1.max_health}"
        # Text shadow
        shadow_surf1 = self.game_engine.fonts['small'].render(health_text1, True, (0, 0, 0))
        shadow_rect1 = shadow_surf1.get_rect(center=(177, 42))
        screen.blit(shadow_surf1, shadow_rect1)
        # Actual text
        health_surf1 = self.game_engine.fonts['small'].render(health_text1, True, (255, 255, 255))
        health_rect1 = health_surf1.get_rect(center=(175, 40))
        screen.blit(health_surf1, health_rect1)
        
        health_text2 = f"{display_health2}/{player2.max_health}"
        # Text shadow
        shadow_surf2 = self.game_engine.fonts['small'].render(health_text2, True, (0, 0, 0))
        shadow_rect2 = shadow_surf2.get_rect(center=(627, 42))
        screen.blit(shadow_surf2, shadow_rect2)
        # Actual text
        health_surf2 = self.game_engine.fonts['small'].render(health_text2, True, (255, 255, 255))
        health_rect2 = health_surf2.get_rect(center=(625, 40))
        screen.blit(health_surf2, health_rect2)
        
        # Player names above health bars with icon
        p1_name = player1.__class__.__name__.upper()
        p2_name = player2.__class__.__name__.upper()
        
        # Create player icon circles
        icon_radius = 12
        pygame.draw.circle(screen, (100, 100, 255), (50, 15), icon_radius)
        pygame.draw.circle(screen, (0, 0, 0), (50, 15), icon_radius, 1)
        pygame.draw.circle(screen, (255, 100, 100), (750, 15), icon_radius)
        pygame.draw.circle(screen, (0, 0, 0), (750, 15), icon_radius, 1)
        
        # Draw "P1" and "P2" in the icons
        p1_icon = self.game_engine.fonts['small'].render("P1", True, (255, 255, 255))
        p1_icon_rect = p1_icon.get_rect(center=(50, 15))
        screen.blit(p1_icon, p1_icon_rect)
        
        p2_icon = self.game_engine.fonts['small'].render("P2", True, (255, 255, 255))
        p2_icon_rect = p2_icon.get_rect(center=(750, 15))
        screen.blit(p2_icon, p2_icon_rect)
        
        # Draw character names with shadow effect
        # Text shadow
        p1_shadow = self.game_engine.fonts['small'].render(p1_name, True, (0, 0, 0))
        p1_shadow_rect = p1_shadow.get_rect(midleft=(70, 17))
        screen.blit(p1_shadow, p1_shadow_rect)
        # Actual text
        p1_name_surf = self.game_engine.fonts['small'].render(p1_name, True, (220, 220, 255))
        p1_name_rect = p1_name_surf.get_rect(midleft=(68, 15))
        screen.blit(p1_name_surf, p1_name_rect)
        
        # Text shadow
        p2_shadow = self.game_engine.fonts['small'].render(p2_name, True, (0, 0, 0))
        p2_shadow_rect = p2_shadow.get_rect(midright=(730, 17))
        screen.blit(p2_shadow, p2_shadow_rect)
        # Actual text
        p2_name_surf = self.game_engine.fonts['small'].render(p2_name, True, (255, 220, 220))
        p2_name_rect = p2_name_surf.get_rect(midright=(728, 15))
        screen.blit(p2_name_surf, p2_name_rect)
    
    def _draw_timer(self, screen, remaining_time):
        """Draw the countdown timer with effects."""
        time_color = (255, 255, 255)
        time_scale = 1.0
        
        if remaining_time < 10:
            time_color = (255, 50, 50)
            # Pulsing effect for low time
            if pygame.time.get_ticks() % 500 < 250:
                time_color = (255, 100, 100)
                time_scale = 1.1
        
        # Create timer background
        timer_bg_width = 80
        timer_bg_height = 40
        timer_bg_rect = pygame.Rect(
            self.game_engine.width // 2 - timer_bg_width // 2,
            20,
            timer_bg_width,
            timer_bg_height
        )
        
        # Draw timer background with shadow
        shadow_offset = 2
        shadow_rect = pygame.Rect(
            timer_bg_rect.x + shadow_offset,
            timer_bg_rect.y + shadow_offset,
            timer_bg_rect.width,
            timer_bg_rect.height
        )
        pygame.draw.rect(screen, (10, 10, 10, 150), shadow_rect, border_radius=10)
        pygame.draw.rect(screen, (50, 50, 80), timer_bg_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 150), timer_bg_rect, 2, border_radius=10)
        
        # Draw time with shadow
        shadow_surf = self.game_engine.fonts['large'].render(str(remaining_time), True, (0, 0, 0))
        shadow_surf = pygame.transform.scale(shadow_surf, 
                                          (int(shadow_surf.get_width() * time_scale), 
                                           int(shadow_surf.get_height() * time_scale)))
        shadow_rect = shadow_surf.get_rect(center=(self.game_engine.width // 2 + 2, 42))
        screen.blit(shadow_surf, shadow_rect)
        
        # Draw actual time
        time_surf = self.game_engine.fonts['large'].render(str(remaining_time), True, time_color)
        time_scaled = pygame.transform.scale(time_surf, 
                                          (int(time_surf.get_width() * time_scale), 
                                           int(time_surf.get_height() * time_scale)))
        time_rect = time_scaled.get_rect(center=(self.game_engine.width // 2, 40))
        screen.blit(time_scaled, time_rect)
        
        # Add clock icon
        clock_radius = 8
        pygame.draw.circle(screen, (200, 200, 200), (timer_bg_rect.x + 20, timer_bg_rect.y + timer_bg_height // 2), clock_radius)
        pygame.draw.circle(screen, (50, 50, 80), (timer_bg_rect.x + 20, timer_bg_rect.y + timer_bg_height // 2), clock_radius, 1)
        
        # Draw clock hands
        center_x = timer_bg_rect.x + 20
        center_y = timer_bg_rect.y + timer_bg_height // 2
        
        # Hour hand (points to 10 o'clock position)
        hour_angle = math.radians(300)  # 10 o'clock
        hour_length = clock_radius * 0.5
        hour_x = center_x + math.cos(hour_angle) * hour_length
        hour_y = center_y + math.sin(hour_angle) * hour_length
        pygame.draw.line(screen, (50, 50, 80), (center_x, center_y), (hour_x, hour_y), 2)
        
        # Minute hand (moves based on remaining time)
        minute_angle = math.radians(90 - (remaining_time / 60 * 360))
        minute_length = clock_radius * 0.7
        minute_x = center_x + math.cos(minute_angle) * minute_length
        minute_y = center_y + math.sin(minute_angle) * minute_length
        pygame.draw.line(screen, (50, 50, 80), (center_x, center_y), (minute_x, minute_y), 1)
    
    def _draw_round_indicator(self, screen, round_number, max_rounds, victories):
        """Draw the round indicator and victory stars."""
        # Create round indicator background
        round_bg_width = 150
        round_bg_height = 30
        round_bg_rect = pygame.Rect(
            self.game_engine.width // 2 - round_bg_width // 2,
            60,
            round_bg_width,
            round_bg_height
        )
        
        # Draw rounded rectangle with shadow
        shadow_offset = 2
        shadow_rect = pygame.Rect(
            round_bg_rect.x + shadow_offset,
            round_bg_rect.y + shadow_offset,
            round_bg_rect.width,
            round_bg_rect.height
        )
        pygame.draw.rect(screen, (10, 10, 10, 150), shadow_rect, border_radius=15)
        pygame.draw.rect(screen, (60, 60, 20), round_bg_rect, border_radius=15)
        pygame.draw.rect(screen, (180, 180, 40), round_bg_rect, 2, border_radius=15)
        
        # Round text with shadow
        round_text = f"ROUND {round_number}/{max_rounds}"
        
        # Text shadow
        shadow_surf = self.game_engine.fonts['small'].render(round_text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(self.game_engine.width // 2 + 1, 76))
        screen.blit(shadow_surf, shadow_rect)
        
        # Actual text
        round_surf = self.game_engine.fonts['small'].render(round_text, True, (255, 255, 100))
        round_rect = round_surf.get_rect(center=(self.game_engine.width // 2, 75))
        screen.blit(round_surf, round_rect)
        
        # Victory indicators container panels
        p1_panel_width = max(1, victories[0]) * 35 + 15
        p1_panel_rect = pygame.Rect(50, 60, p1_panel_width, 30)
        
        p2_panel_width = max(1, victories[1]) * 35 + 15
        p2_panel_rect = pygame.Rect(self.game_engine.width - 50 - p2_panel_width, 60, p2_panel_width, 30)
        
        # Draw victory panels with shadows and gradient
        if victories[0] > 0:
            # Player 1 panel shadow
            shadow_rect = pygame.Rect(
                p1_panel_rect.x + shadow_offset,
                p1_panel_rect.y + shadow_offset,
                p1_panel_rect.width,
                p1_panel_rect.height
            )
            pygame.draw.rect(screen, (10, 10, 10, 150), shadow_rect, border_radius=15)
            
            # Create gradient panel
            for x in range(p1_panel_width):
                progress = x / p1_panel_width
                color = (
                    int(50 + progress * 50),
                    int(50 + progress * 100),
                    int(150 + progress * 100)
                )
                pygame.draw.line(screen, color, 
                               (p1_panel_rect.x + x, p1_panel_rect.y), 
                               (p1_panel_rect.x + x, p1_panel_rect.y + p1_panel_rect.height))
            
            pygame.draw.rect(screen, (100, 100, 255), p1_panel_rect, 2, border_radius=15)
        
        if victories[1] > 0:
            # Player 2 panel shadow
            shadow_rect = pygame.Rect(
                p2_panel_rect.x + shadow_offset,
                p2_panel_rect.y + shadow_offset,
                p2_panel_rect.width,
                p2_panel_rect.height
            )
            pygame.draw.rect(screen, (10, 10, 10, 150), shadow_rect, border_radius=15)
            
            # Create gradient panel
            for x in range(p2_panel_width):
                progress = 1 - (x / p2_panel_width)  # Reversed for player 2
                color = (
                    int(150 + progress * 100),
                    int(50 + progress * 50),
                    int(50 + progress * 50)
                )
                pygame.draw.line(screen, color, 
                               (p2_panel_rect.x + x, p2_panel_rect.y), 
                               (p2_panel_rect.x + x, p2_panel_rect.y + p2_panel_rect.height))
            
            pygame.draw.rect(screen, (255, 100, 100), p2_panel_rect, 2, border_radius=15)
        
        # Victory indicators (stars) with animation
        for i in range(victories[0]):
            star_x = 65 + i * 30
            star_y = 75
            self._draw_star(screen, star_x, star_y, (255, 255, 100))
        
        for i in range(victories[1]):
            star_x = self.game_engine.width - 65 - i * 30
            star_y = 75
            self._draw_star(screen, star_x, star_y, (255, 255, 100))
    
    def _draw_star(self, screen, x, y, color, size=12):
        """Draw an animated star shape for victory indicators."""
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.2 + 0.8
        adjusted_size = size * pulse
        
        points = []
        for i in range(10):
            angle = math.pi * 2 * i / 10
            # Alternate between outer and inner radius
            radius = adjusted_size if i % 2 == 0 else adjusted_size / 2
            px = x + math.sin(angle) * radius
            py = y - math.cos(angle) * radius  # Negative for y to flip
            points.append((px, py))
        
        # Add glow effect
        glow_surf = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
        glow_color = (*color, 50)
        pygame.draw.polygon(glow_surf, glow_color, [
            (p[0] - x + size*2, p[1] - y + size*2) for p in points
        ])
        screen.blit(glow_surf, (x - size*2, y - size*2))
        
        # Draw star
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 1)  # Black outline
    
    def _draw_ai_indicator(self, screen, ai_enabled, ai_difficulty):
        """Draw the AI status indicator."""
        # Create AI indicator background
        ai_bg_width = 150
        ai_bg_height = 24
        ai_bg_rect = pygame.Rect(
            self.game_engine.width - ai_bg_width - 10,
            10,
            ai_bg_width,
            ai_bg_height
        )
        
        # Draw AI indicator background with rounded corners
        pygame.draw.rect(screen, (0, 0, 0, 120), ai_bg_rect, border_radius=12)
        
        # AI status text and color
        if ai_enabled:
            ai_text = f"AI: ON (LEVEL {ai_difficulty})"
            ai_color = (100, 255, 100)
            # Draw AI difficulty indicators (1-3 dots)
            for i in range(ai_difficulty):
                dot_x = ai_bg_rect.right - 15 - (i * 10)
                dot_y = ai_bg_rect.centery
                pygame.draw.circle(screen, ai_color, (dot_x, dot_y), 3)
        else:
            ai_text = "AI: OFF"
            ai_color = (255, 100, 100)
        
        # Add computer icon
        pygame.draw.rect(screen, ai_color, (ai_bg_rect.x + 10, ai_bg_rect.centery - 5, 10, 10), 1, border_radius=2)
        pygame.draw.rect(screen, ai_color, (ai_bg_rect.x + 8, ai_bg_rect.centery + 5, 14, 2))
            
        # Draw text with shadow
        ai_shadow = self.game_engine.fonts['small'].render(ai_text, True, (0, 0, 0))
        ai_shadow_rect = ai_shadow.get_rect(midleft=(ai_bg_rect.x + 30, ai_bg_rect.centery + 1))
        screen.blit(ai_shadow, ai_shadow_rect)
        
        ai_surf = self.game_engine.fonts['small'].render(ai_text, True, ai_color)
        ai_rect = ai_surf.get_rect(midleft=(ai_bg_rect.x + 28, ai_bg_rect.centery))
        screen.blit(ai_surf, ai_rect)
    
    def _draw_stats(self, screen, hit_counter, max_combo):
        """Draw combat statistics."""
        # Create stats panel background
        stats_width = 180
        stats_height = 50
        stats_rect = pygame.Rect(10, self.game_engine.height - stats_height - 10, stats_width, stats_height)
        
        # Draw rounded panel with shadow
        shadow_offset = 2
        shadow_rect = pygame.Rect(
            stats_rect.x + shadow_offset,
            stats_rect.y + shadow_offset,
            stats_rect.width,
            stats_rect.height
        )
        pygame.draw.rect(screen, (10, 10, 10, 150), shadow_rect, border_radius=10)
        
        # Background with gradient
        for y in range(stats_height):
            progress = y / stats_height
            color = (
                int(20 + progress * 20),
                int(20 + progress * 20),
                int(40 + progress * 30),
                200
            )
            pygame.draw.line(screen, color, 
                          (stats_rect.x, stats_rect.y + y), 
                          (stats_rect.x + stats_rect.width, stats_rect.y + y))
        
        pygame.draw.rect(screen, (80, 80, 120), stats_rect, 2, border_radius=10)
        
        # Stats title
        title_text = "BATTLE STATS"
        title_shadow = self.game_engine.fonts['small'].render(title_text, True, (0, 0, 0))
        title_shadow_rect = title_shadow.get_rect(midtop=(stats_rect.centerx + 1, stats_rect.y + 6))
        screen.blit(title_shadow, title_shadow_rect)
        
        title_surf = self.game_engine.fonts['small'].render(title_text, True, (180, 180, 255))
        title_rect = title_surf.get_rect(midtop=(stats_rect.centerx, stats_rect.y + 5))
        screen.blit(title_surf, title_rect)
        
        # Draw hit counter with icon
        pygame.draw.circle(screen, (200, 200, 200), (stats_rect.x + 20, stats_rect.y + 30), 6)
        pygame.draw.circle(screen, (0, 0, 0), (stats_rect.x + 20, stats_rect.y + 30), 6, 1)
        pygame.draw.line(screen, (0, 0, 0), (stats_rect.x + 20, stats_rect.y + 30), (stats_rect.x + 24, stats_rect.y + 26), 2)
        
        hits_text = f"Hits: {hit_counter}"
        hits_shadow = self.game_engine.fonts['small'].render(hits_text, True, (0, 0, 0))
        hits_shadow_rect = hits_shadow.get_rect(midleft=(stats_rect.x + 35, stats_rect.y + 31))
        screen.blit(hits_shadow, hits_shadow_rect)
        
        hits_surf = self.game_engine.fonts['small'].render(hits_text, True, (200, 200, 200))
        hits_rect = hits_surf.get_rect(midleft=(stats_rect.x + 33, stats_rect.y + 30))
        screen.blit(hits_surf, hits_rect)
        
        # Draw combo counter with lightning icon
        combo_x = stats_rect.x + stats_rect.width - 70
        combo_y = stats_rect.y + 30
        
        # Draw lightning bolt icon
        lightning_points = [
            (combo_x - 15, combo_y - 7),  # Top
            (combo_x - 10, combo_y - 2),  # Middle right
            (combo_x - 12, combo_y),      # Middle
            (combo_x - 5, combo_y + 7),   # Bottom
            (combo_x - 10, combo_y - 2),  # Back to middle right
            (combo_x - 15, combo_y)       # Middle left
        ]
        pygame.draw.polygon(screen, (255, 220, 50), lightning_points)
        pygame.draw.polygon(screen, (0, 0, 0), lightning_points, 1)
        
        combo_text = f"Max: {max_combo}x"
        combo_shadow = self.game_engine.fonts['small'].render(combo_text, True, (0, 0, 0))
        combo_shadow_rect = combo_shadow.get_rect(midleft=(combo_x, combo_y + 1))
        screen.blit(combo_shadow, combo_shadow_rect)
        
        combo_surf = self.game_engine.fonts['small'].render(combo_text, True, (255, 220, 50))
        combo_rect = combo_surf.get_rect(midleft=(combo_x, combo_y))
        screen.blit(combo_surf, combo_rect)
    
    def _draw_controls_help(self, screen):
        """Draw controls help text."""
        # Create controls panel background
        controls_width = 380
        controls_height = 26
        controls_rect = pygame.Rect(
            (self.game_engine.width - controls_width) // 2,
            self.game_engine.height - controls_height - 10,
            controls_width,
            controls_height
        )
        
        # Draw rounded panel with shadow
        shadow_offset = 2
        shadow_rect = pygame.Rect(
            controls_rect.x + shadow_offset,
            controls_rect.y + shadow_offset,
            controls_rect.width,
            controls_rect.height
        )
        pygame.draw.rect(screen, (10, 10, 10, 150), shadow_rect, border_radius=13)
        pygame.draw.rect(screen, (0, 0, 0, 180), controls_rect, border_radius=13)
        pygame.draw.rect(screen, (80, 80, 100), controls_rect, 1, border_radius=13)
        
        # Draw key indicators
        key_bg_color = (60, 60, 80)
        key_text_color = (220, 220, 220)
        
        # Player 1 controls indicator
        p1_text = "P1: "
        p1_surf = self.game_engine.fonts['small'].render(p1_text, True, (150, 150, 255))
        p1_rect = p1_surf.get_rect(midleft=(controls_rect.x + 15, controls_rect.centery))
        screen.blit(p1_surf, p1_rect)
        
        # W key
        w_rect = pygame.Rect(controls_rect.x + 40, controls_rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, w_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 130), w_rect, 1, border_radius=3)
        w_surf = self.game_engine.fonts['small'].render("W", True, key_text_color)
        w_rect = w_surf.get_rect(center=(controls_rect.x + 48, controls_rect.centery))
        screen.blit(w_surf, w_rect)
        
        # A key
        a_rect = pygame.Rect(controls_rect.x + 60, controls_rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, a_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 130), a_rect, 1, border_radius=3)
        a_surf = self.game_engine.fonts['small'].render("A", True, key_text_color)
        a_rect = a_surf.get_rect(center=(controls_rect.x + 68, controls_rect.centery))
        screen.blit(a_surf, a_rect)
        
        # S key
        s_rect = pygame.Rect(controls_rect.x + 80, controls_rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, s_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 130), s_rect, 1, border_radius=3)
        s_surf = self.game_engine.fonts['small'].render("S", True, key_text_color)
        s_rect = s_surf.get_rect(center=(controls_rect.x + 88, controls_rect.centery))
        screen.blit(s_surf, s_rect)
        
        # D key
        d_rect = pygame.Rect(controls_rect.x + 100, controls_rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, d_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 130), d_rect, 1, border_radius=3)
        d_surf = self.game_engine.fonts['small'].render("D", True, key_text_color)
        d_rect = d_surf.get_rect(center=(controls_rect.x + 108, controls_rect.centery))
        screen.blit(d_surf, d_rect)
        
        # + symbol
        plus_surf = self.game_engine.fonts['small'].render("+", True, (150, 150, 150))
        plus_rect = plus_surf.get_rect(center=(controls_rect.x + 125, controls_rect.centery))
        screen.blit(plus_surf, plus_rect)
        
        # G key (attack)
        g_rect = pygame.Rect(controls_rect.x + 140, controls_rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, g_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 130), g_rect, 1, border_radius=3)
        g_surf = self.game_engine.fonts['small'].render("G", True, (255, 150, 100))
        g_rect = g_surf.get_rect(center=(controls_rect.x + 148, controls_rect.centery))
        screen.blit(g_surf, g_rect)
        
        # H key (kick)
        h_rect = pygame.Rect(controls_rect.x + 160, controls_rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, h_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 130), h_rect, 1, border_radius=3)
        h_surf = self.game_engine.fonts['small'].render("H", True, (255, 150, 100))
        h_rect = h_surf.get_rect(center=(controls_rect.x + 168, controls_rect.centery))
        screen.blit(h_surf, h_rect)
        
        # J key (special)
        j_rect = pygame.Rect(controls_rect.x + 180, controls_rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, j_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 130), j_rect, 1, border_radius=3)
        j_surf = self.game_engine.fonts['small'].render("J", True, (255, 150, 100))
        j_rect = j_surf.get_rect(center=(controls_rect.x + 188, controls_rect.centery))
        screen.blit(j_surf, j_rect)
        
        # Separator
        sep_surf = self.game_engine.fonts['small'].render("|", True, (150, 150, 150))
        sep_rect = sep_surf.get_rect(center=(controls_rect.x + 210, controls_rect.centery))
        screen.blit(sep_surf, sep_rect)
        
        # Toggle AI
        t_rect = pygame.Rect(controls_rect.x + 225, controls_rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, t_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 130), t_rect, 1, border_radius=3)
        t_surf = self.game_engine.fonts['small'].render("T", True, key_text_color)
        t_rect = t_surf.get_rect(center=(controls_rect.x + 233, controls_rect.centery))
        screen.blit(t_surf, t_rect)
        
        ai_text = ": AI"
        ai_surf = self.game_engine.fonts['small'].render(ai_text, True, (150, 150, 150))
        ai_rect = ai_surf.get_rect(midleft=(controls_rect.x + 245, controls_rect.centery))
        screen.blit(ai_surf, ai_rect)
        
        # AI Level
        y_rect = pygame.Rect(controls_rect.x + 280, controls_rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, y_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 130), y_rect, 1, border_radius=3)
        y_surf = self.game_engine.fonts['small'].render("Y", True, key_text_color)
        y_rect = y_surf.get_rect(center=(controls_rect.x + 288, controls_rect.centery))
        screen.blit(y_surf, y_rect)
        
        level_text = ": Level"
        level_surf = self.game_engine.fonts['small'].render(level_text, True, (150, 150, 150))
        level_rect = level_surf.get_rect(midleft=(controls_rect.x + 300, controls_rect.centery))
        screen.blit(level_surf, level_rect)
    
    def _draw_moves_info(self, screen, player):
        """Draw character-specific move information."""
        # Create moves panel background
        moves_width = 200
        moves_height = 70
        moves_rect = pygame.Rect(
            self.game_engine.width - moves_width - 10,
            self.game_engine.height - moves_height - 10,
            moves_width,
            moves_height
        )
        
        # Draw rounded panel with shadow
        shadow_offset = 2
        shadow_rect = pygame.Rect(
            moves_rect.x + shadow_offset,
            moves_rect.y + shadow_offset,
            moves_rect.width,
            moves_rect.height
        )
        pygame.draw.rect(screen, (10, 10, 10, 150), shadow_rect, border_radius=10)
        
        # Background with gradient
        for y in range(moves_height):
            progress = y / moves_height
            color = (
                int(40 + progress * 20),
                int(20 + progress * 20),
                int(60 + progress * 30),
                200
            )
            pygame.draw.line(screen, color, 
                          (moves_rect.x, moves_rect.y + y), 
                          (moves_rect.x + moves_rect.width, moves_rect.y + y))
        
        pygame.draw.rect(screen, (120, 80, 160), moves_rect, 2, border_radius=10)
        
        # Character name and title
        char_type = player.__class__.__name__
        title_text = f"{char_type} MOVES"
        
        # Shadow
        title_shadow = self.game_engine.fonts['small'].render(title_text, True, (0, 0, 0))
        title_shadow_rect = title_shadow.get_rect(midtop=(moves_rect.centerx + 1, moves_rect.y + 6))
        screen.blit(title_shadow, title_shadow_rect)
        
        # Actual text
        title_surf = self.game_engine.fonts['small'].render(title_text, True, (220, 180, 255))
        title_rect = title_surf.get_rect(midtop=(moves_rect.centerx, moves_rect.y + 5))
        screen.blit(title_surf, title_rect)
        
        # Draw move keys with icons
        key_bg_color = (60, 30, 80)
        
        # G key (Punch)
        move_y = moves_rect.y + 30
        g_rect = pygame.Rect(moves_rect.x + 15, move_y - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, g_rect, border_radius=3)
        pygame.draw.rect(screen, (120, 80, 160), g_rect, 1, border_radius=3)
        g_surf = self.game_engine.fonts['small'].render("G", True, (255, 200, 100))
        g_rect = g_surf.get_rect(center=(moves_rect.x + 23, move_y))
        screen.blit(g_surf, g_rect)
        
        # Punch icon
        punch_icon = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(punch_icon, (255, 150, 50), (7, 7), 6)
        pygame.draw.circle(punch_icon, (0, 0, 0), (7, 7), 6, 1)
        pygame.draw.line(punch_icon, (0, 0, 0), (7, 7), (12, 3), 2)
        screen.blit(punch_icon, (moves_rect.x + 40, move_y - 7))
        
        # Punch text
        punch_text = "Punch"
        punch_surf = self.game_engine.fonts['small'].render(punch_text, True, (200, 200, 200))
        punch_rect = punch_surf.get_rect(midleft=(moves_rect.x + 60, move_y))
        screen.blit(punch_surf, punch_rect)
        
        # H key (Kick)
        move_y = moves_rect.y + 50
        h_rect = pygame.Rect(moves_rect.x + 15, move_y - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, h_rect, border_radius=3)
        pygame.draw.rect(screen, (120, 80, 160), h_rect, 1, border_radius=3)
        h_surf = self.game_engine.fonts['small'].render("H", True, (255, 200, 100))
        h_rect = h_surf.get_rect(center=(moves_rect.x + 23, move_y))
        screen.blit(h_surf, h_rect)
        
        # Kick icon
        kick_icon = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.rect(kick_icon, (255, 150, 50), (2, 4, 10, 6), border_radius=2)
        pygame.draw.line(kick_icon, (0, 0, 0), (2, 7), (12, 7), 1)
        pygame.draw.line(kick_icon, (0, 0, 0), (12, 7), (12, 10), 1)
        screen.blit(kick_icon, (moves_rect.x + 40, move_y - 7))
        
        # Kick text
        kick_text = "Kick"
        kick_surf = self.game_engine.fonts['small'].render(kick_text, True, (200, 200, 200))
        kick_rect = kick_surf.get_rect(midleft=(moves_rect.x + 60, move_y))
        screen.blit(kick_surf, kick_rect)
        
        # J key (Special)
        move_y = moves_rect.y + 50
        j_rect = pygame.Rect(moves_rect.x + 110, move_y - 8, 16, 16)
        pygame.draw.rect(screen, key_bg_color, j_rect, border_radius=3)
        pygame.draw.rect(screen, (120, 80, 160), j_rect, 1, border_radius=3)
        j_surf = self.game_engine.fonts['small'].render("J", True, (100, 200, 255))
        j_rect = j_surf.get_rect(center=(moves_rect.x + 118, move_y))
        screen.blit(j_surf, j_rect)
        
        # Special icon (star)
        special_icon = pygame.Surface((14, 14), pygame.SRCALPHA)
        self._draw_star(special_icon, 7, 7, (100, 200, 255), 6)
        screen.blit(special_icon, (moves_rect.x + 135, move_y - 7))
        
        # Special text
        special_text = "Special"
        special_surf = self.game_engine.fonts['small'].render(special_text, True, (200, 200, 200))
        special_rect = special_surf.get_rect(midleft=(moves_rect.x + 155, move_y))
        screen.blit(special_surf, special_rect)