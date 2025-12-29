import pygame
import serial
import random
import math

# --- CẤU HÌNH ---
DE1_PORT_NAME = 'COM5'
USE_DE1 = True

# --- COLORS (PALETTE CYBERPUNK) ---
BG_COLOR = (10, 10, 18)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_LIME = (50, 255, 50)
NEON_YELLOW = (255, 230, 0)
NEON_RED = (255, 50, 50)
WHITE = (255, 255, 255)
DARK_GRAY = (40, 40, 50)
GRID_COLOR = (0, 50, 100)
GRAY = (50, 50, 50)

LANE_COLORS = [NEON_CYAN, NEON_MAGENTA, NEON_LIME, NEON_YELLOW]

# --- INIT ---
pygame.init()
WIDTH, HEIGHT = 500, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBER BEAT: OVERDRIVE")
clock = pygame.time.Clock()

# Fonts
font_score = pygame.font.SysFont('Impact', 40)
font_combo = pygame.font.SysFont('Verdana', 50, bold=True)
font_small = pygame.font.SysFont('Consolas', 14)

# Serial
ser_de1 = None
if USE_DE1:
    try:
        ser_de1 = serial.Serial(DE1_PORT_NAME, 115200, timeout=0.005)
        print(f"Connected to {DE1_PORT_NAME}")
    except: 
        USE_DE1 = False
        print("Running in Simulation Mode")

# Game Vars
LANE_WIDTH = WIDTH // 4
HIT_Y = HEIGHT - 130
notes = []
particles = []
inputs_visual = [0, 0, 0, 0] # Dùng để làm hiệu ứng sáng lane khi bấm
score = 0
combo = 0
health = 100
max_health = 100
game_state = "MENU"
grid_offset = 0

# --- CLASS ---
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.size = random.randint(3, 6)
        self.life = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 10
        self.size = max(0, self.size - 0.1)

    def draw(self, surf):
        if self.life > 0 and self.size > 0:
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(self.life)), (int(self.size), int(self.size)), int(self.size))
            surf.blit(s, (self.x - self.size, self.y - self.size))

class Note:
    def __init__(self, lane):
        self.lane = lane
        self.y = -50
        self.color = LANE_COLORS[lane]
        self.active = True
        self.height = 30
        self.width = LANE_WIDTH - 20

    def update(self):
        self.y += 8 # Tốc độ nhanh hơn xíu
        if self.active and self.y > HEIGHT:
            self.active = False
            return "MISS"
        return None

    def draw(self, surface):
        if self.active:
            x = self.lane * LANE_WIDTH + 10
            
            # Draw Glow (Layer mờ)
            glow = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            glow.fill((*self.color, 50))
            surface.blit(glow, (x - 10, self.y - 10))
            
            # Draw Core Note
            pygame.draw.rect(surface, self.color, (x, self.y, self.width, self.height), border_radius=4)
            # Center white strip
            pygame.draw.rect(surface, WHITE, (x + 10, self.y + 10, self.width - 20, 5))

# --- VFX FUNCTIONS ---
def draw_grid():
    global grid_offset
    grid_offset = (grid_offset + 2) % 40
    # Vertical lines
    for i in range(5):
        x = i * LANE_WIDTH
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    # Horizontal moving lines
    for y in range(grid_offset, HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)
    
    # Darken bottom (Fade out effect)
    gradient = pygame.Surface((WIDTH, 200), pygame.SRCALPHA)
    for i in range(200):
        alpha = int((i / 200) * 255)
        pygame.draw.line(gradient, (10, 10, 18, alpha), (0, i), (WIDTH, i))
    # screen.blit(gradient, (0, HEIGHT-200)) # Optional fog

