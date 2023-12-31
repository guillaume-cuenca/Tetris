import pygame
import sys
import time
import random
from collections import namedtuple

unit = 25  # square cell: unit x unit pixels
unit_width = 10  # grid width in # of cells
unit_height = 18  # grid height in # of cells
margin = unit
size = width, height = (unit * unit_width) + (2 * margin) + 200, (unit * unit_height) + (2 * margin)
grid_left = margin
grid_top = margin
grid_height = unit * unit_height
grid_width = unit * unit_width
drop_speed = 500  # in msecs
move_speed = 200  # lateral

Tetromino = namedtuple('Tetromino', ['states', 'color'])

# See http://en.wikipedia.org/wiki/Tetromino
tetrominoes = {
    'I': Tetromino(states=[[0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0]],
                   color=pygame.color.Color('red')),

    'S': Tetromino(states=[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0],
                           [0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]],
                   color=pygame.color.Color('green')),

    'Z': Tetromino(states=[[1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]],
                   color=pygame.color.Color('pink')),

    'T': Tetromino(states=[[0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                           [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]],
                   color=pygame.color.Color('blue')),

    'O': Tetromino(states=[[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0]],
                   color=pygame.color.Color('yellow')),

    'L': Tetromino(states=[[0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                           [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                           [0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                   color=pygame.color.Color('turquoise')),

    'J': Tetromino(states=[[0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                           [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]],
                   color=pygame.color.Color('purple'))
}

class Piece:
    def __init__(self):
        self.reset()

    def draw(self):
        show_local_grid = False  # set to True to see what's going on
        for i in range(4):
            for j in range(4):
                k = (i * 4) + j
                if tetrominoes[self.tetromino].states[self.state][k]:
                    pygame.draw.rect(screen, tetrominoes[self.tetromino].color,
                                     (self.left + (j * unit), self.top + (i * unit), unit - 2, unit - 2), 3)
                elif show_local_grid:
                    pygame.draw.rect(screen, pygame.color.Color('lightgrey'),
                                     (self.left + (j * unit), self.top + (i * unit), unit, unit), 1)

    def reset(self):
        self.left = margin + (grid_width / 2) - (2 * unit)
        self.top = margin - (2 * unit)
        self.tetromino = random.choice(list(tetrominoes.keys()))
        self.state = 0

    def canGo(self, dir):
        if dir == 'down':
            return not self.isColliding(1, 0)
        elif dir == 'left':
            return not self.isColliding(0, -1)
        elif dir == 'right':
            return not self.isColliding(0, 1)

    def isColliding(self, gi_disp, gj_disp, state=None):
        gi, gj = self.getGridCoords()
        for i in range(4):
            for j in range(4):
                k = (i * 4) + j
                if tetrominoes[self.tetromino].states[state if state is not None else self.state][k] \
                        and grid[int(gi + i + gi_disp + 4)][int(gj + j + gj_disp + 4)]:
                    return True
        return False

    def drop(self):
        if self.canGo('down'):
            self.top += unit
        else:
            self.fixToGrid()
            self.reset()
            pygame.time.set_timer(pygame.USEREVENT + 1, drop_speed)
            lines_cleared = lookForRowClearing()
            if lines_cleared:
                score.clear_lines(lines_cleared)

    def rotate(self):
        next_state = self.state + 1
        next_state %= len(tetrominoes[self.tetromino].states)
        if not self.isColliding(0, 0, next_state):
            self.state += 1
            self.state %= len(tetrominoes[self.tetromino].states)

    def move(self, dir):
        if dir == 'left' and self.canGo('left'):
            self.left -= unit
        elif dir == 'right' and self.canGo('right'):
            self.left += unit

    def getGridCoords(self):
        gi = (self.top - margin) / unit
        gj = (self.left - margin) / unit
        return gi, gj

    def fixToGrid(self):
        gi, gj = self.getGridCoords()
        for i in range(4):
            for j in range(4):
                k = (i * 4) + j
                if tetrominoes[self.tetromino].states[self.state][k]:
                    grid[int(gi + i + 4)][int(gj + j + 4)] = tetrominoes[self.tetromino].color
        lookForRowClearing()
        for j in range(4, unit_width + 4):
            if grid[4][int(j)]:
                sys.exit(0)

class NextPiece:
    def __init__(self):
        self.generate_next()

    def generate_next(self):
        self.tetromino = random.choice(list(tetrominoes.keys()))
        self.state = 0

    def draw(self):
        show_local_grid = True  # set to False to hide the local grid
        for i in range(4):
            for j in range(4):
                k = (i * 4) + j
                if tetrominoes[self.tetromino].states[self.state][k]:
                    pygame.draw.rect(screen, tetrominoes[self.tetromino].color,
                                     (width - 150 + (j * unit), margin + (i * unit), unit - 2, unit - 2), 3)
                elif show_local_grid:
                    pygame.draw.rect(screen, pygame.color.Color('lightgrey'),
                                     (width - 150 + (j * unit), margin + (i * unit), unit, unit), 1)

class Score:
    def __init__(self):
        self.value = 0
        self.lines_cleared = 0

    def increase_score(self, points):
        self.value += points

    def increase_lines_cleared(self, lines):
        self.lines_cleared += lines

    def draw_score(self, screen):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.value}", True, pygame.color.Color('white'))

        # Modifier la position x pour déplacer le score à droite
        score_x = width - margin - 138  # Nouvelle position x
        score_y = margin - -150

        screen.blit(score_text, (score_x, score_y))

        # Afficher le nombre de lignes créées
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, pygame.color.Color('white'))
        lines_x = width - margin - 138  # Nouvelle position x (sous le score)
        lines_y = margin - -110  # Ajuster la position en fonction de la police utilisée
        screen.blit(lines_text, (lines_x, lines_y))

    def clear_lines(self, lines):
        # Supprimer les lignes complètes du tableau de score
        for line in lines:
            del grid[line]
            grid.insert(0, [0] * (unit_width + 8))

        # Mettre à jour le score en fonction du nombre de lignes supprimées
        self.increase_score(len(lines))

        # Mettre à jour le nombre total de lignes créées
        self.increase_lines_cleared(len(lines))

def drawGrid():
    for i in range(unit_height + 8):
        for j in range(unit_width + 8):
            if grid[int(i)][int(j)] and grid[int(i)][int(j)] != -1:
                pygame.draw.rect(screen, grid[int(i)][int(j)],
                                 (margin + ((j - 4) * unit), margin + ((i - 4) * unit), unit - 2, unit - 2), 3)

def lookForRowClearing():
    lines_to_clear = []
    i = unit_height - 1 + 4
    while i >= 4:
        full_row = all(grid[int(i)][int(j)] for j in range(4, unit_width + 4))
        if full_row:
            lines_to_clear.append(int(i))
        i -= 1
    return lines_to_clear

pygame.init()
screen = pygame.display.set_mode(size)
pygame.time.set_timer(pygame.USEREVENT + 1, drop_speed)

p = Piece()
next_piece = NextPiece()
score = Score()

grid = [[0 for i in range(unit_width + 8)] for j in range(unit_height + 8)]
for i in range(unit_height + 8):
    for j in range(unit_width + 8):
        if i >= unit_height + 4:
            grid[int(i)][int(j)] = -1
        elif j < 4 or j >= unit_width + 4:
            grid[int(i)][int(j)] = -1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.USEREVENT + 1:
            p.drop()
        elif event.type == pygame.USEREVENT + 2:
            p.move('left')
        elif event.type == pygame.USEREVENT + 3:
            p.move('right')
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit(0)
            if event.key == pygame.K_UP:
                p.rotate()
            elif event.key == pygame.K_DOWN:
                p.drop()
                score.increase_score(1)
            elif event.key == pygame.K_LEFT:
                p.move('left')
                pygame.time.set_timer(pygame.USEREVENT + 2, move_speed)
            elif event.key == pygame.K_RIGHT:
                p.move('right')
                pygame.time.set_timer(pygame.USEREVENT + 3, move_speed)
            elif event.key == pygame.K_SPACE:
                while p.canGo('down'):
                    p.drop()
                score.increase_score(1)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pygame.time.set_timer(pygame.USEREVENT + 1, drop_speed)
            if event.key == pygame.K_LEFT:
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)
            if event.key == pygame.K_RIGHT:
                pygame.time.set_timer(pygame.USEREVENT + 3, 0)

    screen.fill(pygame.color.Color('black'))

    pygame.draw.lines(screen, pygame.color.Color('grey'), False,
                      [(grid_left - 3, grid_top),
                       (grid_left - 3, grid_top + grid_height),
                       (grid_left + grid_width, grid_top + grid_height),
                       (grid_left + grid_width, grid_top)], 1)

    p.draw()
    drawGrid()

    # Dessiner le score 
    score.draw_score(screen)

    pygame.display.update()