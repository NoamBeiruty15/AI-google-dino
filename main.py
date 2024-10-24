import pygame
import sys
import os

from google_dino import run_google_dino
from train_AI_google_dino import train_AI_google_dino 

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 700, 400
BACKGROUND_COLOR = (255, 255, 255)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER_COLOR = (75, 75, 75)
FONT_COLOR = (255, 255, 255)
GROUND_IMG = pygame.image.load(os.path.join("images", "ground.png"))
DINO_IMG = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "dinorun1.png")), (60, 60)
)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Google Dino")

# Button class
class Button:
    def __init__(self, text, pos, size, action=None):
        self.text = text
        self.rect = pygame.Rect(pos, size)
        self.font = pygame.font.Font(None, 40)
        self.action = action  

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, BUTTON_HOVER_COLOR, self.rect)
        else:
            pygame.draw.rect(surface, BUTTON_COLOR, self.rect)

        # Render the text
        text_surface = self.font.render(self.text, True, FONT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_pressed(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse_pos) and mouse_pressed[0]:  # Left mouse button

            if self.action:
                self.action()  

buttons = [Button("Play", (120, 125), (200, 50), action=run_google_dino),  
            Button("Train A.I.", (380, 125), (200, 50), action=train_AI_google_dino)]


# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for button in buttons:
        button.is_pressed()

    screen.fill((255, 255, 255))

    screen.blit(GROUND_IMG, (0, 190))
    screen.blit(DINO_IMG, (50, 235))

    # Draw buttons
    for button in buttons:
        button.is_pressed()
        button.draw(screen)

    # Update the display
    pygame.display.flip()
