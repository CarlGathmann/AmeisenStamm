from collision.tests import collide
import pygame as pg
import collision as col
from collision import Vector as vec
from random import randint, uniform
from bresenham import bresenham as br

#Game properties:
FPS = 60
WIDTH = 1080
HEIGHT = 760
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
FOOD_SPAWNING = False
ANT_SPAWNING = True
AGING = False

#Ant properties:
STAMM = 1
MAX_SPEED = 2
MAX_FORCE = 0.2
WANDER_RING_DISTANCE = 500
WANDER_RING_RADIUS = 50
PHERO_LENGTH = 20
PHERO_PERIOD = 100
VISION_LENGTH = 80
VISION_RADIUS = 10

clock = pg.time.Clock()
disp = pg.display.set_mode((WIDTH,HEIGHT))
drawing = False
food_list = []
ant_list = []
phero_list = []
phero_dict = {}
vision_dict = {}
food_delay = 0


class Ant():

    def __init__(self):

        self.pos = vec(WIDTH / 2 ,HEIGHT / 2)
        self.rect = col.Circle(vec(self.pos.x,self.pos.y),3)
        self.vel = vec(MAX_SPEED, 0).rotate(uniform(0, 360))
        self.acc = vec(0,0)
        self.mass = 2
        self.home = col.Circle(vec(WIDTH / 2 ,HEIGHT / 2),2)
        self.target = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.food_target = None
        self.phero_target = None
        self.mission = False
        self.food_found = False
        self.want_to_go = 'food'
        self.phero_space = 0
        self.age = 0

        vision_points = self.pos, self.pos - self.vel.normalize().rotate(VISION_RADIUS)*VISION_LENGTH, self.pos - self.vel.normalize().rotate(-VISION_RADIUS)*VISION_LENGTH
        self.vision = col.Poly(self.vel.normalize(),vision_points)

    def seek(self, target):
        desired = (target - self.pos).normalize() * MAX_SPEED
        if desired-self.vel == 0:
            print(desired-self.vel)
        steer = (desired - self.vel).normalize().limit(MAX_FORCE)
        return steer

    def wander(self):  
        circle_pos = self.pos + self.vel.normalize() * WANDER_RING_DISTANCE
        target = circle_pos + vec(WANDER_RING_RADIUS, 0).rotate(uniform(0, 360))
 
        return self.seek(target)

    def draw(self):
        pg.draw.circle(disp,WHITE,self.rect.pos,self.rect.radius)
        pg.draw.circle(disp,CYAN,self.home.pos,10)
        #pg.draw.polygon(disp, WHITE, self.vision.base_points,1)

    def applyForce(self, force):
        self.acc += force
        
    def ant_spawner(self):
        ant = Ant()
        ant_list.append(ant)

    def phero_spawning(self):
        if self.phero_space >= randint(0,PHERO_PERIOD):
                ant_pos = self.pos
                if ant.food_found:
                    phero = Phero('food', ant_pos)
                    phero_list.append(phero)
                    phero_dict[tuple(phero.pos)] = phero
                else:
                    phero = Phero('home', ant_pos)
                    phero_list.append(phero)
                    phero_dict[tuple(phero.pos)] = phero
                self.phero_space = 0
            
        if len(phero_list) > len(ant_list)*PHERO_LENGTH:
            phero_dict.pop(tuple(phero_list[len(phero_list)-1].pos))
            phero_list.pop(0)
                
                    
        self.phero_space += 1

    def update(self):

        self.phero_spawning()

        if self.mission:
            self.acc += self.seek(self.target)
        else: 
            self.acc += self.wander()
        
        self.vel = self.vel.limit(MAX_SPEED)
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0
        
        if self.pos.x > WIDTH-20:
            desired = vec(MAX_SPEED,self.vel.y)
            steer = (desired - self.vel).limit(MAX_SPEED)
            self.applyForce(-steer/3)
        if self.pos.x < 20:
            desired = vec(MAX_SPEED,self.vel.y)
            steer = (desired - self.vel).limit(MAX_SPEED)
            self.applyForce(steer/3)
        if self.pos.y > HEIGHT-20:
            desired = vec(self.vel.x,MAX_SPEED)
            steer = (desired - self.vel).limit(MAX_SPEED)
            self.applyForce(-steer/3)
        if self.pos.y < 20:
            desired = vec(self.vel.x,MAX_SPEED)
            steer = (desired - self.vel).limit(MAX_SPEED)
            self.applyForce(steer/3)

        self.rect.pos = self.pos

        vision_points = self.pos - self.vel.normalize().rotate(VISION_RADIUS)*VISION_LENGTH, self.pos, self.pos - self.vel.normalize().rotate(-VISION_RADIUS)*VISION_LENGTH
        self.vision.set_points(vision_points)

        if AGING:
            self.age += 1
            if self.age >= 2000:
                ant_list.remove(self)

        self.draw()

        if collide(self.vision,self.home):
            if self.food_found:
                self.mission = True
                self.target = self.home.pos

        if collide(self.rect,self.home) & self.food_found:
            if ANT_SPAWNING:
                self.ant_spawner()
            self.food_found = False
            self.mission = False
            self.food_target = None
            self.phero_target = None
            self.want_to_go = 'food'
            self.vel *= -1

        if self.food_target != None: 
            if collide(self.rect,self.food_target.rect):
                self.vel *= -1
                self.mission = False
                self.want_to_go = 'home'
                try:
                    food_list.remove(self.food_target)
                    self.food_target = None
                except ValueError:
                    self.mission = False
                    self.food_target = None
                    self.food_found = False

        for food in food_list:
            if not self.food_found:
                if collide(food.rect,self.vision):
                    self.mission  = True
                    self.food_found = True
                    self.food_target = food
                    self.target = self.food_target.pos
        
        for phero in phero_list:
            if not collide(self.vision,self.home):
                if collide(self.vision, phero.rect):
                    if not self.food_found:
                        if self.want_to_go == 'food':
                            if phero.type == 'food':
                                if self.phero_target == None:
                                    self.mission = True
                                    self.phero_target = phero
                                    self.target = self.phero_target.pos
                                else:
                                    if phero.red < self.phero_target.red:
                                        self.mission = True
                                        self.phero_target = phero
                                        self.target = self.phero_target.pos
                    else:
                        if self.want_to_go == 'home':
                            if phero.type == 'home':
                                if self.phero_target == None:
                                    self.mission = True
                                    self.phero_target = phero
                                    self.target = self.phero_target.pos
                                else:
                                    if phero.green < self.phero_target.green:
                                        self.mission = True
                                        self.phero_target = phero
                                        self.target = self.phero_target.pos
                        
        if self.phero_target != None:
            if collide(self.rect, self.phero_target.rect):
                self.mission = False
            if self.phero_target.green <= 254:
                self.phero_target.green += 1
            if self.phero_target.red <= 254:
                self.phero_target.red += 1

        
                    

