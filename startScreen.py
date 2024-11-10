import pygame as pg
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import subprocess

pg.init()


# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Font settings
FONT_NAME = pg.font.match_font('arial')
FONT_SIZE = 36
FONT_COLOR = (0, 0, 0)

# Colors
LIGHT_BLUE = (173, 216, 230)

# Button properties
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
BUTTON_COLOR = (100, 100, 255)
BUTTON_TEXT = "Start"

# Initialize the display
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.OPENGL | pg.DOUBLEBUF)

def draw_text(text, font, color, surface, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def draw_button(x, y, width, height):
    glColor3fv(BUTTON_COLOR)
    glBegin(GL_QUADS)
    glVertex2fv((x, y))
    glVertex2fv((x + width, y))
    glVertex2fv((x + width, y + height))
    glVertex2fv((x, y + height))
    glEnd()

def start_screen():
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return

            if event.type == pg.MOUSEBUTTONDOWN:
                if (WIDTH // 2 - BUTTON_WIDTH // 2) <= event.pos[0] <= (WIDTH // 2 + BUTTON_WIDTH // 2) \
                        and (HEIGHT // 2 + 50) <= event.pos[1] <= (HEIGHT // 2 + 50 + BUTTON_HEIGHT):
                    # Start the game
                    pg.quit()
                    subprocess.run(["python", "N:/MyGame/Platformer/LevelOne.py"])
                    return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)

        # Draw light blue background
        glClearColor(LIGHT_BLUE[0]/255, LIGHT_BLUE[1]/255, LIGHT_BLUE[2]/255, 1)

        # Draw the game name
        draw_text("Platformer", pg.font.Font(FONT_NAME, FONT_SIZE), FONT_COLOR, screen, WIDTH // 2, HEIGHT // 2 - 100)

        # Draw the start button
        draw_button(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + 50, BUTTON_WIDTH, BUTTON_HEIGHT)
        draw_text(BUTTON_TEXT, pg.font.Font(FONT_NAME, FONT_SIZE), FONT_COLOR, screen, WIDTH // 2, HEIGHT // 2 + 75)

        pg.display.flip()

start_screen()
