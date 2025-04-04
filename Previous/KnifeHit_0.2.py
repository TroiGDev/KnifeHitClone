import pygame
import math

import random

#------------------------------------------------------------------------------------------------------

pygame.init()
screenWidth = 400
screenHeight = 800
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Knife Hit')

#remove window icon
transparent_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
transparent_surface = pygame.image.load('./../Sprites/Apple.png').convert_alpha()
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
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.size = 100
        self.rotationSpeed = 0.1
        self.angle = 0

        self.dead = False

        #load images
        super().__init__()

        topImageNames = ["BrightLogTop.png", "MediumLogTop.png", "DarkLogTop.png"]
        bottomImageNames = ["BrightLogBottom.png", "MediumLogBottom.png", "DarkLogBottom.png"]
        randomLogTypeIndex = random.randint(0, len(topImageNames) - 1)

        self.logTop = orderedSpirte(self, topImageNames[randomLogTypeIndex], 0, 0, self.size*2, self.size*2, 4)
        self.logBottom = orderedSpirte(self, bottomImageNames[randomLogTypeIndex], 15, 0, self.size*2, self.size*2, 2)
        self.logTopOutline = orderedSpirte(self, "LogOutlineBlack.png", 0, 0, self.size*2 + 5, self.size*2 + 5, 1)
        self.logBottomOutline = orderedSpirte(self, "LogOutlineBlack.png", 15, 0, self.size*2 + 5, self.size*2 + 5, 1)
        self.logShadow = orderedSpirte(self, "LogShadow.png", 35, 0, self.size*2, self.size*2, 0)

    def updateSprites(self):
        self.logTop.update()
        self.logBottom.update()
        self.logTopOutline.update()
        self.logBottomOutline.update()
        self.logShadow.update()

class Knife(pygame.sprite.Sprite):
    def __init__(self, x, y):
        knives.append(self)

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

        self.knifeSprite = orderedSpirte(self, "Knife.png", 0, 0, 20, 20 * 3.387, 3)
        self.outlineSprite = orderedSpirte(self, "KnifeOutlineBlack.png", 0, 0, 24, 24 * 2.887, 1)
        self.shadowSprite = orderedSpirte(self, "KnifeShadow.png", 35, 0, 20, 20 * 3.387, 0)

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
            self.angle += log.rotationSpeed * dTs
            self.vecToLog = rotateVector(self.vecToLog, log.rotationSpeed * dTs)

            self.x = log.x - self.vecToLog[0]
            self.y = log.y - self.vecToLog[1]

    def throw(self, force):
        if self.hasThrown == False:
            self.vel = (self.vel[0] + force[0], self.vel[1] + force[1])
            self.hasThrown = True

    def collide(self):
        #collide with log
        if self.hasHit == False:
            #get vector to log
            vecToLog = (log.x - self.x, log.y - self.y)
            distToLog = math.sqrt(vecToLog[0] * vecToLog[0] + vecToLog[1] * vecToLog[1])

            if distToLog < log.size + 10:
                self.hasHit = True
                self.vel = (0, 0)
                self.vecToLog = vecToLog

            #collide with other knives
            for knife in knives:
                if knife != self and knife.hasHit == True:
                    vecToKnife = (knife.x - self.x, knife.y - self.y)
                    distToKnife = math.sqrt(vecToKnife[0] * vecToKnife[0] + vecToKnife[1] * vecToKnife[1])
                    if distToKnife < 10:
                        self.dead = True

