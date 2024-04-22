#import library
import pygame
import random
import os
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy



#intialise pygame
mixer.init()
pygame.init()

#game window
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

#create game window
main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Beach Ball Bouncing')

#set frame rate
clock = pygame.time.Clock()
FPS = 60

#load music and sound
pygame.mixer.music.load('Assets/Beachmusic.mp3')
pygame.mixer.music.set_volume(0.10)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound('Assets/jump.mp3')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('Assets/death.mp3')
death_fx.set_volume(0.5)


#game variables
SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0
main_menu = True

if os.path.exists('score.txt'): 
 with open('score.txt', 'r') as file:
    high_score = int(file.read())
else:
    high_score = 0

#define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL = (75,194,252,255)

#define font
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)

#Load images
ball_image = pygame.image.load('Assets/ball.png').convert_alpha()
bg_image = pygame.image.load('Assets/background.png').convert_alpha()
platform_image = pygame.image.load('Assets/log.png').convert_alpha()
#bird sprite sheet
bird_sheet_img = pygame.image.load('Assets/bird.png').convert_alpha()
bird_sheet = SpriteSheet(bird_sheet_img)



#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    main_screen.blit(img, (x, y))

#function for drawing info panel
def draw_panel():
    pygame.draw.rect(main_screen, PANEL, (0, 0, SCREEN_WIDTH, 30))
    pygame.draw.line(main_screen, WHITE,(0, 30),(SCREEN_WIDTH, 30), 2)
    draw_text('SCORE: ' + str(score), font_small, WHITE, 0, 0)

#function for drawing the background
def draw_bg(bg_scroll):
    main_screen.blit(bg_image, (0, 0 + bg_scroll)) 
    main_screen.blit(bg_image, (0, -600 + bg_scroll))



#player class
class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(ball_image, (67, 67))
        self.width = 45
        self.height = 46
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip  = False

    def move(self):
        #reset variable
        scroll = 0
        dx = 0
        dy = 0

        #porcess keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx = -10
            self.flip = True
        if key[pygame.K_d]:
            dx = 10
            self.flip = False

        #gravity
        self.vel_y += GRAVITY
        dy += self.vel_y 

        #ensure player doesn't go off the edge of the screen
        if self.rect.left + dx < 0:
            dx =  -self.rect.left
        if self.rect.right + dx >SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right 


        #check collision with platforms
        for platform in platform_group:
            #collision in the y direction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if above the platform
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                       self.rect.bottom = platform.rect.top
                       dy = 0
                       self.vel_y = -20
                       jump_fx.play()
        

        #check if the player has bounced top the top of the screen
        if self.rect.top <= SCROLL_THRESH:
            #if the player is jumping
            if self.vel_y < 0:
               scroll = -dy


        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy + scroll

        #update mask
        self.mask = pygame.mask.from_surface(self.image)

        return scroll

    def draw(self):
        main_screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 13, self.rect.y - 15))


#platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 16))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        #moving platform side to side if it is a moving platform
        if self.moving == True:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

        #change platform direction if it have moved fully or hit wall  
        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right >SCREEN_WIDTH:
            self.direction *= -1
            self.move_counter = 0

        #update platfroms vertical positions
        self.rect.y += scroll

        #check if platform hasgone off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


#player instance
ball = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

#create sprite groups
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

#create starting platforms
platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 120, 100, False)
platform_group.add(platform)





#Game loop
run = True
while run:

    clock.tick(FPS)

    

    if game_over == False:

        scroll = ball.move()
    

        #draw background
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        #generate platforms
        if len(platform_group) < MAX_PLATFORMS:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint (80, 120)  
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 1000:
               p_moving = True
            else:
                p_moving = False    
            platform = Platform(p_x, p_y, p_w, p_moving)
            platform_group.add(platform)
        
        #update platfroms
        platform_group.update(scroll)

        #generate enemies
        if len(enemy_group) == 0 and score > 2000:
            enemy = Enemy(SCREEN_WIDTH, 100,bird_sheet, 1.5)
            enemy_group.add(enemy)

        #update enemies
        enemy_group.update(scroll, SCREEN_WIDTH)

        #update score
        if scroll > 0:
            score += scroll

        #draw line at prev highscore
        pygame.draw.line(main_screen, WHITE,(0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
        draw_text('HIGH SCORE', font_small, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH)

        #draw sprites
        platform_group.draw(main_screen)
        enemy_group.draw(main_screen)
        ball.draw()

        #draw panel
        draw_panel()

       
        #check game over
        if ball.rect.top > SCREEN_HEIGHT:
            game_over = True
            death_fx.play()
        #check for collision with enemies
        if pygame.sprite.spritecollide(ball, enemy_group, False):
            if pygame.sprite.spritecollide(ball, enemy_group, False, pygame.sprite.collide_mask):
                game_over = True
                death_fx.play()
    else:
        if fade_counter < SCREEN_WIDTH:
            fade_counter += 5
            for y in range(0, 6, 2):
                pygame.draw.rect(main_screen, BLACK, (0, y * 100, fade_counter, 100))
                pygame.draw.rect(main_screen, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * 100, SCREEN_WIDTH / 2, 100))
        else:
            draw_text('GAME OVER!', font_big, WHITE, 130, 200 )
            draw_text('SCORE: ' + str(score), font_big, WHITE, 130, 250)
            draw_text('PRESS SPACE TO PLAY AGAIN', font_big, WHITE, 40, 300)
            #update high score
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                #reset variables
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                #reposition ball
                ball.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
                #reset enemies
                enemy_group.empty()
                #reset platforms
                platform_group.empty()
                #create starting platforms
                platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 120, 100, False)
                platform_group.add(platform)         

    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            #update high score
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            run = False 

    #Update display window
    pygame.display.update()


pygame.quit()