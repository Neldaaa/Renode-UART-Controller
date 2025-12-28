import pygame
import serial
import random

# --- CẤU HÌNH ---
DE1_PORT_NAME = 'COM5'
USE_DE1 = True

# --- COLORS ---
BLACK = (5, 5, 10)
NEON_BLUE = (0, 243, 255)
NEON_PINK = (255, 0, 255)
NEON_GREEN = (57, 255, 20)
NEON_YELLOW = (255, 240, 31)
WHITE = (255, 255, 255)
GRAY = (50, 50, 60)

LANE_COLORS = [NEON_BLUE, NEON_PINK, NEON_GREEN, NEON_YELLOW]

# --- INIT ---
pygame.init()
WIDTH, HEIGHT = 500, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBER BEAT REVOLUTION")
clock = pygame.time.Clock()

# Fonts
font_big = pygame.font.SysFont('Impact', 60)
font_med = pygame.font.SysFont('Verdana', 30, bold=True)
font_small = pygame.font.SysFont('Consolas', 16)

# Serial
ser_de1 = None
if USE_DE1:
    try:
        ser_de1 = serial.Serial(DE1_PORT_NAME, 115200, timeout=0.005)
    except: USE_DE1 = False

# Game Vars
LANE_WIDTH = WIDTH // 4
HIT_Y = HEIGHT - 120
notes = []
particles = []
score = 0
combo = 0
health = 100 # Thêm thanh máu
game_state = "MENU" # MENU, PLAYING, GAMEOVER

class Note:
    def __init__(self, lane):
        self.lane = lane
        self.y = -50
        self.color = LANE_COLORS[lane]
        self.active = True

    def update(self):
        self.y += 7 # Tốc độ
        if self.active and self.y > HEIGHT:
            self.active = False
            return "MISS"
        return None

    def draw(self, surface):
        if self.active:
            rect = (self.lane * LANE_WIDTH + 5, self.y, LANE_WIDTH - 10, 30)
            pygame.draw.rect(surface, self.color, rect, border_radius=5)
            # Inner Glow
            pygame.draw.rect(surface, WHITE, (rect[0]+5, rect[1]+5, rect[2]-10, 5), border_radius=2)

def draw_menu():
    screen.fill(BLACK)
    # Title neon effect
    title = font_big.render("CYBER BEAT", True, NEON_BLUE)
    title_shadow = font_big.render("CYBER BEAT", True, (0, 0, 100))
    screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 4, 154))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
    
    sub = font_med.render("PRESS ANY KEY TO START", True, NEON_PINK)
    
    # Blinking effect
    if pygame.time.get_ticks() % 1000 < 500:
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 400))
    
    hint = font_small.render("Controls: DE1 Keys [3][2][1][0] or D F J K", True, GRAY)
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 600))

def reset_game():
    global notes, score, combo, health
    notes = []
    score = 0
    combo = 0
    health = 100

def check_hit(lane_idx):
    global score, combo, health
    hit = False
    for note in notes:
        if note.active and note.lane == lane_idx:
            if abs(note.y - HIT_Y) < 50:
                note.active = False
                score += 100 + (combo * 10)
                combo += 1
                health = min(100, health + 2)
                hit = True
                break
    if not hit:
        combo = 0
        health -= 5

# --- LOOP ---
running = True
spawn_timer = 0

while running:
    # INPUT
    inputs = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "MENU" or game_state == "GAMEOVER":
                game_state = "PLAYING"
                reset_game()
            else:
                if event.key == pygame.K_d: inputs.append(0)
                if event.key == pygame.K_f: inputs.append(1)
                if event.key == pygame.K_j: inputs.append(2)
                if event.key == pygame.K_k: inputs.append(3)

    if USE_DE1 and ser_de1.in_waiting:
        try:
            c = ser_de1.read().decode('utf-8')
            if game_state != "PLAYING" and c in ['0','1','2','3']:
                game_state = "PLAYING"
                reset_game()
            elif game_state == "PLAYING":
                if c == '3': inputs.append(0)
                elif c == '2': inputs.append(1)
                elif c == '1': inputs.append(2)
                elif c == '0': inputs.append(3)
        except: pass

    # UPDATE & DRAW
    if game_state == "MENU":
        draw_menu()
    
    elif game_state == "PLAYING":
        screen.fill(BLACK)
        
        # Process Hits
        for lane in inputs: check_hit(lane)

        # Spawn
        spawn_timer += 1
        if spawn_timer > 20:
            if random.random() < 0.7:
                notes.append(Note(random.randint(0,3)))
            spawn_timer = 0

        # Draw Lanes
        for i in range(4):
            x = i * LANE_WIDTH
            pygame.draw.line(screen, (30,30,40), (x, 0), (x, HEIGHT), 2)
            # Key Label
            lbl = font_small.render(f"KEY {3-i}", True, GRAY)
            screen.blit(lbl, (x + 30, HEIGHT - 30))

        # Hit Line
        pygame.draw.line(screen, WHITE, (0, HIT_Y), (WIDTH, HIT_Y), 2)
        glow = pygame.Surface((WIDTH, 20), pygame.SRCALPHA)
        glow.fill((255, 255, 255, 30))
        screen.blit(glow, (0, HIT_Y-10))

        # Update Notes
        for note in notes:
            status = note.update()
            note.draw(screen)
            if status == "MISS":
                combo = 0
                health -= 10
        
        notes = [n for n in notes if n.active or n.y <= HEIGHT]

        # UI
        sc_surf = font_med.render(f"{score}", True, WHITE)
        screen.blit(sc_surf, (10, 10))
        
        if combo > 1:
            cb_surf = font_big.render(f"{combo}x", True, NEON_YELLOW)
            screen.blit(cb_surf, (WIDTH//2 - 40, HEIGHT//2))

        # Health Bar
        pygame.draw.rect(screen, (100,0,0), (WIDTH-120, 10, 110, 20))
        pygame.draw.rect(screen, NEON_GREEN if health > 50 else (255,0,0), (WIDTH-120, 10, health * 1.1, 20))
        
        if health <= 0:
            game_state = "GAMEOVER"

    elif game_state == "GAMEOVER":
        screen.fill(BLACK)
        txt = font_big.render("GAME OVER", True, (255, 0, 0))
        sc = font_med.render(f"Score: {score}", True, WHITE)
        rst = font_small.render("Press Button to Restart", True, GRAY)
        
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200))
        screen.blit(sc, (WIDTH//2 - sc.get_width()//2, 300))
        screen.blit(rst, (WIDTH//2 - rst.get_width()//2, 500))

    pygame.display.flip()
    clock.tick(60)

if ser_de1: ser_de1.close()
pygame.quit()