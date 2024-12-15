from controller import Robot

robot = Robot()
time_step = int(robot.getBasicTimeStep())

# Motors
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0)
right_motor.setVelocity(0)

# IR sensors
ir_sensors = []
sensor_names = ['s1', 's2', 's3', 's4','s5']
weights = [-2, -1, 0, 1, 2]  

for name in sensor_names:
    sensor = robot.getDevice(name)
    sensor.enable(time_step)
    ir_sensors.append(sensor)

# PID constants
Kp = 0.5  # Proportional gain
Ki = 0.01  # Integral gain
Kd = 0.1  # Derivative gain

# PID variables
integral = 0
previous_error = 0

# Maximum speed for the motors
MAX_SPEED = 6.28

while robot.step(time_step) != -1:
    # Read sensor values
    sensor_values = [sensor.getValue() for sensor in ir_sensors]
    print("sensor_values = ", sensor_values)
    
    # Normalize sensor values (0 for white, 1 for black)
    normalized_values = [(1 if value < 500 else 0) for value in sensor_values] 
    
    numerator = sum(normalized_values[i] * weights[i] for i in range(len(weights)))
    denominator = sum(normalized_values)

    if denominator != 0:
        error = numerator / denominator
    else:
        error = previous_error
        
    print("-"*50)
    print("error = ", error)

    # PID control
    integral += error
    derivative = error - previous_error
    correction = Kp * error + Ki * integral + Kd * derivative
    previous_error = error

    left_speed = MAX_SPEED - correction
    right_speed = MAX_SPEED + correction

    left_speed = max(min(left_speed, MAX_SPEED), -MAX_SPEED)
    right_speed = max(min(right_speed, MAX_SPEED), -MAX_SPEED)

    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)
