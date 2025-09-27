import pygame
import random
import sys
from collections import deque # For Breadth-First Search

pygame.init()
pygame.mixer.init()

# --- Global Game Settings ---
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game") # Changed caption

clock = pygame.time.Clock()
snake_speed = 60    # target FPS (frames per second)

tile_size = 16  # <--- CHANGED THIS FROM 32 TO 16

# --- Game States ---
GAME_STATE_MAIN_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_SETTINGS = 2
GAME_STATE_GAME_OVER = 3

current_game_state = GAME_STATE_MAIN_MENU # Start at main menu

# --- Game Variables (will be reset for each game) ---
move_delay = 0 # Will be set by difficulty
move_counter = 0
paused = False
input_buffer = None
input_buffer_timer = 0
buffer_delay = 5
cheat_mode = False

# --- Settings Variables (persist across games) ---
difficulty_level = "Medium" # Default difficulty
sound_enabled = True        # Default sound state
auto_play = False           # Default auto-play state (as requested in the last turn)

# Difficulty mappings: {level_name: move_delay_frames}
DIFFICULTY_MAP = {
    "Easy": 12,
    "Medium": 8, # Adjusted slightly for better default
    "Hard": 4,
    "Insane": 2
}

# --- Load Assets ---
try:
    sheet = pygame.image.load("f92be3bf-c946-4fd6-a596-b69edf486679.png").convert_alpha()
except pygame.error as e:
    print(f"Error loading sprite sheet: {e}")
    print("Please make sure 'f92be3bf-c946-4fd6-a596-b69edf486679.png' is in the same directory.")
    pygame.quit()
    sys.exit()

eat_sound = None # Initialize to None in case loading fails
game_over_sound = None # Initialize to None in case loading fails
try:
    eat_sound = pygame.mixer.Sound("apple_crunch.wav")
    game_over_sound = pygame.mixer.Sound("game_over_buzz.wav")
except pygame.error as e:
    print(f"Error loading sound files: {e}")
    print("Make sure 'apple_crunch.wav' and 'game_over_buzz.wav' are in the same directory.")

# Function to apply sound settings
def apply_sound_settings():
    volume = 1.0 if sound_enabled else 0.0
    if eat_sound:
        eat_sound.set_volume(volume)
    if game_over_sound:
        game_over_sound.set_volume(volume)
apply_sound_settings() # Apply initial sound setting

# Extract sprite from sheet
def get_sprite(x, y, w, h):
    """Extracts a sprite from the loaded sprite sheet and scales it."""
    sprite = pygame.Surface((w, h), pygame.SRCALPHA)
    sprite.blit(sheet, (0, 0), pygame.Rect(x, y, w, h))
    # Scaled to the new tile_size
    return pygame.transform.scale(sprite, (tile_size, tile_size)) 

# Sprite definitions
sprites = {
    "apple": get_sprite(0, 191, 64, 64),
    "body_horizontal": get_sprite(64, 0, 64, 64),
    "body_vertical": get_sprite(128, 64, 64, 64),
    "corner": get_sprite(0, 0, 64, 64),
    "head_up": get_sprite(191, 0, 64, 64),
    "head_right": get_sprite(256, 0, 64, 64),
    "head_down": get_sprite(256, 64, 64, 64),
    "head_left": get_sprite(191, 64, 64, 64),
    "tail_up": get_sprite(191, 128, 64, 64),
    "tail_right": get_sprite(256, 128, 64, 64),
    "tail_down": get_sprite(256, 191, 64, 64),
    "tail_left": get_sprite(192, 192, 64, 64),
}

# Fonts for text
font = pygame.font.SysFont("comicsansms", 25)
game_over_font = pygame.font.SysFont("comicsansms", 60, bold=True)
instruction_font = pygame.font.SysFont("comicsansms", 20)
menu_font = pygame.font.SysFont("comicsansms", 40) # For menu options
title_font = pygame.font.SysFont("comicsansms", 70, bold=True) # For main menu title

# --- Helper Functions for Drawing ---
def show_score(score):
    """Displays the current score on the screen."""
    value = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(value, [10, 10])

