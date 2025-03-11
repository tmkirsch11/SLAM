import cv2
import heapq
import numpy as np
import time

def find_shortest_path(image_path, start, end):
    """Finds the shortest path using A* search algorithm, animates path drawing, and moves robot step by step."""
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)  # Load in color to draw the path
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray_image.shape

    # Stop the program identifying the robot itself as an obstacle
    cv2.circle(gray_image, start, 10, (255, 255, 255), -1) 

    # Ensure start and end are in free space
    if gray_image[start[1], start[0]] <= 150:
        print("Start position is in an obstacle! Aborting pathfinding.")
        return []
    if gray_image[end[1], end[0]] <= 150:
        print("End position is in an obstacle! Choose a different destination.")
        return []

    # Mark start and end points
    cv2.circle(image, start, 5, (0, 255, 0), -1)  # Green for start
    cv2.circle(image, end, 5, (0, 0, 255), -1)  # Red for end

    def heuristic(a, b):
        # Calculates the Manhattan distance between two points 'a' and 'b'
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(node):
        # Returns a list of valid neighbors for the given node.
        # It considers diagonal and orthogonal directions and ensures the point is within bounds and not blocked.
        x, y = node
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        result = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # Check if the neighbor is within bounds and not blocked (gray_image value > 150)
            if 0 <= nx < width and 0 <= ny < height and gray_image[ny, nx] > 150:
                result.append((nx, ny))
        return result

    # Initialize the open set with the start node (cost, distance, node)
    open_set = [(0 + heuristic(start, end), 0, start)]
    # Keep track of distances from the start node to each node
    distances = {start: 0}
    # Store the previous node for each node to reconstruct the path
    previous = {}
    # Set to keep track of visited nodes
    visited_nodes = set()

    while open_set:
        # Get the node with the lowest f = g + h value (priority queue)
        _, current_dist, current_node = heapq.heappop(open_set)

        # Skip the node if it has already been visited
        if current_node in visited_nodes:
            continue

        # Mark the current node as visited
        visited_nodes.add(current_node)

        # If the current node is the end node, we can stop the search
        if current_node == end:
            break

        # Explore each neighbor of the current node
        for neighbor in neighbors(current_node):
            # Calculate the new cost to reach the neighbor
            new_cost = current_dist + heuristic(current_node, neighbor)
            
            # If the neighbor has not been visited or we found a shorter path, update the cost and previous node
            if neighbor not in distances or new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                # Push the neighbor into the open set with its f = g + h value
                heapq.heappush(open_set, (new_cost + heuristic(neighbor, end), new_cost, neighbor))
                # Record the path to reconstruct the path later
                previous[neighbor] = current_node

    # Reconstruct the path from the end node to the start node
    path = []
    node = end
    while node in previous:
        path.append(node)
        node = previous[node]

    # Reverse the path to get it from start to end
    path.reverse()

    # Animate path drawing
    def animate_path_drawing(image, path):
        for i in range(len(path) - 1):
            cv2.line(image, path[i], path[i + 1], (255, 0, 0), 2)  # Blue path
            cv2.imshow("Path Animation - Sam KM", image)
            cv2.waitKey(1)  # Animation delay

        cv2.imwrite("mapped_environment_with_path.png", image)
        cv2.waitKey(500)
        cv2.destroyAllWindows()

    # Animate robot following the path
    def follow_path(image, path):
        time.sleep(1)  # Pause before the robot starts moving
        for i, point in enumerate(path):
            image_copy = image.copy()  # Create a fresh copy each time to remove the previous green dot
            cv2.circle(image_copy, point, 5, (0, 255, 0), -1)  # Green dot at the current position
            cv2.imshow("Robot Moving - Sam KM", image_copy)
            cv2.waitKey(10)  # Delay between movements

    if path:
        animate_path_drawing(image, path)
        follow_path(image, path)

    return path
