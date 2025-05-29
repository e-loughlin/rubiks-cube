import numpy as np
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, glutBitmapCharacter
from pygame.locals import *

# Colors for Rubik's cube faces: White, Yellow, Blue, Green, Red, Orange
FACE_COLORS = {
    "W": (1, 1, 1),  # white
    "Y": (1, 1, 0),  # yellow
    "O": (1, 0.5, 0),  # orange
    "R": (1, 0, 0),  # red
    "G": (0, 1, 0),  # green
    "B": (0, 0, 1),  # blue
}


def rotate_matrix(matrix, clockwise=True):
    if clockwise:
        return [list(reversed(col)) for col in zip(*matrix)]
    else:
        return [list(col) for col in zip(*matrix)][::-1]


class RubiksCube:
    def __init__(self):
        self.reset_cube()

    def rotate_face(self, face, clockwise=True):
        self.cube[face] = rotate_matrix(self.cube[face], clockwise)

        # Correct edge mapping (face: [ (adj_face, index, row/col, reverse) ])
        edge_map = {
            "F": [
                ("U", 2, "row"),
                ("R", 0, "col"),
                ("D", 0, "row", True),
                ("L", 2, "col", True),
            ],
            "B": [
                ("U", 0, "row"),
                ("L", 0, "col", True),
                ("D", 2, "row", True),
                ("R", 2, "col"),
            ],
            "L": [
                ("U", 0, "col"),
                ("F", 0, "col"),
                ("D", 0, "col"),
                ("B", 2, "col", True),
            ],
            "R": [
                ("U", 2, "col"),
                ("B", 0, "col", True),
                ("D", 2, "col"),
                ("F", 2, "col"),
            ],
            "U": [("B", 0, "row"), ("R", 0, "row"), ("F", 0, "row"), ("L", 0, "row")],
            "D": [("F", 2, "row"), ("R", 2, "row"), ("B", 2, "row"), ("L", 2, "row")],
        }

        def get_strip(face, idx, mode, reverse=False):
            strip = (
                self.cube[face][idx][:]
                if mode == "row"
                else [self.cube[face][i][idx] for i in range(3)]
            )
            return strip[::-1] if reverse else strip

        def set_strip(face, idx, mode, strip, reverse=False):
            if reverse:
                strip = strip[::-1]
            if mode == "row":
                self.cube[face][idx] = strip
            else:
                for i in range(3):
                    self.cube[face][i][idx] = strip[i]

        # Pull out the current edge strips
        edge_info = edge_map[face]
        strips = [
            get_strip(*info[:3], reverse=info[3] if len(info) == 4 else False)
            for info in edge_info
        ]

        # Rotate the strips
        if clockwise:
            rotated = strips[-1:] + strips[:-1]
        else:
            rotated = strips[1:] + strips[:1]

        for info, strip in zip(edge_info, rotated):
            set_strip(
                *info[:3], strip=strip, reverse=info[3] if len(info) == 4 else False
            )

    def apply_move(self, move):
        # print(f"Applying move: {move}")
        if move.endswith("2"):
            base = move[0]
            self.rotate_face(base, True)
            self.rotate_face(base, True)
        elif move.endswith("'"):
            base = move[0]
            self.rotate_face(base, False)
        else:
            self.rotate_face(move[0], True)

        # print(self.cube)

    def reset_cube(self):
        self.cube = {
            "U": [["W"] * 3 for _ in range(3)],
            "D": [["Y"] * 3 for _ in range(3)],
            "L": [["O"] * 3 for _ in range(3)],
            "R": [["R"] * 3 for _ in range(3)],
            "F": [["G"] * 3 for _ in range(3)],
            "B": [["B"] * 3 for _ in range(3)],
        }

    def get_face_colors(self, face):
        return [
            [FACE_COLORS[self.cube[face][i][j]] for j in range(3)] for i in range(3)
        ]

    def draw(self):
        self.draw_face("F", z=-1.5, axis="z")
        self.draw_face("B", z=1.5, angle=180, axis="y")
        self.draw_face("U", y=1.5, angle=90, axis="x")
        self.draw_face("D", y=-1.5, angle=-90, axis="x")
        self.draw_face("R", x=1.5, angle=-90, axis="y")
        self.draw_face("L", x=-1.5, angle=90, axis="y")
        self.draw_axes()

    def draw_label(self, text, x, y, z):
        glRasterPos3f(x, y, z)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    def draw_axes(self):
        glLineWidth(3.0)

        # X axis (Red)
        glColor3f(1, 0.2, 0.2)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(3, 0, 0)
        glEnd()
        self.draw_label("X", 3.2, 0, 0)

        # Y axis (White)
        glColor3f(0.8, 0.8, 0.8)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 3, 0)
        glEnd()
        self.draw_label("Y", 0, 3.2, 0)

        # Z axis (Blue)
        glColor3f(0.2, 0.2, 1)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 3)
        glEnd()
        self.draw_label("Z", 0, 0, 3.2)

    def draw_face(self, face, x=0, y=0, z=0, angle=0, axis="z"):
        TILE_SIZE = 1.0
        GAP = 0.001
        START = -TILE_SIZE * 1.5 - GAP  # centers the 3x3 grid

        glPushMatrix()
        glTranslatef(x, y, z)
        if angle != 0:
            if axis == "x":
                glRotatef(angle, 1, 0, 0)
            elif axis == "y":
                glRotatef(angle, 0, 1, 0)
            elif axis == "z":
                glRotatef(angle, 0, 0, 1)

        colors = self.get_face_colors(face)

        for i in range(3):
            for j in range(3):
                color = colors[i][j]
                dx = START + j * (TILE_SIZE + GAP)
                dy = -START - i * (TILE_SIZE + GAP)  # invert Y for OpenGL

                # Draw tile
                glColor3fv(color)
                glBegin(GL_QUADS)
                glVertex3f(dx, dy, 0)
                glVertex3f(dx + TILE_SIZE, dy, 0)
                glVertex3f(dx + TILE_SIZE, dy - TILE_SIZE, 0)
                glVertex3f(dx, dy - TILE_SIZE, 0)
                glEnd()

                # Draw black outline
                glColor3f(0, 0, 0)
                glLineWidth(2)
                glBegin(GL_LINE_LOOP)
                glVertex3f(dx, dy, 0.001)
                glVertex3f(dx + TILE_SIZE, dy, 0.001)
                glVertex3f(dx + TILE_SIZE, dy - TILE_SIZE, 0.001)
                glVertex3f(dx, dy - TILE_SIZE, 0.001)
                glEnd()

                # # Draw (i, j) text at center
                # text = f"({i},{j})"
                # glColor3f(0, 0, 0)
                # glRasterPos3f(dx + TILE_SIZE / 4, dy - TILE_SIZE / 2.0, 0.002)
                # for ch in text:
                #     glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

        glPopMatrix()
