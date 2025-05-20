import pygame
import collections
import random
import math

# Initialize Pygame
pygame.init()

# Font for Health Display & UI
health_font = pygame.font.Font(None, 36) # For health
ui_font = pygame.font.Font(None, 30) # For other UI elements like score and selected elements
game_over_font = pygame.font.Font(None, 74)
info_font = pygame.font.Font(None, 32)

# Custom event for enemy spawning
ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1

# Define Elements
ELEMENTS = ["FIRE", "WATER", "AIR"]

# Game State
game_state = "playing"
game_start_time = 0 # Will be set when a game (re)starts
time_survived = 0

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255) # For player and WATER projectile
RED = (255, 0, 0) # For FIRE projectile
WHITE = (255, 255, 255) # For AIR projectile
GREEN = (0, 255, 0) # For Enemies
GREY = (128, 128, 128) # For placeholder or other uses

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.speed = random.randint(1, 2) # Randomize speed slightly

        # Spawn randomly off one of the screen edges
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = -self.rect.height - random.randint(5, 50)
        elif edge == 'bottom':
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = SCREEN_HEIGHT + random.randint(5, 50)
        elif edge == 'left':
            self.rect.x = -self.rect.width - random.randint(5, 50)
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        elif edge == 'right':
            self.rect.x = SCREEN_WIDTH + random.randint(5, 50)
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        
        # print(f"Enemy spawned at ({self.rect.x}, {self.rect.y}) with speed {self.speed}")


    def update(self, player_rect): # player_rect is the rect of the player
        # Calculate direction vector from enemy to player
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance > 0: # Avoid division by zero
            # Normalize vector
            dx /= distance
            dy /= distance
            # Move enemy
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
        # else:
            # print("Enemy is very close to player or on top.")


# Projectile Class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed_y = -7 # Moves upwards

    def update(self, *args): # Add *args to accept player_rect if passed by all_sprites.update()
        self.rect.y += self.speed_y
        if self.rect.bottom < 0: # If projectile goes off the top of the screen
            self.kill() # Remove from all sprite groups

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self): # Player does not need an update method for now, movement is explicit
        super().__init__()
        # Player represented by a blue 32x32 rectangle
        self.image = pygame.Surface([32, 32])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.selected_elements = collections.deque(maxlen=2)
        self.health = 100 # Player health

    def select_element(self, element_name):
        if element_name in ELEMENTS:
            self.selected_elements.append(element_name)
            print(f"Player selected elements: {list(self.selected_elements)}")
        else:
            print(f"Warning: Unknown element {element_name} selected by player.")

    def cast_spell(self, all_sprites_group, projectiles_group):
        spell_elements = list(self.selected_elements)
        projectile = None
        spell_cast = False

        if spell_elements == ["FIRE", "FIRE"]:
            print("Casting FIRE spell!")
            projectile = Projectile(self.rect.centerx, self.rect.top, RED)
            spell_cast = True
        elif spell_elements == ["WATER", "WATER"]:
            print("Casting WATER spell!")
            projectile = Projectile(self.rect.centerx, self.rect.top, BLUE)
            spell_cast = True
        elif spell_elements == ["AIR", "AIR"]:
            print("Casting AIR spell!")
            projectile = Projectile(self.rect.centerx, self.rect.top, WHITE)
            spell_cast = True
        else:
            if len(spell_elements) == 2: # Only fizzle if two elements were selected
                print(f"Spell fizzled with elements: {spell_elements}")

        if projectile:
            all_sprites_group.add(projectile)
            projectiles_group.add(projectile)
        
        if spell_cast or len(spell_elements) == 2 : # Clear elements if a spell was cast or if it fizzled with two elements
            self.selected_elements.clear()
            print("Player elements cleared.")


    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Project - Element Test")

# Create player instance
player = Player() # This is global now

