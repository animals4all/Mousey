# Mousey (a Nibbles clone)
# By Caroline Larsen
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, math, time, sys
from pygame.locals import *

TITLE = 'Mousie! v1.0'

GAME_FPS = 15.0
TITLE_FPS = 15.0
SPEAK_FPS = 1.0
CELLSIZE = 50
WINDOWWIDTH = CELLSIZE * 20
WINDOWHEIGHT = CELLSIZE * 16 
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
GRAY      = ( 95,  95,  95)
YELLOW    = (255, 255,   0)
BLUE      = (  0,   0, 175)
BGCOLOR   = BLACK

UP        = 'up'
DOWN      = 'down'
LEFT      = 'left'
RIGHT     = 'right'

NAVMODES = 3
class NavMode: Sound, Temperature, Direction = range(NAVMODES)

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
    justWon = True
    pauseGame = False

    wonVolume = 0.2
    wonSound = pygame.mixer.Sound('Coin.ogg')
    wonSound.set_volume (wonVolume)

    spokenVolume = 0.3
    hotterSound = pygame.mixer.Sound('Hotter.wav')
    hotterSound.set_volume(spokenVolume)
    colderSound = pygame.mixer.Sound('Colder.wav')
    colderSound.set_volume(spokenVolume)
    leftSound = pygame.mixer.Sound('Left.wav')
    leftSound.set_volume(spokenVolume)
    rightSound = pygame.mixer.Sound('Right.wav')
    rightSound.set_volume(spokenVolume)
    upSound = pygame.mixer.Sound('Up.wav')
    upSound.set_volume(spokenVolume)
    downSound = pygame.mixer.Sound('Down.wav')
    downSound.set_volume(spokenVolume)

    navMode = NavMode.Sound
    navSound = pygame.mixer.Sound('Continuous1min.ogg')
    if navMode == NavMode.Sound:
        navVolumeLevel = 0.1
    else:
        navVolumeLevel = 0.0
    navSound.set_volume(navVolumeLevel)
    navSound.play(-1)

    gameTimer = speakTimer = winTimer = time.time()
    averageWinTime = -2.0
    keyState = {LEFT : False, RIGHT : False, UP : False, DOWN : False}

    # Set a random start point for the mouse somewhere near the center.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    mouseCoord = {'x': startx,'y': starty}

    # Set the cheese in a random place.
    cheese = getRandomLocation(mouseCoord)

    # Find the distance between the mouse and the cheese.
    distance = math.sqrt ((mouseCoord['x'] - cheese['x']) ** 2 + (mouseCoord['y'] - cheese['y']) ** 2)
    prevDistance = distance

    while True: # The main game loop

        if pauseGame:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        pauseGame = False
                        keyState = {LEFT : False, RIGHT : False, UP : False, DOWN : False}
                        if navMode == NavMode.Sound:
                             navSound.set_volume (0.1)
                    elif (event.key == K_ESCAPE):
                        terminate()                             
        
        # Provide spoken directions no faster than SPEAK_FPS
        if (pauseGame == False) and (navMode != NavMode.Sound) and (time.time() - speakTimer >= 1.0 / SPEAK_FPS):
            speakTimer = time.time()
            
            if navMode == NavMode.Temperature:
                if prevDistance > distance:
                    # Getting closer to cheese.
                    hotterSound.play ()
                elif prevDistance < distance:
                    # Getting farther from the cheese.
                    colderSound.play ()
                    
            elif navMode == NavMode.Direction:

                if mouseCoord['x'] < cheese ['x']:
                    rightSound.play ()
                elif mouseCoord ['x'] > cheese ['x']:
                    leftSound.play ()
                elif mouseCoord['y'] < cheese ['y']:
                    downSound.play ()
                elif mouseCoord ['y'] > cheese ['y']:
                    upSound.play ()
                
            prevDistance = distance 
                
        # Process input and update display no faster than GAME_FPS
        if (pauseGame == False) and (time.time() - gameTimer >= 1.0 / GAME_FPS):
            gameTimer = time.time()
            
            # Process all user input events.
            for event in pygame.event.get():           
                if event.type == KEYDOWN or event.type == KEYUP:
                    keyDown = (event.type == KEYDOWN)

                    # Don't reset the timer until they've pressed the
                    # first key after winning
                    if justWon and event.key != K_SPACE:
                        justWon = False
                        winTimer = time.time()
                        
                    if (event.key == K_LEFT or event.key == K_a):
                        keyState[LEFT] = keyDown              
                    elif (event.key == K_RIGHT or event.key == K_d):
                        keyState[RIGHT] = keyDown
                    elif (event.key == K_UP or event.key == K_w):
                        keyState[UP] = keyDown
                    elif (event.key == K_DOWN or event.key == K_s):
                        keyState[DOWN] = keyDown
                    elif (event.key == K_n and keyDown):
                        averageWinTime = -2.0
                        navMode = (navMode + 1) % NAVMODES
                        if navMode != NavMode.Sound:
                            navSound.set_volume(0.0)
                        else:
                            navSound.set_volume(0.1)
                    elif (event.key == K_ESCAPE):
                        terminate()
                elif event.type == QUIT:
                    terminate()
          
            # Did the mouse eat the cheese?
            if mouseCoord['x'] == cheese['x'] and mouseCoord['y'] == cheese['y']:
                
                # Get the winning time and compute the running average win time
                # Throw out the initial win time 
                if averageWinTime <= -2.0:
                    averageWinTime = -1.0
                elif averageWinTime <= -1.0:
                    averageWinTime = winTime
                else:
                    averageWinTime = (averageWinTime + winTime) / 2.0

                # Flag as just won so timer doesn't start again until key press
                justWon = True

                # Play winning sound and update the score
                wonSound.play()
                score = score + 1

                # Move the cheese
                cheese = getRandomLocation(mouseCoord)

                # Pause game and turn off sound if it was playing
                pauseGame = True
                if navMode == NavMode.Sound:
                     navSound.set_volume (0.0)

            # Move the mouse by updating its position based on the key state.
            if keyState[LEFT] and mouseCoord [ 'x' ] > 0:
                mouseCoord['x'] = mouseCoord['x'] - 1
            if keyState[RIGHT] and mouseCoord [ 'x' ] < CELLWIDTH - 1:
                mouseCoord['x'] = mouseCoord['x'] + 1
            if keyState[UP] and mouseCoord [ 'y' ] > 0:
                mouseCoord['y'] = mouseCoord['y'] - 1
            if keyState[DOWN] and mouseCoord[ 'y' ] < CELLHEIGHT - 1:
                mouseCoord['y'] = mouseCoord['y'] + 1
    
            # Find the distance between the mouse and the cheese.
            distance = math.sqrt ((mouseCoord['x'] - cheese['x']) ** 2 + (mouseCoord['y'] - cheese['y']) ** 2)

            if navMode == NavMode.Sound:
                # Determine the volume level based on inverse distance squared
                newVolumeLevel = 1.0 / ((distance / MAXDISTANCE * 6.0 + 1.0) ** 2.0)
                if newVolumeLevel != navVolumeLevel:
                    navVolumeLevel = newVolumeLevel
                    navSound.set_volume (navVolumeLevel)
    
            # Draw everything
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawMouse(mouseCoord)
            drawCheese(cheese)
            if justWon:
                winTime = 0.0
            else:
                winTime = time.time() - winTimer
            drawScore(score, distance, winTime, averageWinTime, navMode, pauseGame)
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


