import random
from config import ROWS, INITIAL_HEALTH, INITIAL_STAMINA, PORTAL_DURATION, TASK_COUNT
from particles import Particle

class GameState:
    def __init__(self, lamp_positions, map_grid):
        self.total_wins = 0
        self.total_losses = 0
        self.lamp_positions = lamp_positions
        self.map_grid = map_grid

        # ── Difficulty / Timer (set by DifficultyScreen before each run) ──────
        self.difficulty_mode  = "EASY"   # "EASY" | "MEDIUM" | "HARD"
        self.selected_timer   = None     # seconds chosen by player (None = no limit)
        self.remaining_time   = None     # seconds remaining (float), None = unlimited

        self.reset()

    # ── Reset keeps difficulty settings intact ─────────────────────────────────
    def reset(self):
        self.dimension = 0
        self.player_pos = [2, 2]
        self.stalker_pos = [ROWS-3, ROWS-3]
        self.lurker_pos  = [ROWS-3, 3]
        self.tasks = self.spawn_tasks(TASK_COUNT)
        self.tasks_completed = 0
        self.game_over = False
        self.won = False
        self.portal_pos = [15, 15]
        self.particles = []
        self.mist_particles = []
        self.health = INITIAL_HEALTH
        self.stamina = INITIAL_STAMINA
        self.heartbeat = 0
        self.screen_shake = 0
        self.tick = 0
        self.mist_timer = 0
        self.eye_flicker = {}
        self.portal_timer = 0
        self.portal_duration = PORTAL_DURATION

        # Reset remaining_time from the chosen timer
        self.remaining_time = float(self.selected_timer) if self.selected_timer else None
        self.time_expired = False   # flag set when timer hits 0

    # ── Apply a difficulty selection from DifficultyScreen ────────────────────
    def apply_difficulty(self, diff_mode, timer_seconds):
        """Called once from main.py after the player confirms on DifficultyScreen."""
        self.difficulty_mode = diff_mode
        self.selected_timer  = timer_seconds   # None for EASY
        self.remaining_time  = float(timer_seconds) if timer_seconds else None
        self.time_expired    = False

    # ── Timer tick (call every frame with dt in milliseconds) ─────────────────
    def tick_timer(self, dt):
        """Decrement remaining_time. Returns True if just expired."""
        if self.remaining_time is None or self.game_over or self.won:
            return False
        self.remaining_time -= dt / 1000.0
        if self.remaining_time <= 0:
            self.remaining_time = 0
            if not self.time_expired:
                self.time_expired = True
                return True  # signal expiry to caller
        return False

    # ── Helpers ───────────────────────────────────────────────────────────────
    def spawn_tasks(self, count):
        t = []
        while len(t) < count:
            r, c = random.randint(2, ROWS-3), random.randint(2, ROWS-3)
            if [r, c] not in t and self.map_grid[r][c] == ".":
                t.append([r, c])
        return t

    def update_particles(self):
        self.particles      = [p for p in self.particles      if p.update()]
        self.mist_particles = [p for p in self.mist_particles if p.update()]

    def add_spark_particles(self, x, y, count=25):
        for _ in range(count):
            self.particles.append(Particle(x, y, "spark"))

    def add_blood_particles(self, x, y, count=30):
        for _ in range(count):
            self.particles.append(Particle(x, y, "blood"))

    def add_mist_particles(self, x, y, count=3):
        for _ in range(count):
            self.mist_particles.append(Particle(x + random.randint(-30, 30), y, "mist"))
