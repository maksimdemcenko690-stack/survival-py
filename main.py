import sys
import random
import pygame

pygame.init()

WIDTH, HEIGHT = 960, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival Game")
clock = pygame.time.Clock()
font_big = pygame.font.SysFont(None, 64)
font_mid = pygame.font.SysFont(None, 32)
font_small = pygame.font.SysFont(None, 24)

TILE = 40
MAP_W, MAP_H = 120, 120

GRASS = (34, 139, 34)
GRASS2 = (40, 150, 40)
TREE_COLOR = (20, 90, 30)
TREE_TRUNK = (90, 60, 30)
WATER = (40, 90, 200)
SKIN = (235, 190, 150)
SHIRT = (60, 90, 200)
PANTS = (50, 50, 60)
RABBIT_COLOR = (170, 130, 90)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
PANEL_BG = (20, 20, 20)
BTN_COLOR = (70, 70, 70)
BTN_HOVER = (100, 100, 100)
BTN_DISABLED = (45, 45, 45)

TEXT = {
    "ru": {"play": "Играть", "settings": "Настройки", "exit": "Выход",
           "lang": "Язык: Русский", "back": "Назад", "title": "Survival Game",
           "inventory": "Инвентарь", "wood": "Дерево", "meat": "Мясо",
           "craft_axe": "Скрафтить топор (3 дерева)",
           "craft_sword": "Скрафтить меч (5 дерева)",
           "have_axe": "Топор: есть", "no_axe": "Топор: нет",
           "have_sword": "Меч: есть", "no_sword": "Меч: нет",
           "hint": "E - инвентарь, F - собрать/атаковать"},
    "en": {"play": "Play", "settings": "Settings", "exit": "Exit",
           "lang": "Language: English", "back": "Back", "title": "Survival Game",
           "inventory": "Inventory", "wood": "Wood", "meat": "Meat",
           "craft_axe": "Craft Axe (3 wood)",
           "craft_sword": "Craft Sword (5 wood)",
           "have_axe": "Axe: owned", "no_axe": "Axe: none",
           "have_sword": "Sword: owned", "no_sword": "Sword: none",
           "hint": "E - inventory, F - gather/attack"},
}

state = {"screen": "menu", "lang": "ru", "inventory_open": False}

inventory = {"wood": 0, "meat": 0}
tools = {"axe": False, "sword": False}


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

player = pygame.Rect(MAP_W * TILE // 2, MAP_H * TILE // 2, 24, 34)
speed = 4
facing = "down"

animals = []
for _ in range(25):
    ax = random.randint(5, MAP_W - 5) * TILE
    ay = random.randint(5, MAP_H - 5) * TILE
    animals.append({"rect": pygame.Rect(ax, ay, 24, 20), "dx": 0, "dy": 0, "timer": 0})


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


def nearest_tree_tile():
    pcx, pcy = player.centerx, player.centery
    best = None
    best_d = 999999
    ptx, pty = pcx // TILE, pcy // TILE
    for ty in range(pty - 1, pty + 2):
        for tx in range(ptx - 1, ptx + 2):
            if 0 <= tx < MAP_W and 0 <= ty < MAP_H and world[ty][tx] == 1:
                cx = tx * TILE + TILE // 2
                cy = ty * TILE + TILE // 2
                d = (cx - pcx) ** 2 + (cy - pcy) ** 2
                if d < best_d:
                    best_d = d
                    best = (tx, ty)
    if best and best_d <= (TILE * 1.4) ** 2:
        return best
    return None


def nearest_animal():
    best = None
    best_d = 999999
    for a in animals:
        d = (a["rect"].centerx - player.centerx) ** 2 + (a["rect"].centery - player.centery) ** 2
        if d < best_d:
            best_d = d
            best = a
    if best and best_d <= (TILE * 1.4) ** 2:
        return best
    return None


def do_interact():
    tree = nearest_tree_tile()
    if tree:
        tx, ty = tree
        world[ty][tx] = 0
        inventory["wood"] += 2 if tools["axe"] else 1
        return
    if tools["sword"]:
        a = nearest_animal()
        if a:
            animals.remove(a)
            inventory["meat"] += 1


def update_animals():
    for a in animals:
        a["timer"] -= 1
        if a["timer"] <= 0:
            a["timer"] = random.randint(30, 90)
            choice = random.choice([(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)])
            a["dx"], a["dy"] = choice[0] * 1.2, choice[1] * 1.2
        nr = a["rect"].move(a["dx"], a["dy"])
        tx, ty = nr.centerx // TILE, nr.centery // TILE
        if not tile_blocked(tx, ty):
            a["rect"] = nr


def draw_player(cam_x, cam_y):
    px = player.x - cam_x
    py = player.y - cam_y
    # ноги
    pygame.draw.rect(screen, PANTS, (px + 4, py + 20, 6, 14))
    pygame.draw.rect(screen, PANTS, (px + 14, py + 20, 6, 14))
    # тело
    pygame.draw.rect(screen, SHIRT, (px + 2, py + 8, 20, 16), border_radius=4)
    # руки
    pygame.draw.rect(screen, SKIN, (px - 2, py + 10, 5, 12))
    pygame.draw.rect(screen, SKIN, (px + 21, py + 10, 5, 12))
    # голова
    pygame.draw.circle(screen, SKIN, (px + 12, py + 6), 8)


def draw_animal(a, cam_x, cam_y):
    r = a["rect"]
    ax = r.x - cam_x
    ay = r.y - cam_y
    pygame.draw.ellipse(screen, RABBIT_COLOR, (ax, ay + 6, 24, 14))
    pygame.draw.circle(screen, RABBIT_COLOR, (ax + 20, ay + 6), 7)
    pygame.draw.rect(screen, RABBIT_COLOR, (ax + 22, ay - 4, 3, 10))


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
            if t == 2:
                color = WATER
            pygame.draw.rect(screen, color, (px, py, TILE, TILE))
            if t == 1:
                pygame.draw.rect(screen, TREE_TRUNK, (px + 16, py + 22, 8, 16))
                pygame.draw.circle(screen, TREE_COLOR, (px + 20, py + 16), 16)

    for a in animals:
        draw_animal(a, cam_x, cam_y)

    draw_player(cam_x, cam_y)

    t = TEXT[state["lang"]]
    hint = font_small.render(t["hint"], True, WHITE)
    screen.blit(hint, (10, HEIGHT - 28))


def button(label, cx, cy, w=280, h=50, enabled=True):
    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    if not enabled:
        color = BTN_DISABLED
    else:
        color = BTN_HOVER if hovered else BTN_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=8)
    text = font_small.render(label, True, WHITE if enabled else (120, 120, 120))
    screen.blit(text, text.get_rect(center=rect.center))
    return rect


