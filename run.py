#import libraries
import pygame
import random
import os
from pygame import mixer

#initialize pygame
mixer.init()
pygame.init()

#Screen window dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600


#Creating the screen
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("FROPPY")

#set frame rate
clock = pygame.time.Clock()
FPS = 60

#game variables
SCROLL_TRESH = 200
GRAVITY = 1
MAX_PLATFORM = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if os.path.exists("Assets\high score.txt") :
    with open("Assets\high score.txt",'r') as file :
        high_score = int(file.read())
high_score = 0

#define colors
WHITE = (255,255,255)
BLACK = (0,0,0)

#define text
font_small = pygame.font.SysFont("Lucida Sans", 20)
font_big = pygame.font.SysFont("Lucida Sans", 24)

#load images
bg_img = pygame.image.load(r"Assests\jumpy bcg.png").convert_alpha()
fropy_img = pygame.image.load(r"Assets\fropy.png").convert_alpha()
log_img = pygame.image.load(r"Assets\log.png").convert_alpha()

#function for displaying text on the screen
def draw_text(text, font, text_col, x, y) :
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#function to display score panel
def draw_panel() :
    draw_text("Score: "+str(score), font_small, BLACK, 0, 0)

#function for drawing the background
def draw_bg(bg_scroll):
    screen.blit(bg_img, (0, 0 + bg_scroll))
    screen.blit(bg_img, (0, -600 + bg_scroll))

#player class
class player:
    def __init__(self,x,y,image) :
        self.image = pygame.transform.scale(image,(60,60))
        self.width = 40
        self.height = 55
        self.rect = pygame.Rect(0,0,self.width,self.height)
        self.rect.center = (x,y)
        self.vel_y = 0
        self.flip = False  #This is for flipping the image

    def move(self):
        #reset variables
        scroll = 0
        dx = 0  #d is delta the change in anything and x and y are the coordiates
        dy = 0

        #proccess keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_a] :
            dx = -10
            self.flip = True
        elif key[pygame.K_d] :
            dx = 10
            self.flip = False
        elif key[pygame.K_RIGHT] :
            dx = 10
            self.flip = False
        elif key[pygame.K_LEFT] :
            dx = -10
            self.flip = True

        #Gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        #ensure player doesn't go off screen
        if self.rect.left + dx < 0 :
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH :
            dx = SCREEN_WIDTH - self.rect.right

        #collision with platform
        for platform in platform_group :
            if platform.rect.colliderect(self.rect.x,self.rect.y + dy , self.width , self.height) :
                #check above platform
                if self.rect.bottom < platform.rect.centery :
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20

        # check if player has reached top
        if self.rect.bottom <= SCROLL_TRESH :
            #if player is jumping
            if self.vel_y < 0 :
                scroll = -dy

        #change rectangle position
        self.rect.x += dx
        self.rect.y += dy + scroll

        return scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip,False),(self.rect.x-12,self.rect.y-5))
        pygame.draw.rect(screen,WHITE,self.rect,2)

#platform class
class Platform(pygame.sprite.Sprite) :
    def __init__(self, x, y, width, moving) :
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(log_img,(width,10))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
    
    def update (self, scroll) :
        #move platforms from side to side if it is a moving platform
        if self.moving == True :
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

        #change platform direction if it has moved fully
        if self.move_counter > 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH :
            self.direction *= -1
            self.move_counter = 0

        # update platform's vertical position
        self.rect.y += scroll

        # check if platform has gone off screen
        if self.rect.top > SCREEN_HEIGHT :
            self.kill()

#creating instances
fropy = player(SCREEN_WIDTH//2,SCREEN_HEIGHT-150,fropy_img) 

#create sprite group
platform_group = pygame.sprite.Group()

#create starting platform
platform = Platform(SCREEN_WIDTH // 2 - 50,SCREEN_HEIGHT - 50, 100, False)
platform_group.add(platform) 

#Game loop
# Game loop
run = True
while run:
    # Setting frame rate
    clock.tick(FPS)
    
    if game_over == False :
        # Fropy movements
        scroll = fropy.move()

        # Clear the screen with the background image
        bg_scroll += scroll
        if bg_scroll >= 600 :
            bg_scroll = 0
        draw_bg(bg_scroll)

        #generate platforms
        if len(platform_group) < MAX_PLATFORM :
            p_w = random.randint(40, 60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 1000:
                p_moving = True
            else :
                p_moving = False
            platform = Platform(p_x, p_y, p_w, p_moving)
            platform_group.add(platform)         

        #update platform positions
        platform_group.update(scroll)

        # Draw the platforms
        platform_group.draw(screen)

        #draw panel
        draw_panel()

        #update score 
        if scroll > 0 :
            score += scroll

        #draw line at previous high score
        pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_TRESH), (SCREEN_WIDTH, score - high_score + SCROLL_TRESH), 3)
        draw_text("High Score", font_small, WHITE, SCREEN_WIDTH-250, score - high_score + SCROLL_TRESH)

        # Draw the player character
        fropy.draw()

        #game over condition
        if fropy.rect.top > SCREEN_HEIGHT :
            game_over = True
    else:
        if fade_counter < SCREEN_WIDTH :
            fade_counter += 5
            for y in range(0, 6, 2) :
                pygame.draw.rect(screen, BLACK, (0, y * 100, fade_counter, 100))
                pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * 100, SCREEN_WIDTH, 100))
        else:
            draw_text("Game Over!", font_big, WHITE, 130, 200)
            draw_text("Score: "+str(score), font_big, WHITE, 130, 250)
            draw_text("PRESS SPACE TO PLAY AGAIN", font_big, WHITE, 40, 300)
            #update high score
            if score > high_score :
                high_score = score
                with open("JUMPY\Assets\high score.txt",'w') as file :
                    file.write(str(high_score)) 
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] :
                #reset variables
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                #reposition fropy
                fropy.rect.center = (SCREEN_WIDTH//2,SCREEN_HEIGHT-150)
                #reset platforms
                platform_group.empty()
                #create starting platform
                platform = Platform(SCREEN_WIDTH // 2 - 50,SCREEN_HEIGHT - 50, 100, False)
                platform_group.add(platform)

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            #update high score
            if score > high_score :
                high_score = score
                with open("JUMPY\Assets\high score.txt",'w') as file :
                    file.write(str(high_score))
            run = False
    
    # Update the window whenever changes are made
    pygame.display.update()

pygame.quit()
