import csv
import os
import sys
from controller import Robot

write_data = False
finished = False
suppress_print = True

robot = Robot()
time_step = int(robot.getBasicTimeStep())

left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0)
right_motor.setVelocity(0)

# IR sensors
ir_sensors = []
sensor_names = ['s1', 's2', 's3', 's4','s5']

offsets = [0.02, 0.01, 0, -0.01, -0.02]

for name in sensor_names:
    sensor = robot.getDevice(name)
    sensor.enable(time_step)
    ir_sensors.append(sensor)

# PID constants
Kp = 80  # Proportional gain
Ki = 0.1  # Integral gain
Kd = 2  # Derivative gain

# PID variables
integral = 0
previous_error = 0

MAX_SPEED = 6.28

if write_data:
    filename = "controle_PID.csv"

    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['timestamp', 'erro'])


while robot.step(time_step) != -1:
    sensor_values = [sensor.getValue() for sensor in ir_sensors]
    
    normalized_values = [(0 if value < 500 else 1) for value in sensor_values] 

    error = 0  
    if normalized_values[2] == 1:  
        error = 0
    elif 1 in normalized_values:  
        first_black_index = normalized_values.index(1)
        error = offsets[first_black_index]  
    else:
        error = previous_error

    # PID control
    integral += error
    derivative = error - previous_error
    correction = Kp * error + Ki * integral + Kd * derivative
    previous_error = error

    if not suppress_print:
        print("-"*50)
        print("error = ", error)
        print("correction = ", correction)
        print("*="*50)
        print("time = ", robot.getTime())

    left_speed = MAX_SPEED - correction
    right_speed = MAX_SPEED + correction

    left_speed = max(min(left_speed, MAX_SPEED), -MAX_SPEED)
    right_speed = max(min(right_speed, MAX_SPEED), -MAX_SPEED)

    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)

    finished = robot.getTime() >= 85.7280

    if write_data:
        timestamp = robot.getTime()
        with open(filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([timestamp, error])
    
    if finished:
        sys.exit(0)