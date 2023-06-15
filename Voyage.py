import pygame,sys
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voyage v1.01")

# Load enemies
RED_SPACE_SHIP = pygame.image.load(os.path.join("rock1.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("rock2.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("rock3.png"))

# Load lazers
YELLOW_LASER = pygame.image.load(os.path.join("pixel_laser_yellow.png"))
GREEN_LASER = pygame.image.load(os.path.join("pixel_laser_green.png"))
RED_LASER = pygame.image.load(os.path.join("pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("pixel_laser_blue.png"))

# Player 
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("ship.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("background.png")), (WIDTH, HEIGHT))

#HEALING

HEAL = pygame.image.load(os.path.join("med.png"))

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

class Laser:
    
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img) 

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 25
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=250):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
                        
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

class Heal(Ship):

    def __init__(self, x, y, health=10000000):
        super().__init__(x, y, health)
        self.ship_img = HEAL
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move(self, vel):
        self.y += vel

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def end_screen():
    title_font = pygame.font.SysFont("Berlin Sans FB", 150)
    title_font1 = pygame.font.SysFont("Berlin Sans FB", 150)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label1 = title_font.render("MISSION", 1, (0,0,255))
        WIN.blit(title_label1, (WIDTH/2 - title_label1.get_width()/2, 200))
        title_label2 = title_font1.render("COMPLETE", 1, (0,0,255))
        WIN.blit(title_label2, (WIDTH/2 - title_label1.get_width()/1.5 , 400))
        pygame.display.update()
        time.sleep(2)
        main_menu()
      
def main():
    run = True
    FPS = 90
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("Berlin Sans FB", 50)
    lost_font = pygame.font.SysFont("Berlin Sans FB", 60)
    loss_font = pygame.font.SysFont("Berlin Sans FB", 80)

    enemies = []
    wave_length = 10
    enemy_vel = 1

    Medkit = []
    num = 2
    med_vel = 1

    player_vel = 5
    laser_vel = 5
    player = Player(300, 630)

    clock = pygame.time.Clock()

    win = True
    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        
        
        # draw text
        lives_label = main_font.render(f"Speed: 11 Km/s", 1, (240,0,255))
        level_label = main_font.render(f"Distance: {level}Km", 1, (240,0,255))     
        
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)
        
        for med in Medkit:
            med.draw(WIN)
        

        player.draw(WIN)
 
        if lost:

            lost_label = loss_font.render("MISSION FAILED !!", 1, (255,0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 270))

            if level > 1:
            
                lost2_label = lost_font.render(f"You Travelled {level} Kilometers", 1, (255,0,0))
                WIN.blit(lost2_label, (WIDTH/2 - lost2_label.get_width()/2, 390))

            settings_font1 = pygame.font.SysFont("Berlin Sans FB", 80)
    

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        if len(enemies) == 0:
            
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        if len(Medkit) == 0:
            
            for i in range (num):
                med = Heal(random.randrange(50, WIDTH-100),random.randrange(-1500,-100))
                Medkit.append(med)


        player.draw(WIN)
        
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel        
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        
        if keys[pygame.K_ESCAPE]:
            main_menu()
            
        for enemy in enemies[:]:
            enemy.move(enemy_vel)


            if collide(enemy, player):
                player.health -= 125
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)

        x = 1

        for i in range(x):
            level +=1
            x+=1
            

        for med in Medkit[:]:
            med.move(med_vel)

            if HEIGHT == 900:
                Medkit.remove(med)
            
            if collide(med,player):
                player.health += 125
                Medkit.remove(med)

            if player.health >= 250:

                player.health = 250

        player.move_lasers(-laser_vel, enemies)

        if level == 252:
            end_screen()
    

def main_menu():
    title_font = pygame.font.SysFont("Berlin Sans FB", 150)
    settings_font = pygame.font.SysFont("Berlin Sans FB", 80)
    movement_font = pygame.font.SysFont("Berlin Sans FB", 50)
    movement_font1 = pygame.font.SysFont("Berlin Sans FB", 47)
    play_font = pygame.font.SysFont("Berlin Sans FB", 80)
    
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label1 = title_font.render("VOYAGE", 1, (0,0,255))
        WIN.blit(title_label1, (WIDTH/2 - title_label1.get_width()/2, 100))
        
        click_label = play_font.render("Click To Play", 1, (0,255,0))
        WIN.blit(click_label, (WIDTH/2 - click_label.get_width()/2, 300))
        
        settings_label = settings_font.render("Controls : ", 1, (255,100,10))
        WIN.blit(settings_label, (WIDTH/2 - settings_label.get_width()/0.85, 480))
    
                                        
        left_label = movement_font.render("Move Left = A ", 1, (210,150,75))
        WIN.blit(left_label, (WIDTH/2 - left_label.get_width()/5, 410))
        
        
        right_label = movement_font.render("Move Right = D ", 1, (210,150,75))
        WIN.blit(right_label, (WIDTH/2 - right_label.get_width()/5.5, 510))

        quit_label = movement_font.render("Main Menu = Escape", 1, (210,150,75))
        WIN.blit(quit_label, (WIDTH/2 - quit_label.get_width()/7, 610))

        quit_label1 = movement_font1.render("Reach 252,000 Km To Reach The Moon", 1, ((255, 0, 0)))
        WIN.blit(quit_label1, (WIDTH/2 - quit_label1.get_width()/2, 700))

        
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()


