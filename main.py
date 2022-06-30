import math
import random
import time
import datetime
import pygame
pygame.init()

class Projectile:
    def __init__(self,window,x,y,colour,radius,dx,dy):
        self.window = window
        self.x = x
        self.y = y
        self.colour = colour
        self.radius = radius
        self.dx = dx
        self.dy = dy
    
    def updatePos(self):
        self.x += self.dx
        self.y += self.dy
    
    def draw(self):
        pygame.draw.circle(self.window,self.colour,(self.x,self.y),self.radius)
    
    def onScreen(self):
        win_x = self.window.get_width()
        win_y = self.window.get_height()
        if not(0 < self.x < win_x and 0 < self.y < win_y):
            return False
        else:
            return True

class Enemy(Projectile):
    def __init__(self,window,x,y,colour,radius,dx,dy):
        super().__init__(window,x,y,colour,radius,dx,dy)
        self.last_hit = None
    
    def checkCollision(self,target):
        if self.last_hit != None:
            if time.perf_counter() - self.last_hit < 0.015:
                return

        if not self.onScreen():
            return
        
        distance = (self.x - target.x)**2 + (self.y - target.y)**2
        if distance < (self.radius + target.radius)**2:
            self.last_hit = time.perf_counter()
            return True
        else:
            return False
        

class Player(Projectile):
    def __init__(self,window,x,y,colour,radius,dx,dy):
        super().__init__(window,x,y,colour,radius,dx,dy)
        self.projectile_arr = []
        self.last_shoot = None
        self.shoot_sound = pygame.mixer.Sound("shoot_sound.wav")
        self.points = 0
    
    def returnNormalisedVector(self,point1, point2):
        vector = (point2[0] - point1[0], point2[1] - point1[1])
        if vector == (0,0):
            return (0,0)
        magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
        nvector = (vector[0] / magnitude, vector[1] / magnitude)
        return nvector
    
    def getEndCoord(self,coord,mouse_pos):
        nvector = self.returnNormalisedVector(coord,mouse_pos)
        scalar = self.radius * 2
        svector = (nvector[0] * scalar, nvector[1] * scalar)
        new_coord = (coord[0] + svector[0], coord[1] + svector[1])
        return new_coord
    
    def move(self,keys):
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.dy
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.dx
        
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.dy
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.dx
    
    def draw(self,mouse_pos):
        self.updateProjectiles()

        if self.x - self.radius < 0:
            self.x = self.radius
        
        if self.x + self.radius > self.window.get_width():
            self.x = self.window.get_width() - self.radius
        
        if self.y - self.radius < 0:
            self.y = self.radius
        
        if self.y + self.radius > self.window.get_height():
            self.y = self.window.get_height() - self.radius

        circle_centre = (self.x,self.y)
        pygame.draw.circle(self.window,self.colour,circle_centre,self.radius)
        line_start = circle_centre
        line_end = self.getEndCoord(line_start,mouse_pos)
        pygame.draw.line(self.window,(0,200,0),line_start,line_end,5)
    
    def updateProjectiles(self):
        for projectile in self.projectile_arr:
            if not projectile.onScreen():
                self.projectile_arr.remove(projectile)
            else:
                projectile.draw()
                projectile.updatePos()
    
    def shoot(self,mouse_click,mouse_pos):
        if not mouse_click[0]:
            return

        if self.last_shoot != None:
            if time.perf_counter() - self.last_shoot < 0.25:
                return
        
        pygame.mixer.Sound.play(self.shoot_sound)
        circle_centre = (self.x, self.y)
        nvector = self.returnNormalisedVector(circle_centre,mouse_pos)
        projectile_x = nvector[0] + self.x
        projectile_y = nvector[1] + self.y
        projectile_colour = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        projectile_radius = PROJECTILE_RADIUS
        projectile_speed = PROJECTILE_SPEED
        dx = nvector[0] * projectile_speed 
        dy = nvector[1] * projectile_speed
        new_projectile = Projectile(self.window,projectile_x,projectile_y,projectile_colour,projectile_radius,dx,dy)
        self.projectile_arr.append(new_projectile)
        self.last_shoot = time.perf_counter()

    