def draw_menu():
    screen.fill((25, 25, 25))
    t = TEXT[state["lang"]]
    title = font_big.render(t["title"], True, WHITE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 140)))
    play_rect = button(t["play"], WIDTH // 2, 280)
    settings_rect = button(t["settings"], WIDTH // 2, 350)
    exit_rect = button(t["exit"], WIDTH // 2, 420)
    return play_rect, settings_rect, exit_rect


def draw_settings():
    screen.fill((25, 25, 25))
    t = TEXT[state["lang"]]
    lang_rect = button(t["lang"], WIDTH // 2, 280)
    back_rect = button(t["back"], WIDTH // 2, 350)
    return lang_rect, back_rect


def draw_inventory_panel():
    t = TEXT[state["lang"]]
    panel_w = 260
    panel = pygame.Rect(WIDTH - panel_w, 0, panel_w, HEIGHT)
    pygame.draw.rect(screen, PANEL_BG, panel)
    pygame.draw.line(screen, GRAY, (panel.left, 0), (panel.left, HEIGHT), 2)

    title = font_mid.render(t["inventory"], True, WHITE)
    screen.blit(title, (panel.left + 20, 20))

    wood_text = font_small.render(f"{t['wood']}: {inventory['wood']}", True, WHITE)
    screen.blit(wood_text, (panel.left + 20, 70))
    meat_text = font_small.render(f"{t['meat']}: {inventory['meat']}", True, WHITE)
    screen.blit(meat_text, (panel.left + 20, 100))

    axe_text = font_small.render(t["have_axe"] if tools["axe"] else t["no_axe"], True, WHITE)
    screen.blit(axe_text, (panel.left + 20, 140))
    sword_text = font_small.render(t["have_sword"] if tools["sword"] else t["no_sword"], True, WHITE)
    screen.blit(sword_text, (panel.left + 20, 165))

    axe_enabled = (not tools["axe"]) and inventory["wood"] >= 3
    sword_enabled = (not tools["sword"]) and inventory["wood"] >= 5

    axe_btn = button(t["craft_axe"], panel.centerx, 230, w=220, h=50, enabled=axe_enabled)
    sword_btn = button(t["craft_sword"], panel.centerx, 300, w=220, h=50, enabled=sword_enabled)

    return axe_btn, sword_btn, axe_enabled, sword_enabled


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state["screen"] == "playing":
                    if state["inventory_open"]:
                        state["inventory_open"] = False
                    else:
                        state["screen"] = "menu"
            if event.key == pygame.K_e and state["screen"] == "playing":
                state["inventory_open"] = not state["inventory_open"]
            if event.key == pygame.K_f and state["screen"] == "playing" and not state["inventory_open"]:
                do_interact()

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
            elif state["screen"] == "playing" and state["inventory_open"]:
                if axe_btn.collidepoint(pos) and axe_enabled:
                    inventory["wood"] -= 3
                    tools["axe"] = True
                elif sword_btn.collidepoint(pos) and sword_enabled:
                    inventory["wood"] -= 5
                    tools["sword"] = True

    if state["screen"] == "menu":
        play_rect, settings_rect, exit_rect = draw_menu()

    elif state["screen"] == "settings":
        lang_rect, back_rect = draw_settings()

    elif state["screen"] == "playing":
        if not state["inventory_open"]:
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
            update_animals()

        draw_world()

        if state["inventory_open"]:
            axe_btn, sword_btn, axe_enabled, sword_enabled = draw_inventory_panel()

    pygame.display.flip()
    clock.tick(60)
