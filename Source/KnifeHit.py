import pygame
import math

import random
import time

#------------------------------------------------------------------------------------------------------

pygame.init()
screenWidth = 400
screenHeight = 800
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Knife Hit')

#remove window icon
transparent_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
transparent_surface = pygame.image.load('./Sprites/Apple.png').convert_alpha()
pygame.display.set_icon(transparent_surface)

#------------------------------------------------------------------------------------------------------

def normalizeVector(v):
    mag = math.sqrt(v[0] * v[0] + v[1] * v[1])
    return (v[0] / mag, v[1] / mag)

def getAngleBetweenVectors(v1, v2):

    # Calculate dot product
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    
    # Calculate magnitudes
    magnitude_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
    magnitude_v2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    # Check for zero vectors
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0
    
    # Calculate cosine of angle
    cos_theta = dot_product / (magnitude_v1 * magnitude_v2)
    
    # Clip to valid range [-1, 1] to handle floating point errors
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    # Calculate angle using arccos and convert to degrees
    angle = math.degrees(math.acos(cos_theta))
    
    return angle

def GetClockwiseAngle(frm, to):
    import numpy as np

    # Normalize vectors
    
    frm_norm = frm / np.linalg.norm(frm)
    if np.linalg.norm(to) != 0:
        to_norm = to / np.linalg.norm(to)
    else:
        to_norm = [0, 1]
    
    # Calculate angle using dot product
    cos_angle = np.dot(frm_norm, to_norm)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle_rad = np.arccos(cos_angle)
    angle_deg = np.degrees(angle_rad)
    
    # Determine direction (clockwise vs counterclockwise)
    determinant = frm_norm[0]*to_norm[1] - frm_norm[1]*to_norm[0]
    return angle_deg if determinant > 0 else 360 - angle_deg

