from datetime import datetime
from dateutil.tz import *
from modules.conf import read_conf, write_conf
from modules.alerte import Alerteur
import smbus
import time

class Batterie:
    """classe de pilotage de la batterie du poulailler"""
    def __init__(self):
        self.module_name = "batterie"
        self.max = 3.3
        self.CONF_FILE = self.module_name
        self.read_config()
        self.bus = smbus.SMBus(1)

    def read_level(self):
        """lit le niveau de batterie"""
        addresse = 0x48
        self.bus.write_byte(addresse,self.channel)
        value = self.bus.read_byte(addresse)
        time.sleep(1)
        volts = self.convert_volts(value,2)
        self.write_level(volts)
        alerteur = Alerteur()
        if volts < self.seuil_min:
            alerteur.add_alert(self.module_name, "Batterie faible.")
        else:
            alerteur.remove_alert(self.module_name)
        return volts

    def convert_volts(self,data,places):
        """convertit une valeur en volts"""
        volts = (data * self.max) / float(255)
        volts = round(volts,places)
        return volts

    def read_config(self):
        """lit le fichier de configuration"""
        cfg = read_conf(self.CONF_FILE)
        self.channel = cfg['channel']
        self.seuil_min = cfg['seuil_min']
        self.last_level = cfg['last_level']
        self.last_level_date = cfg['last_level_date']
    
    def write_level(self,level):
        """ecrit la date courante dans le fichier de configuration pour le niveau donne"""
        self.last_level = level
        self.last_level_date = datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M:%S")
        self.write_config()
    
    def write_config(self):
        """ecrit la configuration dans le fichier de configuration"""
        cfg = {
            'channel':self.channel,
            'seuil_min':self.seuil_min,
            'last_level':self.last_level,
            'last_level_date':self.last_level_date
        }
        write_conf(self.CONF_FILE,cfg)
