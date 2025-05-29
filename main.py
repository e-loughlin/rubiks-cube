import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from rubiks_cube import RubiksCube


def draw_legend(font):
    legend_lines = [
        "Moves: U R F D L B   (clockwise)",
        "       Q W E S A Z   (counter-clockwise)",
        "SPACE: Reset Cube",
        "Drag Mouse: Rotate View",
        "ESC: Quit",
    ]

    width, height = 800, 120
    surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
    surface.fill((0, 0, 0, 180))

    for i, line in enumerate(legend_lines):
        text = font.render(line, True, (255, 255, 255))  # force white
        surface.blit(text, (10, i * 20))

    surface = pygame.transform.flip(surface, False, True)  # Flip vertically
    texture_data = pygame.image.tostring(surface, "RGBA", True)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 600, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    glColor4f(1, 1, 1, 1)  # <--- This is important!

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        width,
        height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        texture_data,
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(0, 0)
    glTexCoord2f(1, 0)
    glVertex2f(width, 0)
    glTexCoord2f(1, 1)
    glVertex2f(width, height)
    glTexCoord2f(0, 1)
    glVertex2f(0, height)
    glEnd()

    glDeleteTextures(tex)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def main():
    pygame.init()

    pygame.font.init()
    font = pygame.font.Font(None, 24)  # Built-in font, guaranteed to work

    # font = pygame.font.SysFont("Arial", 16)

    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Rubik's Cube Emulator")
    screen = pygame.display.get_surface()

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.2, 0.2, 0.2, 1)  # dark gray instead of black

    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)

    cube = RubiksCube()
    mouse_down = False
    last_pos = (0, 0)
    rot_x, rot_y = 25, -45

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_u:
                    cube.apply_move("U")
                elif key == pygame.K_r:
                    cube.apply_move("R")
                elif key == pygame.K_f:
                    cube.apply_move("F")
                elif key == pygame.K_d:
                    cube.apply_move("D")
                elif key == pygame.K_l:
                    cube.apply_move("L")
                elif key == pygame.K_b:
                    cube.apply_move("B")

                elif key == pygame.K_q:
                    cube.apply_move("U'")
                elif key == pygame.K_w:
                    cube.apply_move("R'")
                elif key == pygame.K_e:
                    cube.apply_move("F'")
                elif key == pygame.K_s:
                    cube.apply_move("D'")
                elif key == pygame.K_a:
                    cube.apply_move("L'")
                elif key == pygame.K_z:
                    cube.apply_move("B'")

                elif key == pygame.K_SPACE:
                    cube = RubiksCube()  # Reset cube

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_down = True
                    last_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    x, y = event.pos
                    dx = x - last_pos[0]
                    dy = y - last_pos[1]
                    rot_x += dy
                    rot_y += dx
                    last_pos = (x, y)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        cube.draw()

        glPopMatrix()

        draw_legend(font)  # <- this will render the legend overlay
        pygame.display.flip()


if __name__ == "__main__":
    main()
