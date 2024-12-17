import csv
import os
import sys
from controller import Robot

write_data = False
write_recovery_data = True  # Para escrever o segundo arquivo
suppress_print = True

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
gps.enable(time_step)

# Aguarda até que o GPS forneça uma posição inicial válida
start_position = None
while robot.step(time_step) != -1:
    start_position = gps.getValues()
    if not any(map(lambda x: x != x, start_position)):  # Verifica se não há 'NaN' nos valores
        break
print(f"Posição inicial capturada: {start_position}")

# Constantes do controlador PD
Kp = 100  # Ganho proporcional
Kd = 2    # Ganho derivativo

# Variáveis do controlador
previous_error = 0  # Para calcular o termo derivativo
minimum_run_time = 5.0  # Tempo mínimo antes de verificar retorno à posição inicial (em segundos)
start_time = robot.getTime()  # Captura o tempo inicial

# Velocidade máxima
MAX_SPEED = 6.28

if write_data:
    filename = "controle_PD.csv"

    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['timestamp', 'erro'])
            
if write_recovery_data:
    recovery_filename = "tempo_retorno_erro_pd.csv"
    if not os.path.exists(recovery_filename):
        with open(recovery_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['timestamp_inicio', 'tempo_retorno'])

# Função para calcular distância euclidiana entre duas posições
def calculate_distance(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2 + (pos1[2] - pos2[2]) ** 2) ** 0.5

# Variáveis para monitorar o tempo de retorno ao erro 0
error_start_time = None
is_error_active = False

# Loop principal
while robot.step(time_step) != -1:

    # Leitura dos sensores e normalização
    position = gps.getValues()  # Captura a posição atual do robô
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

    # Controle PD
    derivative = (error - previous_error) / (time_step / 1000.0)  # tempo em segundos
    correction = Kp * error + Kd * derivative
    previous_error = error  # Atualiza para a próxima iteração

    if not suppress_print:
        print("-" * 50)
        print("error = ", error)
        print("correction = ", correction)
        print("*=" * 50)
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
            
      # Monitoramento do tempo de retorno ao erro 0
    if error != 0:
        if not is_error_active:  # Novo erro detectado
            is_error_active = True
            error_start_time = robot.getTime()
    elif is_error_active:  # Erro voltou a 0
        is_error_active = False
        recovery_time = robot.getTime() - error_start_time
        with open(recovery_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([error_start_time, recovery_time])

    # Verifica se a posição atual é próxima à posição inicial
    # Apenas realiza a verificação após o tempo mínimo de execução
    current_time = robot.getTime()
    distance_to_start = calculate_distance(position, start_position)

    print(f"Tempo: {current_time:.2f}s | Distância até a posição inicial: {distance_to_start:.4f}")

    if current_time - start_time > minimum_run_time and distance_to_start < 0.05:  # Tolerância ajustada
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
        print("O robô retornou à posição inicial. Volta completa!")
        break
