from datetime import datetime
from RPi import GPIO
from dateutil.tz import *
from modules.conf import read_conf, write_conf
from modules.alerte import Alerteur

class Abreuvoir:
    """classe de pilotage de l'abreuvoir du poulailler"""
    def __init__(self, pin_bas, pin_milieu, pin_haut):
        """initialise les pins des triggers bas/milieu/haut de l'abreuvoir"""
        self.CONF_FILE = 'abreuvoir'
        self.pin_bas = pin_bas
        self.pin_milieu = pin_milieu
        self.pin_haut = pin_haut
        GPIO.setup(self.pin_bas,GPIO.IN,pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.pin_milieu,GPIO.IN,pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.pin_haut,GPIO.IN,pull_up_down = GPIO.PUD_UP)
        self.read_config()
        self.init_interrupt()

    def init_interrupt(self):
        """ajoute des interruptions sur les trois pins"""
        GPIO.add_event_detect(self.pin_bas,GPIO.FALLING, callback = self.callback_interrupt, bouncetime = 500)
        GPIO.add_event_detect(self.pin_milieu,GPIO.FALLING, callback = self.callback_interrupt, bouncetime = 500)
        GPIO.add_event_detect(self.pin_haut,GPIO.FALLING, callback = self.callback_interrupt, bouncetime = 500)
    
    def callback_interrupt(self,bouton):
        """callback d'interruption"""
        if bouton == self.pin_bas:
            if self.last_level != 0:
                self.write_level(0)
                alerteur = Alerteur()
                alerteur.send_alert("Niveau d'eau faible dans l'abreuvoir.")
        elif bouton == self.pin_milieu:
            self.write_level(1)
        else:
            self.write_level(2)

    def read_config(self):
        """lit le fichier de configuration"""
        cfg = read_conf(self.CONF_FILE)
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
            'last_level':self.last_level,
            'last_level_date':self.last_level_date
        }
        write_conf(self.CONF_FILE,cfg)
