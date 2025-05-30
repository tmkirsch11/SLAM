import math
import pygame
import numpy as np
import time

class buildEnvironment:
    def __init__(self, MapDimensions, scale, robot_radius=5):
        pygame.init()
        self.scale = scale
        self.robot_radius = robot_radius  # Define robot radius in pixels
        self.maph, self.mapw = MapDimensions
        self.externalMap = pygame.image.load('map1.png')
        self.MapWindowName = 'Mapping - Tom Kirsch'
        pygame.display.set_caption(self.MapWindowName)
        self.map = pygame.display.set_mode((self.mapw, self.maph))
        self.map.blit(self.externalMap, (0, 0))

        # Occupancy Grid using Log-Odds
        grid_width = self.mapw // self.scale
        grid_height = self.maph // self.scale
        self.occupancy_grid = np.zeros((grid_width, grid_height))  # Log-odds values

        # Log-Odds Parameters
        self.L_PRIOR = 0       # Prior log-odds
        self.L_OCC = 0.9       # Increase when occupied
        self.L_FREE = -0.7     # Decrease when free
        self.prob_threshold = 0.6  # Threshold for occupancy

        # Colours
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.white = (255, 255, 255)

        # Robot position (default center)
        self.robot_position = (self.mapw // 2, self.maph // 2)
        self.robot_angle = 0
        self.started_timer = False
        self.start_time = 0
        self.end_time = 0

    def AD2pos(self, distance, angle, robotPosition):
        """ Converts LiDAR distance & angle to a world position. """
        x = distance * math.cos(angle) + robotPosition[0]
        y = -distance * math.sin(angle) + robotPosition[1]
        return int(x), int(y)

    def dataStorage(self, obstacle_data, free_spaces):
        """ Processes LiDAR data and updates the occupancy grid. """
        for element in obstacle_data:
            obstacle_point = self.AD2pos(element[0], element[1], element[2])
            self.update_map(obstacle_point, self.robot_position, True)
        
        for element in free_spaces:
            self.update_map(element, self.robot_position, False)


    def update_map(self, obstacle, robot_position, obstacle_bool):
        """ Updates occupancy probabilities using log-odds. """
        grid_x, grid_y = obstacle[0] // self.scale, obstacle[1] // self.scale
        robot_x, robot_y = robot_position[0] // self.scale, robot_position[1] // self.scale

        if not (0 <= grid_x < self.occupancy_grid.shape[0] and 0 <= grid_y < self.occupancy_grid.shape[1]):
            return

        # Mark free space along the beam using Bresenham's line algorithm
        self.mark_free_space((robot_x, robot_y), (grid_x, grid_y), obstacle_bool)

        # Increase log-odds for occupied cells
        if obstacle_bool == True:
            self.occupancy_grid[grid_x, grid_y] += self.L_OCC

    def mark_free_space(self, start, end, obstacle_bool):
        """ Uses Bresenham's line algorithm to mark free cells between the sensor and the detected obstacle. """
        x0, y0 = start
        x1, y1 = end

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while (x0, y0) != (x1, y1):
            if obstacle_bool:
                self.occupancy_grid[x0, y0] += self.L_FREE  # Reduce log-odds for free space
            else:
                self.occupancy_grid[x0, y0] += -0.005
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def show_sensorData(self):
        """ Converts log-odds values to probabilities and visualizes them. """
        self.infomap = self.map.copy()
        probability_map = self.get_probability_map()

        for x in range(probability_map.shape[0]):
            for y in range(probability_map.shape[1]):
                probability = probability_map[x, y]
                color_value = int((1 - probability) * 255)  # Convert probability to grayscale
                color = (color_value, color_value, color_value)
                pygame.draw.rect(self.infomap, color, 
                                 (x * self.scale, y * self.scale, self.scale, self.scale))


    def get_probability_map(self):
        """ Converts log-odds to probability using the inverse sigmoid function. """
        return 1 / (1 + np.exp(-np.clip(self.occupancy_grid, -100, 100)))

    def update_robot_position(self, new_position):
        """ Updates the robot's position while keeping sensor data. """
        if self.robot_position != new_position:
            if self.started_timer == False:
                self.started_timer = True
                self.start_time = time.time()
            else:
                self.end_time = time.time()
                diff = self.end_time - self.start_time
                
                # Store diffs and print max when a new max is found
                if not hasattr(self, "diff_list"):
                    self.diff_list = []
                
                self.diff_list.append(diff)
                # if diff == max(self.diff_list):  # Print only when a new max is found
                #     print(f"New max time: {diff:.6f} seconds")

                self.started_timer = False

        self.robot_position = new_position
        self.draw_robot(self.robot_angle)


    def draw_robot(self, angle=0):
        """Draws the robot as a triangle pointing in the direction of movement."""
        x, y = self.robot_position
        size = self.robot_radius * 2  # Triangle size

        # Calculate triangle vertices
        points = [
            (x + size * math.cos(angle), y + size * math.sin(angle)),  # Front
            (x + size * 0.5 * math.cos(angle + 2.1), y + size * 0.5 * math.sin(angle + 2.1)),  # Back-left
            (x + size * 0.5 * math.cos(angle - 2.1), y + size * 0.5 * math.sin(angle - 2.1))   # Back-right
        ]

        # Draw triangle
        pygame.draw.polygon(self.infomap, self.green, points)





