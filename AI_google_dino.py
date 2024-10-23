import pygame
import sys
import os
import random
import neat

# Initialize game
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 550
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Google Dino")
clock = pygame.time.Clock()

# Variables
FPS = 60
GRAVITY = 1
JUMP_STRENGTH = -16
GROUND_LEVEL = 400
generation = 0

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

    def update(self, speed, genomes):
        self.rect.x -= speed
        
        self.animation_frame = (self.animation_frame + 0.1) % len(self.images)
        self.image = self.images[int(self.animation_frame)]

        if not self.passed and self.rect.right < 50:
            self.passed = True
            for i, genome in enumerate(genomes):
                genomes[i].fitness += 1

        if self.rect.x < 0:
            self.alive = False
        

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def check_colliding(self, dinos, genomes, networks):
        for i, dino in enumerate(dinos):
            if self.rect.colliderect(dino.rect):
                offset_x = self.rect.x - dino.rect.x
                offset_y = self.rect.y - dino.rect.y

                if dino.mask.overlap(pygame.mask.from_surface(self.image), (offset_x, offset_y)):
                    genomes[i].fitness -= 10
                    genomes.pop(i)
                    networks.pop(i)
                    dinos.remove(dino)  

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

    def update(self, speed, genomes):
        self.rect.x -= speed 

        if self.passed == False and self.rect.x < 50:
            self.passed = True
            for i, genome in enumerate(genomes):
                genomes[i].fitness += 1

        if self.rect.x < 0: 
            self.alive = False

    def check_colliding(self, dinos, genomes, networks):
        for i, dino in enumerate(dinos):
            if self.rect.colliderect(dino.rect):

                offset_x = self.rect.x - dino.rect.x
                offset_y = self.rect.y - dino.rect.y
                
                if dino.mask.overlap(pygame.mask.from_surface(self.image), (offset_x, offset_y)):
                    genomes[i].fitness -= 5
                    genomes.pop(i)
                    networks.pop(i)
                    dinos.remove(dino) 
 
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Game:
    def __init__(self, genomes, config):
        self.networks = []
        self.genomes = []
        self.birds = []
        self.config = config
        self.config_genomes = genomes

        self.running = True
        self.gamespeed = 8
        self.score = 0
        self.dinos = []
        self.ground = Ground() 
        self.obstacles = []
        self.obstacle_spawn_ticker = 0
        self.min_score_birds_start_spawning = 600
        self.obstacle_index = 0
    
    def create_neural_networks(self):
        for genome_id, genome in self.config_genomes: 
            genome.fitness = 0  

            network = neat.nn.FeedForwardNetwork.create(genome, self.config)
            self.networks.append(network)
            self.dinos.append(Dino())
            self.genomes.append(genome)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                self.running = False
        
        for i, dino in enumerate(self.dinos):
            if self.obstacles:
                next_obstacle = self.obstacles[self.obstacle_index]

                output = self.networks[i].activate(
                    (next_obstacle.rect.x - dino.rect.x, next_obstacle.rect.y, self.gamespeed, 1 if dino.is_jumping else 0, 1 if dino.is_ducking else 0, next_obstacle.image.get_width(), next_obstacle.image.get_height())
                ) # Input 1: distance between dino and next obstacle. Input 2: next obstacle's y. Input 3: gamespeed. Input 4: is dino currently jumping?. Input 5: is dino currently ducking?. 
                # Input 6: next obstacle width. Input 7: next obstacle height.

                if output[0] > 0.5: # Tell the dino he is a good boy if he jumps close to a cactus, tell dino he is a bad boy if not!
                    dino.jump()
                    distance = next_obstacle.rect.x - dino.rect.x

                    if distance > 200:
                        self.genomes[i].fitness -= distance / 100 + 1
                    else:
                        self.genomes[i].fitness += 15

                if output[1] > 0.5:  # Tell the dino he is a good boy if he ducks when a bird is the next obstacle, tell dino he is a bad boy if a cactus is the next obstacle
                    if isinstance(next_obstacle, Bird):  
                        self.genomes[i].fitness += 5  
                    elif isinstance(next_obstacle, Cactus):  
                        self.genomes[i].fitness -= 2

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
        if self.obstacle_spawn_ticker >= random.randint(50, 200):
            # Check if score is high enough to spawn birds
            if self.score >= self.min_score_birds_start_spawning:
                if random.randint(1, 100) <= 75:
                    self.spawn_cactus()
                else:
                    self.spawn_bird()
            else:  # Spawn only cactus if the score is low
                if random.randint(1, 100) <= 80:
                    self.spawn_cactus()
            
            # Reset the ticker after spawning
            self.obstacle_spawn_ticker = 0

    def update(self):
        if not self.dinos:
            self.running = False

        for dino in self.dinos:
            dino.update()

        if self.obstacles:
            for i, obstacle in enumerate(self.obstacles):
                if not obstacle.passed:
                    self.obstacle_index = i
                else:
                    self.obstacle_index = 0

                if not obstacle.alive:
                    self.obstacles.pop(i)
                    continue

                obstacle.update(self.gamespeed, self.genomes)
                obstacle.check_colliding(self.dinos, self.genomes, self.networks)


        self.ground.update(self.gamespeed)
        
        self.spawn_obstacles()

        for genome in self.genomes:
            genome.fitness += 0.05

        self.score += 0.1
        self.gamespeed += 0.0015
        self.obstacle_spawn_ticker += 1
 
    def render(self):
        screen.fill((255, 255, 255))  # White background
        self.ground.draw(screen)

        for obstacle in self.obstacles:
            obstacle.draw(screen)

        for dino in self.dinos:
            dino.draw(screen)

        font = pygame.font.Font(None, 36)

        score_text = font.render(f"Score: {round(self.score)}", True, (0, 0, 0))
        screen.blit(score_text, (screen.get_width() - score_text.get_width() - 30, 10))

        generation_text = font.render(f"Alive: {len(self.dinos)}", True, (0, 0, 0))
        screen.blit(generation_text, (10, 10))

        generation_text = font.render(f"Gen: {generation}", True, (0, 0, 0))
        screen.blit(generation_text, (10, 40))

        pygame.display.flip()

    def run(self, generation):
        self.create_neural_networks()
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            clock.tick(FPS)

# ------------- A.I stuff -------------

def eval_genomes(genomes, config):
    global generation
    generation += 1

    game = Game(genomes, config) 
    game.run(generation)  


def run_neat(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    p = neat.Population(config)


    winner = p.run(eval_genomes, 1000)

    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    local_dir = os.path.dirname((__file__))
    config_path = os.path.join(local_dir, "neat-config.txt")
    run_neat(config_path)