def draw_neon_text(text, font, color, center_pos):
    # Shadow/Glow
    glow_surf = font.render(text, True, (color[0]//2, color[1]//2, color[2]//2))
    screen.blit(glow_surf, (center_pos[0] - glow_surf.get_width()//2 + 2, center_pos[1] + 2))
    # Main text
    txt_surf = font.render(text, True, color)
    screen.blit(txt_surf, (center_pos[0] - txt_surf.get_width()//2, center_pos[1]))

def draw_health_bar():
    # Khung Bar góc cạnh
    bar_w, bar_h = 200, 20
    x, y = WIDTH - bar_w - 20, 20
    
    # Border
    pygame.draw.rect(screen, WHITE, (x-2, y-2, bar_w+4, bar_h+4), 1)
    
    # Background
    pygame.draw.rect(screen, (30,0,0), (x, y, bar_w, bar_h))
    
    # Health fill
    fill_w = int((health / max_health) * bar_w)
    
    # Màu sắc thay đổi theo máu
    if health > 60: col = NEON_LIME
    elif health > 30: col = NEON_YELLOW
    else: col = NEON_RED
    
    if fill_w > 0:
        pygame.draw.rect(screen, col, (x, y, fill_w, bar_h))
    
    # Text HP
    hp_txt = font_small.render(f"INTEGRITY: {int(health)}%", True, col)
    screen.blit(hp_txt, (x, y + 25))

def spawn_particles(x, y, color):
    for _ in range(10):
        particles.append(Particle(x, y, color))

def reset_game():
    global notes, score, combo, health, particles
    notes = []
    particles = []
    score = 0
    combo = 0
    health = 100

def check_hit(lane_idx):
    global score, combo, health
    hit = False
    for note in notes:
        if note.active and note.lane == lane_idx:
            # Hit window rộng hơn chút cho dễ thở
            if abs(note.y - HIT_Y) < 60:
                note.active = False
                spawn_particles(note.lane * LANE_WIDTH + LANE_WIDTH//2, note.y, note.color)
                
                # Tính điểm dựa trên độ chính xác
                accuracy = abs(note.y - HIT_Y)
                pts = 300 if accuracy < 15 else (100 if accuracy < 40 else 50)
                
                score += pts + (combo * 10)
                combo += 1
                health = min(100, health + 5)
                hit = True
                break
    if not hit:
        combo = 0
        health -= 8 # Phạt nặng nếu bấm loạn xạ

# --- MAIN LOOP ---
running = True
spawn_timer = 0

while running:
    # 1. READ INPUT
    current_inputs = []
    key_pressed = [False] * 4 # Dùng cho hiệu ứng hình ảnh
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if game_state in ["MENU", "GAMEOVER"]:
                game_state = "PLAYING"
                reset_game()
            else:
                if event.key == pygame.K_d: current_inputs.append(0)
                if event.key == pygame.K_f: current_inputs.append(1)
                if event.key == pygame.K_j: current_inputs.append(2)
                if event.key == pygame.K_k: current_inputs.append(3)

    if USE_DE1 and ser_de1.in_waiting:
        try:
            line = ser_de1.read_all().decode('utf-8') # Đọc hết buffer
            for c in line:
                if game_state != "PLAYING" and c in ['0','1','2','3']:
                    game_state = "PLAYING"
                    reset_game()
                elif game_state == "PLAYING":
                    if c == '3': current_inputs.append(0)
                    if c == '2': current_inputs.append(1)
                    if c == '1': current_inputs.append(2)
                    if c == '0': current_inputs.append(3)
        except: pass

    # Cập nhật trạng thái visual cho các nút đang bấm
    for i in current_inputs:
        if 0 <= i < 4: 
            inputs_visual[i] = 5 # Frame counter cho hiệu ứng sáng
            key_pressed[i] = True

    # 2. UPDATE & DRAW
    screen.fill(BG_COLOR)
    
    if game_state == "MENU":
        draw_grid()
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5 # 0 to 1
        col_pulse = (int(NEON_CYAN[0]*pulse), int(NEON_CYAN[1]*pulse), 255)
        
        draw_neon_text("CYBER BEAT", pygame.font.SysFont('Impact', 80), NEON_MAGENTA, (WIDTH//2, 200))
        draw_neon_text("REVOLUTION", pygame.font.SysFont('Impact', 60), NEON_CYAN, (WIDTH//2, 280))
        
        if pygame.time.get_ticks() % 1000 < 600:
            draw_neon_text("- PRESS START -", font_score, WHITE, (WIDTH//2, 500))
            
    elif game_state == "PLAYING":
        draw_grid()
        
        # --- DRAW LANES UI ---
        # Hit Line (Thanh ngang cố định)
        pygame.draw.rect(screen, DARK_GRAY, (0, HIT_Y - 5, WIDTH, 10))
        pygame.draw.line(screen, NEON_CYAN, (0, HIT_Y), (WIDTH, HIT_Y), 2)
        
        # Lane Feedback (Hiệu ứng khi bấm)
        for i in range(4):
            x = i * LANE_WIDTH
            # Nếu đang bấm, vẽ cột sáng mờ
            if inputs_visual[i] > 0:
                s = pygame.Surface((LANE_WIDTH, HEIGHT), pygame.SRCALPHA)
                s.fill((*LANE_COLORS[i], 30)) # 30 độ trong suốt
                screen.blit(s, (x, 0))
                # Receptor sáng lên
                pygame.draw.rect(screen, LANE_COLORS[i], (x + 10, HIT_Y - 5, LANE_WIDTH - 20, 10), border_radius=5)
                inputs_visual[i] -= 1
            else:
                # Receptor bình thường (Khung rỗng)
                pygame.draw.rect(screen, GRAY, (x + 10, HIT_Y - 5, LANE_WIDTH - 20, 10), 2, border_radius=5)
            
            # Key Label
            lbl = font_small.render(f"K{3-i}", True, GRAY)
            screen.blit(lbl, (x + LANE_WIDTH//2 - 10, HEIGHT - 30))

        # --- LOGIC ---
        for lane in current_inputs: check_hit(lane)

        spawn_timer += 1
        if spawn_timer > 25: # Tốc độ spawn
            if random.random() < 0.6:
                notes.append(Note(random.randint(0,3)))
            spawn_timer = 0

        # Draw Notes
        for note in notes:
            status = note.update()
            note.draw(screen)
            if status == "MISS":
                combo = 0
                health -= 10 # Trừ nhiều máu hơn
                # Visual feedback for miss
                screen.fill((50,0,0), special_flags=pygame.BLEND_ADD)

        notes = [n for n in notes if n.active]

        # Draw Particles
        for p in particles:
            p.update()
            p.draw(screen)
        particles = [p for p in particles if p.life > 0]

        # --- HUD ---
        # Score
        draw_neon_text(f"{score}", font_score, WHITE, (60, 40))
        
        # Combo (Giữa màn hình, nảy lên theo nhịp)
        if combo > 5:
            scale = 1.0 + min(0.5, combo / 50)
            c_surf = pygame.transform.rotozoom(font_combo.render(f"{combo} COMBO", True, NEON_CYAN), 0, scale)
            screen.blit(c_surf, (WIDTH//2 - c_surf.get_width()//2, HEIGHT//2 - 100))
            
        # Health
        draw_health_bar()

        if health <= 0:
            game_state = "GAMEOVER"

    elif game_state == "GAMEOVER":
        screen.fill((20, 0, 0)) # Nền đỏ thẫm
        draw_neon_text("SYSTEM FAILURE", font_combo, NEON_RED, (WIDTH//2, 250))
        draw_neon_text(f"FINAL SCORE: {score}", font_score, WHITE, (WIDTH//2, 350))
        draw_neon_text("PRESS ANY KEY TO REBOOT", font_small, NEON_CYAN, (WIDTH//2, 550))

    pygame.display.flip()
    clock.tick(60)

if ser_de1: ser_de1.close()
pygame.quit()