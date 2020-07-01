from datetime import datetime
from dateutil.tz import *
from modules.conf import read_conf, write_conf
import spidev

class Batterie:
    """classe de pilotage de la batterie du poulailler"""
    def __init__(self):
        self.module_name = "batterie"
        self.max = 2.88
        self.CONF_FILE = self.module_name
        self.read_config()
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz=1000000

    def read_level(self):
        """lit le niveau de batterie"""
        value = self.read_channel(self.channel)
        volts = self.convert_volts(value,2)
        self.write_level(volts)
        return volts

    def read_channel(self,channel):
        """lit la valeur du channel indiqué en paramètre sur le MCP3008"""
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data
    
    def convert_volts(self,data,places):
        """convertit une valeur en volts"""
        volts = (data * 3.3) / float(1023)
        volts = round(volts,places)
        return volts

    def read_config(self):
        """lit le fichier de configuration"""
        cfg = read_conf(self.CONF_FILE)
        self.channel = cfg['channel']
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
            'last_level':self.last_level,
            'last_level_date':self.last_level_date
        }
        write_conf(self.CONF_FILE,cfg)
