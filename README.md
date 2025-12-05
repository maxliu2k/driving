# Driving Project Checklist (12/5/25)
## RPi Version
[X] Record all the voice lines spoken by main.py so that we can also allow the flutter app to vocalize
[ ] Find some method, however janky, to mount in a way for the rpi to see the road
[ ] Test the gps_test.py file to make sure speed testing works
[X] Run the turn detection in a separate thread (or if on main, somewhere where it does it constantly)
[-] Speed Optimizations
[ ] Audio/Accelerometer Testing
## Flutter App (SafeStudent Driving)
[ ] For the flutter app tweak visuals/text as needed (also includes app store description)
    Current Description:

    SafeStudent Driving uses your device’s camera to watch the road ahead and keep you engaged behind the wheel. Whether you’re learning to drive or commuting daily, the app monitors traffic lights and common hazards, sending gentle alerts and tracking how well you respond.

    Key Features:
    - Traffic Light Detection: Automatically detects traffic light states to then notify the user.
    - Easy Setup: Simply mount your device on the dash and grant camera permission.

    Stay safer on the road and build better driving habits with real‑time feedback from SafeStudent Driving.
    Download now to transform your driving experience! 

[ ] Publish v1.1
    - Added proper TTS prompts
    - Added additional models to improve detection.
    - Bug Fixes
## Research Paper
[ ] Preliminaries
[ ] Outline Bullets
    [X] Section 1
    [X] Section 2
    [X] Section 3
    [ ] Section 4
    [ ] Section 5
    [ ] Section 6
    [ ] Section 7
[ ] Paragraphs for Sections 1-7
[ ] Section 8 Sources (0/15)
## Competition Entries
[X] Determine which competitions so that we can nail down deliverables (Congressional App Challenge, locals)
[ ] Determine any addition places to submit (e.g. Diamond Challenge, Conrad Challenge, Game Gala)
## Optionals:
[-] Train improved versions of the AI models (in-progress)
[?] Set up the systemctls to automate the python scripts on the rpi

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
[-]  *Case

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