def getRandomLocation(avoidCoord):
    # Return a random location not too close to avoidCoord
    while True:
        randomCoord = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
        distance = math.sqrt ((randomCoord['x'] - avoidCoord['x']) ** 2 + (randomCoord['y'] - avoidCoord['y']) ** 2)
        if distance > MAXDISTANCE / 3.0:
            return randomCoord

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


def drawScore(score, distance, winTime, avgTime, navMode, pauseGame):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 160, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)
    
    distSurf = BASICFONT.render('Distance: %s' % round(distance,1), True, WHITE)
    distRect = distSurf.get_rect()
    distRect.topleft = (WINDOWWIDTH - 160, 30)
    DISPLAYSURF.blit(distSurf, distRect)

    navModeStrings = [ 'Sound', 'Temperature', 'Direction', 'Sound & Direction' ]
    navSurf = BASICFONT.render('Navigation: %s' % navModeStrings[navMode], True, WHITE)
    navRect = navSurf.get_rect()
    navRect.topleft = (10, 10)
    DISPLAYSURF.blit(navSurf, navRect)
    
    timeSurf = BASICFONT.render('Time: %s secs' % round(winTime,1), True, WHITE)
    timeRect = timeSurf.get_rect()
    timeRect.topleft = (10, 30)
    DISPLAYSURF.blit(timeSurf, timeRect)

    if avgTime >= 0.0:
       avgTimeSurf = BASICFONT.render('Average time: %s secs' % round(avgTime, 1), True, WHITE)
       avgTimeRect = avgTimeSurf.get_rect()
       avgTimeRect.topleft = (10, 50)
       DISPLAYSURF.blit(avgTimeSurf, avgTimeRect)
    elif avgTime == -1.0:
       avgTimeSurf = BASICFONT.render('Average time: %s secs' % round(winTime,1), True, WHITE)
       avgTimeRect = avgTimeSurf.get_rect()
       avgTimeRect.topleft = (10, 50)
       DISPLAYSURF.blit(avgTimeSurf, avgTimeRect)
    elif avgTime == -2.0:
       avgTimeSurf = BASICFONT.render('***PRACTICE RUN***', True, WHITE)
       avgTimeRect = avgTimeSurf.get_rect()
       avgTimeRect.topleft = (10, 50)
       DISPLAYSURF.blit(avgTimeSurf, avgTimeRect)        


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
