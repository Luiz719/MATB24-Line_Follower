from controller import Robot
import numpy as np
import csv

filename = 'my_data.csv'

# Initialize Webots Robot
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Initialize the camera
camera = robot.getDevice("camera")
camera.enable(timestep)

# Initialize the receiver
receiver = robot.getDevice("receiver")
receiver.enable(timestep)

# Initialize 4-wheel motors
left_front_motor = robot.getDevice("front left wheel")
left_back_motor = robot.getDevice("back left wheel")
right_front_motor = robot.getDevice("front right wheel")
right_back_motor = robot.getDevice("back right wheel")

# Main loop
while robot.step(timestep) != -1:
    speeds = [0,0,0,0]
    with open(filename, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([*speeds])

    