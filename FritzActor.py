from datetime import datetime

class FritzActor (object):
    def __init__(self, ain, name, temp, power, energy, timestamp=datetime.now().strftime("%d.%m.%Y, %H:%M:%S")):
        self.ain = ain
        self.name = name
        self.temp = temp
        self.power = power
        self.energy = energy
        self.timestamp = timestamp
