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
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

class Log(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

        self.size = 100
        self.rotationSpeed = 0.1
        self.angle = 0

        super().__init__()

        #load images
        topImageNames = ["BrightLogTop.png", "MediumLogTop.png", "DarkLogTop.png"]
        bottomImageNames = ["BrightLogBottom.png", "MediumLogBottom.png", "DarkLogBottom.png"]
        randomLogTypeIndex = random.randint(0, len(topImageNames) - 1)
        imageNames = [topImageNames[randomLogTypeIndex], bottomImageNames[randomLogTypeIndex], "LogOutlineBlack.png", "LogOutlineBlack.png", "LogShadow.png"]
        imageYOffsets = [0, 15, 0, 15, 35]
        self.zLayers = [4, 2, 1, 1, 0]
        imageSizes = [self.size*2, self.size*2, self.size*2 + 5, self.size*2 + 5, self.size*2]
        
        self.originalImages = []
        self.images = []
        self.imageRects = []

        for i in range(len(imageNames)):
            fullpath = './../Sprites/' + imageNames[i]
            self.originalImages.append(pygame.image.load(fullpath).convert_alpha())
            self.originalImages[i] = pygame.transform.scale(self.originalImages[i], (imageSizes[i], imageSizes[i]))
            self.images.append(self.originalImages[i])
            self.imageRects.append(self.images[i].get_rect(center=(self.x, self.y + imageYOffsets[i])))

    def queueBlit(self):
        #draw all images in reverse order for z order
        for i in reversed(range(len(self.originalImages))):
            self.images[i] = pygame.transform.rotate(self.originalImages[i], -self.angle)
            self.imageRects[i] = self.images[i].get_rect(center=self.imageRects[i].center)

            #screen.blit(self.images[i], self.imageRects[i])
            newSprite = orderedSpirte(self.images[i], self.imageRects[i], self.zLayers[i])

class Knife(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        knives.append(self)

        self.x = x
        self.y = y
        self.color = color
        
        self.vel = (0, 0)

        #bool to only throw knife once
        self.hasThrown = False

        #vars for after collision, vectolog for position relative to log
        self.hasHit = False
        self.vecToLog = None

        #load images
        super().__init__()
        self.angle = 0
        imageNames = ["Knife.png", "KnifeOutlineBlack.png", "KnifeShadow.png"]
        self.imageYOffsets = [0, 0, 35]
        imageWidths = [20, 24, 20]
        self.zLayers = [3, 1, 0]
        imageHeights = [imageWidths[0] * 3.387, imageWidths[1] * 2.887, imageWidths[0] * 3.387]

        self.originalImages = []
        self.images = []
        self.imageRects = []

        for i in range(len(imageNames)):
            fullpath = './../Sprites/' + imageNames[i]
            self.originalImages.append(pygame.image.load(fullpath).convert_alpha())
            self.originalImages[i] = pygame.transform.scale(self.originalImages[i], (imageWidths[i], imageHeights[i]))
            self.images.append(self.originalImages[i])
            self.imageRects.append(self.images[i].get_rect(center=(self.x, self.y + self.imageYOffsets[i])))

    def queueBlit(self):
        #draw all images in reverse order for z order
        for i in reversed(range(len(self.originalImages))):
            self.images[i] = pygame.transform.rotate(self.originalImages[i], -self.angle)
            self.imageRects[i] = self.images[i].get_rect(center=self.imageRects[i].center)

            #screen.blit(self.images[i], self.imageRects[i])
            newSprite = orderedSpirte(self.images[i], self.imageRects[i], self.zLayers[i])

    def move(self, dTs):
        if self.hasHit == False:
            self.x = self.x + self.vel[0] * dTs
            self.y = self.y + self.vel[1] * dTs
            
            #move image rects to self xy
            for i in range(len(self.imageRects)):
                self.imageRects[i].x = self.x - self.imageRects[i].width/2
                self.imageRects[i].y = self.y + self.imageYOffsets[i] - self.imageRects[i].height/2 

        else:
            #rotate by constant log rotaiton
            self.angle += log.rotationSpeed * dTs
            self.vecToLog = rotateVector(self.vecToLog, log.rotationSpeed * dTs)

            self.x = log.x - self.vecToLog[0]
            self.y = log.y - self.vecToLog[1]

            #move image rects to self xy
            for i in range(len(self.imageRects)):
                self.imageRects[i].x = self.x - self.imageRects[i].width/2
                self.imageRects[i].y = self.y - self.imageRects[i].height/2 + self.imageYOffsets[i]

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
                        global running
                        running = False

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

class orderedSpirte:
    def __init__(self, image, rect, zLayer):
        orderedSprites.append(self)
        self.image = image
        self.rect = rect
        self.zLayer = zLayer

orderedSprites = []

def blitImages(orderedSprites):
    #sort sprites by z layer
    orderedSprites.sort(key=lambda x: x.zLayer)

    #blit ordered list of sprites
    for sprite in orderedSprites:
        screen.blit(sprite.image, sprite.rect)

    #reset ordered arrays for next frame appending
    return []

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

knifeThrowForce = (0, -0.7)

knives = []

knif = Knife(200, 600, (255, 255, 255))
log = Log(200, 200, (255, 255, 255))

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
                newKnife = Knife(200, 600, (255, 255, 255))

    log.angle += log.rotationSpeed * dTs

    for knife in knives:
        knife.move(dTs)
        knife.collide()
        knife.queueBlit()

    log.queueBlit()

    #draw images in z order
    orderedSprites = blitImages(orderedSprites)

    # Update the display
    pygame.display.flip()

    #update delta time
    prevT = currT

# Quit Pygame
pygame.quit()
