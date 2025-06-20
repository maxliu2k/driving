# Driving Project Checklist (5/16/25)
[ ] Record all the voice lines spoken by main.py so that we can also allow the flutter app to vocalize
[ ] Find some method, however janky, to mount in a way for the rpi to see the road
[ ] Test the gps_test.py file to make sure speed testing works
[ ] For the flutter app tweak visuals/text as needed (also includes app store description)
[X] Determine which competitions so that we can nail down deliverables (Congressional App Challenge, locals)
[ ] Run the turn detection in a separate thread (or if on main, somewhere where it does it constantly)
## Optionals:
[ ] Train improved versions of the AI models (in-progress)
[ ] Set up the systemctls to automate the python scripts on the rpi

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

https://doc-hosting.flycricket.io/safestudent-driving-privacy-policy/7b806e17-6135-49f2-ab7d-c87ca4a062df/privacy
https://doc-hosting.flycricket.io/safestudent-driving-terms-of-use/1c5412f5-1a90-4afa-a9e6-6dcdc683c3f3/terms

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
    sudo nano /etc/systemd/system/driving.service
    ```

    ```bash
    [Unit]
    Description=Start Driving Assistant
    After=network.target

    [Service]
    Type=simple
    User=maxliu2k
    WorkingDirectory=/home/maxliu2k/Driving/
    ExecStart=/home/maxliu2k/Driving/venv/bin/python/home/maxliu2k/Driving/main.py
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

# Notes:
- in the event your PAT expires and you have to make a new one, you can do so by running the following command:
```bash
git config --global credential.helper store
git pull
```