class Game:
    def __init__(self,win_x,win_y):
        self.win_x = win_x
        self.win_y = win_y
        self.window = pygame.display.set_mode((win_x,win_y))
        self.player = Player(self.window,PLAYER_X,PLAYER_Y,PLAYER_COLOUR,PLAYER_RADIUS,PLAYER_DX,PLAYER_DY)

        self.enemy_arr = []
        self.last_spawn = None
        self.hit_sound = pygame.mixer.Sound("hit_sound.wav")

    def reset(self):
        self.player.x = PLAYER_X
        self.player.y = PLAYER_Y
        self.player.points = 0
        self.player.projectile_arr = []
        self.enemy_arr = []
    
    def spawnEnemy(self):
        if self.last_spawn != None:
            if time.perf_counter() - self.last_spawn < 0.65:
                return
        
        if len(self.enemy_arr) > 50:
            return

        pad = 25
        outside_x = random.choice([True,False])
        if outside_x:
            enemy_y = random.randint(0,self.win_y)
            spawn_right = random.choice([True,False])
            if spawn_right:
                enemy_x = random.randint(self.win_x, self.win_x + pad)
            else:
                enemy_x = random.randint(-pad,0)

        else:
            enemy_x = random.randint(0,self.win_x)
            spawn_above = random.choice([True,False])
            if spawn_above:
                enemy_y = random.randint(-pad,0)
            else:
                enemy_y = random.randint(self.win_y, self.win_y + pad)
        
        enemy_colour = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        enemy_radius = random.uniform(ENEMY_RADIUS, ENEMY_RADIUS * 2)
        enemy_speed = random.uniform(ENEMY_SPEED, ENEMY_SPEED * 2)
        nvector = self.player.returnNormalisedVector((enemy_x,enemy_y),(self.player.x,self.player.y))
        enemy_dx = nvector[0] * enemy_speed
        enemy_dy = nvector[1] * enemy_speed
        new_enemy = Enemy(self.window,enemy_x,enemy_y,enemy_colour,enemy_radius,enemy_dx,enemy_dy)
        self.enemy_arr.append(new_enemy)
        self.last_spawn = time.perf_counter()
    
    def drawEnemies(self):
        self.spawnEnemy()
        x_exten = 50
        y_exten = 50
        for enemy in self.enemy_arr:
            if not(-x_exten < enemy.x < self.window.get_width() + x_exten and -y_exten < enemy.y < self.window.get_height() + y_exten):
                self.enemy_arr.remove(enemy)
            else:
                self.updateVel(enemy,self.player)
                enemy.updatePos()
                enemy.draw()
    
    def updateVel(self,enemy,player):
        nvector = self.player.returnNormalisedVector((enemy.x,enemy.y),(player.x,player.y))
        enemy_speed = math.sqrt(enemy.dx**2 + enemy.dy**2)
        dx = nvector[0] * enemy_speed
        dy = nvector[1] * enemy_speed
        enemy.dx = dx
        enemy.dy = dy
    
    def checkEnemyHit(self):
        for enemy in self.enemy_arr:
            if enemy.checkCollision(self.player):
                return True
        return False
    
    def checkProjectileHit(self):
        for projectile in self.player.projectile_arr:
            for enemy in self.enemy_arr:
                if enemy.checkCollision(projectile):
                    pygame.mixer.Sound.play(self.hit_sound)
                    reduction_factor = 0.05
                    self.player.points += enemy.radius * reduction_factor
                    enemy.radius *= (1-reduction_factor)

                    radius_threshold = self.player.radius * 0.5
                    if enemy.radius < radius_threshold:
                        self.enemy_arr.remove(enemy)
    
    def drawGrid(self):
        square_w = 50
        square_h = 50

        x_coord = 0
        y_coord = 0

        for y in range(0,int(self.win_y // square_h)):
            x_coord = 0
            for x in range(0,int(self.win_x // square_w)):
                pygame.draw.rect(self.window,(0,0,200),(x_coord,y_coord,square_w,square_h))
                pygame.draw.rect(self.window,(0,0,0),(x_coord,y_coord,square_w-2,square_h-2))
                x_coord += square_w
            y_coord += square_h
    
    def displayScore(self):
        font = pygame.font.SysFont("Consolas",20,True)
        game_over_str = "Score: {}".format(int(self.player.points))
        game_over_txt = font.render(game_over_str,False,(0,200,0))
        game_over_rect = game_over_txt.get_rect()
        game_over_rect.center = (self.win_x * 0.5, self.win_y * 0.1)
        self.window.blit(game_over_txt,game_over_rect)
        pygame.display.update()
    
    def displayGameOver(self):
        self.window.fill((0,0,0))
        font = pygame.font.SysFont("Consolas",50,True)
        game_over_str = "Game Over! Score: {}".format(int(self.player.points))
        game_over_txt = font.render(game_over_str,False,(0,0,200))
        game_over_rect = game_over_txt.get_rect()
        game_over_rect.center = (self.win_x / 2, self.win_y / 2)
        self.window.blit(game_over_txt,game_over_rect)
        pygame.display.update()
        pygame.time.delay(2000)

    def saveScore(self):
        with open("scores.txt", mode = "a", encoding ="utf-8") as read_file:
            date_str = datetime.datetime.today().strftime('%Y-%m-%d')
            score_str = "Score:{}".format(self.player.points)
            read_file.write(date_str + " | " + score_str + "\n")
            read_file.close()

    def startGame(self):
        end_game = False
        clock = pygame.time.Clock()
        while not end_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    end_game = True

            pressed_keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            self.player.move(pressed_keys)
            self.player.shoot(mouse_pressed, mouse_pos)
            self.player.draw(mouse_pos)

            self.drawEnemies()
            self.checkProjectileHit()
            if self.checkEnemyHit():
                print("Game Over!")
                self.displayGameOver()
                self.saveScore()
                self.reset()
 
            self.displayScore()
            pygame.display.update()
            self.drawGrid()
            clock.tick(FPS)
            
        pygame.quit()

FPS = 60
WIN_X = 1000
WIN_Y = 500

PLAYER_X = WIN_X / 2
PLAYER_Y = WIN_Y / 2
PLAYER_COLOUR = (200,0,0)
PLAYER_RADIUS = 25
PLAYER_DX = 1.25
PLAYER_DY = 1.25

PROJECTILE_SPEED = 2.75
PROJECTILE_RADIUS = 6

ENEMY_RADIUS = 14.5
ENEMY_SPEED = 1.15

if __name__ == "__main__":
    game = Game(WIN_X,WIN_Y)
    game.startGame()
