# Direction: Stationary, Acceleration: 1.11, Ax: -0.05, Ay: 0.01, Az: 1.11, Gyro X: -0.29, Gyro Y: -0.07, Gyro Z: -0.09
Ax_offset = 0.05
Ay_offset = -0.01
Az_offset = 1.11
Gx_offset = 0.29
Gy_offset = 0.07
Gz_offset = 0.09

import smbus					#import SMBus module of I2C
from time import sleep          #import
import math

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

bus = smbus.SMBus(1) 	# For Raspberry Pi
Device_Address = 0x68   # MPU6050 device address

def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value

def get_motion_data():
    """
    Ax: Acceleration in X direction
    Ay: Acceleration in Y direction
    Az: Acceleration in Z direction
    Gx: Angular velocity in X direction
    Gy: Angular velocity in Y direction
    Gz: Angular velocity in Z direction
    """

    #Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)

    #Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)

    #Full scale range +/- 250 degree/C as per sensitivity scale factor
    Ax = acc_x/16384.0
    Ay = acc_y/16384.0
    Az = acc_z/16384.0

    Gx = gyro_x/131.0
    Gy = gyro_y/131.0
    Gz = gyro_z/131.0

    return Ax, Ay, Az, Gx, Gy, Gz

def get_direction_and_acceleration():
    Ax, Ay, Az, Gx, Gy, Gz = get_motion_data()

    # Calculate magnitude of acceleration vector
    accel_magnitude = math.sqrt(Ax**2 + Ay**2 + Az**2)

    # Determine direction based on Ax and Ay
    if Ax > 0.5:
        direction = "Right"
    elif Ax < -0.5:
        direction = "Left"
    elif Ay > 0.5:
        direction = "Forward"
    elif Ay < -0.5:
        direction = "Backward"
    else:
        direction = "Stationary"
    
    return direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz


def main():
    MPU_Init()

    print("Reading Data of Gyroscope and Accelerometer")

    # counter = 0
    # Ax_avg = 0
    # Ay_avg = 0
    # Az_avg = 0
    # Gx_avg = 0
    # Gy_avg = 0
    # Gz_avg = 0
    while True:
        # counter += 1
        direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz = get_direction_and_acceleration()
        # Ax_avg += Ax
        # Ay_avg += Ay
        # Az_avg += Az
        # Gx_avg += Gx
        # Gy_avg += Gy
        # Gz_avg += Gz

        # if counter % 10 == 0:
        #     Ax_avg /= 10
        #     Ay_avg /= 10
        #     Az_avg /= 10
        #     Gx_avg /= 10
        #     Gy_avg /= 10
        #     Gz_avg /= 10

            # print(f"Direction: {direction}, Acceleration: {accel_magnitude:.2f}, Ax: {Ax_avg:.2f}, Ay: {Ay_avg:.2f}, Az: {Az_avg:.2f}, Gyro X: {Gx_avg:.2f}, Gyro Y: {Gy_avg:.2f}, Gyro Z: {Gz_avg:.2f}")	
        print(f"Direction: {direction}, Acceleration: {accel_magnitude:.2f}, Ax: {(Ax + Ax_offset):.2f}, Ay: {(Ay + Ay_offset):.2f}, Az: {(Az + Az_offset):.2f}, Gyro X: {(Gx + Gx_offset):.2f}, Gyro Y: {(Gy + Gy_offset):.2f}, Gyro Z: {(Gz + Gz_offset):.2f}")
        sleep(1)

if __name__ == "__main__":
    main()