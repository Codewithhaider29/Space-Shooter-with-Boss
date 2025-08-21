import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter with Boss")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
DARK_RED = (139, 0, 0)

# Create background with stars
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 1.5)
        
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            
    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

# Create stars for background
stars = [Star() for _ in range(100)]

# Load or create sounds
try:
    # Try to load sound files if available
    shoot_sound = pygame.mixer.Sound("shoot.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")
    powerup_sound = pygame.mixer.Sound("powerup.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")
    boss_spawn_sound = pygame.mixer.Sound("boss_spawn.wav")
    boss_hit_sound = pygame.mixer.Sound("boss_hit.wav")
    
    # Load background music
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
except:
    # Create placeholder sounds if files aren't available
    shoot_sound = pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1))))
    explosion_sound = pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1))))
    powerup_sound = pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1))))
    game_over_sound = pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1))))
    boss_spawn_sound = pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1))))
    boss_hit_sound = pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1))))
    
    print("Sound files not found. Using placeholder sounds.")

# Player settings
player_size = 50
player_pos = [WIDTH // 2, HEIGHT - 2 * player_size]
player_speed = 8
player_health = 100
player_max_health = 100
player_level = 1
player_bullet_power = 1

# Enemy settings
enemy_size = 40
enemy_list = []
enemy_spawn_timer = 0
enemy_spawn_delay = 30  # frames

# Boss settings
boss = None
boss_spawn_timer = 0
boss_spawn_delay = 1000  # frames (about 16 seconds at 60 FPS)
boss_health = 0
boss_max_health = 500
boss_size = 120

# Bullet settings
bullet_list = []
bullet_speed = 15
bullet_cooldown = 0
bullet_cooldown_max = 10  # frames

# Power-up settings
powerup_list = []
powerup_spawn_timer = 0
powerup_spawn_delay = 300  # frames

# Explosion effects
explosion_list = []

# Game variables
score = 0
level = 1
game_over = False
game_paused = False

# Fonts
font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 35)
font_small = pygame.font.SysFont("Arial", 24)
font_tiny = pygame.font.SysFont("Arial", 18)

# Clock
clock = pygame.time.Clock()

