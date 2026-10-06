import sys
import random
import pygame

pygame.init()

WIDTH, HEIGHT = 960, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival Game")
clock = pygame.time.Clock()
font_big = pygame.font.SysFont(None, 64)
font_mid = pygame.font.SysFont(None, 36)

TILE = 40
MAP_W, MAP_H = 120, 120

GRASS = (34, 139, 34)
GRASS2 = (40, 150, 40)
TREE = (20, 90, 30)
WATER = (40, 90, 200)
PLAYER_COLOR = (255, 220, 100)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
BTN_COLOR = (70, 70, 70)
BTN_HOVER = (100, 100, 100)

TEXT = {
    "ru": {"play": "Играть", "settings": "Настройки", "exit": "Выход",
           "lang": "Язык: Русский", "back": "Назад", "title": "Survival Game"},
    "en": {"play": "Play", "settings": "Settings", "exit": "Exit",
           "lang": "Language: English", "back": "Back", "title": "Survival Game"},
}

state = {"screen": "menu", "lang": "ru"}


def gen_map():
    grid = [[0] * MAP_W for _ in range(MAP_H)]
    for y in range(MAP_H):
        for x in range(MAP_W):
            r = random.random()
            if r < 0.07:
                grid[y][x] = 1  # дерево
            elif r < 0.09:
                grid[y][x] = 2  # вода
    return grid


world = gen_map()

player = pygame.Rect(MAP_W * TILE // 2, MAP_H * TILE // 2, 28, 28)
speed = 4


def tile_blocked(tx, ty):
    if tx < 0 or ty < 0 or tx >= MAP_W or ty >= MAP_H:
        return True
    return world[ty][tx] in (1, 2)


def try_move(dx, dy):
    new_rect = player.move(dx, dy)
    corners = [
        (new_rect.left, new_rect.top),
        (new_rect.right, new_rect.top),
        (new_rect.left, new_rect.bottom),
        (new_rect.right, new_rect.bottom),
    ]
    for cx, cy in corners:
        if tile_blocked(cx // TILE, cy // TILE):
            return
    player.x = new_rect.x
    player.y = new_rect.y


def draw_world():
    cam_x = max(0, min(MAP_W * TILE - WIDTH, player.centerx - WIDTH // 2))
    cam_y = max(0, min(MAP_H * TILE - HEIGHT, player.centery - HEIGHT // 2))

    start_tx = cam_x // TILE
    start_ty = cam_y // TILE
    tiles_x = WIDTH // TILE + 2
    tiles_y = HEIGHT // TILE + 2

    for ty in range(start_ty, min(MAP_H, start_ty + tiles_y)):
        for tx in range(start_tx, min(MAP_W, start_tx + tiles_x)):
            px = tx * TILE - cam_x
            py = ty * TILE - cam_y
            t = world[ty][tx]
            color = GRASS if (tx + ty) % 2 == 0 else GRASS2
            if t == 1:
                color = TREE
            elif t == 2:
                color = WATER
            pygame.draw.rect(screen, color, (px, py, TILE, TILE))

    pygame.draw.rect(
        screen, PLAYER_COLOR,
        (player.x - cam_x, player.y - cam_y, player.width, player.height)
    )


def button(label, cx, cy, w=260, h=56):
    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, BTN_HOVER if hovered else BTN_COLOR, rect, border_radius=8)
    text = font_mid.render(label, True, WHITE)
    screen.blit(text, text.get_rect(center=rect.center))
    return rect, hovered


def draw_menu():
    screen.fill((25, 25, 25))
    t = TEXT[state["lang"]]
    title = font_big.render(t["title"], True, WHITE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 140)))

    play_rect, play_h = button(t["play"], WIDTH // 2, 280)
    settings_rect, settings_h = button(t["settings"], WIDTH // 2, 350)
    exit_rect, exit_h = button(t["exit"], WIDTH // 2, 420)

    return play_rect, settings_rect, exit_rect


def draw_settings():
    screen.fill((25, 25, 25))
    t = TEXT[state["lang"]]
    lang_rect, _ = button(t["lang"], WIDTH // 2, 280)
    back_rect, _ = button(t["back"], WIDTH // 2, 350)
    return lang_rect, back_rect


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state["screen"] == "playing":
                state["screen"] = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if state["screen"] == "menu":
                if play_rect.collidepoint(pos):
                    state["screen"] = "playing"
                elif settings_rect.collidepoint(pos):
                    state["screen"] = "settings"
                elif exit_rect.collidepoint(pos):
                    pygame.quit()
                    sys.exit()
            elif state["screen"] == "settings":
                if lang_rect.collidepoint(pos):
                    state["lang"] = "en" if state["lang"] == "ru" else "ru"
                elif back_rect.collidepoint(pos):
                    state["screen"] = "menu"

    if state["screen"] == "menu":
        play_rect, settings_rect, exit_rect = draw_menu()

    elif state["screen"] == "settings":
        lang_rect, back_rect = draw_settings()

    elif state["screen"] == "playing":
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = speed
        if dx:
            try_move(dx, 0)
        if dy:
            try_move(0, dy)

        draw_world()

    pygame.display.flip()
    clock.tick(60)
