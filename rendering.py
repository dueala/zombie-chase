import pygame
import random
import math
from config import *
from sprites import ZOMBIE_SPRITE, LAMP_SPRITE

def draw_lamp_light(surf, pos, tick):
    """Draw lamp light effect"""
    lx = pos[1]*CELL_SIZE + CELL_SIZE//2
    ly = pos[0]*CELL_SIZE + CELL_SIZE//2
    flicker = random.randint(-3, 3)
    r = LAMP_RADIUS + flicker
    light = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
    for i in range(r, 0, -4):
        t = i/r
        red   = int(255*(1-t**2))
        green = int(160*(1-t**2))
        alpha = int(45*(1-t**1.5))
        pygame.draw.circle(light, (red, green, 20, alpha), (r, r), i)
    surf.blit(light, (lx-r, ly-r))
    surf.blit(LAMP_SPRITE, (pos[1]*CELL_SIZE, pos[0]*CELL_SIZE))


def draw_world_object(surf, obj, tick):
    """Draw world objects (trees, houses, bushes, stones, water)"""
    x, y = obj.x, obj.y
    cs   = CELL_SIZE
    mid  = cs//2

    if obj.type == 'tree':
        pygame.draw.circle(surf, C_TREE,  (x+mid, y+mid),   13)
        pygame.draw.circle(surf, C_TREE2, (x+mid, y+mid-2),  9)
        pygame.draw.rect(surf, (40, 20, 5), (x+mid-2, y+mid+4, 4, 7))
    elif obj.type == 'house':
        pygame.draw.rect(surf, C_HOUSE, (x+3, y+8, cs-6, cs-10))
        pygame.draw.polygon(surf, (80, 35, 10), [(x+mid, y+2), (x+3, y+10), (x+cs-3, y+10)])
        pygame.draw.rect(surf, (5, 5, 8), (x+mid-3, y+14, 6, 5))
    elif obj.type == 'bush':
        pygame.draw.circle(surf, (25, 100, 25), (x+mid, y+mid), 7)
        pygame.draw.circle(surf, (15, 70, 15), (x+mid-3, y+mid+2), 5)
    elif obj.type == 'stone':
        pygame.draw.polygon(surf, C_STONE, [(x+mid, y+4), (x+cs-4, y+cs-4), (x+4, y+cs-4)])
        pulse = int(80 + 60*math.sin(tick*0.05 + obj.seed))
        glow  = pygame.Surface((cs, cs), pygame.SRCALPHA)
        pygame.draw.polygon(glow, (*C_RUNE, pulse), [(mid, 4), (cs-4, cs-4), (4, cs-4)])
        surf.blit(glow, (x, y))
    elif obj.type == 'water':
        s      = pygame.Surface((cs, cs), pygame.SRCALPHA)
        ripple = int(80 + 30*math.sin(tick*0.04 + obj.seed*0.1))
        s.fill((*C_WATER, ripple))
        surf.blit(s, (x, y))


def draw_fog(surf, px, py, state):
    """Draw fog of war effect"""
    fog_r = max(FOG_RADIUS_MIN, FOG_RADIUS_MAX - state.tasks_completed*FOG_REDUCTION_PER_TASK)
    # Hard mode: denser fog
    try:
        from difficulty import DIFF_HARD
        if state.difficulty_mode == DIFF_HARD:
            fog_r = max(FOG_RADIUS_MIN, fog_r - 20)
    except ImportError:
        pass

    pulse    = int(10*math.sin(state.tick*0.08)) if state.heartbeat > 100 else 0
    fog_r   += pulse
    fog_alpha = min(240, 200 + state.tasks_completed*8)

    mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    mask.fill((C_FOG[0], C_FOG[1], C_FOG[2], fog_alpha))

    for i in range(fog_r, 0, -4):
        a = max(0, int((1-i/fog_r)**1.5*fog_alpha))
        pygame.draw.circle(mask, (C_FOG[0], C_FOG[1], C_FOG[2], a), (px, py), i)

    for lp in state.lamp_positions:
        lx = lp[1]*CELL_SIZE + CELL_SIZE//2
        ly = lp[0]*CELL_SIZE + CELL_SIZE//2
        lamp_r = 45
        for i in range(lamp_r, 0, -3):
            a = max(0, int((1-i/lamp_r)**1.5*fog_alpha))
            pygame.draw.circle(mask, (C_FOG[0]+5, C_FOG[1]+3, C_FOG[2], a), (lx, ly), i)

    surf.blit(mask, (0, 0))


def draw_torch_light(surf, px, py, tick):
    """Draw torch light around player"""
    flicker = random.randint(-6, 6)
    r       = TORCH_RADIUS + flicker
    light   = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
    for i in range(r, 0, -3):
        t     = i/r
        alpha = int(60*(1-t**1.5))
        pygame.draw.circle(light, (255, 140, 20, alpha), (r, r), i)
    surf.blit(light, (px-r, py-r))