class Enemy:
    def __init__(self, x, y, enemy_type="normal"):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.speed = random.uniform(2.0, 5.0) * (1 + level * 0.1)
        self.size = enemy_size
        if enemy_type == "fast":
            self.speed *= 1.5
            self.size = int(enemy_size * 0.7)
            self.color = YELLOW
        elif enemy_type == "big":
            self.speed *= 0.7
            self.size = int(enemy_size * 1.5)
            self.color = PURPLE
        else:
            self.color = RED
            
    def update(self):
        self.y += self.speed
        return self.y > HEIGHT
        
    def draw(self):
        # Draw enemy as a triangular spaceship
        points = [
            (self.x + self.size//2, self.y),  # Nose
            (self.x, self.y + self.size),     # Bottom left
            (self.x + self.size, self.y + self.size)  # Bottom right
        ]
        pygame.draw.polygon(screen, self.color, points)
        
        # Add details to the enemy ship
        if self.type == "fast":
            # Engine glow for fast enemies
            pygame.draw.polygon(screen, ORANGE, [
                (self.x + self.size//4, self.y + self.size),
                (self.x + self.size//2, self.y + self.size + 5),
                (self.x + 3*self.size//4, self.y + self.size)
            ])
        elif self.type == "big":
            # Cockpit for big enemies
            pygame.draw.circle(screen, CYAN, (self.x + self.size//2, self.y + self.size//2), self.size//4)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class Boss:
    def __init__(self):
        self.x = WIDTH // 2 - boss_size // 2
        self.y = 50
        self.size = boss_size
        self.health = boss_max_health
        self.max_health = boss_max_health
        self.speed = 2
        self.direction = 1  # 1 for right, -1 for left
        self.attack_timer = 0
        self.attack_delay = 60  # frames
        self.bullets = []
        
    def update(self):
        # Move side to side
        self.x += self.speed * self.direction
        
        # Change direction if hitting screen edge
        if self.x <= 0 or self.x >= WIDTH - self.size:
            self.direction *= -1
            
        # Attack periodically
        self.attack_timer += 1
        if self.attack_timer >= self.attack_delay:
            self.attack()
            self.attack_timer = 0
            
        # Update boss bullets
        for bullet in self.bullets[:]:
            bullet['y'] += 5  # Boss bullets move downward
            if bullet['y'] > HEIGHT:
                self.bullets.remove(bullet)
                
        return self.health <= 0
        
    def attack(self):
        # Fire multiple bullets in a spread pattern
        for angle in range(-30, 31, 15):
            rad_angle = math.radians(angle)
            self.bullets.append({
                'x': self.x + self.size // 2,
                'y': self.y + self.size,
                'dx': math.sin(rad_angle) * 5,
                'dy': math.cos(rad_angle) * 5
            })
        
    def draw(self):
        # Draw boss as a large menacing ship
        # Main body
        pygame.draw.polygon(screen, DARK_RED, [
            (self.x + self.size//2, self.y),  # Nose
            (self.x, self.y + self.size),     # Bottom left
            (self.x + self.size, self.y + self.size)  # Bottom right
        ])
        
        # Details
        pygame.draw.circle(screen, RED, (self.x + self.size//2, self.y + self.size//3), self.size//5)
        pygame.draw.circle(screen, YELLOW, (self.x + self.size//2, self.y + self.size//3), self.size//10)
        
        # Engines
        for i in range(3):
            offset = (i - 1) * self.size//4
            pygame.draw.rect(screen, ORANGE, 
                           (self.x + self.size//2 + offset - 5, self.y + self.size, 10, 15))
        
        # Draw boss bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, RED, (int(bullet['x']), int(bullet['y'])), 8)
            
        # Draw boss health bar
        bar_width = 200
        pygame.draw.rect(screen, RED, (WIDTH//2 - bar_width//2, 20, bar_width, 20))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, (WIDTH//2 - bar_width//2, 20, health_width, 20))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - bar_width//2, 20, bar_width, 20), 2)
        
        # Boss health text
        health_text = font_small.render(f"BOSS: {self.health}/{self.max_health}", True, WHITE)
        screen.blit(health_text, (WIDTH//2 - health_text.get_width()//2, 45))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
        
    def get_bullet_rects(self):
        rects = []
        for bullet in self.bullets:
            rects.append(pygame.Rect(bullet['x'] - 4, bullet['y'] - 4, 8, 8))
        return rects

class Bullet:
    def __init__(self, x, y, bullet_type="normal"):
        self.x = x
        self.y = y
        self.type = bullet_type
        self.speed = bullet_speed
        self.size = (5, 15)
        self.power = player_bullet_power
        
        if bullet_type == "power":
            self.speed *= 1.2
            self.size = (8, 20)
            self.color = YELLOW
            self.power = player_bullet_power * 2
        else:
            self.color = GREEN
            
    def update(self):
        self.y -= self.speed
        return self.y < 0
        
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size[0], self.size[1]))
        # Add a glow effect
        pygame.draw.circle(screen, WHITE, (self.x + self.size[0]//2, self.y + self.size[1]), 3)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size[0], self.size[1])

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.type = random.choice(["health", "rapid", "power", "upgrade"])
        self.size = 30
        
        if self.type == "health":
            self.color = GREEN
        elif self.type == "rapid":
            self.color = BLUE
        elif self.type == "upgrade":
            self.color = PURPLE
        else:  # power
            self.color = YELLOW
            
    def update(self):
        self.y += self.speed
        return self.y > HEIGHT
        
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        # Draw letter indicating type
        text = font_small.render(self.type[0].upper(), True, WHITE)
        screen.blit(text, (self.x + self.size//2 - text.get_width()//2, 
                          self.y + self.size//2 - text.get_height()//2))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class Explosion:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.life = 20
        self.max_life = 20
        self.particles = []
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'life': random.randint(10, 20),
                'size': random.randint(2, 5),
                'color': (random.randint(200, 255), random.randint(100, 200), random.randint(0, 100))
            })
        
    def update(self):
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
        
        self.life -= 1
        return self.life <= 0
        
    def draw(self):
        for p in self.particles:
            if p['life'] > 0:
                alpha = min(255, p['life'] * 12)
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])

def draw_player():
    # Draw player as a triangular spaceship
    x, y = player_pos
    size = player_size
    
    # Main ship body
    points = [
        (x + size//2, y),              # Nose
        (x, y + size),                 # Bottom left
        (x + size, y + size)           # Bottom right
    ]
    
    # Change color based on player level
    if player_level == 1:
        color = BLUE
    elif player_level == 2:
        color = GREEN
    else:
        color = PURPLE
        
    pygame.draw.polygon(screen, color, points)
    
    # Cockpit
    pygame.draw.circle(screen, CYAN, (x + size//2, y + size//3), size//6)
    
    # Engine glow
    pygame.draw.polygon(screen, ORANGE, [
        (x + size//4, y + size),
        (x + size//2, y + size + 10),
        (x + 3*size//4, y + size)
    ])
    
    # Wings
    pygame.draw.polygon(screen, color, [
        (x, y + 2*size//3),
        (x - size//4, y + size),
        (x, y + size)
    ])
    pygame.draw.polygon(screen, color, [
        (x + size, y + 2*size//3),
        (x + size + size//4, y + size),
        (x + size, y + size)
    ])
    
    # Draw level indicator
    if player_level > 1:
        level_text = font_tiny.render(f"Lv.{player_level}", True, WHITE)
        screen.blit(level_text, (x + size//2 - level_text.get_width()//2, y + size + 5))

def spawn_enemy():
    enemy_type = "normal"
    rand = random.random()
    if rand < 0.1:  # 10% chance for big enemy
        enemy_type = "big"
    elif rand < 0.3:  # 20% chance for fast enemy
        enemy_type = "fast"
    
    x = random.randint(0, WIDTH - enemy_size)
    enemy_list.append(Enemy(x, 0, enemy_type))

def spawn_powerup():
    x = random.randint(0, WIDTH - 30)
    powerup_list.append(PowerUp(x, 0))

def spawn_boss():
    global boss
    boss = Boss()
    boss_spawn_sound.play()

def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

def show_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    text = font_large.render("GAME OVER", True, RED)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
    
    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 20))
    
    restart_text = font_small.render("Press R to restart or Q to quit", True, WHITE)
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))

def show_hud():
    # Score
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))
    
    # Level
    level_text = font_small.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (20, 50))
    
    # Player level
    player_level_text = font_small.render(f"Ship Level: {player_level}", True, WHITE)
    screen.blit(player_level_text, (20, 80))
    
    # Health bar
    pygame.draw.rect(screen, RED, (WIDTH - 220, 20, 200, 20))
    health_width = int(200 * (player_health / player_max_health))
    pygame.draw.rect(screen, GREEN, (WIDTH - 220, 20, health_width, 20))
    pygame.draw.rect(screen, WHITE, (WIDTH - 220, 20, 200, 20), 2)
    
    # Health text
    health_text = font_small.render(f"Health: {player_health}/{player_max_health}", True, WHITE)
    screen.blit(health_text, (WIDTH - 220, 45))
    
    # Bullet power
    power_text = font_small.render(f"Bullet Power: {player_bullet_power}", True, WHITE)
    screen.blit(power_text, (WIDTH - 220, 70))

def upgrade_player():
    global player_level, player_max_health, player_health, player_bullet_power
    
    player_level += 1
    player_max_health += 50
    player_health = player_max_health  # Fully heal when upgrading
    player_bullet_power += 1
    
    # Visual effect for upgrade
    for _ in range(20):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 5)
        explosion_list.append(Explosion(
            player_pos[0] + player_size//2, 
            player_pos[1] + player_size//2, 
            player_size
        ))

def reset_game():
    global enemy_list, bullet_list, powerup_list, explosion_list, boss
    global score, level, game_over, player_health, player_pos, bullet_cooldown
    global player_max_health, player_level, player_bullet_power, boss_spawn_timer
    
    enemy_list = []
    bullet_list = []
    powerup_list = []
    explosion_list = []
    boss = None
    
    score = 0
    level = 1
    game_over = False
    player_max_health = 100
    player_health = player_max_health
    player_level = 1
    player_bullet_power = 1
    player_pos = [WIDTH // 2, HEIGHT - 2 * player_size]
    bullet_cooldown = 0
    boss_spawn_timer = 0

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                game_paused = not game_paused
                if game_paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                    pygame.mixer.music.play(-1)
                elif event.key == pygame.K_q:
                    running = False
    
    if game_paused:
        # Display pause message
        pause_text = font_large.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
        pygame.display.update()
        continue
    
    # Draw background
    screen.fill(BLACK)
    
    # Update and draw stars
    for star in stars:
        star.update()
        star.draw()
    
    if not game_over:
        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_pos[0] > 0:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH - player_size:
            player_pos[0] += player_speed
            
        # Handle shooting
        if bullet_cooldown > 0:
            bullet_cooldown -= 1
            
        if keys[pygame.K_SPACE] and bullet_cooldown == 0:
            # Fire from the nose of the ship
            bullet_list.append(Bullet(player_pos[0] + player_size//2 - 2, player_pos[1]))
            
            # Higher level players can fire multiple bullets
            if player_level >= 2:
                bullet_list.append(Bullet(player_pos[0] + player_size//4 - 2, player_pos[1]))
                bullet_list.append(Bullet(player_pos[0] + 3*player_size//4 - 2, player_pos[1]))
                
            bullet_cooldown = bullet_cooldown_max
            shoot_sound.play()
        
        # Spawn enemies
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= enemy_spawn_delay:
            spawn_enemy()
            enemy_spawn_timer = 0
            
        # Spawn power-ups
        powerup_spawn_timer += 1
        if powerup_spawn_timer >= powerup_spawn_delay:
            spawn_powerup()
            powerup_spawn_timer = 0
            
        # Spawn boss
        if boss is None:
            boss_spawn_timer += 1
            if boss_spawn_timer >= boss_spawn_delay:
                spawn_boss()
                boss_spawn_timer = 0
            
        # Update enemies
        for enemy in enemy_list[:]:
            if enemy.update():
                enemy_list.remove(enemy)
                score += 1
            elif check_collision(enemy.get_rect(), pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)):
                enemy_list.remove(enemy)
                player_health -= 10
                explosion_list.append(Explosion(enemy.x + enemy.size//2, enemy.y + enemy.size//2, enemy.size))
                explosion_sound.play()
                if player_health <= 0:
                    game_over = True
                    game_over_sound.play()
                    pygame.mixer.music.stop()
        
        # Update bullets
        for bullet in bullet_list[:]:
            if bullet.update():
                bullet_list.remove(bullet)
            else:
                # Check for collisions with enemies
                for enemy in enemy_list[:]:
                    if check_collision(bullet.get_rect(), enemy.get_rect()):
                        if bullet in bullet_list:
                            bullet_list.remove(bullet)
                        enemy_list.remove(enemy)
                        score += 5
                        explosion_list.append(Explosion(enemy.x + enemy.size//2, enemy.y + enemy.size//2, enemy.size))
                        explosion_sound.play()
                        break
                
                # Check for collisions with boss
                if boss and check_collision(bullet.get_rect(), boss.get_rect()):
                    if bullet in bullet_list:
                        bullet_list.remove(bullet)
                    boss.health -= bullet.power
                    boss_hit_sound.play()
                    if boss.health <= 0:
                        score += 100
                        explosion_list.append(Explosion(boss.x + boss.size//2, boss.y + boss.size//2, boss.size*2))
                        explosion_sound.play()
                        boss = None
                        # Spawn power-ups when boss is defeated
                        for _ in range(3):
                            spawn_powerup()
        
        # Update boss
        if boss:
            if boss.update():  # Returns True if boss is defeated
                boss = None
            
            # Check for collision with player
            if check_collision(boss.get_rect(), pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)):
                player_health -= 30
                explosion_list.append(Explosion(player_pos[0] + player_size//2, player_pos[1] + player_size//2, player_size*2))
                explosion_sound.play()
                if player_health <= 0:
                    game_over = True
                    game_over_sound.play()
                    pygame.mixer.music.stop()
            
            # Check for collision with boss bullets
            for bullet_rect in boss.get_bullet_rects():
                if check_collision(bullet_rect, pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)):
                    player_health -= 15
                    explosion_list.append(Explosion(player_pos[0] + player_size//2, player_pos[1] + player_size//2, player_size))
                    explosion_sound.play()
                    if player_health <= 0:
                        game_over = True
                        game_over_sound.play()
                        pygame.mixer.music.stop()
        
        # Update power-ups
        for powerup in powerup_list[:]:
            if powerup.update():
                powerup_list.remove(powerup)
            elif check_collision(powerup.get_rect(), pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)):
                powerup_list.remove(powerup)
                powerup_sound.play()
                # Apply power-up effect
                if powerup.type == "health":
                    player_health = min(player_max_health, player_health + 30)
                elif powerup.type == "rapid":
                    bullet_cooldown_max = max(5, bullet_cooldown_max - 2)
                elif powerup.type == "power":
                    player_bullet_power += 1
                elif powerup.type == "upgrade":
                    upgrade_player()
        
        # Update explosions
        for explosion in explosion_list[:]:
            if explosion.update():
                explosion_list.remove(explosion)
        
        # Level up based on score
        level = score // 50 + 1
    
    # Draw player
    draw_player()
    
    # Draw enemies
    for enemy in enemy_list:
        enemy.draw()
    
    # Draw boss
    if boss:
        boss.draw()
    
    # Draw bullets
    for bullet in bullet_list:
        bullet.draw()
    
    # Draw power-ups
    for powerup in powerup_list:
        powerup.draw()
    
    # Draw explosions
    for explosion in explosion_list:
        explosion.draw()
    
    # Draw HUD
    show_hud()
    
    # Show game over screen if game is over
    if game_over:
        show_game_over()
    
    # Update display
    pygame.display.update()
    
    # Cap the frame rate
    clock.tick(60)

pygame.quit()