from datetime import datetime
from RPi import GPIO
from dateutil.tz import *
import time
from modules.conf import read_conf, write_conf
from modules.alerte import Alerteur

class PorteDC:
    """classe de pilotage d'une porte basée sur moteur DC avec pilotage par driver L298N"""
    def __init__(self):
        self.module_name = "porte_dc"
        self.CONF_FILE = self.module_name
        self.read_config()
        self.max_delai = 10
        self.motor = MotorDC(self.pin_enable,self.pin_in_1,self.pin_in_2)
        GPIO.setup(self.pin_bas,GPIO.IN,pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.pin_haut,GPIO.IN,pull_up_down = GPIO.PUD_UP)

    def is_opened(self):
        """teste si la porte est ouverte"""
        return not GPIO.input(self.pin_haut)
    
    def is_closed(self):
        """teste si la porte est fermee"""
        return not GPIO.input(self.pin_bas)

    def open(self):
        """ouvre la porte"""
        Alerteur().remove_alert(self.module_name)
        self.motor.forward()
        max = self.max_delai*2
        i = 0
        while i < max:
            if self.is_opened():
                break
            time.sleep(0.5)
            i += 1
        self.motor.stop()
        if i == max:
            Alerteur().add_alert(self.module_name,"La porte n'est pas ouverte entierement.")
        self.write_state("open")
        
    def close(self):
        """ferme la porte"""
        Alerteur().remove_alert(self.module_name)
        self.motor.backward()
        max = self.max_delai*2
        i = 0
        while i < max:
            if self.is_closed():
                break
            time.sleep(0.5)
            i += 1
        self.motor.stop()
        if i == max:
            Alerteur().add_alert(self.module_name,"La porte n'est pas fermee entierement.")
        self.write_state("close")

    def read_config(self):
        """lit le fichier de configuration"""
        cfg = read_conf(self.CONF_FILE)
        self.open_last_date = cfg['open']['last_date']
        self.open_next_date = cfg['open']['next_date']
        self.close_last_date = cfg['close']['last_date']
        self.close_next_date = cfg['close']['next_date']
        self.pin_bas = cfg['PIN_BAS']
        self.pin_haut = cfg['PIN_HAUT']
        self.pin_enable = cfg['PIN_ENABLE']
        self.pin_in_1 = cfg['PIN_IN_1']
        self.pin_in_2 = cfg['PIN_IN_2']
    
    def write_state(self,state):
        """ecrit la date courante dans le fichier de configuration pour l'etat donne"""
        if state == "open":
            self.open_last_date = datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.close_last_date = datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M:%S")
        self.write_config()
    
    def write_config(self):
        """ecrit la configuration dans le fichier de configuration"""
        cfg = {
            'open':{
                'last_date':self.open_last_date,
                'next_date':self.open_next_date
            },
            'close':{
                'last_date':self.close_last_date,
                'next_date':self.close_next_date
            },
            'PIN_BAS':self.pin_bas,
            'PIN_HAUT':self.pin_haut,
            'PIN_ENABLE':self.pin_enable,
            'PIN_IN_1':self.pin_in_1,
            'PIN_IN_2':self.pin_in_2,
        }
        write_conf(self.CONF_FILE,cfg)

class MotorDC:
    """classe de pilotage d'un moteur DC sur driver L298N"""
    def __init__(self, pin_enable, pin_in_1, pin_in_2):
        """initialise les pins de pilotage du driver"""
        self.vitesse = 75
        self.pin_enable = pin_enable
        self.pin_in_1 = pin_in_1
        self.pin_in_2 = pin_in_2
        GPIO.setup(self.pin_enable,GPIO.OUT)
        GPIO.setup(self.pin_in_1,GPIO.OUT)
        GPIO.setup(self.pin_in_2,GPIO.OUT)
        GPIO.output(self.pin_in_1,GPIO.LOW)
        GPIO.output(self.pin_in_2,GPIO.LOW)
        self.speed = GPIO.PWM(self.pin_enable,1000)
        self.speed.start(0)

    def stop(self):
        """arrete le moteur"""
        self.speed.ChangeDutyCycle(0)
        GPIO.output(self.pin_in_1,GPIO.LOW)
        GPIO.output(self.pin_in_2,GPIO.LOW)
        
    def forward(self):
        """fait avancer le moteur"""
        self.speed.ChangeDutyCycle(self.vitesse)
        GPIO.output(self.pin_in_1,GPIO.HIGH)
        GPIO.output(self.pin_in_2,GPIO.LOW)
        
    def backward(self):
        """fait reculer le moteur"""
        self.speed.ChangeDutyCycle(self.vitesse)
        GPIO.output(self.pin_in_1,GPIO.LOW)
        GPIO.output(self.pin_in_2,GPIO.HIGH)
        