class Apple(pygame.sprite.Sprite):
    def __init__(self):
        apples.append(self)

        #get initial position relative to log
        self.angle = random.randint(0, 360)
        self.vecToLog = angleToVector(self.angle) * (log.size + 15)
        self.angle -= 90

        self.x = log.x - self.vecToLog[0]
        self.y = log.y - self.vecToLog[1]

        self.dead = False

        #load images
        super().__init__()

        self.appleSprite = orderedSpirte(self, "Apple.png", 0, 0, 35, 35, 6)
        self.outlineSprite = orderedSpirte(self, "AppleOutlineBlack.png", 0, 0, 40, 40, 5)
        self.shadowSprite = orderedSpirte(self, "AppleShadow.png", 35, 0, 35, 35, 0)

    def updateSprites(self):
        self.appleSprite.update()
        self.outlineSprite.update()
        self.shadowSprite.update()

    def move(self, dTs):
        #rotate by constant log rotaiton
        self.angle += log.rotationSpeed * dTs
        self.vecToLog = rotateVector(self.vecToLog, log.rotationSpeed * dTs)
        self.x = log.x - self.vecToLog[0]
        self.y = log.y - self.vecToLog[1]

    def collide(self):
        #collide with knives
        for knife in knives:
            vecToKnife = (knife.x - self.x, knife.y - self.y)
            distToKnife = math.sqrt(vecToKnife[0] * vecToKnife[0] + vecToKnife[1] * vecToKnife[1])
            if distToKnife < 25:
                self.dead = True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

class KnifeBar(pygame.sprite.Sprite):
    def __init__(self, x, y, numOfKnives):
        self.x = x
        self.y = y

        self.maxKnives = numOfKnives
        self.knivesLeft = numOfKnives

        print(self.maxKnives)

        self.angle = 160
        self.dead = False

        #create knife slot images
        self.spacing = 20
        self.emptySlotSprites = []
        self.fullSlotSprites = []
        for i in range(self.maxKnives):
            emptySlot = orderedSpirte(self, "KnifeShadow.png", 15, self.spacing*i - (self.maxKnives * self.spacing) / 2 + self.spacing / 2, 15, 15  * 3.387, 100)
            self.emptySlotSprites.append(emptySlot)

            fullSlot = orderedSpirte(self, "Knife.png", 0, self.spacing*i - (self.maxKnives * self.spacing) / 2 + self.spacing / 2, 15, 15  * 3.387, 101)
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
    def __init__(self, parent, fileName, yOffset, xOffset, width, height, zLayer):
        
        orderedSprites.append(self)
        self.parent = parent

        self.fullPath = './../Sprites/' + fileName
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
    orderedSprites.sort(key=lambda x: x.zLayer)

    #blit ordered list of sprites
    for sprite in orderedSprites:
        if sprite.doBlit == True:
            screen.blit(sprite.image, sprite.rect)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def checkForWin():
    #check if any apples left
    if len(apples) == 0:
        #Win
        print("Win!")
        return False

    #check if no more knives and all knives have ghit the log
    else:
        if knifeBar.knivesLeft <= 0:

            hitKnives = 0
            for knife in knives:
                if knife.hasHit == True:
                    hitKnives += 1

            if hitKnives == len(knives):
                #Lose
                print("Lose!")
                return False
            
    return True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

orderedSprites = []

knives = []
apples = []

#initialize objects
log = Log(200, 200)

#spawn apples, get number of available knives
numOfApples = random.randint(2, 5)
for i in range(numOfApples):
    newApple = Apple()

#initialize knife bar
knifeBar = KnifeBar(200, 700, int(numOfApples * 1.5))

#spawn initial knife 
knifeThrowForce = (0, -0.7)
newKnife = Knife(200, 600)

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
                for knife in knives:
                    knife.throw(knifeThrowForce)

                #spawn new knife 
                knifeBar.knivesLeft -= 1
                if knifeBar.knivesLeft > 0:
                    newKnife = Knife(200, 600)
                    print(knifeBar.knivesLeft)

    #update log
    log.angle += log.rotationSpeed * dTs
    log.updateSprites()

    #update knives
    for knife in knives:
        knife.move(dTs)
        knife.collide()
        knife.updateSprites()

    #update apples
    for apple in apples:
        apple.move(dTs)
        apple.collide()
        apple.updateSprites()

    #update knife bar
    knifeBar.updateSprites()

    #delete dead objects
    apples = [apple for apple in apples if apple.dead == False]
    knives = [knife for knife in knives if knife.dead == False]
    orderedSprites = [ordrdSprt for ordrdSprt in orderedSprites if ordrdSprt.parent.dead == False]

    #check for win/lose condition, (if statement to allow for close button quiting)
    if running == True:
        running = checkForWin()

    #draw ordered sprites
    blitOrderedSprites()

    # Update the display
    pygame.display.flip()

    #update delta time
    prevT = currT

# Quit Pygame
pygame.quit()