class Food():

    def __init__(self, pos):
        self.pos = pos
        self.rect = col.Circle(self.pos,2)
    
    def draw(self):
        pg.draw.circle(disp,WHITE,self.rect.pos,self.rect.radius)


class Phero():

    def __init__(self, phero_type, pos):
        self.green = 255
        self.red = 255
        self.tick = 1
        self.pos = pos
        self.rect = col.Circle(pos, 0.1)
        self.type = phero_type

    def draw(self):
        if self.type == 'home':
            pg.draw.circle(disp,(0,self.green,0),self.rect.pos,1)
        elif self.type == 'food':
            pg.draw.circle(disp,(self.red,0,0),self.rect.pos,1)
        self.tick += 1
    
    def update(self):
        if self.type == 'home':
            div = (self.green*len(ant_list))/(PHERO_LENGTH*len(ant_list)*5)
            self.green -= div
        elif self.type == 'food':
            div = (self.red*len(ant_list))/(PHERO_LENGTH*len(ant_list)*5)
            self.red -= div
        self.tick += 1  

pg.init()

for i in range(STAMM):
    ant = Ant()
    ant_list.append(ant)

go = True
start = False


def bresenham_dict(first_pos,second_pos):
    return dict(br(int(first_pos.x),int(first_pos.y),int(second_pos.x),int(second_pos.y)))

def food_spawner(food_delay):
    food_delay += 1

    if food_delay >= randint(100,1000):
        rand_x = randint(20,WIDTH-20)
        rand_y = randint(20,HEIGHT-20)
        food = Food(vec(rand_x,rand_y))
        food_list.append(food)
        food_delay = 0
    return food_delay

while go:

    disp.fill(BLACK)
    clock.tick(FPS)

    mouse_position_x = pg.mouse.get_pos()[0]
    mouse_position_y = pg.mouse.get_pos()[1]
    for event in pg.event.get():
        if event.type == pg.QUIT:
            go = False
        if event.type == pg.MOUSEBUTTONDOWN:
            drawing = True
            
            food = Food(vec(mouse_position_x,mouse_position_y))
            food_list.append(food)
        elif event.type == pg.MOUSEMOTION:
            if drawing:
                food = Food(vec(mouse_position_x,mouse_position_y))
                food_list.append(food)
        elif event.type == pg.MOUSEBUTTONUP:
            drawing = False
        elif event.type == pg.KEYDOWN:
            start = not start

    if not start:
        for food in food_list:
            food.draw()
        for ant in ant_list:
            ant.draw()
        for phero in phero_list:
            phero.draw()
        


    if start:
        
        for phero in phero_list:
            phero.update()
            phero.draw()

        for ant in ant_list:
            ant.update()
        
        for food in food_list:
            food.draw()
            
        if FOOD_SPAWNING:
            food_delay = food_spawner(food_delay)
        
        print(len(phero_dict))

    pg.display.flip()

pg.quit()