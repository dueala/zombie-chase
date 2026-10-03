import pygame
import sys
import random
import math

# Import all modules
from config import *
from sprites import make_background, make_zombie_sprite, make_task_sprite, make_lamp_sprite
from particles import Particle
from world import generate_world
from pathfinding import get_path
from rendering import *
from ui import StartScreen, InGameButtons, OnScreenControls
from game_state import GameState
from difficulty import DifficultyScreen, DIFF_EASY, DIFF_MEDIUM, DIFF_HARD

# ── Game-flow states ──────────────────────────────────────────────────────────
FLOW_START      = 0   # title / start screen
FLOW_DIFFICULTY = 1   # difficulty + timer selection
FLOW_PLAYING    = 2   # in-game
FLOW_GAME_OVER  = 3   # end screen (win or lose)

# ── Initialize global assets ──────────────────────────────────────────────────
BACKGROUND_IMG = make_background()
ZOMBIE_SPRITE  = make_zombie_sprite()
TASK_SPRITE    = make_task_sprite()
LAMP_SPRITE    = make_lamp_sprite()

# Generate world
WORLD_OBJECTS, MAP_GRID, LAMP_POSITIONS = generate_world()


def handle_player_movement(state, keys, controls, move_timer, dt):
    """Handle player movement and stamina"""
    # Hard mode: slightly reduced stamina regen
    regen = STAMINA_REGEN if state.difficulty_mode != DIFF_HARD else max(0, STAMINA_REGEN - 1)

    threshold = MOVE_SPEED_SPRINT if keys[pygame.K_LSHIFT] and state.stamina > SPRINT_THRESHOLD else MOVE_SPEED_NORMAL
    if move_timer > threshold:
        new_p = list(state.player_pos)
        moved = False

        if keys[pygame.K_UP]    or keys[pygame.K_w]: new_p[0] -= 1; moved = True
        elif keys[pygame.K_DOWN]  or keys[pygame.K_s]: new_p[0] += 1; moved = True
        elif keys[pygame.K_LEFT]  or keys[pygame.K_a]: new_p[1] -= 1; moved = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: new_p[1] += 1; moved = True

        if not moved and controls.active_buttons:
            for k in controls.active_buttons:
                d = controls.buttons[k]['direction']
                new_p[0] += d[1]; new_p[1] += d[0]; moved = True; break

        if moved and 0 <= new_p[0] < ROWS and 0 <= new_p[1] < ROWS and MAP_GRID[new_p[0]][new_p[1]] == ".":
            state.player_pos = new_p

        move_timer = 0

        sprinting = keys[pygame.K_LSHIFT] and state.stamina > SPRINT_THRESHOLD
        state.stamina = max(0, state.stamina - SPRINT_STAMINA_COST) if sprinting else min(100, state.stamina + regen)

    return move_timer


def handle_zombie_movement(state, zombie_timer, dt):
    """Handle zombie AI movement — Hard mode uses faster speed"""
    if state.difficulty_mode == DIFF_HARD:
        z_speed = max(180, ZOMBIE_SPEED_HARD - 40)   # faster than hard baseline
    elif state.tasks_completed < 2:
        z_speed = ZOMBIE_SPEED_EASY
    else:
        z_speed = ZOMBIE_SPEED_HARD

    if zombie_timer > z_speed and state.dimension == 0:
        for za in ['stalker_pos', 'lurker_pos']:
            curr = getattr(state, za)
            step = get_path(curr, state.player_pos, MAP_GRID)
            if step:
                setattr(state, za, step)
            else:
                dr, dc = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                nr, nc = curr[0] + dr, curr[1] + dc
                if 0 <= nr < ROWS and 0 <= nc < ROWS and MAP_GRID[nr][nc] == ".":
                    setattr(state, za, [nr, nc])
        zombie_timer = 0

    return zombie_timer


