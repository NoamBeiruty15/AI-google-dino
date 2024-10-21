import pygame
import sys

# Initialize game
pygame.init()

SCREEN_WIDTH = 950
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Template")

# Variables
FPS = 60
clock = pygame.time.Clock()

# Classes
class Game:
    def __init__(self):
        self.running = True
        self.score = 0

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        pass  

    def render(self):
        screen.fill((255, 255, 255))
        # Drawing code here
        pygame.display.flip()

    def run(self):
        while self.running:
            self.process_events()
            self.update()
            self.render()
            clock.tick(FPS)

class Dino:
    def __init

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
