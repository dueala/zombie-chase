import pygame
import random
import math

# --- Screen and Grid Configuration ---
WIDTH, HEIGHT = 900, 900
ROWS = 30
CELL_SIZE = WIDTH // ROWS

# --- Game States ---
GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2

# --- Colors ---
C_FOG = (5, 8, 5)
C_PLAYER = (220, 230, 255)
C_TASK = (0, 255, 200)
C_PORTAL = (180, 0, 255)
C_GOLD = (255, 200, 40)
C_DIM_BG = (10, 5, 20)
C_RUNE = (100, 0, 200)
C_TREE = (10, 45, 10)
C_TREE2 = (20, 70, 15)
C_HOUSE = (55, 28, 8)
C_WATER = (0, 80, 200)
C_STONE = (80, 80, 80)

# --- Game Timing and Speeds ---
FPS = 30
MOVE_SPEED_NORMAL = 90
MOVE_SPEED_SPRINT = 65
ZOMBIE_SPEED_EASY = 420
ZOMBIE_SPEED_HARD = 260
PARTICLE_MIST_TIMER = 300
PORTAL_DURATION = 10000  # 10 seconds

# --- Gameplay Constants ---
INITIAL_HEALTH = 100
INITIAL_STAMINA = 100
TASK_COUNT = 5
SPRINT_STAMINA_COST = 4
STAMINA_REGEN = 1
SPRINT_THRESHOLD = 5

# --- Visual Effects ---
FOG_RADIUS_MAX = 170
FOG_RADIUS_MIN = 80
FOG_REDUCTION_PER_TASK = 8
TORCH_RADIUS = 80
LAMP_RADIUS = 55

# --- Font Configuration ---
def get_fonts():
    font_ui = pygame.font.SysFont("Courier", 20, bold=True)
    font_msg = pygame.font.SysFont("Impact", 72)
    font_small = pygame.font.SysFont("Courier", 15)
    return font_ui, font_msg, font_small

# --- Initialize Pygame and Display ---
def init_display():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Jungle Survival: Fog of War")
    
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    
    clock = pygame.time.Clock()
    return screen, clock, screen_width, screen_height
