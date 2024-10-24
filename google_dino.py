import pygame
import sys
import os
import random

# Initialize game
pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Google Dino")
clock = pygame.time.Clock()

# Variables
FPS = 60
GRAVITY = 1
JUMP_STRENGTH = -16
GROUND_LEVEL = 235

# Load assets
DINO_RUNNING_IMAGES = [
    pygame.transform.scale(
        pygame.image.load(os.path.join("images", f"dinorun{i}.png")), (60, 60)
    )
    for i in range(1, 3)  
]

DINO_DUCKING_IMAGES = [
    pygame.transform.scale(
        pygame.image.load(os.path.join("images", f"dinoduck{i}.png")), (70, 60)
    )
    for i in range(1, 3)  
]

BIRD_IMAGES = [
    pygame.transform.scale(
        pygame.image.load(os.path.join("images", f"bird{i}.png")), (70, 60)
    )
    for i in range(1, 3)  
]

GROUND_IMG = pygame.image.load(os.path.join("images", "ground.png"))

LARGE_CACTUS_IMAGE_NAMES = ["cactusLargeSingle", "cactusLargeDouble", "cactusLargeTriple"]
SMALL_CACTUS_IMAGE_NAMES = ["cactusSmallSingle", "cactusSmallDouble", "cactusSmallTriple"]
    

# Classes
class Ground:
    def __init__(self):
        self.image = GROUND_IMG
        self.x1 = 0  
        self.x2 = self.image.get_width()  
        self.y = GROUND_LEVEL - 45

    def update(self, speed):

        self.x1 -= speed
        self.x2 -= speed

        if self.x1 <= -self.image.get_width():
            self.x1 = self.image.get_width()
        if self.x2 <= -self.image.get_width():
            self.x2 = self.image.get_width()

    def draw(self, surface):
        surface.blit(self.image, (self.x1, self.y))
        surface.blit(self.image, (self.x2, self.y))

class Dino:
    def __init__(self):
        self.running_images = DINO_RUNNING_IMAGES
        self.ducking_images = DINO_DUCKING_IMAGES
        self.image = self.running_images[0] 
        self.rect = self.image.get_rect()
        self.rect.x = 50  
        self.rect.y = GROUND_LEVEL 
        self.jump_vel = 0
        self.is_jumping = False
        self.is_ducking = False
        self.animation_frame = 0
        self.mask = pygame.mask.from_surface(self.image) 

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.jump_vel = JUMP_STRENGTH
            self.is_jumping = True
    
    def duck(self):
        if not self.is_jumping:
            self.is_ducking = True

    def update(self):
        # Jump logic
        self.rect.y += self.jump_vel
        if self.rect.y >= GROUND_LEVEL:
            self.rect.y = GROUND_LEVEL
            self.jump_vel = 0
            self.is_jumping = False
        else:
            self.jump_vel += GRAVITY  

        # Rendering correct image logic
        if self.is_ducking:
            self.animation_frame = (self.animation_frame + 0.1) % len(self.ducking_images)
            self.image = self.ducking_images[int(self.animation_frame)]
        elif self.is_jumping:
            self.image = self.running_images[0]  
        else:
            self.animation_frame = (self.animation_frame + 0.1) % len(self.running_images)
            self.image = self.running_images[int(self.animation_frame)]

        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Bird:
    def __init__(self, x, y):
        self.images = BIRD_IMAGES
        self.image = self.images[0]  
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_frame = 0
        self.alive = True
        self.passed = False

    def update(self, speed):
        self.rect.x -= speed
        
        self.animation_frame = (self.animation_frame + 0.1) % len(self.images)
        self.image = self.images[int(self.animation_frame)]

        if not self.passed and self.rect.right < 50:
            self.passed = True

        if self.rect.right < 0:
            self.alive = False
        

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def check_colliding(self, dinos):
        for dino in dinos:
            if self.rect.colliderect(dino.rect):
                offset_x = self.rect.x - dino.rect.x
                offset_y = self.rect.y - dino.rect.y

                if dino.mask.overlap(pygame.mask.from_surface(self.image), (offset_x, offset_y)):
                    return True  

