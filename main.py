import env, sensors
import pygame
import math
import voice_recog
import threading

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
voice_movement = {"forward": False}  # Dictionary to track movement states

# Start voice recognition in a separate thread
voice_thread = voice_recog.start_voice_recognition()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get voice command (if any)
    command = voice_recog.get_command()
    if command:
        if command == "forward":
            voice_movement["forward"] = True
        elif command == "stop":
            voice_movement["forward"] = False

    # Apply movement based on voice and keyboard input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        position[0] -= speed  # Move left
    if keys[pygame.K_RIGHT]:
        position[0] += speed  # Move right
    if keys[pygame.K_UP] or voice_movement["forward"]:  # Move up if "forward" is said
        position[1] -= speed  
    if keys[pygame.K_DOWN]:
        position[1] += speed  # Move down

    # Update laser position
    laser.position = tuple(position)
    sensor_data = laser.sense_obstacles()
    if sensor_data != -1:
        environment.dataStorage(sensor_data["obstacles"], sensor_data["free_spaces"])
        environment.show_sensorData()
        environment.update_robot_position(tuple(position))

    # Update display
    environment.map.blit(environment.infomap, (0, 0))
    pygame.display.update()

# Stop voice recognition when exiting
voice_recog.stop_voice_recognition()
voice_thread.join()
