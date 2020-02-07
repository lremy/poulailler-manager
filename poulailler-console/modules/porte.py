from datetime import datetime
from RPi import GPIO
from dateutil.tz import *
import time
from modules.conf import read_conf, write_conf
from modules.alerte import Alerteur

class Porte:
    """classe de pilotage de la porte de poulailler"""
    def __init__(self, stepper, pin_bas, pin_haut):
        """initialise le stepper de la porte et les pins des triggers haut/bas de la porte"""
        self.module_name = "porte"
        self.CONF_FILE = self.module_name
        self.stepper = stepper
        self.max_rotation = 2500
        self.pin_haut = pin_haut
        self.pin_bas = pin_bas
        GPIO.setup(pin_haut,GPIO.IN,pull_up_down = GPIO.PUD_UP)
        GPIO.setup(pin_bas,GPIO.IN,pull_up_down = GPIO.PUD_UP)
        self.read_config()

    def is_opened(self):
        """teste si la porte est ouverte"""
        return not GPIO.input(self.pin_haut)
    
    def is_closed(self):
        """teste si la porte est fermee"""
        return not GPIO.input(self.pin_bas)

    def open(self):
        """ouvre la porte"""
        i = self.max_rotation * 1.01
        while not (self.is_opened() or i == 0):
            self.stepper.forward_step()
            i = i - 1
        if i == 0: # la porte n'est pas arrivee jusqu'en haut
            Alert().add_alert(self.module_name,"La porte n'est pas ouverte entierement.")
        else:
            Alert().remove_alert(self.module_name)
        self.stepper.stop_motor()
        self.write_state("open")
        
    def close(self):
        """ferme la porte"""
        i = self.max_rotation * 1.01
        while not (self.is_closed() or i == 0):
            self.stepper.backward_step()
            i = i - 1
        if i == 0: # la porte n'est pas arrivee jusqu'en bas
            Alert().add_alert(self.module_name,"La porte n'est pas fermee entierement.")
        else:
            Alert().remove_alert(self.module_name)
        self.stepper.stop_motor()
        self.write_state("close")

    def read_config(self):
        """lit le fichier de configuration"""
        cfg = read_conf(self.CONF_FILE)
        self.open_last_date = cfg['open']['last_date']
        self.open_next_date = cfg['open']['next_date']
        self.close_last_date = cfg['close']['last_date']
        self.close_next_date = cfg['close']['next_date']
    
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
            }
        }
        write_conf(cfg,self.CONF_FILE)

class Stepper:
    """classe de pilotage d'un Stepper"""
    def __init__(self, pin_a1, pin_a2, pin_b1, pin_b2):
        """initialise les 4 pins de pilotage du stepper"""
        self.p_a1 = pin_a1
        self.p_a2 = pin_a2
        self.p_b1 = pin_b1
        self.p_b2 = pin_b2
        self.delay = 0.005
        GPIO.setup(self.p_a1, GPIO.OUT)
        GPIO.setup(self.p_a2, GPIO.OUT)
        GPIO.setup(self.p_b1, GPIO.OUT)
        GPIO.setup(self.p_b2, GPIO.OUT)

    def forward_step(self):
        """fait avancer le stepper"""
        self.set_stepper(1, 0, 1, 0)
        self.set_stepper(0, 1, 1, 0)
        self.set_stepper(0, 1, 0, 1)
        self.set_stepper(1, 0, 0, 1)

    def backward_step(self):
        """fait reculer le stepper"""
        self.set_stepper(1, 0, 0, 1)
        self.set_stepper(0, 1, 0, 1)
        self.set_stepper(0, 1, 1, 0)
        self.set_stepper(1, 0, 1, 0)
    
    def stop_motor(self):
        """arrete le moteur"""
        self.set_stepper(0, 0, 0, 0)

    def set_stepper(self, in1, in2, in3, in4):
        """definit les valeurs des pins pour changer la position du stepper"""
        GPIO.output(self.p_a1, in1)
        GPIO.output(self.p_a2, in2)
        GPIO.output(self.p_b1, in3)
        GPIO.output(self.p_b2, in4)
        time.sleep(self.delay)
