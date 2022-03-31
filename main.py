import pygame, sys, math, random, time

screen = pygame.display.set_mode((800, 800))
playerImg = pygame.image.load("char1.png")
player_y = 0
player_x = 0

def time_convert(sec):
    min = sec // 60
    return sec, min


def time_convert(sec):
    min = sec // 60
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

        player = Player(self, width/2, height/2)
        #generator = Generator(self)
        rocket = None
        angle = 0


        while not done:         
        
            curr_time = time.time()

            time_lapsed = curr_time - start_time

            seconds, minutes = time_convert(time_lapsed)

            self.difficulty = minutes


            # make it so cooldown only updates every 30 seconds
            self.spawn_cooldown = 420 / self.difficulty

            

            #if len(self.enemies) == 0:
             #   self.displayText("Wave Clear")

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
                self.cooldown()
                if self.cool_down_count == 0:
                    mouse_x, mouse_y = pygame.mouse.get_pos()


                    distance_x = mouse_x - player_x
                    distance_y = mouse_y - player_y

                    angle = math.atan2(distance_y, distance_x)

                    speed_x = 2 * math.cos(angle)
                    speed_y = 2 * math.sin(angle)

                    self.rockets.append([player.x, player.y, speed_x, speed_y])
                    self.cool_down_count = 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            pygame.display.flip()
            self.clock.tick(60)
            screen.fill((0, 0, 0))

            for enemy in self.enemies:
                enemy.draw()
                enemy.checkCollision(self)
                if (enemy.y > height):
                    self.lost = True
                    self.displayText("YOU DIED")

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
        textsurface = font.render(text, False, (44, 0, 62))
        screen.blit(textsurface, (110, 160))

    def cooldown(self):
        if self.cool_down_count >= 10:
            self.cool_down_count = 0
        elif self.cool_down_count > 0:
            self.cool_down_count += 1
    
    def spawn_cooldown(self, cooldown):
        if self.spawn_cooldown_count >= cooldown:
            self.spawn_cooldown_count = 0
        elif self.spawn_cooldown_count > 0:
            self.spawn_cooldown_count += 1


class Enemy:
    def __init__(self, player):
        self.image = pygame.Surface((40, 40).convert_alpha())
        self.player = player
        self.image.fill(148, 54, 224)
        self.orig_img = self.image
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        self.direction = random.randrange(4)
        if self.direction == 0:
            self.rect.x = random.randrange(800 - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_x = 0
            self.speed_y = random.randrange(1, 8)
        if self.direction == 1:
            self.rect.x = random.randrange(800 - self.rect.width)
            self.rect.y = random.randrange(800, 800 + 60)
            self.speed_x = 0
            self.speed_y = random.randrange(1, 8)
        if self.direction == 2:
            self.rect.x = random.randrange(-100, -40)
            self.rect.y = random.randrange(800 - self.rect.height)
            self.speed_x = random.randrange(1, 8)
            self.speed_y = 0
        if self.direction == 3:
            self.rect.x = random.randrange(800, 800+60)
            self.rect.y = random.randrange(800 - self.rect.height)
            self.speed_x = random.randrange(1, 8)
            self.speed_y = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y    
        dir_x, dir_y = self.player.rect.x - self.rect.x, self.player.rect.y - self.rect.y
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

    def checkCollision(self, game):
        for rocket in game.rockets:
            if (rocket.x < self.x + self.size and
                    rocket.x > self.x - self.size and
                    rocket.y < self.y + self.size and
                    rocket.y > self.y - self.size):
                game.rockets.remove(rocket)
                game.enemies.remove(self)


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
    start_time = time.time()