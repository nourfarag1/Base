import os
import random
import math
import pygame as pg
from os import listdir
from os.path import isfile, join
import subprocess
import time
import pygame.mixer_music

pg.init()

pg.display.set_caption('Platformer')


BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800

FPS = 60

PLAYER_VEL = 5

sound = pg.mixer.Sound("N:/MyGame/Music Elle3ba.mp3")


# Font settings
FONT_NAME = pg.font.match_font('arial')
FONT_SIZE = 24
FONT_COLOR = (0, 0, 0)

# Health bar
MAX_HEALTH = 100
health = MAX_HEALTH

HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_COLOR = (255, 0, 0)

window = pg.display.set_mode((WIDTH, HEIGHT))
font = pg.font.Font(FONT_NAME, FONT_SIZE)

# Initialize score
score = 0


def flip(sprites):
    return [pg.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("Platformer", "assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pg.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pg.Surface(
                (width, height), pg.SRCALPHA, 32)
            rect = pg.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pg.transform.scale2x(surface))

        # handling directions
        if direction:
            all_sprites[image.replace(
                ".png", "") + "_right"] = sprites
            all_sprites[image.replace(
                ".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("Platformer", "assets", "Terrain", "Terrain.png")
    image = pg.image.load(path).convert_alpha()
    surface = pg.Surface((size, size), pg.SRCALPHA, 32)
    rect = pg.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)

    return pg.transform.scale2x(surface)


class Player(pg.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets(
        "MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.decrease_health(5)

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1
    
    def decrease_health(self, amount):
        global health
        health -= amount

        
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
        

    def update(self):
        self.rect = self.sprite.get_rect(
            topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pg.Rect(x, y, width, height)
        self.image = pg.Surface((width, height), pg.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pg.mask.from_surface(self.image)


def getBackground(name):
    image = pg.image.load(join("Platformer", "assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)

    return tiles, image


def Draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    # Display score
    score_text = font.render(
        f"Score: {score}", True, FONT_COLOR)
    window.blit(score_text, (WIDTH - 150, 10))

    # Display Healthbar
    health_bar_rect = pg.Rect(WIDTH - 200, 40, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
    pg.draw.rect(window, HEALTH_BAR_COLOR, health_bar_rect)
    current_health = max(0, health)
    remaining_health_rect = pg.Rect(WIDTH - 200, 40, current_health * HEALTH_BAR_WIDTH // MAX_HEALTH, HEALTH_BAR_HEIGHT)
    pg.draw.rect(window, (0, 255, 0), remaining_health_rect)

    pg.display.update()


def handleVerticalCollision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pg.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pg.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object

def game_over(player):

    # Display "Game Over!" message in the middle of the window
    game_over_text = font.render("Game Over!", True, FONT_COLOR)
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(game_over_text, text_rect)
    pg.display.update()

    # Display "Play Again?" button
    button_rect = pg.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    pg.draw.rect(window, (98, 147, 0), button_rect)
    button_text = font.render("Play Again?", True, FONT_COLOR)
    button_text_rect = button_text.get_rect(center=button_rect.center)
    window.blit(button_text, button_text_rect)

    pg.display.update()

    # Wait for the user to click the button
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    pg.quit()
                    subprocess.run(["python", "N:/MyGame/startScreen.py"])
                    quit()
                    


def handleMove(player, objects):
    global score
    keys = pg.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pg.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pg.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handleVerticalCollision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            if obj.animation_name == "on":
                player.make_hit()

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pg.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Fruit(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fruit")
        self.fruit = load_sprite_sheets("Items", "Fruits", width, height)
        self.image = self.fruit["Melon"][0]
        self.mask = pg.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Melon"

    def collected(self):
        self.animation_name = "Collected"

    def loop(self):
        sprites = self.fruit[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.image)

class Flag(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "flag")
        self.flag = load_sprite_sheets("Items", "Flags", width, height)
        self.image = self.flag["Idle"][0]
        self.mask = pg.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle"
        self.triggered = False

    def passed(self):
        self.animation_name = "Moving"

    def loop(self):
        sprites = self.flag[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Checkpoint(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "checkpoint")
        self.checkpoint = load_sprite_sheets("Items", "Checkpoints", width, height)
        self.image = self.checkpoint["NoFlag"][0]
        self.mask = pg.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "NoFlag"
        self.triggered = False

    def Checked(self):
        self.animation_name = "Idle"

    def loop(self):
        sprites = self.checkpoint[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def main(window):
    global score, sound
    clock = pg.time.Clock()
    background, bg_image = getBackground("Brown.png")
    sound.play()

    level_passed = False

    block_size = 96

    flag = Flag(-500, HEIGHT - block_size - 120, 64, 64)

    checkpoint = Checkpoint(1000, HEIGHT - block_size - 120, 64, 96)

    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()

    fruits = []

    min_fruit_y = HEIGHT // 2
    max_fruit_y = HEIGHT - 100

    for _ in range(5):
        fruit_x = random.randint(0, WIDTH - 42)
        fruit_y = random.randint(1 * HEIGHT // 2, HEIGHT - 32)
        # Ensure the fruit is above the terrain level
        while fruit_y + 32 > HEIGHT - block_size:
            fruit_y = random.randint(min_fruit_y, max_fruit_y)
        fruit = Fruit(fruit_x, fruit_y, 32, 32)
        fruit.rect = pg.Rect(fruit_x, fruit_y, 32, 32)
        fruits.append(fruit)

    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]

    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 3, block_size), flag, checkpoint, fire, *fruits]
    
    # Adjust player's initial x-position to the beginning of terrain
    player_x = -600
    player_y = HEIGHT - 2 * block_size  # Set player's initial y-position (just above the second row of blocks)
    player = Player(player_x, player_y, 50, 50)

    # Set initial offset_x to 0
    offset_x = -1000

    # Define scroll area width
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        flag.loop()
        checkpoint.loop()
        fire.loop()
        for fruit in fruits:
            fruit.loop()

        collected_fruits = []

        for fruit in fruits:
            if not fruit.animation_name == "Collected":  # Check if fruit is not already collected
                if pg.sprite.collide_mask(player, fruit):
                    fruit.collected()
                    score += 1
                    collected_fruits.append(fruit)

        if pg.sprite.collide_mask(player, flag):
            if not flag.triggered:
                flag.triggered = True
                flag.passed()

        if pg.sprite.collide_mask(player, checkpoint):
            if not checkpoint.triggered:
                if score >= 5:
                    checkpoint.triggered = True
                    checkpoint.Checked()
                    level_passed = True

        if pg.sprite.collide_mask(player, fire):
            fire.off()

        # Check if player's health is zero or below zero
        if health <= 0:
            game_over(player)
            break

        # Check if player fell off the terrain
        if player.rect.top > HEIGHT:
            game_over(player)
            break

        handleMove(player, objects)
        Draw(window,  background, bg_image,
             player, objects, offset_x)
        
        if level_passed:
            # Display "You Passed This Level" text
            passed_text = font.render("You Passed This Level", True, FONT_COLOR)
            text_rect = passed_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(passed_text, text_rect)

            # Display "Next Level" button
            next_level_button_rect = pg.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
            pg.draw.rect(window, (0, 255, 0), next_level_button_rect)
            button_text = font.render("Next Level", True, FONT_COLOR)
            button_text_rect = button_text.get_rect(center=next_level_button_rect.center)
            window.blit(button_text, button_text_rect)

            pg.display.update()

            # # Wait for 4 seconds
            # time.sleep(4)

            # Check if "Next Level" button is clicked
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    if next_level_button_rect.collidepoint(mouse_pos):
                        # Redirect to another file
                        pg.quit()
                        subprocess.run(["python","N:/MyGame/Platformer/LevelTwo.py"])
                        quit()
        
        # Update offset_x based on player's movement to scroll the screen
        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pg.quit()
    quit()



if __name__ == "__main__":
    main(window)
