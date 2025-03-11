import env, sensors
import pygame
import cv2
from path_planner import find_shortest_path

# Initialize environment
pixels_per_square = 5  # Each pixel is 5cm
environment = env.buildEnvironment((600, 1200), pixels_per_square)  # 30m x 60m
environment.originalMap = environment.map.copy()
laser = sensors.LaserSensor(200, environment.originalMap, uncertainty=(0.5, 0.01))
environment.map.fill((0, 0, 0))
environment.infomap = environment.map.copy()

# Start position at the center of the screen
position = [environment.map.get_width() // 2, environment.map.get_height() // 2]
speed = 5  # Movement speed

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        position[0] -= speed  # Move left
    if keys[pygame.K_RIGHT]:
        position[0] += speed  # Move right
    if keys[pygame.K_UP]:
        position[1] -= speed  # Move up
    if keys[pygame.K_DOWN]:
        position[1] += speed  # Move down

    # Update laser position
    laser.position = tuple(position)
    sensor_data = laser.sense_obstacles()
    if sensor_data != -1:
        environment.dataStorage(sensor_data)
        environment.show_sensorData()
        environment.update_robot_position(tuple(position))

    environment.map.blit(environment.infomap, (0, 0))
    pygame.display.update()

# Save the mapped environment when closing
pygame.image.save(environment.infomap, "mapped_environment.png")
pygame.quit()

# Open the path selection window
def select_destination():
    image = cv2.imread("mapped_environment.png")
    cv2.imshow("Select Destination - Sam KM", image)
    
    def get_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            destination = (x, y)
            path = find_shortest_path("mapped_environment.png", tuple(position), destination)
            for point in path:
                cv2.circle(image, point, 2, (0, 0, 255), -1)
    
    cv2.setMouseCallback("Select Destination - Sam KM", get_click)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    select_destination()

