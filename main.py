import env, sensors
import pygame
import math
import voice_recog
import threading
import re  # Import regex for extracting numbers

# Initialize environment
pixels_per_square = 5  # Each pixel is 5cm
environment = env.buildEnvironment((600, 1200), pixels_per_square)  # 30m x 60m
environment.originalMap = environment.map.copy()
laser = sensors.LaserSensor(200, environment.originalMap, uncertainty=(0.5, 0.01))
environment.map.fill((0, 0, 0))
environment.infomap = environment.map.copy()

# Start position at the center of the screen
position = [environment.map.get_width() // 2, environment.map.get_height() // 2]
robot_angle = 0
speed = 5  # Movement speed
angular_speed = 5



voice_movement = {
    "forward": False,
    "turn": False,
    "radians": 0,  # Store turn angle in radians
    "right": False,
    "left": False
}

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
        #command = command.lower().replace(" ", "")  # Normalize input

        if command == "forward":
            voice_movement["forward"] = True
        elif command == "stop":
            voice_movement["forward"] = False
        else:
            # Check for rotation commands like "turn 180 to the left"
            pattern1 = re.search(r"turn\s*(\d+)\s*(degrees|radians)?\s*(left|right|anticlockwise|clockwise)?", command)
            # Pattern 2: "turn left 180 degrees"
            pattern2 = re.search(r"turn\s*(left|right|anticlockwise|clockwise)\s*(\d+)\s*(degrees|radians)?", command)

            if pattern1 or pattern2:
                if pattern1:
                    angle = int(pattern1.group(1))
                    direction = pattern1.group(3)
                    unit = pattern1.group(2) if pattern1.group(2) else "degrees"
                elif pattern2:
                    direction = pattern2.group(1)
                    angle = int(pattern2.group(2))
                    unit = pattern2.group(2) if pattern2.group(2) else "degrees"

                print(angle, unit, direction)
                # Convert to radians if necessary
                if unit == "degrees":
                    voice_movement["radians"] = math.radians(angle)
                else:
                    voice_movement["radians"] = angle  # Already in radians

                # Set the correct turning direction
                if direction in ["left", "anticlockwise"]:
                    voice_movement["left"] = True
                    voice_movement["right"] = False
                elif direction in ["right", "clockwise"]:
                    voice_movement["right"] = True
                    voice_movement["left"] = False

                # Mark turning as active
                voice_movement["turn"] = True
    
    if voice_movement["left"] == True:
        robot_angle -= voice_movement["radians"]
        voice_movement["left"] = False
    elif voice_movement["right"] == True:
        robot_angle += voice_movement["radians"]
        voice_movement["right"] = False



    # Apply movement based on voice and keyboard input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        robot_angle -= math.radians(angular_speed)  # Rotate left
    if keys[pygame.K_RIGHT]:
        robot_angle += math.radians(angular_speed)  # Rotate right
    if keys[pygame.K_UP] or voice_movement["forward"]:  # Move forward in the current direction
        position[0] += speed * math.cos(robot_angle)  # Update X using cosine
        position[1] += speed * math.sin(robot_angle)  # Update Y using sine
    if keys[pygame.K_DOWN]:  # Move backward
        position[0] -= speed * math.cos(robot_angle)
        position[1] -= speed * math.sin(robot_angle)

    # Update laser position
    laser.position = tuple(position)
    environment.robot_angle = robot_angle
    sensor_data = laser.sense_obstacles()
    if sensor_data != -1:
        environment.dataStorage(sensor_data["obstacles"], sensor_data["free_spaces"])
        environment.show_sensorData()
        environment.update_robot_position((int(position[0]), int(position[1])))


    # Update display
    environment.map.blit(environment.infomap, (0, 0))
    pygame.display.update()

# Stop voice recognition when exiting
voice_recog.stop_voice_recognition()
voice_thread.join()
