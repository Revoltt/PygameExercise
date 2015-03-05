#!/usr/bin/env python
# coding: utf

import pygame
import random
import math

SIZE = 640, 480
BALLNUMBER = 3
GRAVITY = 0.3
ANGLECONST = 5
PIXCONST = 10

def intn(*arg):
    return map(int,arg)

def Init(sz):
    '''Turn PyGame on'''
    global screen, screenrect
    pygame.init()
    screen = pygame.display.set_mode(sz)
    screenrect = screen.get_rect()

class GameMode:
    '''Basic game mode class'''
    def __init__(self):
        self.background = pygame.Color("black")

    def Events(self,event):
        '''Event parser'''
        pass

    def Draw(self, screen):
        screen.fill(self.background)

    def Logic(self, screen):
        '''What to calculate'''
        pass

    def Leave(self):
        '''What to do when leaving this mode'''
        pass

    def Init(self):
        '''What to do when entering this mode'''
        pass

class Ball:
    '''Simple ball class'''

    def __init__(self, filename, pos = (0.0, 0.0), speed = (0.0, 0.0)):
        '''Create a ball from image'''
        self.fname = filename
        self.surface = pygame.image.load(filename)
        self.rect = self.surface.get_rect()
        self.speed = speed
        self.pos = pos
        self.newpos = pos
        self.active = True

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def action(self):
        '''Proceed some action'''
        if self.active:
            self.pos = self.pos[0]+self.speed[0], self.pos[1]+self.speed[1]
            self.speed = self.speed[0], self.speed[1] + GRAVITY

    def logic(self, surface):
        x,y = self.pos
        dx, dy = self.speed
        if x < self.rect.width/2:
            x = self.rect.width/2
            dx = -dx
        elif x > surface.get_width() - self.rect.width/2:
            x = surface.get_width() - self.rect.width/2
            dx = -dx
        if y < self.rect.height/2:
            y = self.rect.height/2
            dy = -dy + 2 * GRAVITY
        elif y > surface.get_height() - self.rect.height/2:
            y = surface.get_height() - self.rect.height/2
            dy = -dy + 2 * GRAVITY
        self.pos = x,y
        self.speed = dx,dy
        self.rect.center = intn(*self.pos)

class BetterBall(Ball):
    
    def __init__(self, filename, sizeMod, rotSpeed, pos = (0.0, 0.0), speed = (0.0, 0.0)):
        self.fname = filename
        temp = pygame.image.load(filename)
        self.surface = pygame.transform.scale(temp, 
                                              (int(temp.get_height() * sizeMod), int(temp.get_width() * sizeMod))) 
        self.originalSurface = self.surface
        self.rect = self.surface.get_rect()
        self.speed = speed
        self.pos = pos
        self.newpos = pos
        self.active = True
        self.angle = rotSpeed
    
    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect)
        return rot_image
    
    def action(self):
        self.surface = self.rot_center(self.originalSurface, self.angle)
        self.angle = self.angle + ANGLECONST
        Ball.action(self)   
    
    def logic(self, surface):
        Ball.logic(self, surface) 
           
class Universe:
    '''Game universe'''

    def __init__(self, msec, tickevent = pygame.USEREVENT):
        '''Run a universe with msec tick'''
        self.msec = msec
        self.tickevent = tickevent

    def Start(self):
        '''Start running'''
        pygame.time.set_timer(self.tickevent, self.msec)

    def Finish(self):
        '''Shut down an universe'''
        pygame.time.set_timer(self.tickevent, 0)