def draw_grid_background():
    """Draws a subtle grid pattern as the background."""
    dark_blue = (40, 120, 180)
    light_blue = (60, 160, 220)
    
    screen.fill(dark_blue)

    for x in range(0, width, tile_size):
        pygame.draw.line(screen, light_blue, (x, 0), (x, height), 1)
    for y in range(0, height, tile_size):
        pygame.draw.line(screen, light_blue, (0, y), (width, y), 1)


def draw_snake(snake):
    """Draws the snake on the screen using appropriate sprites and rotations."""
    for i, pos in enumerate(snake):
        sprite = None
        angle = 0

        if i == len(snake) - 1:  # Head segment
            # Ensure the snake has at least 2 segments to calculate direction from previous
            if len(snake) > 1:
                direction = (snake[i][0] - snake[i-1][0], snake[i][1] - snake[i-1][1])
            else: # If snake is just a head (first segment), assume a default direction (e.g., right)
                direction = (1, 0) 
            
            if direction == (0, -1):  sprite = sprites["head_up"]
            elif direction == (0, 1):   sprite = sprites["head_down"]
            elif direction == (-1, 0):  sprite = sprites["head_left"]
            else:                       sprite = sprites["head_right"]
        elif i == 0:  # Tail segment
            # Ensure the snake has at least 2 segments to calculate direction to next
            if len(snake) > 1:
                direction = (snake[i+1][0] - snake[i][0], snake[i+1][1] - snake[i][1])
            else: # If snake is just a head (and this is the same as head), this case won't be hit usually.
                direction = (1, 0) # Fallback, though should not be reached in proper game flow
            
            if direction == (0, -1):  sprite = sprites["tail_up"]
            elif direction == (0, 1):   sprite = sprites["tail_down"]
            elif direction == (-1, 0):  sprite = sprites["tail_left"]
            else:                       sprite = sprites["tail_right"]
        else:  # Body segment
            prev = snake[i - 1]
            curr = snake[i]
            next = snake[i + 1]

            dx1, dy1 = curr[0] - prev[0], curr[1] - prev[1]
            dx2, dy2 = next[0] - curr[0], next[1] - curr[1]

            if dx1 == dx2 and dy1 == dy2: # Straight
                if dx1 == 0: sprite = sprites["body_vertical"]
                else:        sprite = sprites["body_horizontal"]
            else: # Corner
                sprite = sprites["corner"]
                if ((dx1, dy1) == (-1, 0) and (dx2, dy2) == (0, 1)) or \
                   ((dx1, dy1) == (0, -1) and (dx2, dy2) == (1, 0)):
                    angle = 0
                elif ((dx1, dy1) == (0, 1) and (dx2, dy2) == (1, 0)) or \
                     ((dx1, dy1) == (-1, 0) and (dx2, dy2) == (0, -1)):
                    angle = 90
                elif ((dx1, dy1) == (1, 0) and (dx2, dy2) == (0, -1)) or \
                     ((dx1, dy1) == (0, 1) and (dx2, dy2) == (-1, 0)):
                    angle = 180
                elif ((dx1, dy1) == (0, -1) and (dx2, dy2) == (-1, 0)) or \
                     ((dx1, dy1) == (1, 0) and (dx2, dy2) == (0, 1)):
                    angle = 270
        
        if sprite: # Only rotate if a sprite was assigned
            if sprite == sprites["corner"]:
                sprite = pygame.transform.rotate(sprite, angle)
            
            screen.blit(sprite, (pos[0] * tile_size, pos[1] * tile_size))


