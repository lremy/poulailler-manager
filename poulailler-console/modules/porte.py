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
        self.max_rotation = 2600
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
        for i in range(self.max_rotation):
            self.stepper.moveOnePeriod(1)
            if self.is_opened():
                break
        if i < self.max_rotation: # la porte n'est pas arrivee jusqu'en haut
            Alerteur().add_alert(self.module_name,"La porte n'est pas ouverte entierement.")
        else:
            Alerteur().remove_alert(self.module_name)
        #self.stepper.stop_motor()
        self.write_state("open")
        
    def close(self):
        """ferme la porte"""
        for i in range(self.max_rotation):
            self.stepper.moveOnePeriod(0)
            if self.is_closed():
                break
        if i < self.max_rotation: # la porte n'est pas arrivee jusqu'en bas
            Alerteur().add_alert(self.module_name,"La porte n'est pas fermee entierement.")
        else:
            Alerteur().remove_alert(self.module_name)
        #self.stepper.stop_motor()
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
        write_conf(self.CONF_FILE,cfg)

class Stepper:
    """classe de pilotage d'un Stepper"""
    def __init__(self, pin_a1, pin_a2, pin_b1, pin_b2):
        """initialise les 4 pins de pilotage du stepper"""
        self.delay = 0.003
        self.motorPins = (pin_a1, pin_a2, pin_b1, pin_b2)    #define pins connected to four phase ABCD of stepper motor
        for i in range(4):
            GPIO.setup(self.motorPins[i], GPIO.OUT)
        self.CCWStep = (0x01,0x02,0x04,0x08) #define power supply order for coil for rotating anticlockwise
        self.CWStep = (0x08,0x04,0x02,0x01)  #define power supply order for coil for rotating clockwise

    def stop_motor(self):
        """arrete le moteur"""
        for i in range(4):
            GPIO.output(self.motorPins[i],GPIO.LOW)

    #as for four phase stepping motor, four steps is a cycle. the function is used to drive the stepping motor clockwise or anticlockwise to take four steps
    def moveOnePeriod(self,direction):
        print(self.delay)
        for j in range(0,4,1):      #four steps of the cycle
            for i in range(0,4,1):  #cycle through 4 pins
                if (direction == 1):#power supply order clockwise
                    GPIO.output(self.motorPins[i],((self.CCWStep[j] == 1<<i) and GPIO.HIGH or GPIO.LOW))
                else :              #power supply order anticlockwise
                    GPIO.output(self.motorPins[i],((self.CWStep[j] == 1<<i) and GPIO.HIGH or GPIO.LOW))
            time.sleep(self.delay)