class GameWithObjects(GameMode):

    def __init__(self, objects=[]):
        GameMode.__init__(self)
        self.objects = objects
        self.newObjects = []

    def locate(self, pos):
        return [obj for obj in self.objects if obj.rect.collidepoint(pos)]
    
    def scalmul(self, vect1, vect2):
        return vect1[0]*vect2[0] + vect1[1]*vect2[1]
    
    def length(self, vect):
        return math.sqrt(vect[0] * vect[0] + vect[1] * vect[1])
    
    def collide(self, obj1, obj2):
        centvect = (obj1.rect.center[0] - obj2.rect.center[0], obj1.rect.center[1] - obj2.rect.center[1])           
        if self.length(centvect) * 2 < obj1.rect.w + obj2.rect.w and obj1.active and obj2.active:
            dx, dy = obj1.speed[0] - obj2.speed[0], obj1.speed[1] - obj2.speed[1] 
            x, y = obj2.pos[0] - obj1.pos[0], obj2.pos[1] - obj1.pos[1]     
            mul = self.scalmul((dx, dy), (x, y)) / self.length((x, y))
            norm = x / self.length((x, y)), y / self.length((x, y))
            pulse = (dx - norm[0] * mul), (dy - norm[1] * mul)
    
            obj1.speed = pulse[0] + obj2.speed[0], pulse[1] + obj2.speed[1] 
            obj2.speed = norm[0] * mul + obj2.speed[0], norm[1] * mul + obj2.speed[1]
            obj1.rect = obj1.rect.move(-int(round(centvect[0] - centvect[0]/self.length(centvect)*(obj1.rect.w/2 + obj2.rect.w/2 + PIXCONST))),
                             -int(round(centvect[1] - centvect[1]/self.length(centvect)*(obj1.rect.w/2 + obj2.rect.w/2 + PIXCONST))))
            obj2.rect = obj2.rect.move(-int(round(-centvect[0] + centvect[0]/self.length(centvect)*(obj1.rect.w/2 + obj2.rect.w/2 + PIXCONST))),
                              -int(round(-centvect[1] + centvect[1]/self.length(centvect)*(obj1.rect.w/2 + obj2.rect.w/2 + PIXCONST))))
            obj1.action()
            obj2.action()
        return obj1, obj2
         
    def Events(self, event):
        GameMode.Events(self, event)
        if event.type == Game.tickevent:
            for i in xrange(len(self.objects)):
                for j in xrange(len(self.objects)):
                    if i != j:
                        x, y = self.collide(self.objects[i], self.objects[j])
                        self.objects[i] = x
                        self.objects[j] = y
            for obj in self.objects:
                obj.action()
                       
            

    def Logic(self, surface):
        GameMode.Logic(self, surface)
        for obj in self.objects:
            obj.logic(surface)

    def Draw(self, surface):
        GameMode.Draw(self, surface)
        for obj in self.objects:
            obj.draw(surface)

class GameWithDnD(GameWithObjects):
    
    def __init__(self, *argp, **argn):
        GameWithObjects.__init__(self, *argp, **argn)
        self.oldpos = 0,0
        self.drag = None
        self.ballPressed = False
    
    def Events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = self.locate(event.pos)
            if click:
                self.drag = click[0]
                self.drag.active = False
                self.oldpos = event.pos
                self.ballPressed = True
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                if self.drag:
                    self.drag.pos = event.pos
                    self.drag.speed = event.rel
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.ballPressed:
                self.drag.active = True
                self.ballPressed = False
            self.drag = None
        GameWithObjects.Events(self, event)

Init(SIZE)
Game = Universe(20)

Run = GameWithDnD()
for i in xrange(BALLNUMBER):
    x, y = random.randrange(screenrect.w), random.randrange(screenrect.h)
    dx, dy = 0.1+random.random()*BALLNUMBER, 0.1+random.random()*BALLNUMBER
    size = random.random() / 2 + 0.5
    speed = random.randint(0, ANGLECONST)
    Run.objects.append(BetterBall("ball.gif", size, speed, (x,y),(dx,dy)))

Game.Start()
Run.Init()
again = True
while again:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        again = False
    Run.Events(event)
    Run.Logic(screen)
    Run.Draw(screen)
    pygame.display.flip()
Game.Finish()
pygame.quit()
