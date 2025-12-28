import pygame
import socket
import serial
import random

# --- CẤU HÌNH ---
RENODE_IP = '127.0.0.1'
RENODE_PORT = 3333
DE1_PORT_NAME = 'COM5'
USE_DE1 = True

# --- MÀU SẮC NEON ---
BG_COLOR = (10, 10, 16)
GRID_COLOR = (30, 30, 40)
SNAKE_COLOR = (0, 255, 200)   # Cyan
FOOD_COLOR = (255, 0, 100)    # Neon Pink
HUD_BG = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (255, 200, 0)  # Vàng cam

# --- PYGAME CONFIG ---
pygame.init()
WIDTH, HEIGHT = 800, 500  # Mở rộng chiều ngang để chứa Menu
PLAY_AREA_W = 600         # Khu vực chơi game
CELL_SIZE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBER SNAKE PRO")
clock = pygame.time.Clock()
font_main = pygame.font.SysFont('Verdana', 18, bold=True)
font_title = pygame.font.SysFont('Impact', 40)
font_small = pygame.font.SysFont('Consolas', 14)

# --- KẾT NỐI ---
try:
    renode_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    renode_sock.connect((RENODE_IP, RENODE_PORT))
    renode_sock.settimeout(0.01)
except: renode_sock = None

ser_de1 = None
if USE_DE1:
    try:
        ser_de1 = serial.Serial(DE1_PORT_NAME, 115200, timeout=0.005)
    except: USE_DE1 = False

def send_mos(char):
    if renode_sock:
        try: renode_sock.sendall(f"{char}\n".encode())
        except: pass

# --- UI DRAWING ---
def draw_ui(score, high_score):
    # Vẽ nền Panel bên phải
    pygame.draw.rect(screen, HUD_BG, (PLAY_AREA_W, 0, WIDTH - PLAY_AREA_W, HEIGHT))
    pygame.draw.line(screen, (50, 255, 255), (PLAY_AREA_W, 0), (PLAY_AREA_W, HEIGHT), 2)

    # Title
    title = font_title.render("CYBER", True, SNAKE_COLOR)
    title2 = font_title.render("SNAKE", True, FOOD_COLOR)
    screen.blit(title, (PLAY_AREA_W + 20, 30))
    screen.blit(title2, (PLAY_AREA_W + 20, 70))

    # Score Box
    score_txt = font_main.render(f"SCORE: {score}", True, TEXT_COLOR)
    high_txt = font_small.render(f"BEST: {high_score}", True, (150, 150, 150))
    screen.blit(score_txt, (PLAY_AREA_W + 20, 140))
    screen.blit(high_txt, (PLAY_AREA_W + 20, 165))

    # --- CONTROLLER GUIDE (VISUAL) ---
    gx, gy = PLAY_AREA_W + 30, 250
    # Vẽ mô phỏng layout phím DE1: [3][2][1][0]
    keys = [('3', 'LEFT'), ('2', 'UP'), ('1', 'DOWN'), ('0', 'RIGHT')]
    for i, (k, action) in enumerate(keys):
        y_pos = gy + i * 50
        # Vẽ nút tròn
        pygame.draw.circle(screen, (50, 50, 70), (gx, y_pos), 15)
        pygame.draw.circle(screen, ACCENT_COLOR, (gx, y_pos), 15, 2)
        
        # Số Key
        k_surf = font_small.render(f"K{k}", True, ACCENT_COLOR)
        screen.blit(k_surf, (gx - 8, y_pos - 7))
        
        # Hướng dẫn text
        act_surf = font_main.render(action, True, TEXT_COLOR)
        screen.blit(act_surf, (gx + 30, y_pos - 10))

def main():
    snake = [[100, 100], [80, 100], [60, 100]]
    snake_dir = [CELL_SIZE, 0]
    next_dir = snake_dir
    food = [random.randrange(0, PLAY_AREA_W//CELL_SIZE)*CELL_SIZE,
            random.randrange(0, HEIGHT//CELL_SIZE)*CELL_SIZE]
    
    score = 0
    high_score = 0
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            # Keyboard fallback
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake_dir != [0, CELL_SIZE]: next_dir = [0, -CELL_SIZE]
                if event.key == pygame.K_DOWN and snake_dir != [0, -CELL_SIZE]: next_dir = [0, CELL_SIZE]
                if event.key == pygame.K_LEFT and snake_dir != [CELL_SIZE, 0]: next_dir = [-CELL_SIZE, 0]
                if event.key == pygame.K_RIGHT and snake_dir != [-CELL_SIZE, 0]: next_dir = [CELL_SIZE, 0]
                if event.key == pygame.K_r and game_over: # Restart
                    return main()

        # DE1 Input
        if USE_DE1 and ser_de1.in_waiting:
            try:
                c = ser_de1.read().decode('utf-8')

                if game_over and c in ['0', '1', '2', '3']:
                    return main()
                
                if not game_over:
                    if c == '2' and snake_dir != [0, CELL_SIZE]: next_dir = [0, -CELL_SIZE]  # Up
                    if c == '1' and snake_dir != [0, -CELL_SIZE]: next_dir = [0, CELL_SIZE] # Down
                    if c == '3' and snake_dir != [CELL_SIZE, 0]: next_dir = [-CELL_SIZE, 0] # Left
                    if c == '0' and snake_dir != [-CELL_SIZE, 0]: next_dir = [CELL_SIZE, 0] # Right
            except: pass

        if not game_over:
            snake_dir = next_dir
            new_head = [snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1]]

            # Collision Logic
            if (new_head[0] < 0 or new_head[0] >= PLAY_AREA_W or 
                new_head[1] < 0 or new_head[1] >= HEIGHT or new_head in snake):
                game_over = True
                send_mos('S')
            else:
                snake.insert(0, new_head)
                if abs(new_head[0] - food[0]) < 5 and abs(new_head[1] - food[1]) < 5:
                    score += 1
                    if score > high_score: high_score = score
                    food = [random.randrange(0, PLAY_AREA_W//CELL_SIZE)*CELL_SIZE,
                            random.randrange(0, HEIGHT//CELL_SIZE)*CELL_SIZE]
                    send_mos('F')
                else:
                    snake.pop()

        # Draw
        screen.fill(BG_COLOR)
        # Grid
        for x in range(0, PLAY_AREA_W, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x,0), (x,HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0,y), (PLAY_AREA_W,y))
        
        # Food (Glowing)
        pygame.draw.circle(screen, FOOD_COLOR, (food[0]+10, food[1]+10), 8)
        pygame.draw.circle(screen, (255, 100, 150), (food[0]+10, food[1]+10), 12, 1)

        # Snake
        for pos in snake:
            pygame.draw.rect(screen, SNAKE_COLOR, (pos[0], pos[1], CELL_SIZE-1, CELL_SIZE-1), border_radius=4)
        
        # UI Sidebar
        draw_ui(score, high_score)

        if game_over:
            overlay = pygame.Surface((PLAY_AREA_W, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0, 180))
            screen.blit(overlay, (0,0))
            msg = font_title.render("GAME OVER", True, (255, 50, 50))
            retry = font_main.render("Press ANY KEY on Board to Restart", True, (200, 200, 200))
            
            screen.blit(msg, (PLAY_AREA_W//2 - 100, HEIGHT//2 - 40))
            screen.blit(retry, (PLAY_AREA_W//2 - 160, HEIGHT//2 + 20)) # Căn chỉnh lại vị trí X một chút cho cân
        pygame.display.flip()
        clock.tick(10 + score//2)

    pygame.quit()

if __name__ == "__main__": main()