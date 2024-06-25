
import math
import numpy as np
import pandas as pd
import time
import json as js
import os

from model.system_motors import SystemMotors
from datetime import datetime  # Importa la función datetime

# My function to calculate the inverse kinematics of the Finger
def FingerInverseKinematics(incl, orien):
    #Medidas en m
    a = 0.013 #‘a' es la longitud del centro del triángulo al cables y en este caso ‘a' y ‘b' son iguales
    Lo = 0.098 # Longitud dedo en reposo
    radio = 0.008 #Radio de la polea donde se enrrolla el cable 

    # ángulos en radianes
    theta=incl*math.pi/180 
    psi=orien*math.pi/180 

    # Vector que guardará las variaciones
    v_lengths = np.zeros(2)

    if (theta!=0):
        R=Lo/theta

        phi8= (math.pi/2)-psi 
        phi7= (7*math.pi/6)-psi 

        v_lengths[0]= theta * a * math.cos(phi8) 
        v_lengths[1]= theta * a * math.cos(phi7)
        

    else:
        v_lengths[0]=0
        v_lengths[1]=0

    # Angulos en radianes de los motores
    posan8 = v_lengths[0]/radio #motor8
    posan7 = v_lengths[1]/radio #motor7

    return posan8, posan7


def main():
    # Motors
    id_fingers=[7,8]
    motors = SystemMotors(2)  # instantiate SystemMotors class >> number of motors
    motors.loadMotors(id_fingers, "SoftGripperMotorConfig.json")  # motor's ids
    motors.startMotors()  # start motors
    
    # Parameters of the DataFrame
    # Initial positions
    orientation = 0
    inclination = 0
    motors.setPositions([0,0])
    print("Vamos a cero")
    time.sleep(3)

    # Parameters of the DataFrame
    cols = ['time','inclination_ref', 'orientation_ref','pitch_ref_rad', 'yaw_ref_rad','pitch_ref_deg','yaw_ref_deg','M7', 'M8']
    data = []
    motors.setupPositionsMode(5, 5)  # setting velocity and acceleration values

    for orientation in range(90, 211, 10):  # Incrementa la orientación de 10 en 10 grados

        for inclination in range(5, 26, 5):  # Baja la inclinación de 5 en 5 grados hasta 25

            posan8, posan7 = FingerInverseKinematics(inclination, orientation)

           # creo que la ecuacion de pitch no deberia tener un -
            pitch = (inclination * math.pi / 180) * math.sin(orientation * math.pi / 180)  # radianes
            yaw = (-inclination * math.pi / 180) * math.cos(orientation * math.pi / 180)  # radianes
            pitch_deg = pitch * 180 / math.pi  # grados
            yaw_deg = yaw * 180 / math.pi # grados

            # Coloca las posiciones de los motores
            motors.setPositions([posan7, -posan8])

            # Muestreo temporal
            for i in np.arange(0, 2, 0.01):  # pasos de 0.01
                current_time = datetime.now().strftime("%M:%S.%f")
                data.append([current_time, inclination, orientation, pitch, yaw, pitch_deg, yaw_deg, motors.motorsArray[0].getPosition(),
                             motors.motorsArray[1].getPosition()])
            

        # Regresar a la posición inicial
        motors.setPositions([0, 0])
        for i in np.arange(0, 2, 0.01):
            current_time = datetime.now().strftime("%M:%S.%f")
            data.append([current_time, 0, 0, 0, 0, 0, 0,motors.motorsArray[0].getPosition(),
                         motors.motorsArray[1].getPosition()])

        df = pd.DataFrame(data, columns=cols)
        df.to_csv('/home/celia/Documentos/ROB. BLANDA/SOFIA_Python/data/Data_prueba_celia/cuarta_prueba/data_test2.2midiendo.csv',
                index=False)
        df.info()

    print("Data Ready")
    motors.setPositions([0,0])
    time.sleep(3)

if __name__ == "__main__":
    main()