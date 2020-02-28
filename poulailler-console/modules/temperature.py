from datetime import datetime
from RPi import GPIO
from dateutil.tz import *
from os import path
import yaml

class Temperature:
    """classe de pilotage d'une sonde de temperature Dallas 18B20"""
    def __init__(self, id):
        """initialise la sonde de temperature"""
        self.id = id
        self.path = "/sys/devices/w1_bus_master1/" + self.id + "/w1_slave"
        self.activated = self.is_activated()

    def read_data(self):
        """lit les données de la sonde"""
        if not self.activated:
            return None
        fic = open(self.path)
        content = fic.read(100)
        fic.close()
        return content

    def read_temperature(self):
        """lit la temperature de la sonde"""
        if not self.activated:
            return None
        content = self.read_data()
        lig = content.split("\n")[1]
        temp = lig.split(" ")[9]
        temp = float(temp[2:])
        temp = temp / 1000
        return temp

    def is_activated(self):
        """renvoie true si la sonde est active"""
        return path.exists(self.path)