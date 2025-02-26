import math
import pygame

class buildEnvironment:
    def __init__(self, MapDimensions):
        pygame.init()
        self.pointCloud = []
        self.externalMap = pygame.image.load('map1.png')
        self.maph, self.mapw = MapDimensions
        self.MapWindowName = 'Mapping - Tom Kirsch'
        pygame.display.set_caption(self.MapWindowName)
        self.map = pygame.display.set_mode((self.mapw, self.maph))
        self.map.blit(self.externalMap, (0, 0))
        
        # Colours
        self.black = (0, 0, 0)
        self.grey = (70, 70, 70)
        self.blue = (0, 0, 255)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)
        self.white = (255, 255, 255)

        # Robot position (default center)
        self.robot_position = (self.mapw // 2, self.maph // 2)

    def AD2pos(self, distance, angle, robotPosition):
        x = distance * math.cos(angle) + robotPosition[0]
        y = -distance * math.sin(angle) + robotPosition[1]
        return (int(x), int(y))

    def dataStorage(self, data):
        print(len(self.pointCloud))
        for element in data:
            point = self.AD2pos(element[0], element[1], element[2])
            if point not in self.pointCloud:
                self.pointCloud.append(point)

    def show_sensorData(self):
        self.infomap = self.map.copy()
        
        # Draw the scanned points
        for point in self.pointCloud:
            self.infomap.set_at((int(point[0]), int(point[1])), self.red)
        
        self.infomap.set_at((int(self.robot_position[0]), int(self.robot_position[1])), self.green)


    def update_robot_position(self, new_position):
        """ Updates the robot's position while keeping sensor data. """
        # Restore the previous robot position to match the background color
        self.infomap.set_at((int(self.robot_position[0]), int(self.robot_position[1])), self.black)

        # Update the robot's position
        self.robot_position = new_position

        # Draw new robot position
        self.infomap.set_at((int(self.robot_position[0]), int(self.robot_position[1])), self.green)

