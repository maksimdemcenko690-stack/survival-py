import sys
import math
import random
import traceback
import pygame


def run_game():
    pygame.init()

    WIDTH, HEIGHT = 960, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Survival Game")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont(None, 64)
    font_mid = pygame.font.SysFont(None, 32)
    font_small = pygame.font.SysFont(None, 22)

    TILE = 40

    # ---------- Overworld ----------
    OVER_W, OVER_H = 120, 120
    GRASS = (34, 139, 34)
    GRASS2 = (40, 150, 40)
    TREE_COLOR = (20, 90, 30)
    TREE_TRUNK = (90, 60, 30)
    WATER = (40, 90, 200)
    CAVE_HOLE = (15, 15, 15)

    def gen_overworld():
        grid = [[0] * OVER_W for _ in range(OVER_H)]
        for y in range(OVER_H):
            for x in range(OVER_W):
                r = random.random()
                if r < 0.07:
                    grid[y][x] = 1  # дерево
                elif r < 0.09:
                    grid[y][x] = 2  # вода
        return grid

    over_grid = gen_overworld()

    spawn_tx, spawn_ty = OVER_W // 2, OVER_H // 2
    # расчистим зону спавна от деревьев/воды
    for y in range(spawn_ty - 3, spawn_ty + 4):
        for x in range(spawn_tx - 3, spawn_tx + 4):
            if 0 <= x < OVER_W and 0 <= y < OVER_H:
                over_grid[y][x] = 0

    entrance_tx, entrance_ty = spawn_tx + 10, spawn_ty + 6
    over_grid[entrance_ty][entrance_tx] = 3  # вход в пещеру
    for y in range(entrance_ty - 1, entrance_ty + 2):
        for x in range(entrance_tx - 1, entrance_tx + 2):
            if 0 <= x < OVER_W and 0 <= y < OVER_H and over_grid[y][x] != 3:
                over_grid[y][x] = 0

    furnace_tx, furnace_ty = spawn_tx + 2, spawn_ty - 2

    # ---------- Cave ----------
    CAVE_W, CAVE_H = 50, 50
    FLOOR = (70, 70, 75)
    WALL = (35, 35, 38)
    STONE_ORE = (120, 120, 120)
    IRON_ORE = (190, 130, 90)
    COAL_ORE = (25, 25, 25)

    def gen_cave():
        grid = [[0] * CAVE_W for _ in range(CAVE_H)]
        for y in range(CAVE_H):
            for x in range(CAVE_W):
                if x == 0 or y == 0 or x == CAVE_W - 1 or y == CAVE_H - 1:
                    grid[y][x] = 1  # стена
                else:
                    r = random.random()
                    if r < 0.10:
                        grid[y][x] = 2  # камень
                    elif r < 0.14:
                        grid[y][x] = 4  # уголь
                    elif r < 0.17:
                        grid[y][x] = 3  # железо
        return grid

    cave_grid = gen_cave()
    cave_spawn_tx, cave_spawn_ty = CAVE_W // 2, CAVE_H // 2
    for y in range(cave_spawn_ty - 2, cave_spawn_ty + 3):
        for x in range(cave_spawn_tx - 2, cave_spawn_tx + 3):
            if 0 <= x < CAVE_W and 0 <= y < CAVE_H:
                cave_grid[y][x] = 0
    cave_exit_tx, cave_exit_ty = cave_spawn_tx, cave_spawn_ty
    cave_grid[cave_exit_ty][cave_exit_tx] = 5  # выход

    # ---------- Персонаж ----------
    SKIN = (235, 190, 150)
    SHIRT = (60, 90, 200)
    PANTS = (50, 50, 60)
    ARMOR_COLOR = (150, 150, 160)

    player = pygame.Rect(spawn_tx * TILE, spawn_ty * TILE, 24, 34)
    speed = 4
    facing = "down"

    RABBIT_COLOR = (170, 130, 90)
    animals = []
    for _ in range(25):
        ax = random.randint(5, OVER_W - 5) * TILE
        ay = random.randint(5, OVER_H - 5) * TILE
        animals.append({"rect": pygame.Rect(ax, ay, 24, 20), "dx": 0, "dy": 0, "timer": 0})

    WHITE = (255, 255, 255)
    RED = (200, 50, 50)
    GREEN = (60, 180, 60)
    ORANGE = (230, 160, 40)
    GRAY = (60, 60, 60)
    PANEL_BG = (20, 20, 20)
    BTN_COLOR = (70, 70, 70)
    BTN_HOVER = (100, 100, 100)
    BTN_DISABLED = (45, 45, 45)
    TORCH_GLOW = (255, 200, 80)

    TEXT = {
        "ru": {
            "play": "Играть", "settings": "Настройки", "exit": "Выход",
            "lang": "Язык: Русский", "back": "Назад", "title": "Survival Game",
            "inventory": "Инвентарь", "wood": "Дерево", "meat": "Мясо",
            "stone": "Камень", "coal": "Уголь", "iron_ore": "Жел. руда",
            "iron": "Железо (плавл.)", "torch": "Факелы",
            "craft_wood_axe": "Топор (3 дерева)",
            "craft_wood_sword": "Меч (5 дерева)",
            "craft_wood_pick": "Кирка (3 дерева)",
            "craft_stone_axe": "Кам. топор (3 камня)",
            "craft_stone_sword": "Кам. меч (5 камня)",
            "craft_stone_pick": "Кам. кирка (3 камня)",
            "craft_torch": "Факел (1 дер.+1 угля = 2шт)",
            "craft_armor": "Броня (30 железа)",
            "eat_meat": "Съесть мясо (+25 голода)",
            "smelt": "Переплавить руду (F у печки)",
            "have": "есть", "no": "нет",
            "hint": "E - инвентарь, F - собрать/атаковать, T - факел",
            "hunger": "Голод", "health": "Здоровье",
            "need_pick": "Нужна кирка!", "need_stone_pick": "Нужна каменная кирка!",
            "cave_hint": "Зайди в дыру, чтобы попасть в пещеру",
            "furnace_hint": "Печка: нужна руда и уголь",
        },
        "en": {
            "play": "Play", "settings": "Settings", "exit": "Exit",
            "lang": "Language: English", "back": "Back", "title": "Survival Game",
            "inventory": "Inventory", "wood": "Wood", "meat": "Meat",
            "stone": "Stone", "coal": "Coal", "iron_ore": "Iron ore",
            "iron": "Iron (smelted)", "torch": "Torches",
            "craft_wood_axe": "Axe (3 wood)",
            "craft_wood_sword": "Sword (5 wood)",
            "craft_wood_pick": "Pickaxe (3 wood)",
            "craft_stone_axe": "Stone axe (3 stone)",
            "craft_stone_sword": "Stone sword (5 stone)",
            "craft_stone_pick": "Stone pickaxe (3 stone)",
            "craft_torch": "Torch (1 wood+1 coal = x2)",
            "craft_armor": "Armor (30 iron)",
            "eat_meat": "Eat meat (+25 hunger)",
            "smelt": "Smelt ore (F near furnace)",
            "have": "owned", "no": "none",
            "hint": "E - inventory, F - gather/attack, T - torch",
            "hunger": "Hunger", "health": "Health",
            "need_pick": "Need a pickaxe!", "need_stone_pick": "Need a stone pickaxe!",
            "cave_hint": "Walk into the hole to enter the cave",
            "furnace_hint": "Furnace: needs ore and coal",
        },
    }

    state = {"screen": "menu", "lang": "ru", "inventory_open": False, "map": "over"}

    inventory = {"wood": 0, "meat": 0, "stone": 0, "coal": 0, "iron_ore": 0, "iron": 0, "torch": 0}
    tools = {"wood_axe": False, "wood_sword": False, "wood_pick": False,
             "stone_axe": False, "stone_sword": False, "stone_pick": False,
             "armor": False}

    over_torches = set()
    cave_torches = set()

    player_hp = 100.0
    player_hunger = 100.0
    hp_timer = 0.0

    HUNGER_DRAIN_PER_SEC = 100.0 / 120.0

    action = {"active": False, "kind": None, "timer": 0.0, "duration": 1.5}
    message = {"text": "", "timer": 0.0}

    day_timer = 0.0
    CYCLE_SECONDS = 240.0

    def show_message(text):
        message["text"] = text
        message["timer"] = 2.0

    def current_grid():
        return over_grid if state["map"] == "over" else cave_grid

    def current_w_h():
        return (OVER_W, OVER_H) if state["map"] == "over" else (CAVE_W, CAVE_H)

    def blocking_set():
        if state["map"] == "over":
            return (1, 2)  # дерево, вода
        return (1,)  # стена

    def tile_blocked(tx, ty):
        w, h = current_w_h()
        if tx < 0 or ty < 0 or tx >= w or ty >= h:
            return True
        return current_grid()[ty][tx] in blocking_set()

    def try_move(dx, dy):
        new_rect = player.move(dx, dy)
        corners = [
            (new_rect.left, new_rect.top),
            (new_rect.right - 1, new_rect.top),
            (new_rect.left, new_rect.bottom - 1),
            (new_rect.right - 1, new_rect.bottom - 1),
        ]
        for cx, cy in corners:
            if tile_blocked(cx // TILE, cy // TILE):
                return
        player.x = new_rect.x
        player.y = new_rect.y

    def nearest_tile_of(types):
        grid = current_grid()
        w, h = current_w_h()
        pcx, pcy = player.centerx, player.centery
        ptx, pty = pcx // TILE, pcy // TILE
        best = None
        best_d = 999999
        for ty in range(pty - 1, pty + 2):
            for tx in range(ptx - 1, ptx + 2):
                if 0 <= tx < w and 0 <= ty < h and grid[ty][tx] in types:
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

    def near_furnace():
        fx = furnace_tx * TILE + TILE // 2
        fy = furnace_ty * TILE + TILE // 2
        d = (fx - player.centerx) ** 2 + (fy - player.centery) ** 2
        return d <= (TILE * 1.6) ** 2

    def start_action(kind, duration):
        action["active"] = True
        action["kind"] = kind
        action["timer"] = 0.0
        action["duration"] = duration

    def finish_action():
        kind = action["kind"]
        if kind == "wood":
            tile = nearest_tile_of((1,))
            if tile:
                over_grid[tile[1]][tile[0]] = 0
                inventory["wood"] += 2 if tools["wood_axe"] or tools["stone_axe"] else 1
        elif kind == "stone":
            tile = nearest_tile_of((2,))
            if tile:
                cave_grid[tile[1]][tile[0]] = 0
                inventory["stone"] += 1
        elif kind == "coal":
            tile = nearest_tile_of((4,))
            if tile:
                cave_grid[tile[1]][tile[0]] = 0
                inventory["coal"] += 1
        elif kind == "iron":
            tile = nearest_tile_of((3,))
            if tile:
                cave_grid[tile[1]][tile[0]] = 0
                inventory["iron_ore"] += 1
        elif kind == "smelt":
            if inventory["iron_ore"] > 0 and inventory["coal"] > 0:
                inventory["iron_ore"] -= 1
                inventory["coal"] -= 1
                inventory["iron"] += 1
        action["active"] = False
        action["kind"] = None

    def do_interact():
        t = TEXT[state["lang"]]
        if state["map"] == "over":
            tree = nearest_tile_of((1,))
            if tree:
                start_action("wood", 1.5)
                return
            if near_furnace():
                if inventory["iron_ore"] > 0 and inventory["coal"] > 0:
                    start_action("smelt", 2.0)
                else:
                    show_message(t["furnace_hint"])
                return
            if tools["wood_sword"] or tools["stone_sword"]:
                a = nearest_animal()
                if a:
                    animals.remove(a)
                    inventory["meat"] += 1
                    return
        else:
            stone = nearest_tile_of((2,))
            coal = nearest_tile_of((4,))
            iron = nearest_tile_of((3,))
            if stone or coal:
                if not (tools["wood_pick"] or tools["stone_pick"]):
                    show_message(t["need_pick"])
                    return
                start_action("stone" if stone else "coal", 1.5)
                return
            if iron:
                if not tools["stone_pick"]:
                    show_message(t["need_stone_pick"])
                    return
                start_action("iron", 1.5)
                return

    def facing_tile():
        ptx, pty = player.centerx // TILE, player.centery // TILE
        if facing == "up":
            return ptx, pty - 1
        if facing == "down":
            return ptx, pty + 1
        if facing == "left":
            return ptx - 1, pty
        return ptx + 1, pty

    def place_torch():
        if inventory["torch"] <= 0:
            return
        tile = facing_tile()
        inventory["torch"] -= 1
        if state["map"] == "over":
            over_torches.add(tile)
        else:
            cave_torches.add(tile)

    def check_teleport():
        ptx, pty = player.centerx // TILE, player.centery // TILE
        if state["map"] == "over":
            if 0 <= ptx < OVER_W and 0 <= pty < OVER_H and over_grid[pty][ptx] == 3:
                state["map"] = "cave"
                player.x = (cave_spawn_tx - 1) * TILE
                player.y = (cave_spawn_ty + 2) * TILE
        else:
            if 0 <= ptx < CAVE_W and 0 <= pty < CAVE_H and cave_grid[pty][ptx] == 5:
                state["map"] = "over"
                player.x = (entrance_tx + 1) * TILE
                player.y = (entrance_ty + 1) * TILE

    def update_animals(dt):
        for a in animals:
            a["timer"] -= dt
            if a["timer"] <= 0:
                a["timer"] = random.uniform(1.0, 2.5)
                choice = random.choice([(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)])
                a["dx"], a["dy"] = choice[0] * 1.2, choice[1] * 1.2
            nr = a["rect"].move(a["dx"], a["dy"])
            tx, ty = nr.centerx // TILE, nr.centery // TILE
            if 0 <= tx < OVER_W and 0 <= ty < OVER_H and over_grid[ty][tx] not in (1, 2):
                a["rect"] = nr

    def draw_player(cam_x, cam_y):
        px = player.x - cam_x
        py = player.y - cam_y
        pygame.draw.rect(screen, PANTS, (px + 4, py + 20, 6, 14))
        pygame.draw.rect(screen, PANTS, (px + 14, py + 20, 6, 14))
        body_color = ARMOR_COLOR if tools["armor"] else SHIRT
        pygame.draw.rect(screen, body_color, (px + 2, py + 8, 20, 16), border_radius=4)
        pygame.draw.rect(screen, SKIN, (px - 2, py + 10, 5, 12))
        pygame.draw.rect(screen, SKIN, (px + 21, py + 10, 5, 12))
        pygame.draw.circle(screen, SKIN, (px + 12, py + 6), 8)

    def draw_animal(a, cam_x, cam_y):
        r = a["rect"]
        ax = r.x - cam_x
        ay = r.y - cam_y
        pygame.draw.ellipse(screen, RABBIT_COLOR, (ax, ay + 6, 24, 14))
        pygame.draw.circle(screen, RABBIT_COLOR, (ax + 20, ay + 6), 7)
        pygame.draw.rect(screen, RABBIT_COLOR, (ax + 22, ay - 4, 3, 10))

    def draw_progress_bar(cam_x, cam_y):
        if not action["active"]:
            return
        ratio = min(1.0, action["timer"] / action["duration"])
        bar_w = 40
        bx = player.centerx - cam_x - bar_w // 2
        by = player.y - cam_y - 16
        pygame.draw.rect(screen, (30, 30, 30), (bx, by, bar_w, 8))
        pygame.draw.rect(screen, GREEN, (bx, by, int(bar_w * ratio), 8))

    def draw_torch(tx, ty, cam_x, cam_y):
        px = tx * TILE + TILE // 2 - cam_x
        py = ty * TILE + TILE // 2 - cam_y
        pygame.draw.rect(screen, (90, 60, 30), (px - 2, py - 4, 4, 14))
        pygame.draw.circle(screen, TORCH_GLOW, (px, py - 8), 5)

    def draw_world():
        grid = current_grid()
        w, h = current_w_h()
        cam_x = max(0, min(w * TILE - WIDTH, player.centerx - WIDTH // 2))
        cam_y = max(0, min(h * TILE - HEIGHT, player.centery - HEIGHT // 2))

        start_tx = cam_x // TILE
        start_ty = cam_y // TILE
        tiles_x = WIDTH // TILE + 2
        tiles_y = HEIGHT // TILE + 2

        for ty in range(start_ty, min(h, start_ty + tiles_y)):
            for tx in range(start_tx, min(w, start_tx + tiles_x)):
                px = tx * TILE - cam_x
                py = ty * TILE - cam_y
                t = grid[ty][tx]
                if state["map"] == "over":
                    color = GRASS if (tx + ty) % 2 == 0 else GRASS2
                    if t == 2:
                        color = WATER
                    elif t == 3:
                        color = CAVE_HOLE
                    pygame.draw.rect(screen, color, (px, py, TILE, TILE))
                    if t == 1:
                        pygame.draw.rect(screen, TREE_TRUNK, (px + 16, py + 22, 8, 16))
                        pygame.draw.circle(screen, TREE_COLOR, (px + 20, py + 16), 16)
                    elif t == 3:
                        pygame.draw.circle(screen, (5, 5, 5), (px + 20, py + 20), 16)
                else:
                    color = FLOOR
                    if t == 1:
                        color = WALL
                    pygame.draw.rect(screen, color, (px, py, TILE, TILE))
                    if t == 2:
                        pygame.draw.circle(screen, STONE_ORE, (px + 20, py + 20), 12)
                    elif t == 3:
                        pygame.draw.circle(screen, IRON_ORE, (px + 20, py + 20), 12)
                    elif t == 4:
                        pygame.draw.circle(screen, COAL_ORE, (px + 20, py + 20), 12)
                    elif t == 5:
                        pygame.draw.rect(screen, (230, 220, 150), (px + 6, py + 6, 28, 28))

        if state["map"] == "over":
            fx = furnace_tx * TILE - cam_x
            fy = furnace_ty * TILE - cam_y
            pygame.draw.rect(screen, (90, 90, 90), (fx + 4, fy + 4, 32, 32))
            pygame.draw.rect(screen, (230, 100, 40), (fx + 12, fy + 16, 16, 12))

            for a in animals:
                draw_animal(a, cam_x, cam_y)
            for tt in over_torches:
                draw_torch(tt[0], tt[1], cam_x, cam_y)
        else:
            for tt in cave_torches:
                draw_torch(tt[0], tt[1], cam_x, cam_y)

        draw_player(cam_x, cam_y)
        draw_progress_bar(cam_x, cam_y)

        phase = (day_timer % CYCLE_SECONDS) / CYCLE_SECONDS
        darkness_alpha = int(150 * (0.5 + 0.5 * math.sin(2 * math.pi * (phase - 0.25))))
        if state["map"] == "cave":
            darkness_alpha = max(darkness_alpha, 140)
        if darkness_alpha > 0:
            dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, darkness_alpha))
            light_positions = [(player.centerx - cam_x, player.centery - cam_y)]
            torch_set = over_torches if state["map"] == "over" else cave_torches
            for tt in torch_set:
                lx = tt[0] * TILE + TILE // 2 - cam_x
                ly = tt[1] * TILE + TILE // 2 - cam_y
                light_positions.append((lx, ly))
            for lx, ly in light_positions:
                pygame.draw.circle(dark, (0, 0, 0, 0), (lx, ly), 110)
            screen.blit(dark, (0, 0))

        t = TEXT[state["lang"]]
        hint = font_small.render(t["hint"], True, WHITE)
        screen.blit(hint, (10, HEIGHT - 26))
        if state["map"] == "over":
            cave_hint = font_small.render(t["cave_hint"], True, WHITE)
            screen.blit(cave_hint, (10, HEIGHT - 50))

        if message["timer"] > 0:
            msg_surf = font_mid.render(message["text"], True, (255, 90, 90))
            screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH // 2, 80)))

        bar_w, bar_h = 200, 18
        hp_ratio = max(0, player_hp) / 100.0
        hunger_ratio = max(0, player_hunger) / 100.0
        pygame.draw.rect(screen, (40, 40, 40), (10, 10, bar_w, bar_h))
        pygame.draw.rect(screen, RED, (10, 10, int(bar_w * hp_ratio), bar_h))
        hp_label = font_small.render(f"{t['health']}", True, WHITE)
        screen.blit(hp_label, (10, 30))

        pygame.draw.rect(screen, (40, 40, 40), (10, 54, bar_w, bar_h))
        pygame.draw.rect(screen, ORANGE, (10, 54, int(bar_w * hunger_ratio), bar_h))
        hunger_label = font_small.render(f"{t['hunger']}", True, WHITE)
        screen.blit(hunger_label, (10, 74))

    def button(label, cx, cy, w=280, h=46, enabled=True):
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
        panel_w = 300
        panel = pygame.Rect(WIDTH - panel_w, 0, panel_w, HEIGHT)
        pygame.draw.rect(screen, PANEL_BG, panel)
        pygame.draw.line(screen, GRAY, (panel.left, 0), (panel.left, HEIGHT), 2)

        y = 16
        title = font_mid.render(t["inventory"], True, WHITE)
        screen.blit(title, (panel.left + 16, y))
        y += 40

        res_lines = [
            f"{t['wood']}: {inventory['wood']}",
            f"{t['meat']}: {inventory['meat']}",
            f"{t['stone']}: {inventory['stone']}",
            f"{t['coal']}: {inventory['coal']}",
            f"{t['iron_ore']}: {inventory['iron_ore']}",
            f"{t['iron']}: {inventory['iron']}",
            f"{t['torch']}: {inventory['torch']}",
        ]
        for line in res_lines:
            surf = font_small.render(line, True, WHITE)
            screen.blit(surf, (panel.left + 16, y))
            y += 22

        y += 6
        tool_lines = [
            ("wood_axe", "Топор" if state["lang"] == "ru" else "Axe"),
            ("wood_sword", "Меч" if state["lang"] == "ru" else "Sword"),
            ("wood_pick", "Кирка" if state["lang"] == "ru" else "Pickaxe"),
            ("stone_axe", "Кам.топор" if state["lang"] == "ru" else "St.axe"),
            ("stone_sword", "Кам.меч" if state["lang"] == "ru" else "St.sword"),
            ("stone_pick", "Кам.кирка" if state["lang"] == "ru" else "St.pick"),
            ("armor", "Броня" if state["lang"] == "ru" else "Armor"),
        ]
        for key, label in tool_lines:
            status = t["have"] if tools[key] else t["no"]
            surf = font_small.render(f"{label}: {status}", True, WHITE)
            screen.blit(surf, (panel.left + 16, y))
            y += 20

        y += 10
        buttons = {}

        def craft_btn(key, label, enabled):
            nonlocal y
            r = button(label, panel.centerx, y + 20, w=260, h=38, enabled=enabled)
            buttons[key] = (r, enabled)
            y += 46

        craft_btn("wood_axe", t["craft_wood_axe"], not tools["wood_axe"] and inventory["wood"] >= 3)
        craft_btn("wood_sword", t["craft_wood_sword"], not tools["wood_sword"] and inventory["wood"] >= 5)
        craft_btn("wood_pick", t["craft_wood_pick"], not tools["wood_pick"] and inventory["wood"] >= 3)
        craft_btn("stone_axe", t["craft_stone_axe"], not tools["stone_axe"] and inventory["stone"] >= 3)
        craft_btn("stone_sword", t["craft_stone_sword"], not tools["stone_sword"] and inventory["stone"] >= 5)
        craft_btn("stone_pick", t["craft_stone_pick"], not tools["stone_pick"] and inventory["stone"] >= 3)
        craft_btn("torch", t["craft_torch"], inventory["wood"] >= 1 and inventory["coal"] >= 1)
        craft_btn("armor", t["craft_armor"], not tools["armor"] and inventory["iron"] >= 30)
        craft_btn("eat", t["eat_meat"], inventory["meat"] > 0)

        return buttons

    def apply_craft(key):
        if key == "wood_axe" and not tools["wood_axe"] and inventory["wood"] >= 3:
            inventory["wood"] -= 3
            tools["wood_axe"] = True
        elif key == "wood_sword" and not tools["wood_sword"] and inventory["wood"] >= 5:
            inventory["wood"] -= 5
            tools["wood_sword"] = True
        elif key == "wood_pick" and not tools["wood_pick"] and inventory["wood"] >= 3:
            inventory["wood"] -= 3
            tools["wood_pick"] = True
        elif key == "stone_axe" and not tools["stone_axe"] and inventory["stone"] >= 3:
            inventory["stone"] -= 3
            tools["stone_axe"] = True
        elif key == "stone_sword" and not tools["stone_sword"] and inventory["stone"] >= 5:
            inventory["stone"] -= 5
            tools["stone_sword"] = True
        elif key == "stone_pick" and not tools["stone_pick"] and inventory["stone"] >= 3:
            inventory["stone"] -= 3
            tools["stone_pick"] = True
        elif key == "torch" and inventory["wood"] >= 1 and inventory["coal"] >= 1:
            inventory["wood"] -= 1
            inventory["coal"] -= 1
            inventory["torch"] += 2
        elif key == "armor" and not tools["armor"] and inventory["iron"] >= 30:
            inventory["iron"] -= 30
            tools["armor"] = True
        elif key == "eat" and inventory["meat"] > 0:
            inventory["meat"] -= 1
            nonlocal_hunger_add(25)

    def nonlocal_hunger_add(v):
        nonlocal player_hunger
        player_hunger = min(100.0, player_hunger + v)

    play_rect = settings_rect = exit_rect = None
    lang_rect = back_rect = None
    inv_buttons = {}

    while True:
        dt = clock.tick(60) / 1000.0

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
                    if not action["active"]:
                        do_interact()
                if event.key == pygame.K_t and state["screen"] == "playing" and not state["inventory_open"]:
                    place_torch()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if state["screen"] == "menu":
                    if play_rect and play_rect.collidepoint(pos):
                        state["screen"] = "playing"
                    elif settings_rect and settings_rect.collidepoint(pos):
                        state["screen"] = "settings"
                    elif exit_rect and exit_rect.collidepoint(pos):
                        pygame.quit()
                        sys.exit()
                elif state["screen"] == "settings":
                    if lang_rect and lang_rect.collidepoint(pos):
                        state["lang"] = "en" if state["lang"] == "ru" else "ru"
                    elif back_rect and back_rect.collidepoint(pos):
                        state["screen"] = "menu"
                elif state["screen"] == "playing" and state["inventory_open"]:
                    for key, (rect, enabled) in inv_buttons.items():
                        if enabled and rect.collidepoint(pos):
                            apply_craft(key)
                            break

        if message["timer"] > 0:
            message["timer"] -= dt

        if state["screen"] == "menu":
            play_rect, settings_rect, exit_rect = draw_menu()

        elif state["screen"] == "settings":
            lang_rect, back_rect = draw_settings()

        elif state["screen"] == "playing":
            day_timer += dt

            if action["active"]:
                action["timer"] += dt
                if action["timer"] >= action["duration"]:
                    finish_action()
            elif not state["inventory_open"]:
                keys = pygame.key.get_pressed()
                dx = dy = 0
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    dx = -speed
                    facing = "left"
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    dx = speed
                    facing = "right"
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    dy = -speed
                    facing = "up"
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    dy = speed
                    facing = "down"
                if dx:
                    try_move(dx, 0)
                if dy:
                    try_move(0, dy)
                check_teleport()
                if state["map"] == "over":
                    update_animals(dt)

            player_hunger = max(0.0, player_hunger - HUNGER_DRAIN_PER_SEC * dt)
            if player_hunger <= 0:
                hp_timer += dt
                drain_interval = 6.0 if tools["armor"] else 3.0
                if hp_timer >= drain_interval:
                    hp_timer = 0.0
                    player_hp = max(0.0, player_hp - 1.0)
            else:
                hp_timer = 0.0

            if player_hp <= 0:
                player_hp = 100.0
                player_hunger = 50.0
                state["map"] = "over"
                player.x = spawn_tx * TILE
                player.y = spawn_ty * TILE

            draw_world()

            if state["inventory_open"]:
                inv_buttons = draw_inventory_panel()

        pygame.display.flip()


if __name__ == "__main__":
    try:
        run_game()
    except Exception:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
