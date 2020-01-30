from datetime import datetime
from RPi import GPIO
from dateutil.tz import *
import yaml

class Temperature:
    """classe de pilotage d'une sonde de temperature Dallas 18B20"""
    def __init__(self, id):
        """initialise la sonde de temperature"""
        self.id = id

    def read_data(self):
        """lit les données de la sonde"""
        fic = open(r"/sys/devices/w1_bus_master1/" + self.id + "/w1_slave")
        content = fic.read(100)
        fic.close()
        return content

    def read_temperature(self):
        """lit la temperature de la sonde"""
        content = self.read_data()
        lig = content.split("\n")[1]
        temp = lig.split(" ")[9]
        temp = float(temp[2:])
        temp = temp / 1000
        return temp