def draw_task(surf, pos, tick, idx):
    """Draw task/completion marker"""
    tx = pos[1]*CELL_SIZE + CELL_SIZE//2
    ty = pos[0]*CELL_SIZE + CELL_SIZE//2
    pulse = int(4*math.sin(tick*0.08 + idx*1.2))
    gs    = pygame.Surface((50, 50), pygame.SRCALPHA)
    a     = int(130 + 80*math.sin(tick*0.08 + idx*1.2))
    pygame.draw.circle(gs, (0, 255, 180, a), (25, 25), 20 + pulse)
    surf.blit(gs, (tx-25, ty-25))

    from sprites import TASK_SPRITE
    surf.blit(TASK_SPRITE, (tx-12, ty-12))

    font_ui, font_msg, font_small = get_fonts()
    lbl = font_small.render(str(idx+1), True, (0, 255, 200))
    surf.blit(lbl, (tx-lbl.get_width()//2, ty+14))


def draw_zombie_sprite(surf, pos, fog_r, px, py, tick, state, key):
    """Draw zombie with visibility and effects"""
    zx   = pos[1]*CELL_SIZE + CELL_SIZE//2
    zy   = pos[0]*CELL_SIZE + CELL_SIZE//2
    dist = math.hypot(px-zx, py-zy)

    if dist > fog_r + 35:
        return

    flick = state.eye_flicker.get(key, 255)
    flick = max(80, min(255, flick + random.randint(-30, 30)))
    state.eye_flicker[key] = flick

    scale = 1.6
    sw    = int(ZOMBIE_SPRITE.get_width()*scale)
    sh    = int(ZOMBIE_SPRITE.get_height()*scale)
    scaled = pygame.transform.scale(ZOMBIE_SPRITE, (sw, sh))

    if dist >= fog_r:
        eye_a = max(0, int(flick*(1-(dist-fog_r)/35)))
        if eye_a > 10:
            esurf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(esurf, (220, 50, 50, eye_a), (4, 4), 4)
            surf.blit(esurf, (zx-6, zy-4))
            esurf2 = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(esurf2, (220, 50, 50, eye_a), (4, 4), 4)
            surf.blit(esurf2, (zx+2, zy-4))
        return

    glow_r = 22 + int(6*math.sin(tick*0.1))
    glow   = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (150, 200, 100, 35), (glow_r, glow_r), glow_r)
    surf.blit(glow, (zx-glow_r, zy-glow_r))

    bob = int(2*math.sin(tick*0.15 + (1 if key == "stalker" else 2)))
    surf.blit(scaled, (zx-sw//2, zy-sh//2 + bob))


def draw_portal(surf, pos, tick):
    """Draw portal effect"""
    px2   = pos[1]*CELL_SIZE + CELL_SIZE//2
    py2   = pos[0]*CELL_SIZE + CELL_SIZE//2
    pulse = int(8*math.sin(tick*0.1))
    r     = CELL_SIZE//2 + pulse

    for i in range(4, 0, -1):
        gs = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
        pygame.draw.circle(gs, (180, 0, 255, 30*i), (r*2, r*2), r + i*5)
        surf.blit(gs, (px2-r*2, py2-r*2))

    pygame.draw.circle(surf, (180, 0, 255), (px2, py2), r, 2)

    font_ui, font_msg, font_small = get_fonts()
    lbl = font_small.render("PORTAL", True, (200, 100, 255))
    surf.blit(lbl, (px2-lbl.get_width()//2, py2+r+4))


# ── Timer helpers ─────────────────────────────────────────────────────────────
def _fmt_time(secs):
    if secs is None:
        return "--:--"
    secs = max(0, int(secs))
    return f"{secs//60}:{secs%60:02d}"

def _diff_color(mode):
    """Return a color for each difficulty mode label."""
    return {
        "EASY":   (60, 220, 100),
        "MEDIUM": (220, 190, 40),
        "HARD":   (220, 50, 50),
    }.get(mode, (160, 160, 160))


def draw_hud(surf, state):
    """Draw heads-up display with health, stamina, timer, and game info"""
    bar_w, bar_h = 160, 12
    bx, by = 18, HEIGHT - 70

    font_ui, font_msg, font_small = get_fonts()

    # ── Health bar ────────────────────────────────────────────────────────────
    surf.blit(font_small.render("HEALTH", True, (200, 60, 60)), (bx, by-16))
    pygame.draw.rect(surf, (40, 10, 10),   (bx, by, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surf, (180, 30, 30),  (bx, by, int(bar_w*state.health/100), bar_h), border_radius=4)
    pygame.draw.rect(surf, (120, 30, 30),  (bx, by, bar_w, bar_h), 1, border_radius=4)

    # ── Stamina bar ───────────────────────────────────────────────────────────
    sy = by - 38
    surf.blit(font_small.render("STAMINA", True, (60, 180, 60)), (bx, sy-16))
    pygame.draw.rect(surf, (10, 30, 10),  (bx, sy, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surf, (40, 160, 40), (bx, sy, int(bar_w*state.stamina/100), bar_h), border_radius=4)
    pygame.draw.rect(surf, (30, 100, 30), (bx, sy, bar_w, bar_h), 1, border_radius=4)

    # ── Ritual progress ───────────────────────────────────────────────────────
    rtxt = font_ui.render(f"RITUAL  {state.tasks_completed} / 5", True, C_GOLD)
    surf.blit(rtxt, (WIDTH - rtxt.get_width() - 18, 18))

    # ── Score ─────────────────────────────────────────────────────────────────
    surf.blit(font_small.render(f"SURVIVED: {state.total_wins}   CONSUMED: {state.total_losses}",
                                True, (160, 160, 120)), (18, 18))

    # ── Difficulty mode label (top-right below ritual) ────────────────────────
    mode     = getattr(state, 'difficulty_mode', 'EASY')
    mode_col = _diff_color(mode)
    mode_lbl = font_small.render(f"MODE: {mode}", True, mode_col)
    surf.blit(mode_lbl, (WIDTH - mode_lbl.get_width() - 18, 42))

    # ── Timer display ─────────────────────────────────────────────────────────
    rt = getattr(state, 'remaining_time', None)
    if rt is not None:
        time_str = _fmt_time(rt)
        low_time = rt <= 10

        if low_time:
            # Red flashing when ≤ 10 s
            flash_a = int(180 + 75 * math.sin(state.tick * 0.3))
            timer_col = (255, max(0, flash_a - 180), max(0, flash_a - 180))
            # Red vignette flash
            vign = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pulse_v = int(abs(math.sin(state.tick * 0.3)) * 80)
            for i in range(0, 40, 4):
                a = max(0, pulse_v - i * 2)
                pygame.draw.rect(vign, (200, 0, 0, a), (i, i, WIDTH-2*i, HEIGHT-2*i), 3)
            surf.blit(vign, (0, 0))
        else:
            timer_col = (200, 200, 100)

        time_lbl = font_ui.render(f"TIME  {time_str}", True, timer_col)
        surf.blit(time_lbl, (WIDTH - time_lbl.get_width() - 18, 62))

    # ── Heartbeat effect ──────────────────────────────────────────────────────
    if state.heartbeat > 60:
        vign  = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pulse = int(state.heartbeat*0.35*abs(math.sin(state.tick*0.12)))
        for i in range(0, 60, 4):
            a = max(0, pulse - i*3)
            pygame.draw.rect(vign, (180, 0, 0, a), (i, i, WIDTH-2*i, HEIGHT-2*i), 4)
        surf.blit(vign, (0, 0))

    # ── Warning message ───────────────────────────────────────────────────────
    if state.tasks_completed >= 2:
        warn_a = int(160 + 80*math.sin(state.tick*0.07))
        warn   = font_small.render("◆  THE FOG THICKENS  ◆", True, (warn_a, warn_a//2, warn_a))
        surf.blit(warn, (WIDTH//2-warn.get_width()//2, 46))

    # ── Dimension indicator ───────────────────────────────────────────────────
    dim_txt = "[ SHADOW REALM ]" if state.dimension == 1 else "[ THE JUNGLE ]"
    dim_col = (180, 0, 255)      if state.dimension == 1 else (60, 160, 60)
    dt      = font_small.render(dim_txt, True, dim_col)
    surf.blit(dt, (WIDTH//2-dt.get_width()//2, 18))

    # ── Shadow realm countdown ────────────────────────────────────────────────
    if state.dimension == 1:
        secs_left = max(0, (PORTAL_DURATION-state.portal_timer)/1000)
        pulse_a   = int(180 + 75*math.sin(state.tick*0.15))
        cntdown   = font_ui.render(f"EJECTING IN  {secs_left:.1f}s", True, (pulse_a, 0, pulse_a))
        surf.blit(cntdown, (WIDTH//2-cntdown.get_width()//2, 44))


def draw_end_screen(surf, state):
    """Draw game over/victory screen"""
    # Check for time-expiry lose
    time_expired = getattr(state, 'time_expired', False)

    if state.won:
        txt   = "SURVIVED"
        sub   = "You escaped the jungle"
        color = (0, 230, 120)
    elif time_expired:
        txt   = "TIME RAN OUT"
        sub   = "The fog consumed you"
        color = (220, 140, 20)
    else:
        txt   = "CONSUMED BY ZOMBIE"
        sub   = "The undead took you"
        color = (200, 20, 20)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surf.blit(overlay, (0, 0))

    pulse = int(10*math.sin(state.tick*0.1))
    font_ui, font_msg, font_small = get_fonts()

    msg = font_msg.render(txt, True, color)
    surf.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 70 + pulse))

    sub_surf = font_ui.render(sub, True, (180, 180, 180))
    surf.blit(sub_surf, (WIDTH//2 - sub_surf.get_width()//2, HEIGHT//2 + 20))

    r_surf = font_small.render("[ R = restart  |  RESTART button  |  ⌂ = main menu ]", True, (120, 120, 120))
    surf.blit(r_surf, (WIDTH//2 - r_surf.get_width()//2, HEIGHT//2 + 55))
