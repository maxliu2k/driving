import time
import serial
import adafruit_gps
# import pynmea2
from voice import Voice

voice = Voice("piper.onnx")
voice.speak("GPS test started")

uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=30)

gps = adafruit_gps.GPS(uart, debug=False)

gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

gps.send_command(b'PMTK220,1000')

last_print = time.monotonic()

# def read_gps_speed(serial_port='/dev/serial0', baudrate=9600):
#     # 1 knot = 1.15078 mph

#     # Open serial connection to GPS
#     speed_mph = 0
#     with serial.Serial(serial_port, baudrate, timeout=1) as ser:
#         while True:
#             try:
#                 line = ser.readline().decode('ascii', errors='replace')
#                 if line.startswith('$GPRMC'):
#                     msg = pynmea2.parse(line)
#                     if msg.status == 'A':  # A = valid, V = invalid
#                         speed_knots = float(msg.spd_over_grnd)
#                         speed_mph = speed_knots * 1.15078
#             except pynmea2.ParseError:
#                 continue
#     return speed_mph

while True:

    gps.update()

    current = time.monotonic()
    voice_delay = 5 # Speak every 5 seconds

    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            print('Waiting for fix...')
            continue

        print('=' * 40)  # Print a separator line.
        print('Latitude: {0:.6f} degrees'.format(gps.latitude))
        print('Longitude: {0:.6f} degrees'.format(gps.longitude))

        # Get the speed
        if gps.speed_knots is not None:
            mph = gps.speed_knots * 1.15078
            print('Speed: {0:.2f} mph'.format(mph))
            if voice_delay <= 0:
                voice.speak(f"{mph:.2f}")
                voice_delay = 5
        else:
            print('Speed: Not available')

        voice_delay -= 1
    
    time.sleep(0.1)