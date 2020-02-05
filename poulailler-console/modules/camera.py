import picamera
from datetime import datetime
from dateutil.tz import *
from modules.conf import read_conf, write_conf

class Camera():
    """classe de pilotage de la caméra du Raspberry Pi"""
    def __init__(self, width, height):
        """initialise la camera"""
        self.camera = picamera.PiCamera()
        self.capture_path = "static/img/camera.jpg"
        self.CONF_FILE = "camera"
        self.width = width
        self.height = height
    
    def capture(self):
        """capture une image"""
        self.camera.resolution = (self.width, self.height)
        self.camera.capture("app/" + self.capture_path)
        self.last_capture = datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M:%S")
        return self.capture_path

    def read_config(self):
        """lit le fichier de configuration"""
        cfg = read_conf(self.CONF_FILE)
        self.last_capture = cfg['last_capture']
    
    def write_config(self):
        """ecrit la configuration dans le fichier de configuration"""
        cfg = {
            'last_capture':self.last_capture,
        }
        write_conf(self.CONF_FILE,cfg)