def update_game_logic(state, dt):
    """Update core game logic"""
    px = state.player_pos[1] * CELL_SIZE + CELL_SIZE // 2
    py = state.player_pos[0] * CELL_SIZE + CELL_SIZE // 2

    # Heartbeat
    if state.dimension == 0:
        min_dist = min(
            math.hypot(px - state.stalker_pos[1]*CELL_SIZE, py - state.stalker_pos[0]*CELL_SIZE),
            math.hypot(px - state.lurker_pos[1] *CELL_SIZE, py - state.lurker_pos[0] *CELL_SIZE),
        )
        # Hard mode: stronger heartbeat
        mult = 1.4 if state.difficulty_mode == DIFF_HARD else 1.0
        state.heartbeat = max(0, min(255, int(mult * (255 - min_dist * 0.6))))
    else:
        state.heartbeat = 0

    # Task completion
    if state.player_pos in state.tasks:
        state.tasks.remove(state.player_pos)
        state.tasks_completed += 1
        state.add_spark_particles(px, py)

    # Portal
    if state.player_pos == state.portal_pos and state.dimension == 0:
        state.dimension = 1
        state.portal_timer = 0

    # Shadow realm timer
    if state.dimension == 1:
        state.portal_timer += dt
        if state.portal_timer >= state.portal_duration:
            state.dimension = 0
            state.portal_timer = 0
            while True:
                nr = random.randint(1, ROWS-2); nc = random.randint(1, ROWS-2)
                if MAP_GRID[nr][nc] == ".":
                    state.player_pos = [nr, nc]; break

    # Zombie collision
    if state.dimension == 0:
        for zp in [state.stalker_pos, state.lurker_pos]:
            if state.player_pos == zp:
                state.screen_shake = 15
                state.add_blood_particles(px, py)
                state.game_over = True
                state.total_losses += 1

    # Win
    if state.tasks_completed == 5:
        state.won = True
        state.total_wins += 1

    # Mist
    state.mist_timer += dt
    if state.mist_timer > PARTICLE_MIST_TIMER:
        mx, my = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        state.add_mist_particles(mx, my)
        state.mist_timer = 0


