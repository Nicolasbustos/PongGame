from math import pi, sin, cos
from random import uniform
import pandas as pd
import pygame
from sklearn.neighbors import KNeighborsRegressor

pygame.init()

WIDTH = 1200
HEIGHT = 600
BORDER = 20

bgcolor = pygame.Color("black")
fgcolor = pygame.Color("white")
VELOCITY = 2


class Ball:
    RADIUS = 10

    def __init__(self, x):
        self.x = x
        self.y = HEIGHT // 2
        self.direction = uniform(5 * pi / 6, 7 * pi / 6)
        self.vx = VELOCITY * cos(self.direction)
        self.vy = VELOCITY * sin(self.direction)

    def show(self, color):
        pygame.draw.circle(screen, color, (self.x, self.y), radius=self.RADIUS)

    def update(self, paddle_right, paddle_left=None):
        self.show(bgcolor)
        if self.x - self.RADIUS <= BORDER and paddle_left is None or self.x + self.RADIUS >= paddle_right.x and \
                paddle_right.y <= self.y + paddle_right.LENGTH / 2 <= paddle_right.y + paddle_right.LENGTH:
            self.vx *= -1
        elif self.y - self.RADIUS <= BORDER or self.y + self.RADIUS >= HEIGHT - BORDER:
            self.vy *= -1
        elif paddle_left is not None:
            if paddle_left.y <= self.y + paddle_left.LENGTH / 2 <= paddle_left.y + paddle_left.LENGTH and \
                    self.x - self.RADIUS <= paddle_left.x + BORDER:
                self.vx *= -1
        self.x += self.vx
        self.y -= self.vy
        self.show(fgcolor)


class Paddle:
    LENGTH = 100

    def __init__(self, right=True):
        self.x = WIDTH - BORDER if right is True else 0
        self.y = HEIGHT//2

    def show(self, color):
        pygame.draw.rect(screen, color, pygame.Rect((self.x, self.y - self.LENGTH / 2), (BORDER, self.LENGTH)))

    def update(self, IA=None, ball=None):
        self.show(bgcolor)
        if IA is None:
            self.y = pygame.mouse.get_pos()[1]
        else:
            self.y = IA.predict([[ball.x, ball.y, ball.vx, ball.vy]])[0]
        self.show(fgcolor)


screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.draw.rect(screen, fgcolor, pygame.Rect((0, 0), (WIDTH - BORDER, BORDER)))
pygame.draw.rect(screen, fgcolor, pygame.Rect((0, HEIGHT-BORDER), (WIDTH - BORDER, BORDER)))
pygame.draw.rect(screen, fgcolor, pygame.Rect((0, 0), (BORDER, HEIGHT)))

ballplay = Ball(WIDTH-Ball.RADIUS - 30)
ballplay.show(fgcolor)

paddle = Paddle()
paddle.show(fgcolor)

data = list()

while ballplay.x + ballplay.RADIUS < paddle.x + 5 and pygame.time.get_ticks() / 1000 <= 120:
    e = pygame.event.poll()
    if e.type == pygame.QUIT:
        break
    ballplay.update(paddle)
    paddle.update()
    data.append([ballplay.x, ballplay.y, ballplay.vx, ballplay.vy, paddle.y])
    pygame.display.flip()

pygame.draw.rect(screen, bgcolor, pygame.Rect((0, 0), (BORDER, HEIGHT)))

df = pd.DataFrame(data, columns=["x", "y", "vx", "vy", "y_hat"])
df.drop_duplicates(inplace=True)
del data
y_train = df.pop("y_hat")
X_train = df
clf = KNeighborsRegressor(n_neighbors=3).fit(X_train, y_train)
ballplay.show(bgcolor)
paddle.show(bgcolor)
del ballplay, paddle, df, X_train, y_train

ballplay = Ball(WIDTH-Ball.RADIUS - 30)
ballplay.show(fgcolor)
paddle_right = Paddle()
paddle_right.show(fgcolor)
paddle_left = Paddle(right=False)
paddle_left.show(fgcolor)

while ballplay.x + ballplay.RADIUS < paddle_right.x + 5 and ballplay.x - ballplay.RADIUS > paddle_left.x + 5:
    e = pygame.event.poll()
    if e.type == pygame.QUIT:
        break
    ballplay.update(paddle_right=paddle_right, paddle_left=paddle_left)
    paddle_left.update()
    paddle_right.update(IA=clf, ball=ballplay)
    pygame.display.flip()






