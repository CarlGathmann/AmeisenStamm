import pygame as pg
from pygame import Vector2 as vec
from bresenham import bresenham
from random import randint
import numpy as np



WIDTH = 800
HEIGHT = 800
GRID = 32
SQUARE = WIDTH/GRID

BLACK = (0,0,0)
GREY = (30,30,30)
WHITE = (255,255,255)
RED = (255,0,0)
BLUE = (0,102,225)
GREEN = (255,255,0)
FPS = 5

clock = pg.time.Clock()
disp = pg.display.set_mode((WIDTH,HEIGHT))
pixel_list = []
pixel_same_x_dict = {}

go = True

class Pixel():

    def __init__(self, pos, color, size):
        self.pos = vec(pos)
        self.x = self.pos.x
        self.y = self.pos.y
        self.color = color
        self.size = size
    
    def draw_pixel(self):
        rect = pg.Rect(self.pos.x-self.size/2,self.pos.y-self.size/2,self.size,self.size)
        pg.draw.rect(disp, self.color, rect)

#use this to create points in self defined coord-system
def create_point(x,y):
    return vec(SQUARE*x+SQUARE/2,SQUARE*y+SQUARE/2)

#gets coodinates of points crossing the funktion between two points
def bresenham_list(first_pos,second_pos):
    return list(bresenham(int(first_pos.x),int(first_pos.y),int(second_pos.x),int(second_pos.y)))

#colorises a list of points so that the line has a color gradient from color_1 to color_2
def colorise_line(list,color1,color2):
    length = len(list)
    new_list = []
    for i in range(length):
        r = (((length-i)/length) * color1[0]) + (((0+i)/length) * color2[0])
        g = (((length-i)/length) * color1[1]) + (((0+i)/length) * color2[1])
        b = (((length-i)/length) * color1[2]) + (((0+i)/length) * color2[2])
        pixel = Pixel(list[i],(r,g,b),SQUARE-1)
        new_list.append(pixel)
        pixel_list.append(pixel)
    return new_list

#gets the linear funktion between two points
def get_function(first_pos, second_pos):
    x1, x2, y1, y2 = (first_pos.x-SQUARE/2)/SQUARE, (second_pos.x-SQUARE/2)/SQUARE, (first_pos.y-SQUARE/2)/SQUARE, (second_pos.y-SQUARE/2)/SQUARE
    m = (y2-y1)/(x2-x1)
    n = -m*x1+y1
    return m,n        

pg.init()

#points to get going
FIRST_POINT = Pixel(create_point(randint(0,GRID-1),randint(0,GRID-1)), RED,SQUARE-0.5)
SECOND_POINT = Pixel(create_point(randint(0,GRID-1),randint(0,GRID-1)),BLUE,SQUARE-0.5)
THIRD_POINT = Pixel(create_point(randint(0,GRID-1),randint(0,GRID-1)),GREEN,SQUARE-0.5)

#main loop
while go:

    #create grid
    for i in range(GRID):
        for j in range(GRID):
            pixel = Pixel(create_point(i,j),GREY, SQUARE-1)
            pixel_list.append(pixel)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            go = False

    if FIRST_POINT.x >= WIDTH-SQUARE:
        FIRST_POINT.pos += (-SQUARE, rand*SQUARE)
    elif FIRST_POINT.x <= SQUARE:
        FIRST_POINT.pos += (SQUARE, rand*SQUARE)
    elif FIRST_POINT.y >= HEIGHT-SQUARE:
        FIRST_POINT.pos += (rand*SQUARE, -SQUARE)
    elif FIRST_POINT.y <= SQUARE:
        FIRST_POINT.pos += (rand*SQUARE, SQUARE)
    else:
        rand = randint(-1,1)
        FIRST_POINT.pos += (rand*SQUARE,rand*SQUARE)

    if SECOND_POINT.x >= WIDTH-SQUARE:
        SECOND_POINT.pos += (-SQUARE, rand*SQUARE)
    elif SECOND_POINT.x <= SQUARE:
        SECOND_POINT.pos += (SQUARE, rand*SQUARE)
    elif SECOND_POINT.y >= HEIGHT-SQUARE:
        SECOND_POINT.pos += (rand*SQUARE, -SQUARE)
    elif SECOND_POINT.y <= SQUARE:
        SECOND_POINT.pos += (rand*SQUARE, SQUARE)
    else:
        rand = randint(-1,1)
        SECOND_POINT.pos += (rand*SQUARE,rand*SQUARE)

    if THIRD_POINT.x >= WIDTH-SQUARE:
        THIRD_POINT.pos += (-SQUARE, rand*SQUARE)
    elif THIRD_POINT.x <= SQUARE:
        THIRD_POINT.pos += (SQUARE, rand*SQUARE)
    elif THIRD_POINT.y >= HEIGHT-SQUARE:
        THIRD_POINT.pos += (rand*SQUARE, -SQUARE)
    elif THIRD_POINT.y <= SQUARE:
        THIRD_POINT.pos += (rand*SQUARE, SQUARE)
    else:
        rand = randint(-1,1)
        THIRD_POINT.pos += (rand*SQUARE,rand*SQUARE)

    #create lines between points with gradients
    first_second = colorise_line(bresenham_list(FIRST_POINT.pos,SECOND_POINT.pos),FIRST_POINT.color,SECOND_POINT.color)
    second_third = colorise_line(bresenham_list(SECOND_POINT.pos,THIRD_POINT.pos),SECOND_POINT.color,THIRD_POINT.color)
    third_first = colorise_line(bresenham_list(THIRD_POINT.pos,FIRST_POINT.pos),THIRD_POINT.color,FIRST_POINT.color)

    for pixel_a in first_second:
        for pixel_b in second_third:
            if pixel_a.x == pixel_b.x:
                colorise_line(bresenham_list(vec(pixel_a.x,pixel_a.y),vec(pixel_b.x,pixel_b.y)),pixel_a.color,pixel_b.color)

    for pixel_a in second_third:
        for pixel_b in third_first:
            if pixel_a.x == pixel_b.x:
                colorise_line(bresenham_list(vec(pixel_a.x,pixel_a.y),vec(pixel_b.x,pixel_b.y)),pixel_a.color,pixel_b.color)

    for pixel_a in third_first:
        for pixel_b in first_second:
            if pixel_a.x == pixel_b.x:
                colorise_line(bresenham_list(vec(pixel_a.x,pixel_a.y),vec(pixel_b.x,pixel_b.y)),pixel_a.color,pixel_b.color)
    
    disp.fill(BLACK)
    clock.tick(FPS)

    for pixel in pixel_list:
        pixel.draw_pixel()
    
    pixel_list.clear()

    pg.display.flip()
pg.quit()