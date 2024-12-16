import csv
import os
import sys
from controller import Robot

write_data = True
finished = False
suppress_print = False

robot = Robot()
time_step = int(robot.getBasicTimeStep())

left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0)
right_motor.setVelocity(0)

# Sensores IR
ir_sensors = []
sensor_names = ['s1', 's2', 's3', 's4', 's5']

# Ofsets para calcular o erro de desvio
offsets = [0.02, 0.01, 0, -0.01, -0.02]

for name in sensor_names:
    sensor = robot.getDevice(name)
    sensor.enable(time_step)
    ir_sensors.append(sensor)

gps = robot.getDevice("gps")

# Constantes do controlador PD
Kp = 100 # Ganho proporcional
Kd = 2    # Ganho derivativo

# Variáveis do controlador
previous_error = 0  # Para calcular o termo derivativo

# Velocidade máxima
MAX_SPEED = 6.28

if write_data:
    filename = "controle_PD.csv"

    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['timestamp', 'erro'])

# Loop principal
while robot.step(time_step) != -1:

    # Leitura dos sensores e normalização
    gps.enable(time_step)
    position = gps.getValues()
    sensor_values = [sensor.getValue() for sensor in ir_sensors]
    normalized_values = [(0 if value < 500 else 1) for value in sensor_values]

    # Calculo do erro com base nos offsets
    error = 0
    if normalized_values[2] == 1:  
        error = 0
    elif 1 in normalized_values:  
        first_black_index = normalized_values.index(1)
        error = offsets[first_black_index]
    else:  # Caso não veja nenhuma linha
        error = previous_error  # Preserva o erro anterior

    # Impressão do erro para debug
    print("-" * 50)
    print("Error = ", error)

    # Controle PD
    # Aqui é necessário dividir pela diferença de tempo (time_step) para a derivada
    derivative = (error - previous_error) / (time_step / 1000.0)  # tempo em segundos
    correction = Kp * error + Kd * derivative
    previous_error = error  # Atualiza para a próxima iteração
    
    print("Correction = ", correction)

    if not suppress_print:
        print("-"*50)
        print("error = ", error)
        print("correction = ", correction)
        print("*="*50)
        print("time = ", robot.getTime())

    # Calcula a velocidade das rodas com base na correção
    left_speed = MAX_SPEED - correction
    right_speed = MAX_SPEED + correction

    left_speed = max(min(left_speed, MAX_SPEED), -MAX_SPEED)
    right_speed = max(min(right_speed, MAX_SPEED), -MAX_SPEED)

    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)
  
    if write_data:
        timestamp = robot.getTime()
        with open(filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([timestamp, error])
    if finished:
        sys.exit(0)
    
    if round(position[0],2) == round(-0.899227,2) and round(position[1],2) == round(0.00317222,2):
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
        print("Volta Completa")
        break
