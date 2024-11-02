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

    while True:
        
        direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz = get_direction_and_acceleration()
        print(f"Direction: {direction}, Acceleration: {accel_magnitude:.2f}, Ax: {Ax:.2f}, Ay: {Ay:.2f}, Az: {Az:.2f}, Gyro X: {Gx:.2f}, Gyro Y: {Gy:.2f}, Gyro Z: {Gz:.2f}")	
        sleep(1)

if __name__ == "__main__":
    main()