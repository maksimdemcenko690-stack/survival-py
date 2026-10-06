import sys
import pygame

pygame.init()

WIDTH, HEIGHT = 960, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival Game - Шаг 1")
clock = pygame.time.Clock()

GRASS_GREEN = (34, 139, 34)
PLAYER_COLOR = (255, 220, 100)

player_x, player_y = WIDTH // 2, HEIGHT // 2
player_size = 32
speed = 4

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_y += speed

    player_x = max(0, min(WIDTH - player_size, player_x))
    player_y = max(0, min(HEIGHT - player_size, player_y))

    screen.fill(GRASS_GREEN)
    pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, player_size, player_size))

    pygame.display.flip()
    clock.tick(60)