def find_path_bfs(snake, food, grid_width, grid_height, current_dx, current_dy):
    """
    Finds the shortest path from snake's head to food using BFS.
    Returns (dx, dy) for the next move, or None if no path found (trapped).
    """
    q = deque()
    q.append((snake[-1][0], snake[-1][1], []))

    visited = set()
    visited.add((snake[-1][0], snake[-1][1]))

    game_grid_for_bfs = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
    for i, (sx, sy) in enumerate(snake):
        if i != 0: # Exclude the tail (snake[0]) as it will move
            game_grid_for_bfs[sy][sx] = 1 

    moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    while q:
        curr_x, curr_y, path = q.popleft()

        if curr_x == food[0] and curr_y == food[1]:
            if path:
                return path[0]
            else:
                return (current_dx, current_dy) # Head is on food

        for move_dx, move_dy in moves:
            next_x, next_y = curr_x + move_dx, curr_y + move_dy

            if not (0 <= next_x < grid_width and 0 <= next_y < grid_height):
                continue
            if game_grid_for_bfs[next_y][next_x] == 1:
                continue
            if (next_x, next_y) in visited:
                continue

            visited.add((next_x, next_y))
            new_path = path + [(move_dx, move_dy)]
            q.append((next_x, next_y, new_path))
    
    # Fallback strategy if no path to food is found
    fallback_moves_priority = [
        (current_dx, current_dy),
        (-current_dy, current_dx), # Right turn
        (current_dy, -current_dx)  # Left turn
    ]

    for move_dx, move_dy in fallback_moves_priority:
        next_x, next_y = snake[-1][0] + move_dx, snake[-1][1] + move_dy
        if (0 <= next_x < grid_width and 0 <= next_y < grid_height) and \
           game_grid_for_bfs[next_y][next_x] == 0:
            return (move_dx, move_dy)

    return None # Completely trapped


