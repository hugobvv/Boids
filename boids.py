import pygame
import random
import math

# Screen settings
WIDTH, HEIGHT = 1000, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 102, 255)
MAX_SPEED = 4
NEIGHBOR_RADIUS = 50  # Distance to consider other birds as neighbors
SEPARATION_RADIUS = 25  # Minimum distance to maintain separation

# Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class Bird:
    def __init__(self, obstacles):
        # Find a valid spawn position
        while True:
            self.position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
            if not any(self.position.distance_to(obstacle.position) < obstacle.size for obstacle in obstacles):
                break
        
        self.size = 8
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * MAX_SPEED
    
    def draw(self, screen):
        # Draw triangle
        angle = math.atan2(self.velocity.y, self.velocity.x)  
        point1 = self.position + pygame.Vector2(self.size, 0).rotate_rad(angle)   
        point2 = self.position + pygame.Vector2(-self.size / 2, self.size / 2).rotate_rad(angle) 
        point3 = self.position + pygame.Vector2(-self.size / 2, -self.size / 2).rotate_rad(angle) 
        pygame.draw.polygon(screen, BLACK, [point1, point2, point3])

    def goesOverScreen(self):
        # Wrap around the screen 
        if self.position.x > WIDTH:  
            self.position.x = 0
        elif self.position.x < 0:    
            self.position.x = WIDTH

        if self.position.y > HEIGHT:  
            self.position.y = 0
        elif self.position.y < 0:   
            self.position.y = HEIGHT

    def moveAwayFromObstacle(self, obstacles):
        # Check if bird is inside an obstacle
        for obstacle in obstacles:
            distance = self.position.distance_to(obstacle.position)
            if distance < obstacle.size: 
                self.velocity.x = -self.velocity.x
                self.velocity.y = -self.velocity.y

    def update(self, birds, obstacles):
        sumDirection = pygame.Vector2(0, 0)
        sumSeparation = pygame.Vector2(0, 0)
        sumVelocity = pygame.Vector2(0, 0)
        nbNearBirds = 0

        for bird in birds:
            if bird == self:
                continue

            distance = self.position.distance_to(bird.position)

            if distance < NEIGHBOR_RADIUS:
                nbNearBirds += 1
                # Cohesion: move towards the average position of nearby birds
                sumDirection += bird.position

                # Separation: avoid crowding neighbors by moving away
                if distance < SEPARATION_RADIUS:
                    separation_vector = self.position - bird.position
                    if separation_vector.length() > 0: 
                        sumSeparation += separation_vector.normalize() / (distance + 1e-5)

                # Alignment: match velocity with nearby birds
                sumVelocity += bird.velocity

        randomForce = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) 
        if nbNearBirds > 0:
            # Calculate average positions and velocities
            average_position = sumDirection / nbNearBirds
            cohesionForce = (average_position - self.position)
            separationForce = sumSeparation   
            alignementForce = ((sumVelocity / nbNearBirds) - self.velocity) 

            # Balance force weight
            cohesionForce *= 0.008
            separationForce *= 0.7
            alignementForce *= 0.04
            randomForce *= 0.5

            # Combine forces
            total_force = cohesionForce + separationForce + alignementForce + randomForce

            # Update velocity with total force applied
            self.velocity += total_force

        else:
            # Add random path
            self.velocity += randomForce * 0.4

        # Cap velocity to max speed
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED

        # Update position
        self.position += self.velocity
        self.goesOverScreen()
        self.moveAwayFromObstacle(obstacles)


class Obstacle:
    def __init__(self):
        # Random position and size
        self.position = pygame.Vector2(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.size = random.randint(20, 100)

    def draw(self, screen):
        # Draw a circle
        pygame.draw.circle(screen, PINK , (int(self.position.x), int(self.position.y)), self.size)


# Initialize random birds and obstacles
obstacles = [Obstacle() for _ in range(4)]
birds = [Bird(obstacles) for _ in range(100)]

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)
    
    for obstacle in obstacles:
        obstacle.draw(screen)

    for bird in birds:
        bird.draw(screen)
        bird.update(birds, obstacles)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
