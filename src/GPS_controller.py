import time
# import serial
# import adafruit_gps


# ===============================
# GPS Manager: Manages the GPS module - handles initialization, location, and speed data.
# ===============================
class GPSManager:
    # Initializes the GPS connection, configures output sentences, and sets the update rate.
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, timeout=30, update_rate=1.0):
        # Initialize UART connection
        # self.uart = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        # self.gps = adafruit_gps.GPS(self.uart, debug=False)

        # Configure GPS to output only RMC (Recommended Minimum) and GGA (Fix Data)
        self.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

        # Set update frequency in milliseconds
        self.gps.send_command(f'PMTK220,{int(1000/update_rate)}'.encode())

        self.update_rate = update_rate  # Output interval in seconds

    # Fetch new data from the GPS module.
    def update(self):
        self.gps.update()

    # Return True if GPS has a valid fix, False otherwise.
    def has_fix(self):   
        return self.gps.has_fix

    # Return (latitude, longitude) if available, else None.
    def get_location(self):       
        if not self.gps.has_fix:
            return None
        return (self.gps.latitude, self.gps.longitude)

    # Return speed in mph if available, else None.
    def get_speed_mph(self):  
        if not self.gps.has_fix:   
            print('===========================GPS Waiting for fix...')
            return None
        else:
            if self.gps.speed_knots is not None:
                return self.gps.speed_knots * 1.15078
            else:
                print('===========================Driving speed is not available')
                return None
