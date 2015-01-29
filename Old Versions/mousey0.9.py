# Mousey (a Nibbles clone)
# By Caroline Larsen
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, math, time, sys
from pygame.locals import *

TITLE = 'Mousie! v0.9'

GAME_FPS = 15.0
TITLE_FPS = 15.0
WINDOWWIDTH = 800
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)
MAXDISTANCE = math.sqrt ( CELLWIDTH ** 2 + CELLHEIGHT ** 2 )

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
DARKYELLOW= (190, 190,   0)
GRAY      = ( 95,  95,   95)
YELLOW    = (255, 255,   0)
BLUE      = (  0,   0,   175)
BGCOLOR   = BLACK

UP        = 'up'
DOWN      = 'down'
LEFT      = 'left'
RIGHT     = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()    
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption(TITLE)
    showStartScreen()
 
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Initialize game stuff.
    score = 0
    wonSound = pygame.mixer.Sound('Meow.wav')
    navSound = pygame.mixer.Sound('Continuous.ogg')
    currentTime = time.time()
    gameTimer = currentTime
    winTimer = currentTime
    averageWinTime = -1.0
    keyState = {'left' : False, 'right' : False, 'up' : False, 'down' : False}

    # Set a random start point for the mouse somewhere near the center.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    mouseCoord = {'x': startx,'y': starty}

    # Set the cheese in a random place.
    cheese = getRandomLocation()

    # Start continuous navigation sound at low volume
    navSound.set_volume (0.1)
    navSound.play(-1)

    while True: # The main game loop

        # Play a sound every interval
        currentTime = time.time()       

        # Process input and update display no faster than GAME_FPS
        if time.time() - gameTimer >= 1.0 / GAME_FPS:
            gameTimer = time.time()
            
            # Process all user input events.
            for event in pygame.event.get():           
                if event.type == KEYDOWN or event.type == KEYUP:
                    keyDown = (event.type == KEYDOWN)
                    if (event.key == K_LEFT or event.key == K_a):
                        keyState['left'] = keyDown              
                    elif (event.key == K_RIGHT or event.key == K_d):
                        keyState['right'] = keyDown
                    elif (event.key == K_UP or event.key == K_w):
                        keyState['up'] = keyDown
                    elif (event.key == K_DOWN or event.key == K_s):
                        keyState['down'] = keyDown
                    elif (event.key == K_ESCAPE):
                        terminate()
                elif event.type == QUIT:
                    terminate()
          
            # Did the mouse eat the cheese?
            if mouseCoord['x'] == cheese['x'] and mouseCoord['y'] == cheese['y']:
                
                # Get the winning time and compute the running average win time
                winTime = time.time() - winTimer
                if averageWinTime > 0.0:
                    averageWinTime = (averageWinTime + winTime) / 2.0
                else:
                    averageWinTime = winTime

                # Reset the win timer
                winTimer = time.time()
                print winTime
                print averageWinTime

                # Play winning sound and update the score
                wonSound.play()
                score = score + 1

                # Move the cheese
                cheese = getRandomLocation()
               
            # Move the mouse by updating its position based on the key state.
            if keyState['left'] and mouseCoord [ 'x' ] > 0:
                mouseCoord['x'] = mouseCoord['x'] - 1
            if keyState['right'] and mouseCoord [ 'x' ] < CELLWIDTH - 1:
                mouseCoord['x'] = mouseCoord['x'] + 1
            if keyState['up'] and mouseCoord [ 'y' ] > 0:
                mouseCoord['y'] = mouseCoord['y'] - 1
            if keyState['down'] and mouseCoord[ 'y' ] < CELLHEIGHT - 1:
                mouseCoord['y'] = mouseCoord['y'] + 1
    
            # Find the distance between the mouse and the cheese.
            distance = math.sqrt ((mouseCoord['x'] - cheese['x']) ** 2 + (mouseCoord['y'] - cheese['y']) ** 2)

            # Determine the volume level based on distance
            #volumeLevel = 1.0 - distance / MAXDISTANCE
            #volumeLevel = 1.0 / (distance / MAXDISTANCE * 9.0 + 1.0)
            volumeLevel = 1.0 / ((distance / MAXDISTANCE * 6.0 + 1.0) ** 2.0)
            navSound.set_volume (volumeLevel)

            # Draw everything
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawMouse(mouseCoord)
            drawCheese(cheese)
            drawScore(score, distance, winTimer)
            pygame.display.update()


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render(TITLE, True, GRAY, BLUE)
    titleSurf2 = titleFont.render(TITLE, True, DARKYELLOW)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(TITLE_FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return


def drawScore(score, distance, timer):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 180, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)
    
    distSurf = BASICFONT.render('Distance: %s' % round(distance,1), True, WHITE)
    distRect = distSurf.get_rect()
    distRect.topleft = (WINDOWWIDTH - 180, 30)
    DISPLAYSURF.blit(distSurf, distRect)

    timeSurf = BASICFONT.render('Time: %s secs' % round(timer,1), True, WHITE)
    timeRect = timeSurf.get_rect()
    timeRect.topleft = (WINDOWWIDTH - 180, 50)
    DISPLAYSURF.blit(timeSurf, timeRect)


def drawMouse(mouseCoord):
    x = mouseCoord['x'] * CELLSIZE
    y = mouseCoord['y'] * CELLSIZE
    mouseSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, WHITE, mouseSegmentRect)
    mouseInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
    pygame.draw.rect(DISPLAYSURF, GRAY, mouseInnerSegmentRect)


def drawCheese(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    cheeseRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, YELLOW, cheeseRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
