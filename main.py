import pygame
import math
import random
import sys

# -------------------------
# Global Constants
# -------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Scenes
SCENE_TITLE = "title"
SCENE_MAIN = "main"

# -------------------------
# Helper Functions
# -------------------------
def load_image(name):
    """Loads an image from the assets folder and returns a pygame.Surface."""
    return pygame.image.load(f"assets/{name}").convert_alpha()

def draw_text(surface, text, x, y, font, color=(255,255,255), center=True):
    """Utility to draw text on a surface."""
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(text_obj, rect)

# -------------------------
# Title Scene
# -------------------------
class TitleScene:
    def __init__(self):
        self.background = None
        self.planet = None
        self.play_button = None
        self.font = None
        self.title_text = "SARIAN"
        # Button rect for detecting clicks
        self.play_button_rect = None

    def load_resources(self):
        self.background = load_image("background.png")
        self.planet = load_image("planet.png")
        self.play_button = load_image("play_button.png")
        # Use a font included with pygame or a TTF file you have:
        self.font = pygame.font.SysFont("Arial", 48)

    def start(self):
        pass  # Any initialization logic goes here

    def handle_events(self, event, game):
        """Handle events (like mouse clicks) for the Title Scene."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if self.play_button_rect and self.play_button_rect.collidepoint(mouse_x, mouse_y):
                # Switch to main scene
                game.change_scene(SCENE_MAIN)

    def update(self, dt, game):
        """Update logic for Title Scene. dt is the time delta."""
        pass

    def draw(self, surface):
        """Draw everything for the Title Scene."""
        # Draw background
        surface.blit(pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0,0))
        # Planet in the center
        planet_scaled = pygame.transform.scale(self.planet, (int(self.planet.get_width()*0.6), 
                                                             int(self.planet.get_height()*0.6)))
        planet_rect = planet_scaled.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        surface.blit(planet_scaled, planet_rect)
        # Title text
        draw_text(surface, self.title_text, SCREEN_WIDTH//2, 150, self.font, color=(255,255,255), center=True)
        # Play button
        play_scaled = pygame.transform.scale(self.play_button, (100, 100))  # adjust as needed
        self.play_button_rect = play_scaled.get_rect(center=(SCREEN_WIDTH//2, 400))
        surface.blit(play_scaled, self.play_button_rect)
        
# -------------------------
# Particles / dust effect
# -------------------------

# -------------------------
# Asteroid Sprite
# -------------------------
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, image, planet_center, speed=20):
        super().__init__()
        self.image_original = image
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=(x,y))
        self.planet_center = planet_center
        self.speed = speed

        # Calculate velocity toward planet center
        dx = planet_center[0] - x
        dy = planet_center[1] - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed

        # For circle collision, store a radius (approx half of scaled sprite's width)
        self.radius = self.rect.width // 2

    def update(self, dt=1.0):
        # Move asteroid; dt scaling normalizes movement per frame
        self.rect.x += self.vx * (dt / 16.67)
        self.rect.y += self.vy * (dt / 16.67)

        # Remove asteroid if it goes off-screen
        if (self.rect.x < -200 or self.rect.x > SCREEN_WIDTH+200 or 
            self.rect.y < -200 or self.rect.y > SCREEN_HEIGHT+200):
            self.kill()
            
# -------------------------
# Shield + Planet
# -------------------------

# -------------------------
# Main Scene
# -------------------------

# -------------------------
# Main Game Class
# -------------------------

# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    game = Game()
    game.run()