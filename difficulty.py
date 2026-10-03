import pygame
import math
from config import WIDTH, HEIGHT

# ─── Difficulty Mode Constants ────────────────────────────────────────────────
DIFF_EASY   = "EASY"
DIFF_MEDIUM = "MEDIUM"
DIFF_HARD   = "HARD"

MEDIUM_TIMERS = [120, 130, 140, 150, 160, 170, 180]   # seconds
HARD_TIMERS   = [40, 50, 60]                            # seconds

def fmt_time(seconds):
    """Format seconds as M:SS"""
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


class DifficultyScreen:
    """Full-screen difficulty + timer selection shown after START, before gameplay."""

    DIFF_COLORS = {
        DIFF_EASY:   {"base": (30, 160, 60),  "glow": (80, 255, 120),  "dark": (10, 60, 25)},
        DIFF_MEDIUM: {"base": (180, 130, 20),  "glow": (255, 210, 60),  "dark": (70, 50, 5)},
        DIFF_HARD:   {"base": (180, 30, 30),   "glow": (255, 80, 80),   "dark": (70, 10, 10)},
    }

    def __init__(self):
        info = pygame.display.Info()
        self.screen_width  = info.current_w
        self.screen_height = info.current_h

        # Fonts
        self.font_title  = pygame.font.SysFont("Impact", 52)
        self.font_diff   = pygame.font.SysFont("Impact", 34)
        self.font_label  = pygame.font.SysFont("Courier", 18, bold=True)
        self.font_small  = pygame.font.SysFont("Courier", 14)
        self.font_btn    = pygame.font.SysFont("Courier", 22, bold=True)
        self.font_timer  = pygame.font.SysFont("Courier", 17, bold=True)

        self.selected_diff  = None   # DIFF_EASY / DIFF_MEDIUM / DIFF_HARD
        self.selected_timer = None   # seconds (int) or None for EASY

        # Layout constants
        self._layout()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _layout(self):
        W, H = WIDTH, HEIGHT
        card_y   = 160
        card_h   = 180
        card_w   = 240
        gap      = 20
        total_w  = card_w * 3 + gap * 2
        start_x  = (W - total_w) // 2

        self.diff_cards = {
            DIFF_EASY:   pygame.Rect(start_x,                 card_y, card_w, card_h),
            DIFF_MEDIUM: pygame.Rect(start_x + card_w + gap,  card_y, card_w, card_h),
            DIFF_HARD:   pygame.Rect(start_x + (card_w+gap)*2, card_y, card_w, card_h),
        }

        # Timer option area (below cards)
        self.timer_area_y = card_y + card_h + 30
        self.timer_btn_h  = 38
        self.timer_btn_w  = 90

        # Start button
        btn_w, btn_h = 220, 58
        self.start_btn = pygame.Rect(W//2 - btn_w//2, H - 110, btn_w, btn_h)

    # ── Coordinate helpers ────────────────────────────────────────────────────
    def _game_pos(self, raw_pos):
        sx = WIDTH  / self.screen_width
        sy = HEIGHT / self.screen_height
        return (int(raw_pos[0] * sx), int(raw_pos[1] * sy))

    # ── Timer options for currently selected difficulty ───────────────────────
    def _timer_options(self):
        if self.selected_diff == DIFF_MEDIUM:
            return MEDIUM_TIMERS
        if self.selected_diff == DIFF_HARD:
            return HARD_TIMERS
        return []

    def _timer_rects(self):
        opts = self._timer_options()
        if not opts:
            return {}
        W = WIDTH
        total_w = len(opts) * self.timer_btn_w + (len(opts)-1) * 12
        sx = (W - total_w) // 2
        rects = {}
        for i, t in enumerate(opts):
            rects[t] = pygame.Rect(sx + i*(self.timer_btn_w+12),
                                   self.timer_area_y + 36,
                                   self.timer_btn_w, self.timer_btn_h)
        return rects

    # ── Public: can the player start? ────────────────────────────────────────
    def ready_to_start(self):
        if self.selected_diff is None:
            return False
        if self.selected_diff == DIFF_EASY:
            return True
        return self.selected_timer is not None

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surf, tick):
        # Background – dark jungle atmosphere
        surf.fill((8, 14, 8))
        self._draw_bg_vines(surf, tick)

        # Title
        title = self.font_title.render("◆  SELECT DIFFICULTY  ◆", True, (180, 220, 160))
        surf.blit(title, (WIDTH//2 - title.get_width()//2, 75))

        sub = self.font_small.render("Choose your fate before entering the fog", True, (80, 110, 70))
        surf.blit(sub, (WIDTH//2 - sub.get_width()//2, 135))

        mouse_gp = self._game_pos(pygame.mouse.get_pos())

        # Difficulty cards
        for diff, rect in self.diff_cards.items():
            self._draw_diff_card(surf, diff, rect, mouse_gp, tick)

        # Timer options
        self._draw_timer_section(surf, mouse_gp, tick)

        # Start button
        self._draw_start_btn(surf, mouse_gp, tick)

        # Bottom hint
        hint = self.font_small.render("← back to main menu: press ESC", True, (50, 70, 50))
        surf.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 36))

    def _draw_bg_vines(self, surf, tick):
        """Subtle animated vine-like lines in background"""
        for i in range(8):
            phase = tick * 0.02 + i * 0.8
            x = int(WIDTH * i / 8)
            pts = []
            for y in range(0, HEIGHT, 12):
                ox = int(18 * math.sin(phase + y * 0.03))
                pts.append((x + ox, y))
            if len(pts) > 1:
                pygame.draw.lines(surf, (15, 35, 12), False, pts, 1)

    def _draw_diff_card(self, surf, diff, rect, mouse_gp, tick):
        colors  = self.DIFF_COLORS[diff]
        hovered = rect.collidepoint(mouse_gp)
        selected = (self.selected_diff == diff)

        # Glow behind selected card
        if selected:
            pulse = int(15 * math.sin(tick * 0.1))
            gr = rect.inflate(pulse*2 + 10, pulse + 6)
            glow_surf = pygame.Surface((gr.width, gr.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*colors["glow"], 40), glow_surf.get_rect(), border_radius=16)
            surf.blit(glow_surf, gr.topleft)

        # Card body
        border_col = colors["glow"] if (selected or hovered) else (30, 50, 30)
        bg_col     = colors["dark"] if selected else (12, 20, 12)
        pygame.draw.rect(surf, bg_col,    rect, border_radius=14)
        pygame.draw.rect(surf, border_col, rect, 2 + (1 if selected else 0), border_radius=14)

        cx = rect.centerx
        # Diff label
        lbl = self.font_diff.render(diff, True, colors["glow"] if selected else colors["base"])
        surf.blit(lbl, (cx - lbl.get_width()//2, rect.y + 18))

        # Icon
        icons = {DIFF_EASY: "🟢", DIFF_MEDIUM: "🟡", DIFF_HARD: "🔴"}
        # Use text surrogate since pygame SysFont doesn't render emoji well
        icon_chars = {DIFF_EASY: "◉", DIFF_MEDIUM: "◈", DIFF_HARD: "◆"}
        icon_cols  = {DIFF_EASY: (60,220,100), DIFF_MEDIUM: (220,190,40), DIFF_HARD: (220,50,50)}
        ic = self.font_diff.render(icon_chars[diff], True, icon_cols[diff])
        surf.blit(ic, (cx - ic.get_width()//2, rect.y + 56))

        # Description lines
        desc = {
            DIFF_EASY:   ["No time limit", "Explore freely", "Survive & complete tasks"],
            DIFF_MEDIUM: ["Choose your timer", "2:00 – 3:00 minutes", "Balanced challenge"],
            DIFF_HARD:   ["Speed run!", "40 – 60 seconds", "Fast zombies, dense fog"],
        }
        for i, line in enumerate(desc[diff]):
            col = (160, 200, 140) if selected else (80, 110, 70)
            t = self.font_small.render(line, True, col)
            surf.blit(t, (cx - t.get_width()//2, rect.y + 100 + i*20))

        # Selected checkmark
        if selected:
            chk = self.font_label.render("✓ SELECTED", True, colors["glow"])
            surf.blit(chk, (cx - chk.get_width()//2, rect.bottom - 26))

    def _draw_timer_section(self, surf, mouse_gp, tick):
        opts = self._timer_options()
        if not opts:
            # Easy mode — show info blurb
            if self.selected_diff == DIFF_EASY:
                msg = self.font_label.render("No timer — take all the time you need.", True, (60, 180, 90))
                surf.blit(msg, (WIDTH//2 - msg.get_width()//2, self.timer_area_y + 14))
            return

        # Section header
        hdr = self.font_label.render("SELECT TIME LIMIT:", True, (160, 160, 100))
        surf.blit(hdr, (WIDTH//2 - hdr.get_width()//2, self.timer_area_y + 6))

        colors = self.DIFF_COLORS[self.selected_diff]
        timer_rects = self._timer_rects()

        for t, rect in timer_rects.items():
            hovered  = rect.collidepoint(mouse_gp)
            selected = (self.selected_timer == t)

            if selected:
                pulse = int(8 * math.sin(tick * 0.12))
                gr = rect.inflate(pulse + 6, pulse + 4)
                gs = pygame.Surface((gr.width, gr.height), pygame.SRCALPHA)
                pygame.draw.rect(gs, (*colors["glow"], 50), gs.get_rect(), border_radius=10)
                surf.blit(gs, gr.topleft)

            bg  = colors["dark"] if selected else (12, 18, 10)
            brd = colors["glow"] if (selected or hovered) else (40, 60, 30)
            pygame.draw.rect(surf, bg,  rect, border_radius=8)
            pygame.draw.rect(surf, brd, rect, 2, border_radius=8)

            tc = colors["glow"] if selected else (140, 160, 110)
            lbl = self.font_timer.render(fmt_time(t), True, tc)
            surf.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))

    def _draw_start_btn(self, surf, mouse_gp, tick):
        ready   = self.ready_to_start()
        hovered = self.start_btn.collidepoint(mouse_gp) and ready

        if ready:
            pulse = int(12 * math.sin(tick * 0.1))
            gr = self.start_btn.inflate(pulse * 2, pulse)
            gs = pygame.Surface((gr.width, gr.height), pygame.SRCALPHA)
            pygame.draw.rect(gs, (80, 220, 80, 45), gs.get_rect(), border_radius=18)
            surf.blit(gs, gr.topleft)
            bg_col  = (50, 180, 55) if hovered else (35, 140, 40)
            brd_col = (180, 255, 150)
            txt_col = (240, 255, 240)
        else:
            bg_col  = (25, 40, 25)
            brd_col = (40, 60, 40)
            txt_col = (60, 80, 60)

        pygame.draw.rect(surf, bg_col,  self.start_btn, border_radius=14)
        pygame.draw.rect(surf, brd_col, self.start_btn, 2, border_radius=14)
        lbl = self.font_btn.render("▶  ENTER THE FOG", True, txt_col)
        surf.blit(lbl, (self.start_btn.centerx - lbl.get_width()//2,
                        self.start_btn.centery - lbl.get_height()//2))

        if not ready and self.selected_diff is not None:
            hint = self.font_small.render("← select a time limit first", True, (90, 90, 60))
            surf.blit(hint, (WIDTH//2 - hint.get_width()//2, self.start_btn.bottom + 8))

    # ── Click handling ─────────────────────────────────────────────────────────
    def handle_click(self, raw_pos):
        """
        Returns:
          'start'     – player clicked START and is ready
          'diff'      – selected/changed difficulty
          'timer'     – selected a timer
          None        – nothing meaningful clicked
        """
        gp = self._game_pos(raw_pos)

        # Difficulty cards
        for diff, rect in self.diff_cards.items():
            if rect.collidepoint(gp):
                if self.selected_diff != diff:
                    self.selected_diff  = diff
                    self.selected_timer = None  # reset timer on diff change
                return 'diff'

        # Timer buttons
        for t, rect in self._timer_rects().items():
            if rect.collidepoint(gp):
                self.selected_timer = t
                return 'timer'

        # Start button
        if self.start_btn.collidepoint(gp) and self.ready_to_start():
            return 'start'

        return None