def reset_game():
    """Resets all game variables to their initial state for a new game."""
    global move_counter, paused, input_buffer, input_buffer_timer, move_delay
    
    move_counter = 0
    paused = False
    input_buffer = None
    input_buffer_timer = 0
    move_delay = DIFFICULTY_MAP[difficulty_level] # Set delay based on chosen difficulty

    x, y = width // tile_size // 2, height // tile_size // 2
    dx, dy = 1, 0
    snake = [[x - 2, y], [x - 1, y], [x, y]]
    length = 3
    
    # Ensure food doesn't spawn on the initial snake
    all_possible_food_positions = []
    for fy in range(height // tile_size):
        for fx in range(width // tile_size):
            all_possible_food_positions.append([fx, fy])

    available_food_positions = [pos for pos in all_possible_food_positions if pos not in snake]
    
    if available_food_positions:
        food = random.choice(available_food_positions)
    else: # Highly unlikely for a start, but good practice
        food = [0,0] # Fallback if no space
    
    return snake, dx, dy, length, food

# --- Menu Drawing Functions ---
def draw_main_menu():
    """Draws the main menu screen."""
    screen.fill((0, 0, 0)) # Black background for menus

    # Title
    title_text = title_font.render("SNAKE", True, (255, 255, 0)) # Yellow title
    title_rect = title_text.get_rect(center=(width // 2, height // 4))
    screen.blit(title_text, title_rect)

    menu_items = [
        ("Play Game", GAME_STATE_PLAYING),
        ("Settings", GAME_STATE_SETTINGS),
        ("Exit", None) # None implies quit
    ]

    button_y_start = height // 2
    button_spacing = 60
    button_rects = {} # Store rects for click detection

    for i, (text, state) in enumerate(menu_items):
        button_text = menu_font.render(text, True, (255, 255, 255))
        button_rect = button_text.get_rect(center=(width // 2, button_y_start + i * button_spacing))
        screen.blit(button_text, button_rect)
        button_rects[text] = (button_rect, state)
    
    return button_rects # Return clickable areas

def draw_settings_menu():
    """Draws the settings menu screen."""
    screen.fill((0, 0, 0))

    settings_title = menu_font.render("SETTINGS", True, (255, 255, 0))
    settings_title_rect = settings_title.get_rect(center=(width // 2, height // 8))
    screen.blit(settings_title, settings_title_rect)

    setting_y_start = height // 4 + 20
    setting_spacing = 50
    button_rects = {}

    # Difficulty
    difficulty_text_label = font.render(f"Difficulty: ", True, (255, 255, 255))
    difficulty_text_label_rect = difficulty_text_label.get_rect(midright=(width // 2 - 20, setting_y_start))
    screen.blit(difficulty_text_label, difficulty_text_label_rect)

    difficulty_value_text = font.render(f"{difficulty_level}", True, (0, 255, 0) if difficulty_level == "Easy" else (255, 165, 0) if difficulty_level == "Medium" else (255, 0, 0) if difficulty_level == "Hard" else (150, 0, 150))
    difficulty_value_rect = difficulty_value_text.get_rect(midleft=(width // 2 + 20, setting_y_start))
    screen.blit(difficulty_value_text, difficulty_value_rect)
    button_rects["Difficulty"] = (difficulty_value_rect.inflate(40, 10), "difficulty_toggle") # Make clickable area larger

    # Sound
    sound_text_label = font.render("Sound: ", True, (255, 255, 255))
    sound_text_label_rect = sound_text_label.get_rect(midright=(width // 2 - 20, setting_y_start + setting_spacing))
    screen.blit(sound_text_label, sound_text_label_rect)

    sound_value_text = font.render("ON" if sound_enabled else "OFF", True, (0, 255, 0) if sound_enabled else (255, 0, 0))
    sound_value_rect = sound_value_text.get_rect(midleft=(width // 2 + 20, setting_y_start + setting_spacing))
    screen.blit(sound_value_text, sound_value_rect)
    button_rects["Sound"] = (sound_value_rect.inflate(40, 10), "sound_toggle")


    # Auto Play
    auto_play_text_label = font.render("Auto Play: ", True, (255, 255, 255))
    auto_play_text_label_rect = auto_play_text_label.get_rect(midright=(width // 2 - 20, setting_y_start + setting_spacing * 2))
    screen.blit(auto_play_text_label, auto_play_text_label_rect)

    auto_play_value_text = font.render("ON" if auto_play else "OFF", True, (0, 255, 0) if auto_play else (255, 0, 0))
    auto_play_value_rect = auto_play_value_text.get_rect(midleft=(width // 2 + 20, setting_y_start + setting_spacing * 2))
    screen.blit(auto_play_value_text, auto_play_value_rect)
    button_rects["AutoPlay"] = (auto_play_value_rect.inflate(40, 10), "auto_play_toggle")


    # Back Button
    back_button_text = menu_font.render("Back", True, (255, 255, 255))
    back_button_rect = back_button_text.get_rect(center=(width // 2, height - 50))
    screen.blit(back_button_text, back_button_rect)
    button_rects["Back"] = (back_button_rect, GAME_STATE_MAIN_MENU)

    return button_rects

# --- Main Game Loop ---
def game_loop():
    global current_game_state, auto_play, difficulty_level, sound_enabled, move_delay, \
           move_counter, paused, input_buffer, input_buffer_timer, cheat_mode, \
           snake, dx, dy, length, food

    running = True
    menu_buttons = {} # To store clickable areas for current menu

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    if current_game_state == GAME_STATE_MAIN_MENU:
                        for text, (rect, target_state) in menu_buttons.items():
                            if rect.collidepoint(event.pos):
                                if target_state is None: # Exit button
                                    running = False
                                else:
                                    current_game_state = target_state
                                    if current_game_state == GAME_STATE_PLAYING:
                                        snake, dx, dy, length, food = reset_game() # Start new game
                                break # Stop checking other buttons
                    elif current_game_state == GAME_STATE_SETTINGS:
                        for text, (rect, action_type) in menu_buttons.items():
                            if rect.collidepoint(event.pos):
                                if action_type == "difficulty_toggle":
                                    difficulty_levels = list(DIFFICULTY_MAP.keys())
                                    current_index = difficulty_levels.index(difficulty_level)
                                    next_index = (current_index + 1) % len(difficulty_levels)
                                    difficulty_level = difficulty_levels[next_index]
                                    move_delay = DIFFICULTY_MAP[difficulty_level] # Update game speed
                                elif action_type == "sound_toggle":
                                    sound_enabled = not sound_enabled
                                    apply_sound_settings() # Update sound volume
                                elif action_type == "auto_play_toggle":
                                    auto_play = not auto_play
                                elif action_type == GAME_STATE_MAIN_MENU: # Back button
                                    current_game_state = GAME_STATE_MAIN_MENU
                                break # Stop checking other buttons
            elif event.type == pygame.KEYDOWN:
                if current_game_state == GAME_STATE_PLAYING:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    # Only process manual input if not in auto_play mode
                    elif not auto_play and not paused:
                        if not input_buffer:
                            if event.key == pygame.K_a and dx == 0:
                                input_buffer = (-1, 0)
                            elif event.key == pygame.K_d and dx == 0:
                                input_buffer = (1, 0)
                            elif event.key == pygame.K_w and dy == 0:
                                input_buffer = (0, -1)
                            elif event.key == pygame.K_s and dy == 0:
                                input_buffer = (0, 1)
                elif current_game_state == GAME_STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        current_game_state = GAME_STATE_PLAYING # Go back to playing state
                        snake, dx, dy, length, food = reset_game() # Start new game
                    elif event.key == pygame.K_m: # Go to main menu from game over
                        current_game_state = GAME_STATE_MAIN_MENU


        # --- Render based on Game State ---
        if current_game_state == GAME_STATE_MAIN_MENU:
            menu_buttons = draw_main_menu() # Update clickable areas for main menu
        elif current_game_state == GAME_STATE_SETTINGS:
            menu_buttons = draw_settings_menu() # Update clickable areas for settings menu
        elif current_game_state == GAME_STATE_PLAYING:
            draw_grid_background()
            if not paused:
                # AI Logic for auto_play
                if auto_play:
                    grid_width = width // tile_size
                    grid_height = height // tile_size
                    
                    ai_move = find_path_bfs(snake, food, grid_width, grid_height, dx, dy)
                    
                    if ai_move:
                        if not (ai_move[0] == -dx and ai_move[1] == -dy):
                            input_buffer = ai_move
                    else:
                        current_game_state = GAME_STATE_GAME_OVER
                        if game_over_sound:
                            game_over_sound.play()
                        continue

                move_counter += 1
                if input_buffer_timer > 0:
                    input_buffer_timer -= 1

                if move_counter >= move_delay:
                    move_counter = 0
                    if input_buffer:
                        dx, dy = input_buffer
                        input_buffer = None
                        input_buffer_timer = buffer_delay
                    
                    head = [snake[-1][0] + dx, snake[-1][1] + dy]
                    
                    # Collision detection
                    if not cheat_mode:
                        if head in snake or \
                           not (0 <= head[0] < width // tile_size) or \
                           not (0 <= head[1] < height // tile_size):
                            current_game_state = GAME_STATE_GAME_OVER
                            if game_over_sound:
                                game_over_sound.play()
                            continue
                    
                    snake.append(head)

                    if head == food:
                        length += 1
                        if eat_sound:
                            eat_sound.play()
                        while True:
                            new_food = [random.randint(0, width // tile_size - 1), random.randint(0, height // tile_size - 1)]
                            if new_food not in snake:
                                food = new_food
                                break
                    
                    if len(snake) > length:
                        del snake[0]

            screen.blit(sprites["apple"], (food[0] * tile_size, food[1] * tile_size))
            draw_snake(snake)
            show_score(length - 3)

            if paused:
                paused_text = game_over_font.render("PAUSED", True, (255, 255, 0))
                text_rect = paused_text.get_rect(center=(width // 2, height // 2))
                screen.blit(paused_text, text_rect)

        elif current_game_state == GAME_STATE_GAME_OVER:
            # Re-draw background and possibly last snake/food for context
            draw_grid_background()
            screen.blit(sprites["apple"], (food[0] * tile_size, food[1] * tile_size))
            draw_snake(snake) # Draw the snake in its final position

            # Overlay for game over text
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) # Semi-transparent black
            screen.blit(overlay, (0,0))

            game_over_text = game_over_font.render("GAME OVER!", True, (255, 0, 0))
            score_text = font.render(f"Final Score: {length - 3}", True, (255, 255, 255))
            restart_text = instruction_font.render("Press 'R' to Restart or 'M' for Main Menu", True, (255, 255, 255))

            go_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 40))
            score_rect = score_text.get_rect(center=(width // 2, height // 2 + 10))
            restart_rect = restart_text.get_rect(center=(width // 2, height // 2 + 60))

            screen.blit(game_over_text, go_rect)
            screen.blit(score_text, score_rect)
            screen.blit(restart_text, restart_rect)
            
        pygame.display.update()
        clock.tick(snake_speed)

    pygame.quit()
    sys.exit()

# Start the game loop (which now starts at the main menu)
game_loop()