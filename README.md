# Driving

# Hardware Checklist

[X]  Raspberry Pi 5
[X]  Speaker
[X]  Camera
[X]  Microphone
[X]  Accelerometer
     - Direction
     - Acceleration/Speed
     - https://learn.adafruit.com/mpu6050-6-dof-accelerometer-and-gyro/python-and-circuitpython
[X]  Battery Source
[X]  GPS Sensor
[ ]  *Case


# Raspberry Pi Integration Steps

1. Get this project onto the raspberry pi

    - navigate to the directory you want the project to be

    ```bash
    git clone [project url]
    ```

    - go into the cloned project
    ```bash
    cd [directory]
    ```

2. Create the python venv

    ```bash
    python3 -m venv venv
    ```

3. Activate the venv

    ```bash
    source venv/bin/activate
    ```

4. Install the dependencies

    ```bash
    pip install -r requirements.txt
    ```

# How to Automate the Programs with Systemctl
    ```bash
    sudo nano /etc/systemd/system/[program name].service
    ```

    ```bash
    [Unit]
    Description=My Python Server
    After=network.target

    [Service]
    Type=simple
    User=pi
    WorkingDirectory=/home/pi/myproject
    ExecStart=/home/pi/myvenv/bin/python /home/pi/myproject/server.py
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    ```

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start [program name]
    sudo systemctl enable [program name]
    ```



# Past Record Drives
- Mistakes made
    - running a red light
    - traffic sign violation (e.g. over speed limit * 1.2)
    - forgetting turn signal
    - "nice to haves"
        - lane changes, seatbelt, etc.
        - Score
            - 0-100 scale
            - based on mistakes and time
            - 