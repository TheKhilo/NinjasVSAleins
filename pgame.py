import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1424, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Load images
player_img = pygame.image.load('player.png')
enemy_img = pygame.image.load('enemy.png')
enemy2_img = pygame.image.load('enemy2.png')
bullet_img = pygame.image.load('bullet.png')
enemy_bullet_img = pygame.image.load('enemy_bullet.png')
explosion_img = pygame.image.load('explosion.png')
background_img = pygame.transform.scale(pygame.image.load('background.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
powerup_img = pygame.image.load('powerup.png')

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.speed = 5
        self.health = 3
        self.powerup_active = False
        self.powerup_end_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        if self.powerup_active and pygame.time.get_ticks() > self.powerup_end_time:
            self.powerup_active = False
            self.speed = 5  # Reset to normal speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def activate_powerup(self):
        self.powerup_active = True
        self.speed = 10  # Increase speed
        self.powerup_end_time = pygame.time.get_ticks() + 5000  # Power-up lasts for 5 seconds

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, img):
        super().__init__()
        self.image = pygame.transform.scale(img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedy = speed
        self.shoot_delay = random.randint(3000, 7000)  # Increased shooting delay
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speedy = random.randint(1, 1)  # Further reduced speed
            global enemies_passed
            enemies_passed += 1

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

    def shoot(self):
        enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(bullet_img, (10, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Enemy Bullet class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(enemy_bullet_img, (10, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 3  # Further reduced bullet speed

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(powerup_img, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedy = 5  # Slightly fast

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.transform.scale(explosion_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(4):
    enemy = Enemy(random.randint(0, SCREEN_WIDTH - 50), random.randint(-100, -40), 1, enemy_img)
    all_sprites.add(enemy)
    enemies.add(enemy)

for i in range(4):
    enemy2 = Enemy(random.randint(0, SCREEN_WIDTH - 50), random.randint(-100, -40), 1, enemy2_img)
    all_sprites.add(enemy2)
    enemies.add(enemy2)

# Score
score = 0
top_scores = []
font = pygame.font.Font(None, 36)
enemies_passed = 0
last_powerup_time = 0
last_speed_increase_time = 0

def draw_health_bar():
    health_bar_length = 200
    health_bar_height = 25
    fill = (player.health / 3) * health_bar_length
    outline_rect = pygame.Rect(10, 50, health_bar_length, health_bar_height)
    fill_rect = pygame.Rect(10, 50, fill, health_bar_height)
    pygame.draw.rect(screen, GREEN, fill_rect)
    pygame.draw.rect(screen, WHITE, outline_rect, 2)

def game_over_screen():
    global top_scores
    top_scores.append(score)
    top_scores = sorted(top_scores, reverse=True)[:3]
    screen.fill(BLACK)
    game_over_text = font.render("GAME OVER", True, RED)
    retry_text = font.render("Press R to Retry or Q to Quit", True, WHITE)
    top_scores_text = font.render(f"Top Scores: {top_scores}", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
    screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + retry_text.get_height()))
    screen.blit(top_scores_text, (SCREEN_WIDTH // 2 - top_scores_text.get_width() // 2, SCREEN_HEIGHT // 2 + retry_text.get_height() * 3))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    main()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    global all_sprites, enemies, bullets, enemy_bullets, powerups, player, score, enemies_passed, last_powerup_time, last_speed_increase_time
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    for i in range(4):
        enemy = Enemy(random.randint(0, SCREEN_WIDTH - 50), random.randint(-100, -40), 1, enemy_img)
        all_sprites.add(enemy)
        enemies.add(enemy)

    for i in range(4):
        enemy2 = Enemy(random.randint(0, SCREEN_WIDTH - 50), random.randint(-100, -40), 1, enemy2_img)
        all_sprites.add(enemy2)
        enemies.add(enemy2)

    score = 0
    enemies_passed = 0
    last_powerup_time = pygame.time.get_ticks()
    last_speed_increase_time = pygame.time.get_ticks()

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        # Update
        all_sprites.update()

        # Check for collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10
            explosion = Explosion(hit.rect.center)
            all_sprites.add(explosion)
            enemy_type = random.choice([enemy_img, enemy2_img])
            enemy = Enemy(random.randint(0, SCREEN_WIDTH - 50), random.randint(-100, -40), 1, enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)

        if pygame.sprite.spritecollide(player, enemies, True) or pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.health -= 1
            if player.health <= 0:
                game_over_screen()
                running = False

        # Power-up collision
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup_hit in powerup_hits:
            player.activate_powerup()

        # Spawn power-up every 10 seconds
        if pygame.time.get_ticks() - last_powerup_time > 10000:
            last_powerup_time = pygame.time.get_ticks()
            powerup = PowerUp(random.randint(0, SCREEN_WIDTH - 30), -30)
            all_sprites.add(powerup)
            powerups.add(powerup)

        # Increase enemy speed every 20 seconds
        if pygame.time.get_ticks() - last_speed_increase_time > 20000:
            last_speed_increase_time = pygame.time.get_ticks()
            for enemy in enemies:
                enemy.speedy += 1

        if enemies_passed >= 5:
            game_over_screen()
            running = False

        # Draw
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)

        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw health bar
        draw_health_bar()

        # Refresh screen
        pygame.display.flip()
        clock.tick(FPS)

main()