def render_game(surf, state, ingame_btns, controls):
    """Render the game world and UI"""
    if state.dimension == 0:
        surf.blit(BACKGROUND_IMG, (0, 0))
    else:
        surf.fill(C_DIM_BG)
        for i in range(0, WIDTH, CELL_SIZE*3):
            a = int(20 + 10*math.sin(state.tick*0.05 + i))
            pygame.draw.line(surf, (a, 0, a*2), (i, 0), (i, HEIGHT))

    for obj in WORLD_OBJECTS:
        draw_world_object(surf, obj, state.tick)
    for lp in LAMP_POSITIONS:
        draw_lamp_light(surf, lp, state.tick)
    for p in state.mist_particles:
        p.draw(surf)

    draw_portal(surf, state.portal_pos, state.tick)

    px = state.player_pos[1] * CELL_SIZE + CELL_SIZE // 2
    py = state.player_pos[0] * CELL_SIZE + CELL_SIZE // 2
    draw_torch_light(surf, px, py, state.tick)

    fog_r = max(FOG_RADIUS_MIN, FOG_RADIUS_MAX - state.tasks_completed*FOG_REDUCTION_PER_TASK)
    # Hard mode: denser fog
    if state.difficulty_mode == DIFF_HARD:
        fog_r = max(FOG_RADIUS_MIN, fog_r - 20)

    if state.dimension == 0:
        draw_zombie_sprite(surf, state.stalker_pos, fog_r, px, py, state.tick, state, "stalker")
        draw_zombie_sprite(surf, state.lurker_pos,  fog_r, px, py, state.tick, state, "lurker")

    draw_fog(surf, px, py, state)

    for i, t in enumerate(state.tasks):
        draw_task(surf, t, state.tick, i)

    pygame.draw.circle(surf, C_PLAYER, (px, py), 9)
    gs = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(gs, (200, 220, 255, 60), (20, 20), 16)
    surf.blit(gs, (px-20, py-20))

    for p in state.particles:
        p.draw(surf)

    draw_hud(surf, state)
    ingame_btns.draw(surf)
    controls.draw(surf)

    if state.won or state.game_over:
        draw_end_screen(surf, state)
        if state.won:
            for _ in range(2):
                state.particles.append(Particle(
                    WIDTH//2 + random.randint(-200, 200),
                    HEIGHT//2 + random.randint(-100, 100), "spark"))


def main():
    """Main game loop"""
    screen, clock, screen_width, screen_height = init_display()

    flow         = FLOW_START
    state        = GameState(LAMP_POSITIONS, MAP_GRID)
    move_timer   = 0
    zombie_timer = 0
    controls     = OnScreenControls()
    ingame_btns  = InGameButtons()
    start_screen = StartScreen()
    diff_screen  = DifficultyScreen()

    while True:
        dt = clock.tick(FPS)
        state.tick += 1
        move_timer   += dt
        zombie_timer += dt

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if flow == FLOW_DIFFICULTY:
                        flow = FLOW_START          # back to title
                    elif flow in (FLOW_PLAYING, FLOW_GAME_OVER):
                        pygame.quit(); sys.exit()
                    else:
                        pygame.quit(); sys.exit()

                if event.key == pygame.K_r and flow in (FLOW_GAME_OVER, FLOW_PLAYING):
                    state.reset()
                    flow = FLOW_PLAYING

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # ── Start screen ──────────────────────────────────────────────
                if flow == FLOW_START:
                    if start_screen.handle_click(event.pos):
                        flow = FLOW_DIFFICULTY      # go to page 2

                # ── Difficulty screen ─────────────────────────────────────────
                elif flow == FLOW_DIFFICULTY:
                    result = diff_screen.handle_click(event.pos)
                    if result == 'start':
                        state.apply_difficulty(diff_screen.selected_diff,
                                               diff_screen.selected_timer)
                        state.reset()
                        flow = FLOW_PLAYING

                # ── In-game / game-over ───────────────────────────────────────
                elif flow in (FLOW_PLAYING, FLOW_GAME_OVER):
                    if ingame_btns.check_exit(event.pos):
                        pygame.quit(); sys.exit()
                    if ingame_btns.check_restart(event.pos):
                        state.reset()
                        flow = FLOW_PLAYING
                    if ingame_btns.check_mainmenu(event.pos):
                        state.reset()
                        diff_screen = DifficultyScreen()
                        flow = FLOW_DIFFICULTY

                    if flow == FLOW_PLAYING:
                        sx2 = WIDTH  / screen_width
                        sy2 = HEIGHT / screen_height
                        gx = int(event.pos[0] * sx2)
                        gy = int(event.pos[1] * sy2)
                        if 0 <= gx < WIDTH and 0 <= gy < HEIGHT:
                            controls.handle_mouse_down((gx, gy))

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if flow == FLOW_PLAYING:
                    sx2 = WIDTH  / screen_width
                    sy2 = HEIGHT / screen_height
                    gx = int(event.pos[0] * sx2)
                    gy = int(event.pos[1] * sy2)
                    if 0 <= gx < WIDTH and 0 <= gy < HEIGHT:
                        controls.handle_mouse_up((gx, gy))

        # ── Game logic update ─────────────────────────────────────────────────
        if flow == FLOW_PLAYING and not state.game_over and not state.won:
            keys = pygame.key.get_pressed()
            move_timer   = handle_player_movement(state, keys, controls, move_timer, dt)
            zombie_timer = handle_zombie_movement(state, zombie_timer, dt)
            update_game_logic(state, dt)

            # Timer countdown
            if state.tick_timer(dt):
                # Timer just expired → lose
                state.game_over   = True
                state.time_expired = True
                state.total_losses += 1

        state.update_particles()

        if state.game_over or state.won:
            flow = FLOW_GAME_OVER

        # ── Screen shake ──────────────────────────────────────────────────────
        sx_off, sy_off = 0, 0
        if state.screen_shake > 0:
            sx_off = random.randint(-state.screen_shake, state.screen_shake)
            sy_off = random.randint(-state.screen_shake, state.screen_shake)
            state.screen_shake = max(0, state.screen_shake - 1)

        # ── Render ────────────────────────────────────────────────────────────
        render_surf = pygame.Surface((WIDTH, HEIGHT))

        if flow == FLOW_START:
            start_screen.draw(render_surf, state.tick)
        elif flow == FLOW_DIFFICULTY:
            diff_screen.draw(render_surf, state.tick)
        else:
            render_game(render_surf, state, ingame_btns, controls)

        scaled = pygame.transform.scale(render_surf, (screen_width, screen_height))
        screen.blit(scaled, (sx_off, sy_off))
        pygame.display.flip()


if __name__ == "__main__":
    main()
