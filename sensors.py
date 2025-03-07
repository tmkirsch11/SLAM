import pygame
import math
import numpy as np

def uncertainty_add(distance, angle, sigma):
    mean = np.array([distance, angle])
    covariance = np.diag(sigma ** 2)
    distance, angle = np.random.multivariate_normal(mean, covariance)
    distance = max(distance,0)
    angle = max(angle,0)
    return [distance, angle]


class LaserSensor:

    def __init__(self,Range, map, uncertainty):
        self.Range = Range
        self.speed = 4 #rounds per second
        self.sigma = np.array([uncertainty[0], uncertainty[1]])
        self.position = (0,0)
        self.map=map
        self.w,self.h = pygame.display.get_surface().get_size()
        self.sensedObstacles = []
    
    def distance(self, obstaclePosition):
        px = (obstaclePosition[0]-self.position[0])**2
        py = (obstaclePosition[1]-self.position[1])**2
        return math.sqrt(px+py)
    
    def sense_obstacles(self):
        data = []
        free_spaces = []  # Stores free positions along the ray
        x1, y1 = self.position

        for angle in np.linspace(0, 2 * math.pi, 60, False):
            x2, y2 = x1 + self.Range * math.cos(angle), y1 - self.Range * math.sin(angle)
            ray_free = []  # Stores free spaces along the current ray

            for i in range(100):  # Iterate along the ray
                u = i / 100
                x = int(x2 * u + x1 * (1 - u))
                y = int(y2 * u + y1 * (1 - u))

                if 0 <= x < self.w and 0 <= y < self.h:
                    colour = self.map.get_at((x, y))

                    if colour[:3] == (0, 0, 0):  # Obstacle detected
                        distance = self.distance((x, y))
                        output = uncertainty_add(distance, angle, self.sigma)
                        output.append(self.position)
                        data.append(output)
                        break  # Stop further checks along this ray
                    
                    else:
                        ray_free.append((x, y))  # Mark as free space

            else:  
                # If no obstacle was found in this ray, add all free spaces
                free_spaces.extend(ray_free)

        return {"obstacles": data, "free_spaces": free_spaces}
