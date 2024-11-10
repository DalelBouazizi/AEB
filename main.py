# -*- coding: utf-8 -*-
import pygame
import sys
import math

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation AEB avec Freinage d'Urgence - Pygame")

# Couleurs
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
MARRON = (139, 69, 19)  # Couleur marron
RED = (255, 0, 0)  # Couleur rouge

# Paramètres du véhicule
CAR_WIDTH, CAR_HEIGHT = 50, 100
car_speed = 1
braking_distance = 100  # Distance minimale pour activer le freinage d'urgence

# Positions des lignes rouges
LEFT_LINE_X = 300
RIGHT_LINE_X = 500

# Temps avant de supprimer l'obstacle (en millisecondes)
REMOVE_OBSTACLE_TIME = 11000  # 5 secondes

# Charger les images
car_image = pygame.image.load("car.png")
car_image = pygame.transform.scale(car_image, (CAR_WIDTH, CAR_HEIGHT))
obstacle_image = pygame.image.load("obstacle.png")
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))
bike_image = pygame.image.load("cycling.png")
bike_image = pygame.transform.scale(bike_image, (40, 60))  # Ajustez la taille selon votre image

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = car_speed
        self.braking = False
        self.image = car_image

    def move(self):
        if not self.braking:
            self.y -= self.speed  # Déplacer la voiture vers le haut

    def draw(self):
        window.blit(self.image, (self.x, self.y))

    def detect_collision(self, obstacle):
        # Coordonnées du centre de la voiture et de l'obstacle
        car_center = (self.x + CAR_WIDTH // 2, self.y + CAR_HEIGHT // 2)
        obstacle_center = (obstacle.x + obstacle.width // 2, obstacle.y + obstacle.height // 2)
        is_in_braking_distance = car_center[1] > obstacle_center[1] and abs(car_center[1] - obstacle_center[1]) <= braking_distance
        if is_in_braking_distance:
            if isinstance(obstacle, MovingObstacle):
                if LEFT_LINE_X < obstacle.x < RIGHT_LINE_X:  # Vérifie si le vélo est entre les lignes rouges
                        self.braking = True  # Activer le freinage pour le vélo
                         # Ne pas continuer si une condition de freinage est déjà remplie

        # Vérifier la condition de freinage pour l'obstacle statique devant la voiture
            else:
                self.braking = True  # Activer le freinage pour l'obstacle statique

    def reset_speed(self):
        """Reinitialiser la vitesse de la voiture a la vitesse initiale."""
        self.speed = car_speed
        self.braking = False

    def draw_dashboard(self):
        font = pygame.font.Font(None, 30)
        speed_text = font.render(f'Speed: {int(self.speed)}', True, (0, 0, 0))
        braking_text = font.render(f'Braking: {"Yes" if self.braking else "No"}', True, (0, 0, 0))
        window.blit(speed_text, (10, 10))
        window.blit(braking_text, (10, 40))

    def draw_sensors(self, obstacles):
        sensor_length = braking_distance
        angles = [-30, 0, 30]

        for angle in angles:
            end_x = self.x + CAR_WIDTH // 2 + sensor_length * math.sin(math.radians(angle))
            end_y = self.y + sensor_length * math.cos(math.radians(angle))

            detected = False
            for obstacle in obstacles:
                if obstacle.rect.collidepoint(end_x, end_y):
                    detected = True
                    break

            color = MARRON if self.braking else GREEN
            pygame.draw.line(window, color, (self.x + CAR_WIDTH // 2, self.y), (end_x, end_y), 3)

class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width, self.height = width, height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        window.blit(obstacle_image, (self.x, self.y))

class MovingObstacle:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.width, self.height = 40, 60
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self):
        self.x += self.speed
        if self.x > WIDTH:
            self.x = -self.width
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        window.blit(bike_image, (self.x, self.y))

# Initialisation de la voiture et des obstacles
car = Car(WIDTH // 2, HEIGHT - CAR_HEIGHT - 10)
static_obstacle = Obstacle(WIDTH // 2, HEIGHT // 3, 50, 50)
moving_obstacle = MovingObstacle(0, HEIGHT // 2, 3)  # Créer un obstacle mobile horizontal avec une vitesse de 3
obstacles = [static_obstacle, moving_obstacle]

# Variables de temps
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    elapsed_time = pygame.time.get_ticks() - start_time

    # Supprimer l'obstacle statique après un certain temps
    if elapsed_time > REMOVE_OBSTACLE_TIME and static_obstacle in obstacles:
        obstacles.remove(static_obstacle)
        car.reset_speed()  # Réinitialiser la vitesse lorsque l'obstacle est supprimé

    for obs in obstacles:
        if isinstance(obs, MovingObstacle):
            obs.move()

    car.braking = False  # Réinitialiser l'état de freinage avant la détection

    for obs in obstacles:
        car.detect_collision(obs)  # Détection de collision avec chaque obstacle
    
    car.move()  # Déplacement de la voiture

    window.fill(WHITE)

    # Dessiner les lignes rouges en arrière-plan
    pygame.draw.line(window, RED, (LEFT_LINE_X, 0), (LEFT_LINE_X, HEIGHT), 3)
    pygame.draw.line(window, RED, (RIGHT_LINE_X, 0), (RIGHT_LINE_X, HEIGHT), 3)

    car.draw()
    car.draw_dashboard()
    car.draw_sensors(obstacles)
    
    for obs in obstacles:
        obs.draw()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()