# Sprite Groups - also global for reset_game access
all_sprites = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Function to reset the game
def reset_game():
    global game_state, game_start_time, time_survived, player
    
    print("Resetting game...")
    game_state = "playing"
    
    # Reset player
    player.health = 100
    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    player.selected_elements.clear()
    
    # Clear sprite groups
    all_sprites.empty()
    projectiles.empty()
    enemies.empty()
    
    # Re-add player to all_sprites
    all_sprites.add(player)
    
    # Reset timers
    game_start_time = pygame.time.get_ticks()
    time_survived = 0
    
    # Restart enemy spawn timer if it was stopped or to ensure it's fresh
    pygame.time.set_timer(ENEMY_SPAWN_EVENT, 0) # Clear existing timer
    pygame.time.set_timer(ENEMY_SPAWN_EVENT, 3000) # Set new timer

# Initialize first game
reset_game() # Call reset_game to initialize everything for the first playthrough

# Timer for enemy spawning is set in reset_game()

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.select_element("FIRE")
                elif event.key == pygame.K_2:
                    player.select_element("WATER")
                elif event.key == pygame.K_3:
                    player.select_element("AIR")
                elif event.key == pygame.K_SPACE:
                    player.cast_spell(all_sprites, projectiles)
                elif event.key == pygame.K_q: # Test quit
                    running = False
                    print("Test: Quit key 'q' pressed.")
            elif event.type == ENEMY_SPAWN_EVENT:
                new_enemy = Enemy()
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)
                # print(f"Enemy spawned. Total enemies: {len(enemies)}")
        
        elif game_state == "game_over":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()

    if game_state == "playing":
        # --- Handle Held Key Presses for Movement ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            player.move(1, 0)
        if keys[pygame.K_UP]:
            player.move(0, -1)
        if keys[pygame.K_DOWN]:
            player.move(0, 1)

        # --- Update Sprites ---
        all_sprites.update(player.rect)

        # --- Collision Detection ---
        # Projectile-Enemy collisions
        pygame.sprite.groupcollide(projectiles, enemies, True, True)
        # Optionally: Add score for destroyed enemies

        # Player-Enemy collisions
        collided_enemies_with_player = pygame.sprite.spritecollide(player, enemies, True)
        for _ in collided_enemies_with_player: # Use _ if enemy_hit not needed
            player.health -= 10
            print(f"Player hit by enemy! Health: {player.health}")
            if player.health <= 0:
                player.health = 0 # Ensure health doesn't go negative for display
                game_state = "game_over"
                time_survived = (pygame.time.get_ticks() - game_start_time) // 1000
                print(f"Game Over! Time Survived: {time_survived}s")
                # Stop enemy spawn timer when game is over
                pygame.time.set_timer(ENEMY_SPAWN_EVENT, 0) 
                break 
        
        # --- Drawing ---
        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        # --- UI Display (Health, Score, Selected Elements) ---
        # Health Display (Top-Left)
        if health_font:
            health_surface = health_font.render(f"Health: {player.health}", True, WHITE)
            screen.blit(health_surface, (10, 10))

        # Score/Time Display (Top-Center)
        if ui_font:
            current_time_survived = (pygame.time.get_ticks() - game_start_time) // 1000
            score_display_text = f"Time: {current_time_survived}s"
            score_surface = ui_font.render(score_display_text, True, WHITE)
            score_rect = score_surface.get_rect(centerx=SCREEN_WIDTH // 2, top=10)
            screen.blit(score_surface, score_rect)

        # Selected Elements Display (Top-Right)
        if ui_font:
            elements_list = list(player.selected_elements)
            # Display '[]' if empty, otherwise the list of elements
            elements_display_text = f"Elements: {elements_list if elements_list else '[]'}"
            elements_surface = ui_font.render(elements_display_text, True, WHITE)
            elements_rect = elements_surface.get_rect(right=SCREEN_WIDTH - 10, top=10)
            screen.blit(elements_surface, elements_rect)

    elif game_state == "game_over":
        screen.fill(GREY) # Dark grey background for game over
        
        game_over_text = game_over_font.render("Game Over", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, text_rect)
        
        score_text = info_font.render(f"Time Survived: {time_survived} seconds", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(score_text, score_rect)
        
        restart_text = info_font.render("Press 'R' to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60) # 60 FPS

# Quit Pygame
pygame.quit()
print("Pygame quit successfully.")
