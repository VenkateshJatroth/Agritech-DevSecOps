import random


class Sensor:
    def __init__(self, location_name):
        # This runs ONCE when you turn the sensor on
        self.location = location_name
        self.battery = 100  # Starts full
        self.id = random.randint(1000, 9999)  # Serial Number

    def read_data(self):
        # 1. Drain the battery SLOWLY (0.1% instead of 1%)
        if self.battery > 0:
            self.battery -= 0.1

            # 2. Return the data
        return {
            "id": self.id,
            "location": self.location,
            "temp": random.randint(20, 35),
            "hum": random.randint(40, 90),

            # 🔴 TRICK: We store it as 99.9, but we show "99" to the user
            # int() cuts off the decimal point so it looks clean.
            "battery": int(self.battery)
        }