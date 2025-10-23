import smbus
from collections import deque

# ===============================
# IMU Controller: Controls the IMU(MPU6050) module
# ===============================
class IMUController:
    # MPU6050 Registers
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

    # Offsets for calibration
    Ax_offset = 0.05
    Ay_offset = -0.01
    Az_offset = -1.11
    Gx_offset = 0.29
    Gy_offset = 0.07
    Gz_offset = 0.09

    # Filtering and Thresholds
    GYRO_WINDOW = 10
    GYRO_THRESHOLD = 5.0  # degrees/sec

    # Initializes the I2C bus, sets device address, creates a gyro buffer, and initializes the MPU6050 sensor.
    def __init__(self, bus_id=1, device_address=0x68):
        self.bus = smbus.SMBus(bus_id)
        self.device_address = device_address
        self.gyro_buffer = deque(maxlen=self.GYRO_WINDOW)
        self.MPU_Init()

    # Configures MPU6050 registers.
    def MPU_Init(self):
        self.bus.write_byte_data(self.device_address, self.SMPLRT_DIV, 7)
        self.bus.write_byte_data(self.device_address, self.PWR_MGMT_1, 1)
        self.bus.write_byte_data(self.device_address, self.CONFIG, 0)
        self.bus.write_byte_data(self.device_address, self.GYRO_CONFIG, 24)
        self.bus.write_byte_data(self.device_address, self.INT_ENABLE, 1)

    # Read 16-bit raw data from a sensor register.
    def read_raw_data(self, addr):
        high = self.bus.read_byte_data(self.device_address, addr)
        low = self.bus.read_byte_data(self.device_address, addr + 1)
        value = (high << 8) | low
        if value > 32768:
            value -= 65536
        return value

    # Return calibrated accelerometer and gyroscope values.
    def get_motion_data(self):
        acc_x = self.read_raw_data(self.ACCEL_XOUT_H)
        acc_y = self.read_raw_data(self.ACCEL_YOUT_H)
        acc_z = self.read_raw_data(self.ACCEL_ZOUT_H)
        gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
        gyro_y = self.read_raw_data(self.GYRO_YOUT_H)
        gyro_z = self.read_raw_data(self.GYRO_ZOUT_H)

        Ax = acc_x / 16384.0 + self.Ax_offset
        Ay = acc_y / 16384.0 + self.Ay_offset
        Az = acc_z / 16384.0 + self.Az_offset
        Gx = gyro_x / 131.0 + self.Gx_offset
        Gy = gyro_y / 131.0 + self.Gy_offset
        Gz = gyro_z / 131.0 + self.Gz_offset

        return Ax, Ay, Az, Gx, Gy, Gz

    # Detect left or right turn based on gyro readings.
    def detect_turn(self):
        _, _, _, Gx, Gy, Gz = self.get_motion_data()
        self.gyro_buffer.append(Gy)

        gyro_avg = sum(self.gyro_buffer) / len(self.gyro_buffer)

        if abs(gyro_avg) > self.GYRO_THRESHOLD:
            return "Right Turn" if gyro_avg > 0 else "Left Turn"
        return "Straight"