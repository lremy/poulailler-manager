from datetime import datetime
from dateutil.tz import *
from modules.conf import read_conf, write_conf
import smbus
import time

class Luminosite:
    """classe de pilotage de la luminosite du poulailler"""
    def __init__(self):
        self.module_name = "luminosite"
        self.CONF_FILE = self.module_name
        self.read_config()
        self.bus = smbus.SMBus(1)

    def read_level(self):
        """lit le niveau de luminosité"""
        addresse = 0x48
        self.bus.write_byte(addresse,self.channel)
        luminosite = self.bus.read_byte(addresse)/255
        time.sleep(1)
        self.write_level(luminosite)
        return luminosite

    def read_config(self):
        """lit le fichier de configuration"""
        cfg = read_conf(self.CONF_FILE)
        self.channel = cfg['channel']
        self.last_level = cfg['last_level']
        self.seuil_ouverture = cfg['seuil_ouverture']
        self.seuil_fermeture = cfg['seuil_fermeture']
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
            'seuil_ouverture':self.seuil_ouverture,
            'seuil_fermeture':self.seuil_fermeture,
            'last_level':self.last_level,
            'last_level_date':self.last_level_date
        }
        write_conf(self.CONF_FILE,cfg)
