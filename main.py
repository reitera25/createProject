import pygame, sys, math, random, time
    
start_time = time.time()
screen = pygame.display.set_mode((800, 800))
playerImg = pygame.image.load("char1.png")
player_y = 0
player_x = 0

RUNNING, PAUSE = 0, 1

state = RUNNING

all_enemies = pygame.sprite.Group()


def time_convert(sec):
    min = sec // 60
    sec = math.floor(sec)
    return sec, min

class Game:
    enemies = []
    rockets = []
    lost = False

    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        done = False
        self.cool_down_count = 0
        self.spawn_cooldown_count = 0

        pause_text = pygame.font.SysFont("Arial", 75).render("Pause", True, pygame.color.Color("White"))


        global player

        player = Player(self, width/2, height/2)
        #generator = Generator(self)
        rocket = None
        angle = 0

        self.s_cooldown = 420


        while not done:         
        
            curr_time = time.time()

            time_lapsed = curr_time - start_time

        

            seconds, minutes = time_convert(time_lapsed)

            self.displayText(str(seconds))

            self.difficulty = minutes + 1


            if int(seconds) % 30 == 0:
                self.s_cooldown = 420 / ((seconds // 30) + 1)

            self.cooldown(self.s_cooldown, 1)

            pressed = pygame.key.get_pressed()
            left, middle, right = pygame.mouse.get_pressed()

            if pressed[pygame.K_a]:
                player.x -= 2 if player.x > 20 else 0
            if pressed[pygame.K_s]:
                player.y += 2 if player.y < height - 20 else 0
            if pressed[pygame.K_w]:
                player.y -= 2 if player.y > 20 else 0
            if pressed[pygame.K_d]:
                player.x += 2 if player.x < width - 20 else 0
            
            if left:
                self.cooldown(10, 0)
                if self.cool_down_count == 0:
                    mouse_x, mouse_y = pygame.mouse.get_pos()


                    distance_x = mouse_x - player_x
                    distance_y = mouse_y - player_y

                    angle = math.atan2(distance_y, distance_x)

                    speed_x = 4 * math.cos(angle)
                    speed_y = 4 * math.sin(angle)

                    self.rockets.append([player.x, player.y, speed_x, speed_y])
                    self.cool_down_count = 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            if pressed[pygame.K_ESCAPE]:
                state = PAUSE
            if not pressed[pygame.K_ESCAPE]:
                state = RUNNING

            if state == PAUSE:
                screen.blit(pause_text, (400, 400))

            pygame.display.flip()
            self.clock.tick(60)
            screen.fill((0, 0, 0))

            all_enemies.update()

            all_enemies.draw(screen)

            for enemy in all_enemies:
                Enemy.checkCollision(enemy)

            for rocket in self.rockets:
                rocket[0] += rocket[2]
                rocket[1] += rocket[3]

                

            for player_x, player_y, speed_x, speed_y in self.rockets:
                player_x = int(player_x)
                player_y = int(player_y)

                pygame.draw.rect(screen, (255, 0, 0), (player_x + 50, player_y + 50, 5, 5))
            
            if not self.lost: 
                player_x, player_y = player.draw()
                

    def displayText(self, text):
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 50)
        textsurface = font.render(text, False, (255, 255, 255))
        screen.blit(textsurface, (110, 160))        
    
    def cooldown(self, cooldown, type):
        if type == 1:
            if self.spawn_cooldown_count >= cooldown:
                self.spawn_cooldown_count = 0
                for i in range(4):
                    n = Enemy(player, self.difficulty)
                    all_enemies.add(n)
                    Enemy.add(n)

            elif self.spawn_cooldown_count >= 0:
                self.spawn_cooldown_count += 1
        elif type == 0:
            if self.cool_down_count >= 10:
                self.cool_down_count = 0
            elif self.cool_down_count > 0:
                self.cool_down_count += 1


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 30)).convert_alpha()
        self.player = player
        self.image.fill((148, 54, 224))
        self.orig_img = self.image
        self.rect = self.image.get_rect()
        self.spawn()
        self.health = health

    def spawn(self):
        self.direction = random.randrange(4)
        if self.direction == 0:
            self.rect.x = random.randrange(800 - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_x = 0
            self.speed_y = random.randrange(1, 6)
        if self.direction == 1:
            self.rect.x = random.randrange(800 - self.rect.width)
            self.rect.y = random.randrange(800, 800 + 60)
            self.speed_x = 0
            self.speed_y = random.randrange(1, 6)
        if self.direction == 2:
            self.rect.x = random.randrange(-100, -40)
            self.rect.y = random.randrange(800 - self.rect.height)
            self.speed_x = random.randrange(1, 6)
            self.speed_y = 0
        if self.direction == 3:
            self.rect.x = random.randrange(800, 800+60)
            self.rect.y = random.randrange(800 - self.rect.height)
            self.speed_x = random.randrange(1, 6)
            self.speed_y = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y    
        dir_x, dir_y = player.x - self.rect.x, player.y - self.rect.y
        self.rot = (180 / math.pi) * math.atan2(-dir_x, -dir_y)
        self.image = pygame.transform.rotate(self.orig_img, self.rot)

        if self.direction == 0:
            if self.rect.top > 800 + 10:
                self.spawn()
        elif self.direction == 1:
            if self.rect.bottom < -10:
                self.spawn()
        elif self.direction == 2:
            if self.rect.left > 800 + 10:
                self.spawn()
        elif self.direction == 3:
            if self.rect.right < -10:
                self.spawn()

    def checkCollision(self):
        for rocket in Game.rockets:
            if (rocket[0] < self.rect.x + 30 and
                    rocket[0] > self.rect.x - 30 and
                    rocket[1] < self.rect.y + 30 and
                    rocket[1] > self.rect.y - 30):
                self.health -= 1
                if self.health <= 0:
                    all_enemies.remove(self)

                Game.rockets.remove(rocket)


class Player:

    def __init__(self, game, x, y):
        self.x = x
        self.game = game
        self.y = y
        self.hitbox = (self.x, self.y, 64, 64)
        self.offset = pygame.Vector2(50, 0)
        
        

    def draw(self):
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.x, mouse_y - self.y
        angle = math.atan2(rel_y, rel_x)
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

        w, h = playerImg.get_size()
        
        pos = (screen.get_width()/2, screen.get_height()/2)
        self.hitbox = (self.x, self.y, 90, 90)


        #if pygame.mouse.get_pressed():
            #print(pygame.mouse.get_pos())
        rotated_image, rotated_image_rect = self.rotate(playerImg, pos, (30, 50), angle)
        offset_rot = self.offset.rotate(angle)
        pygame.Surface.blit(screen, rotated_image, (self.x, self.y))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 100, 100), 1)

        return self.x, self.y



    def rotate(surf, image, pos, originPos, angle):

        image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

        rotated_offset = offset_center_to_pivot.rotate(-angle)

        rotated_image_center = (pos[0] - rotated_offset.x - 15, pos[1] - rotated_offset.y)

        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

        return rotated_image, rotated_image_rect



class Generator:
    def __init__(self, game):
        margin = 30
        width = 50
        for x in range(margin, game.width - margin, width):
            for y in range(margin, int(game.height / 2), width):
                game.enemies.append(Enemy(game, x, y))


if __name__ == '__main__':
    game = Game(800, 800)
