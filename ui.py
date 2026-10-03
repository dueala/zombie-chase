import pygame
import os
import math
from config import WIDTH, HEIGHT, CELL_SIZE

class StartScreen:
    def __init__(self):
        self.button_font = pygame.font.SysFont("Courier", 36, bold=True)
        
        # Get screen dimensions
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # The START button is positioned to match the image's button area
        btn_w, btn_h = 260, 72
        self.start_button_rect = pygame.Rect(WIDTH//2 - btn_w//2, int(HEIGHT * 0.565), btn_w, btn_h)
        
        self.background_image = None
        # Try loading cover image from same folder as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for name in ("cover_image.png", "cover_image.jpg", "cover_image.jpeg",
                     "start_screen.png", "start_screen.jpg"):
            candidate = os.path.join(script_dir, name)
            if os.path.exists(candidate):
                try:
                    raw = pygame.image.load(candidate).convert()
                    self.background_image = pygame.transform.scale(raw, (WIDTH, HEIGHT))
                    print(f"Loaded cover image: {candidate}")
                    break
                except Exception as e:
                    print(f"Failed to load {candidate}: {e}")

    def draw(self, surf, tick):
        if self.background_image:
            surf.blit(self.background_image, (0, 0))
        else:
            surf.fill((18, 30, 15))

        # Draw pulsing glow behind the button area
        glow_pulse = int(20 * math.sin(tick * 0.08))
        glow_r = self.start_button_rect.inflate(glow_pulse * 2, glow_pulse)
        glow_surf = pygame.Surface((glow_r.width + 40, glow_r.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (80, 200, 80, 60),
                         glow_surf.get_rect(), border_radius=20)
        surf.blit(glow_surf, (glow_r.x - 20, glow_r.y - 20))

        # Hover detection
        mouse_pos = pygame.mouse.get_pos()
        sx = WIDTH / self.screen_width
        sy = HEIGHT / self.screen_height
        gx = int(mouse_pos[0] * sx)
        gy = int(mouse_pos[1] * sy)
        hovered = self.start_button_rect.collidepoint(gx, gy)

        # Semi-transparent overlay on the button so it stands out over the image
        btn_surf = pygame.Surface(
            (self.start_button_rect.width, self.start_button_rect.height), pygame.SRCALPHA)
        bg_col = (60, 190, 60, 210) if hovered else (40, 150, 40, 180)
        border_col = (200, 255, 150, 255) if hovered else (100, 220, 100, 200)
        pygame.draw.rect(btn_surf, bg_col, btn_surf.get_rect(), border_radius=18)
        pygame.draw.rect(btn_surf, border_col, btn_surf.get_rect(), 3, border_radius=18)

        label = self.button_font.render("▶  START", True,
                                        (240, 255, 240) if hovered else (210, 240, 210))
        label_rect = label.get_rect(center=btn_surf.get_rect().center)
        btn_surf.blit(label, label_rect)
        surf.blit(btn_surf, self.start_button_rect)

    def handle_click(self, pos):
        sx = WIDTH / self.screen_width
        sy = HEIGHT / self.screen_height
        gx = int(pos[0] * sx)
        gy = int(pos[1] * sy)
        return self.start_button_rect.collidepoint(gx, gy)

class InGameButtons:
    """Exit (✕) top-right and Restart (↺) next to it."""
    BTN_SIZE = 44
    BTN_MARGIN = 14

    def __init__(self):
        # Get screen dimensions
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        m = self.BTN_MARGIN
        s = self.BTN_SIZE
        # Both buttons in game-coordinate space (rendered on 900×900 surface)
        self.exit_rect    = pygame.Rect(WIDTH - s - m,       m, s, s)
        self.restart_rect = pygame.Rect(WIDTH - s*2 - m*2,   m, s, s)
        self.menu_rect    = pygame.Rect(WIDTH - s*3 - m*3,   m, s, s)
        self._btn_font = pygame.font.SysFont("Courier", 22, bold=True)

    def _draw_btn(self, surf, rect, label, base_col, hover_col, mouse_game_pos):
        hovered = rect.collidepoint(mouse_game_pos)
        col = hover_col if hovered else base_col
        # Drop-shadow
        shadow = rect.move(2, 2)
        pygame.draw.rect(surf, (0, 0, 0, 120), shadow, border_radius=8)
        pygame.draw.rect(surf, col, rect, border_radius=8)
        border = (255, 255, 255, 180) if hovered else (180, 180, 180, 120)
        pygame.draw.rect(surf, border, rect, 2, border_radius=8)
        lbl = self._btn_font.render(label, True, (255, 255, 255))
        surf.blit(lbl, lbl.get_rect(center=rect.center))

    def draw(self, surf):
        mouse_raw = pygame.mouse.get_pos()
        sx = WIDTH / self.screen_width
        sy = HEIGHT / self.screen_height
        mgp = (int(mouse_raw[0] * sx), int(mouse_raw[1] * sy))

        self._draw_btn(surf, self.exit_rect, "✕", (180, 40, 40), (220, 70, 70), mgp)
        self._draw_btn(surf, self.restart_rect, "↺", (40, 100, 180), (70, 140, 220), mgp)
        self._draw_btn(surf, self.menu_rect, "⌂", (80, 60, 140), (120, 90, 200), mgp)

    def check_exit(self, pos):
        sx = WIDTH / self.screen_width
        sy = HEIGHT / self.screen_height
        gx = int(pos[0] * sx)
        gy = int(pos[1] * sy)
        return self.exit_rect.collidepoint(gx, gy)

    def check_restart(self, pos):
        sx = WIDTH / self.screen_width
        sy = HEIGHT / self.screen_height
        gx = int(pos[0] * sx)
        gy = int(pos[1] * sy)
        return self.restart_rect.collidepoint(gx, gy)

    def check_mainmenu(self, pos):
        sx = WIDTH / self.screen_width
        sy = HEIGHT / self.screen_height
        gx = int(pos[0] * sx)
        gy = int(pos[1] * sy)
        return self.menu_rect.collidepoint(gx, gy)

class OnScreenControls:
    def __init__(self):
        # Get screen dimensions
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        self.button_size = 60
        self.margin = 20
        self.active_buttons = set()
        start_x = self.screen_width - self.button_size*2 - self.margin*2
        start_y = self.screen_height - self.button_size*2 - self.margin*4
        self.buttons = {
            'up': {'rect': pygame.Rect(start_x+self.button_size, start_y, self.button_size, self.button_size), 'direction': (0,-1)},
            'down': {'rect': pygame.Rect(start_x+self.button_size, start_y+self.button_size, self.button_size, self.button_size), 'direction': (0,1)},
            'left': {'rect': pygame.Rect(start_x, start_y+self.button_size, self.button_size, self.button_size), 'direction': (-1,0)},
            'right': {'rect': pygame.Rect(start_x+self.button_size*2, start_y+self.button_size, self.button_size, self.button_size), 'direction': (1,0)},
        }

    def draw_arrow_button(self, surf, key, active):
        btn = self.buttons[key]
        rect = btn['rect']
        col = (100, 200, 100) if active else (50, 150, 50)
        pygame.draw.rect(surf, col, rect, border_radius=8)
        pygame.draw.rect(surf, (30, 100, 30), rect, 2, border_radius=8)
        cx, cy = rect.centerx, rect.centery
        ac = (200, 255, 200) if active else (150, 200, 150)
        if key == 'up':
            pts = [(cx, cy-15), (cx-10, cy+5), (cx+10, cy+5)]
        elif key == 'down':
            pts = [(cx, cy+15), (cx-10, cy-5), (cx+10, cy-5)]
        elif key == 'left':
            pts = [(cx-15, cy), (cx+5, cy-10), (cx+5, cy+10)]
        elif key == 'right':
            pts = [(cx+15, cy), (cx-5, cy-10), (cx-5, cy+10)]
        pygame.draw.polygon(surf, ac, pts)

    def draw(self, surf):
        for k in self.buttons:
            self.draw_arrow_button(surf, k, k in self.active_buttons)

    def handle_mouse_down(self, pos):
        for k, b in self.buttons.items():
            if b['rect'].collidepoint(pos):
                self.active_buttons.add(k)
                return b['direction']
        return None

    def handle_mouse_up(self, pos):
        for k, b in self.buttons.items():
            if b['rect'].collidepoint(pos):
                self.active_buttons.discard(k)

    def clear_all(self):
        self.active_buttons.clear()
