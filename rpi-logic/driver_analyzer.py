"""
Load the model, which classifies if they are wearing a seatbelt or not.
-*additional model that listens for the turn signal.

Analyze the driver

1. Identify if they are wearing a seatbelt.
2. If not, text-to-speech to remind them to wear a seatbelt.

If the accelerometer detects a sharp turn, then the driver is likely to be turning.
If no turn signal is detected, then text-to-speech to remind them to use the turn signal next time.
"""

class DriverAnalyzer:
    def __init__(self, accelerometer):
        self.accelerometer = accelerometer
        self.seatbelt_model = "Insert model here"

    def analyze(self):
        seatbelt_status = self.seatbelt_model.predict()
        if not seatbelt_status:
            self.remind_seatbelt()

        if self.accelerometer.detect_turn():
            pass