class Cactus:
    def __init__(self, image_name, x):
        if "SmallSingle" in image_name:
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("images", image_name)), (40, 50)
            )
            self.rect_y_offset = 10
        elif "SmallDouble" in image_name:
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("images", image_name)), (50, 60)
            )
            self.rect_y_offset = 5
        elif "SmallTriple" in image_name:
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("images", image_name)), (70, 75)
            )
            self.rect_y_offset = -5
        elif "LargeSingle" in image_name:
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("images", image_name)), (40, 55)
            )
            self.rect_y_offset = 5
        elif "LargeDouble" in image_name:
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("images", image_name)), (50, 65)
            )
            self.rect_y_offset = -5
        elif "LargeTriple" in image_name:
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("images", image_name)), (75, 80)
            )
            self.rect_y_offset = -20
        else:
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("images", image_name)), (45, 60)
            )
            self.rect_y_offset = 7.5

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = GROUND_LEVEL + self.rect_y_offset  
        self.passed = False
        self.alive = True

    def update(self, speed):
        self.rect.x -= speed 

        if not self.passed and self.rect.right < 50:
            self.passed = True

        if self.rect.right < 0: 
            self.alive = False

    def check_colliding(self, dinos):
        for dino in dinos:
            if self.rect.colliderect(dino.rect):

                offset_x = self.rect.x - dino.rect.x
                offset_y = self.rect.y - dino.rect.y
                
                if dino.mask.overlap(pygame.mask.from_surface(self.image), (offset_x, offset_y)):
                    return True
 


    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Game:
    def __init__(self):
        self.running = True
        self.gamespeed = 8
        self.score = 0
        self.dinos = [Dino()]
        self.ground = Ground() 
        self.obstacles = []
        self.obstacle_spawn_ticker = 0
        self.min_score_birds_start_spawning = 600
        self.obstacle_index = 0
        self.paused = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  
                    self.running = False
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) and self.paused == True: # Replay game, for ever
                game = Game()
                game.run()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.dinos[0].jump()
                if event.key == pygame.K_DOWN:
                    self.dinos[0].duck()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.dinos[0].is_ducking = False

    def spawn_cactus(self):

        if random.choice([True, False]):
            image_name = random.choice(SMALL_CACTUS_IMAGE_NAMES) + ".png"
        else:
            image_name = random.choice(LARGE_CACTUS_IMAGE_NAMES) + ".png"

        new_cactus = Cactus(image_name, SCREEN_WIDTH)
        self.obstacles.append(new_cactus)
    
    def spawn_bird(self):

        high_bird = random.choice([True, False])

        if high_bird:
            bird_y = random.randint(GROUND_LEVEL - 75, GROUND_LEVEL - 40)
        else:
            bird_y = random.randint(GROUND_LEVEL - 30, GROUND_LEVEL - 5)
        
        bird_x = SCREEN_WIDTH

        new_bird = Bird(bird_x, bird_y)
        self.obstacles.append(new_bird)
    
    def spawn_obstacles(self):
        if self.obstacle_spawn_ticker > random.randint(45, 200):
            if not self.score < self.min_score_birds_start_spawning:
                if random.randint(1,100) <= 75:
                    self.spawn_cactus()
                    self.obstacle_spawn_ticker = 0
                else:
                    self.spawn_bird()
                    self.obstacle_spawn_ticker = 0
            else:
                if random.randint(1,100) <= 80:
                    self.spawn_cactus()
                    self.obstacle_spawn_ticker = 0
                else:
                    return

    def update(self):
        if self.paused:
            return
        if not self.dinos:
            self.running = False

        for dino in self.dinos:
            dino.update()   

        if self.obstacles:
            for obstacle in self.obstacles:
                if (len(self.obstacles) > 1 and self.obstacles[0].passed):
                    self.obstacle_index = 1
                else:
                    self.obstacle_index = 0

                if not obstacle.alive:  
                    self.obstacles.remove(obstacle)
                    continue

                obstacle.update(self.gamespeed)

                if obstacle.check_colliding(self.dinos):
                    self.paused = True
                    self.dinos[0].image = DINO_DEAD_IMAGE


        self.ground.update(self.gamespeed)
        
        self.spawn_obstacles()

        self.score += 0.1
        self.gamespeed += 0.0015
        self.obstacle_spawn_ticker += 1
 
    def render(self):
        screen.fill((255, 255, 255))  # White background
        self.ground.draw(screen)

        for dino in self.dinos:
            dino.draw(screen)

        for obstacle in self.obstacles:
            obstacle.draw(screen)

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {round(self.score)}", True, (0, 0, 0))
        screen.blit(score_text, (screen.get_width() - score_text.get_width() - 30, 10))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            clock.tick(FPS)

# Start the game
def run_google_dino():
    game = Game()
    game.run()

if __name__ == "__main__":
    run_google_dino()