def vectorDotProduct(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def angleToVector(angleDeg):
    import numpy as np

    # Convert angle to radians
    angleRad = math.radians(angleDeg)
    
    # Calculate normalized vector components
    x = math.cos(angleRad)
    y = math.sin(angleRad)
    
    return np.array([x, y])

def rotateVector(v, angleDeg):
    import numpy as np

    # Convert angle to radians
    angleRad = math.radians(angleDeg)
    
    # Create rotation matrix
    cos_angle = math.cos(angleRad)
    sin_angle = math.sin(angleRad)
    rotation_matrix = np.array([[cos_angle, -sin_angle],[sin_angle, cos_angle]])
    
    # Apply rotation
    rotated_vector = np.dot(rotation_matrix, v)
    
    return rotated_vector
#------------------------------------------------------------------------------------------------------

class Log(pygame.sprite.Sprite):
    def __init__(self, gs, x, y):
        self.gs = gs
        self.x = x
        self.y = y

        self.size = 100

        self.speed = random.uniform(0.07, 0.14)
        self.dir = random.choice([1, -1])
        self.rotationSpeed = self.speed * self.dir

        self.angle = 0

        self.dead = False

        #load images
        super().__init__()

        topImageNames = ["BrightLogTop.png", "MediumLogTop.png", "DarkLogTop.png"]
        bottomImageNames = ["BrightLogBottom.png", "MediumLogBottom.png", "DarkLogBottom.png"]
        randomLogTypeIndex = random.randint(0, len(topImageNames) - 1)

        self.logTop = orderedSpirte(self, self.gs, topImageNames[randomLogTypeIndex], 0, 0, self.size*2, self.size*2, 4)
        self.logBottom = orderedSpirte(self, self.gs, bottomImageNames[randomLogTypeIndex], 15, 0, self.size*2, self.size*2, 2)
        self.logTopOutline = orderedSpirte(self, self.gs, "LogOutlineBlack.png", 0, 0, self.size*2 + 5, self.size*2 + 5, 1)
        self.logBottomOutline = orderedSpirte(self, self.gs, "LogOutlineBlack.png", 15, 0, self.size*2 + 5, self.size*2 + 5, 1)
        self.logShadow = orderedSpirte(self, self.gs, "LogShadow.png", 35, 0, self.size*2, self.size*2, 0)

    def updateSprites(self):
        self.logTop.update()
        self.logBottom.update()
        self.logTopOutline.update()
        self.logBottomOutline.update()
        self.logShadow.update()

class Knife(pygame.sprite.Sprite):
    def __init__(self, gs, x, y):
        self.gs = gs
        self.gs.knives.append(self)

        self.x = x
        self.y = y
        
        self.vel = (0, 0)

        #bool to only throw knife once
        self.hasThrown = False

        #vars for after collision, vectolog for position relative to log
        self.hasHit = False
        self.vecToLog = None

        self.dead = False

        #load images
        super().__init__()
        self.angle = 0

        self.knifeSprite = orderedSpirte(self, self.gs, "Knife.png", 0, 0, 20, 20 * 3.387, 3)
        self.outlineSprite = orderedSpirte(self, self.gs, "KnifeOutlineBlack.png", 0, 0, 24, 24 * 2.887, 1)
        self.shadowSprite = orderedSpirte(self, self.gs, "KnifeShadow.png", 35, 0, 20, 20 * 3.387, 0)

    def updateSprites(self):
        self.knifeSprite.update()
        self.outlineSprite.update()
        self.shadowSprite.update()

    def move(self, dTs):
        if self.hasHit == False:
            self.x = self.x + self.vel[0] * dTs
            self.y = self.y + self.vel[1] * dTs
        else:
            #rotate by constant log rotaiton
            self.angle += self.gs.log.rotationSpeed * dTs
            self.vecToLog = rotateVector(self.vecToLog, self.gs.log.rotationSpeed * dTs)

            self.x = self.gs.log.x - self.vecToLog[0]
            self.y = self.gs.log.y - self.vecToLog[1]

    def throw(self, force):
        if self.hasThrown == False:
            self.vel = (self.vel[0] + force[0], self.vel[1] + force[1])
            self.hasThrown = True

    def collide(self):
        #collide with log
        if self.hasHit == False:
            #get vector to log
            vecToLog = (self.gs.log.x - self.x, self.gs.log.y - self.y)
            distToLog = math.sqrt(vecToLog[0] * vecToLog[0] + vecToLog[1] * vecToLog[1])

            if distToLog < self.gs.log.size + 10:
                self.hasHit = True
                self.vel = (0, 0)
                self.vecToLog = vecToLog

            #collide with other knives
            for knife in self.gs.knives:
                if knife != self and knife.hasHit == True:
                    vecToKnife = (knife.x - self.x, knife.y - self.y)
                    distToKnife = math.sqrt(vecToKnife[0] * vecToKnife[0] + vecToKnife[1] * vecToKnife[1])
                    if distToKnife < 10:
                        self.dead = True

class Apple(pygame.sprite.Sprite):
    def __init__(self, gs):
        self.gs = gs
        self.gs.apples.append(self)

        #get initial position relative to log
        self.angle = random.randint(0, 360)
        self.vecToLog = angleToVector(self.angle) * (gs.log.size + 15)
        self.angle -= 90

        self.x = gs.log.x - self.vecToLog[0]
        self.y = gs.log.y - self.vecToLog[1]

        self.dead = False

        #load images
        super().__init__()

        tops = ["Apple.png", "Orange.png", "Banana.png"]
        outlines = ["AppleOutlineBlack.png", "OrangeOutlineBlack.png", "BananaOutlineBlack.png"]
        shadows = ["AppleShadow.png", "OrangeShadow.png", "BananaShadow.png"]
        randomFruitTypeIndex = random.randint(0, len(tops) - 1)

        self.topImage = orderedSpirte(self, self.gs, tops[randomFruitTypeIndex], 0, 0, 35, 35, 6)
        self.outline = orderedSpirte(self, self.gs, outlines[randomFruitTypeIndex], 0, 0, 40, 40, 5)
        self.shadow = orderedSpirte(self, self.gs, shadows[randomFruitTypeIndex], 35, 0, 35, 35, 0)

    def updateSprites(self):
        self.topImage.update()
        self.outline.update()
        self.shadow.update()

    def move(self, dTs):
        #rotate by constant log rotaiton
        self.angle += self.gs.log.rotationSpeed * dTs
        self.vecToLog = rotateVector(self.vecToLog, self.gs.log.rotationSpeed * dTs)
        self.x = self.gs.log.x - self.vecToLog[0]
        self.y = self.gs.log.y - self.vecToLog[1]

    def collide(self):
        #collide with knives
        for knife in self.gs.knives:
            vecToKnife = (knife.x - self.x, knife.y - self.y)
            distToKnife = math.sqrt(vecToKnife[0] * vecToKnife[0] + vecToKnife[1] * vecToKnife[1])
            if distToKnife < 25:
                self.dead = True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

class KnifeBar(pygame.sprite.Sprite):
    def __init__(self, gs, x, y, numOfKnives):
        self.gs = gs
        self.x = x
        self.y = y

        self.maxKnives = numOfKnives
        self.knivesLeft = numOfKnives

        self.angle = 160
        self.dead = False

        #create knife slot images
        self.spacing = 20
        self.emptySlotSprites = []
        self.fullSlotSprites = []
        for i in range(self.maxKnives):
            emptySlot = orderedSpirte(self, self.gs, "KnifeShadow.png", 15, self.spacing*i - (self.maxKnives * self.spacing) / 2 + self.spacing / 2, 15, 15  * 3.387, 100)
            self.emptySlotSprites.append(emptySlot)

            fullSlot = orderedSpirte(self, self.gs, "Knife.png", 0, self.spacing*i - (self.maxKnives * self.spacing) / 2 + self.spacing / 2, 15, 15  * 3.387, 101)
            self.fullSlotSprites.append(fullSlot)

    def updateSprites(self):
        for sprite in self.emptySlotSprites:
            sprite.update()

        for i in range(self.maxKnives):
            self.fullSlotSprites[i].update()
            
            if i >= self.knivesLeft:
                self.fullSlotSprites[i].doBlit = False
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

class orderedSpirte:
    def __init__(self, parent, gs, fileName, yOffset, xOffset, width, height, zLayer):
        self.gs = gs
        self.gs.orderedSprites.append(self)
        self.parent = parent

        self.fullPath = './Sprites/' + fileName
        self.yOffset = yOffset
        self.xOffset = xOffset
        self.width = width
        self.height = height
        self.zLayer = zLayer

        self.doBlit = True

        self.originalImage = pygame.image.load(self.fullPath).convert_alpha()
        self.originalImage = pygame.transform.scale(self.originalImage, (self.width, self.height))
        self.image = self.originalImage
        self.rect = self.image.get_rect(center=(self.parent.x + self.xOffset, self.parent.y + self.yOffset))

    def update(self):
        self.image = pygame.transform.rotate(self.originalImage, -self.parent.angle)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.parent.x + self.xOffset
        self.rect.centery = self.parent.y + self.yOffset

def blitOrderedSprites():
    gs.orderedSprites.sort(key=lambda x: x.zLayer)

    #blit ordered list of sprites
    for sprite in gs.orderedSprites:
        if sprite.doBlit == True:
            screen.blit(sprite.image, sprite.rect)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

class GameState():
    def __init__(self):
        #initialize all objects for one scene

        #initialize transition
        self.transition = gameSceneTransition(self)

        self.orderedSprites = []
        self.knives = []
        self.apples = []

        #initialize objects
        self.log = Log(self, 200, 200)

        #spawn apples, get number of available knives
        self.numOfApples = random.randint(2, 5)
        for i in range(self.numOfApples):
            newApple = Apple(self)

        #initialize knife bar
        self.knifeBar = KnifeBar(self, 200, 700, int(self.numOfApples * 1.5))

        #spawn initial knife 
        self.knifeThrowForce = (0, -0.7)
        newKnife = Knife(self, 200, 600)

    def restartScene(self):
        #re initialize all objects for new scene

        #initialize transition
        self.transition = gameSceneTransition(self)

        self.orderedSprites = []
        self.knives = []
        self.apples = []

        #initialize objects
        self.log = Log(self, 200, 200)

        #spawn apples, get number of available knives
        self.numOfApples = random.randint(2, 5)
        for i in range(self.numOfApples):
            newApple = Apple(self)

        #initialize knife bar
        self.knifeBar = KnifeBar(self, 200, 700, int(self.numOfApples * 1.5))

        #spawn initial knife 
        self.knifeThrowForce = (0, -0.7)
        newKnife = Knife(self, 200, 600)

class gameSceneTransition():
    def __init__(self, gs):
        self.gs = gs
        
        self.a = 255
        self.ta = 0

        self.overlaySurface = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
        self.overlaySurface.fill((0, 0, 0, self.a))  # RGBA: black with 50% opacity

    def updateOverlay(self):
        #interpolate towards target a
        self.a = self.a + 0.01*(self.ta - self.a) + 0.1

        if self.a > 255:
            self.a = 255
        if self.a < 0:
            self.a = 0

        self.overlaySurface.fill((0, 0, 0, int(self.a)))  # RGBA: black with 50% opacity
        screen.blit(self.overlaySurface, (0, 0))

    def outTransition(self):
        #set target a to black
        self.ta = 255

        #restart scene
        if self.a == self.ta:
            self.gs.restartScene()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def checkForWin():
    #check if any apples left
    if len(gs.apples) == 0:
        #Win
        gs.transition.outTransition()

    #check if no more knives and all knives have ghit the log
    else:
        if gs.knifeBar.knivesLeft <= 0:

            hitKnives = 0
            for knife in gs.knives:
                if knife.hasHit == True:
                    hitKnives += 1

            if hitKnives == len(gs.knives):
                #Lose
                gs.transition.outTransition()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

#initialize vars as game state
gs = GameState()

#get delta time initial ticks
prevT = pygame.time.get_ticks()

running = True
while running:

    #update delta time
    currT = pygame.time.get_ticks()
    dTms = currT - prevT
    dTs = dTms

    # Fill screen
    screen.fill((30, 30, 30))

    # Handle inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for knife in gs.knives:
                    knife.throw(gs.knifeThrowForce)

                #spawn new knife 
                gs.knifeBar.knivesLeft -= 1
                if gs.knifeBar.knivesLeft > 0:
                    newKnife = Knife(gs, 200, 600)

    #update log
    gs.log.angle += gs.log.rotationSpeed * dTs
    gs.log.updateSprites()

    #update knives
    for knife in gs.knives:
        knife.move(dTs)
        knife.collide()
        knife.updateSprites()

    #update apples
    for apple in gs.apples:
        apple.move(dTs)
        apple.collide()
        apple.updateSprites()

    #update knife bar
    gs.knifeBar.updateSprites()

    #delete dead objects
    gs.apples = [apple for apple in gs.apples if apple.dead == False]
    gs.knives = [knife for knife in gs.knives if knife.dead == False]
    gs.orderedSprites = [ordrdSprt for ordrdSprt in gs.orderedSprites if ordrdSprt.parent.dead == False]

    #check for win/lose condition, (if statement to allow for close button quiting)
    checkForWin()

    #draw ordered sprites
    blitOrderedSprites()

    #update transition animation
    gs.transition.updateOverlay()

    # Update the display
    pygame.display.flip()

    #update delta time
    prevT = currT

# Quit Pygame
pygame.quit()
