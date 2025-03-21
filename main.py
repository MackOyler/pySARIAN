import pygame
import math
import random
import sys

# -------------------------
# Global Constants
# -------------------------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
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
# Decorative Moon Class
# -------------------------
class Moon(pygame.sprite.Sprite):
    def __init__(self, image, planet_center, orbit_radius, orbit_speed, initial_angle, scale):
        super().__init__()
        self.original_image = pygame.transform.scale(
            image, (int(image.get_width() * scale), int(image.get_height() * scale))
        )
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.planet_center = planet_center
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed  # degrees per frame
        self.angle = initial_angle
        self.update_position()
        
    def update_position(self):
        rad = math.radians(self.angle)
        self.rect.center = (
            self.planet_center[0] + self.orbit_radius * math.cos(rad),
            self.planet_center[1] + self.orbit_radius * math.sin(rad)
        )
    
    def update(self):
        self.angle = (self.angle + self.orbit_speed) % 360
        self.update_position()

# -------------------------
# Title Scene
# -------------------------
class TitleScene:
    def __init__(self):
        self.background = None
        self.planet = None
        self.play_button = None
        self.font = None
        self.play_button_rect = None
        self.title_image = None  # Title sprite

    def load_resources(self):
        self.background = load_image("background.png")
        self.planet = load_image("planet.png")
        self.play_button = load_image("play_button.png")
        self.font = pygame.font.SysFont("Arial", 48)
        
        # Load and scale the title sprite (title.png)
        self.title_image = load_image("title.png")
        desired_width = 300  # Adjust this value to control the title image size
        original_width, original_height = self.title_image.get_size()
        aspect_ratio = original_height / original_width
        scaled_height = int(desired_width * aspect_ratio)
        self.title_image = pygame.transform.scale(self.title_image, (desired_width, scaled_height))

    def start(self):
        pass

    def handle_events(self, event, game):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if self.play_button_rect and self.play_button_rect.collidepoint(mouse_x, mouse_y):
                game.change_scene(SCENE_MAIN)

    def update(self, dt, game):
        pass

    def draw(self, surface):
        # Draw background
        surface.blit(pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        
        # Draw planet in the center
        planet_scaled = pygame.transform.scale(
            self.planet, (int(self.planet.get_width() * 0.4), int(self.planet.get_height() * 0.4))
        )
        planet_rect = planet_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(planet_scaled, planet_rect)
        
        # Draw title sprite (remove any text, using only the image)
        title_rect = self.title_image.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(self.title_image, title_rect)
        
        # Draw the play button
        play_scaled = pygame.transform.scale(self.play_button, (100, 100))
        self.play_button_rect = play_scaled.get_rect(center=(SCREEN_WIDTH // 2, 400))
        surface.blit(play_scaled, self.play_button_rect)

# -------------------------
# Particle Class (dust effect)
# -------------------------
class DustParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, image, lifetime=30):
        super().__init__()
        self.image_original = image
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = lifetime
        self.age = 0

    def update(self):
        self.age += 1
        if self.age >= self.lifetime:
            self.kill()
        else:
            scale_factor = 1.0 - (self.age / self.lifetime)
            w = int(self.image_original.get_width() * scale_factor)
            h = int(self.image_original.get_height() * scale_factor)
            if w <= 0 or h <= 0:
                self.kill()
            else:
                self.image = pygame.transform.smoothscale(self.image_original, (w, h))
                self.rect = self.image.get_rect(center=self.rect.center)

# -------------------------
# PlusOne Sprite (for the "+1" popup)
# -------------------------
class PlusOne(pygame.sprite.Sprite):
    def __init__(self, x, y, font, color=(255,255,255), lifetime=30):
        super().__init__()
        self.font = font
        self.text = "+1"
        self.image = self.font.render(self.text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = lifetime
        self.age = 0
        self.vy = -1  # Moves upward slowly

    def update(self):
        self.age += 1
        self.rect.y += self.vy
        if self.age >= self.lifetime:
            self.kill()

# -------------------------
# Asteroid Sprite
# -------------------------
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, image, planet_center, speed=5):
        super().__init__()
        self.image_original = image
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.planet_center = planet_center
        self.speed = speed

        dx = planet_center[0] - x
        dy = planet_center[1] - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed
        self.radius = self.rect.width // 2

    def update(self, dt=1.0):
        self.rect.x += self.vx * (dt / 16.67)
        self.rect.y += self.vy * (dt / 16.67)
        if (self.rect.x < -200 or self.rect.x > SCREEN_WIDTH + 200 or 
            self.rect.y < -200 or self.rect.y > SCREEN_HEIGHT + 200):
            self.kill()

# -------------------------
# Shield + Planet
# -------------------------
class Shield:
    """
    A shield that uses a single bounding circle for collision,
    matching the scaled sprite as closely as possible.
    """
    def __init__(self, image, planet_center, radius=150, angle=100):
        self.image_original = image
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.center = planet_center
        self.radius = radius  # Distance from planet center
        self.angle_deg = angle

        # Scale the shield
        self.scale = 0.07
        new_w = int(self.image.get_width() * self.scale)
        new_h = int(self.image.get_height() * self.scale)
        self.image = pygame.transform.scale(self.image, (new_w, new_h))
        self.rect = self.image.get_rect()

        # Single bounding circle approximating the shield's shape
        shield_collision_factor = 0.47  # Tweak this to adjust collision accuracy
        self.collision_radius = (new_w / 2) * shield_collision_factor

    def rotate_left(self, speed):
        self.angle_deg -= speed

    def rotate_right(self, speed):
        self.angle_deg += speed

    def get_position(self):
        rad = math.radians(self.angle_deg)
        x = self.center[0] + self.radius * math.cos(rad)
        y = self.center[1] + self.radius * math.sin(rad)
        return (x, y)

    def update(self):
        pass

    def draw(self, surface):
        shield_center = self.get_position()
        angle_for_blit = -self.angle_deg - 90
        rotated_image = pygame.transform.rotate(self.image, angle_for_blit)
        rect = rotated_image.get_rect(center=shield_center)
        surface.blit(rotated_image, rect)

    def get_collision_circles(self):
        return [(self.get_position()[0], self.get_position()[1], self.collision_radius)]

# -------------------------
# Main Scene
# -------------------------
class MainScene:
    def __init__(self):
        self.background = None
        self.planet = None
        self.shield_image = None
        self.asteroid_image = None
        self.pause_button = None
        self.dust_image = None

        self.score = 0         # Current score (displayed as 1UP)
        self.high_score = 0    # Highest score for the session
        self.lives = 3         # Internal lives count (not displayed)
        self.is_paused = False

        self.planet_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)

        self.asteroids = pygame.sprite.Group()
        self.dust_particles = pygame.sprite.Group()
        self.plus_ones = pygame.sprite.Group()
        self.moons = pygame.sprite.Group()

        self.spawn_event = 0
        self.spawn_delay = 1000  # ms

        self.font_small = None
        self.font_big = None

    def load_resources(self):
        self.background = load_image("background.png")
        self.planet = load_image("planet.png")
        self.shield_image = load_image("shield.png")
        self.asteroid_image = load_image("asteroid.png")
        self.pause_button = load_image("pause_button.png")
        self.dust_image = load_image("dust.png")
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_big = pygame.font.SysFont("Arial", 40)
        # Load the 5 moon images
        self.moon_images = [
            load_image("moon1.png"),
            load_image("moon2.png"),
            load_image("moon3.png"),
            load_image("moon4.png"),
            load_image("moon5.png")
        ]

    def start(self):
        self.score = 0
        self.lives = 3
        self.is_paused = False

        self.planet_scaled = pygame.transform.scale(
            self.planet, (int(self.planet.get_width() * 0.25),
                          int(self.planet.get_height() * 0.25))
        )
        self.planet_rect = self.planet_scaled.get_rect(center=self.planet_center)
        self.shield = Shield(self.shield_image, self.planet_center, radius=150, angle=100)

        self.asteroids.empty()
        self.dust_particles.empty()
        self.plus_ones.empty()
        self.moons.empty()

        # Define fixed orbits for 5 moons (radius, starting angle)
        fixed_orbits = [
            (190,   0),
            (250,  72),
            (320, 144),
            (380, 216),
            (450, 288)
        ]
        orbit_speed = 0.1
        for i, img in enumerate(self.moon_images):
            radius, angle = fixed_orbits[i]
            scale = random.uniform(0.05, 0.09)
            moon = Moon(img, self.planet_center, orbit_radius=radius, orbit_speed=orbit_speed, initial_angle=angle, scale=scale)
            self.moons.add(moon)

        self.spawn_event = pygame.time.get_ticks()

    def handle_events(self, event, game):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if self.pause_btn_rect.collidepoint(mouse_x, mouse_y):
                self.is_paused = not self.is_paused
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_p, pygame.K_SPACE):
                self.is_paused = not self.is_paused

    def update(self, dt, game):
        if self.is_paused:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.shield.rotate_left(4)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.shield.rotate_right(4)

        now = pygame.time.get_ticks()
        if now - self.spawn_event > self.spawn_delay:
            self.spawn_asteroid()
            self.spawn_event = now

        self.asteroids.update(dt)
        self.dust_particles.update()
        self.plus_ones.update()
        self.moons.update()

        self.check_shield_collisions()
        self.check_planet_collisions()

    def draw(self, surface):
        surface.blit(pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        self.moons.draw(surface)
        surface.blit(self.planet_scaled, self.planet_rect)
        self.shield.draw(surface)

        self.asteroids.draw(surface)
        self.dust_particles.draw(surface)
        self.plus_ones.draw(surface)

        draw_text(surface, f"HIGH SCORE: {self.high_score}", SCREEN_WIDTH // 2, 20,
                  self.font_small, (255, 0, 0))
        draw_text(surface, f"1UP: {self.score}", SCREEN_WIDTH - 80, 20,
                  self.font_small, (255, 255, 255), center=False)

        pause_scaled = pygame.transform.scale(self.pause_button, (50, 50))
        self.pause_btn_rect = pause_scaled.get_rect(topleft=(20, 20))
        surface.blit(pause_scaled, self.pause_btn_rect)

        if self.is_paused:
            draw_text(surface, "PAUSED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                      self.font_big, (255, 255, 0))

    def spawn_asteroid(self):
        angle = random.randint(0, 359)
        distance = 600
        rad = math.radians(angle)
        x = self.planet_center[0] + distance * math.cos(rad)
        y = self.planet_center[1] + distance * math.sin(rad)
        asteroid = Asteroid(
            x,
            y,
            pygame.transform.scale(self.asteroid_image, (50, 50)),
            self.planet_center,
            speed=5
        )
        self.asteroids.add(asteroid)

    def check_shield_collisions(self):
        circles = self.shield.get_collision_circles()  # returns [(cx, cy, r)]
        for asteroid in self.asteroids:
            for (cx, cy, cr) in circles:
                dx = asteroid.rect.centerx - cx
                dy = asteroid.rect.centery - cy
                dist_sq = dx * dx + dy * dy
                radius_sum = asteroid.radius + cr
                if dist_sq <= (radius_sum * radius_sum):
                    self.handle_asteroid_blocked(asteroid)
                    break

    def handle_asteroid_blocked(self, asteroid):
        dust = DustParticle(
            asteroid.rect.centerx,
            asteroid.rect.centery,
            pygame.transform.scale(self.dust_image, (32, 32)),
            lifetime=30
        )
        self.dust_particles.add(dust)

        plus_one = PlusOne(asteroid.rect.centerx, asteroid.rect.centery,
                           self.font_small, lifetime=30)
        self.plus_ones.add(plus_one)

        asteroid.kill()
        self.score += 1
        if self.score > self.high_score:
            self.high_score = self.score

    def check_planet_collisions(self):
        planet_radius = self.planet_rect.width * 0.5
        px, py = self.planet_rect.center
        for asteroid in self.asteroids:
            dx = asteroid.rect.centerx - px
            dy = asteroid.rect.centery - py
            dist_sq = dx * dx + dy * dy
            radius_sum = asteroid.radius + planet_radius
            if dist_sq <= (radius_sum * radius_sum):
                asteroid.kill()
                self.lives -= 1
                if self.lives <= 0:
                    self.start()

# -------------------------
# Main Game Class
# -------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sarian in Pygame")
        self.clock = pygame.time.Clock()

        self.scenes = {
            SCENE_TITLE: TitleScene(),
            SCENE_MAIN: MainScene()
        }
        self.current_scene_key = SCENE_TITLE
        self.current_scene = self.scenes[self.current_scene_key]

        for scene in self.scenes.values():
            scene.load_resources()

        self.current_scene.start()

    def change_scene(self, new_scene_key):
        self.current_scene_key = new_scene_key
        self.current_scene = self.scenes[new_scene_key]
        self.current_scene.start()

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.current_scene.handle_events(event, self)
            self.current_scene.update(dt, self)
            self.current_scene.draw(self.screen)
            pygame.display.flip()

# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    game = Game()
    game.run()