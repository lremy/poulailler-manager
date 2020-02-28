import picamera
from datetime import datetime
from dateutil.tz import *
from modules.conf import read_conf, write_conf
from os import listdir, remove
from subprocess import run, PIPE

class Camera():
    """classe de pilotage de la caméra du Raspberry Pi"""
    def __init__(self, width, height):
        """initialise la camera"""
        self.activated = self.is_activated()
        if self.activated:
            self.camera = picamera.PiCamera()
        self.capture_path = "static/img/"
        self.CONF_FILE = "camera"
        self.width = width
        self.height = height
        self.read_config()
    
    def capture(self):
        """capture une image; renvoie la dernière image capturée"""
        if not self.activated:
            return None
        self.camera.resolution = (self.width, self.height)
        date = datetime.now(tzlocal())
        self.last_capture = date.strftime("%Y-%m-%d %H:%M:%S")
        self.last_image = self.capture_path + "camera-{}.jpg".format(date.strftime("%Y%m%d-%H%M%S"))
        self.camera.capture("app/" + self.last_image)
        self.write_config()
        # supprime la plus ancienne image s'il y a plus de 5 images
        images = list(f for f in listdir("app/" + self.capture_path) if f.startswith("camera-"))
        images.sort()
        if len(images) > 5:
            remove("app/" + self.capture_path + images[0])
        return self.last_image

    def read_config(self):
        """lit le fichier de configuration"""
        cfg = read_conf(self.CONF_FILE)
        self.last_capture = cfg['last_capture']
    
    def write_config(self):
        """ecrit la configuration dans le fichier de configuration"""
        cfg = {
            'last_capture':self.last_capture,
            'last_image':self.last_image,
        }
        write_conf(self.CONF_FILE,cfg)

    def is_activated(self):
        """renvoie True si la caméra est active"""
        cp = run(["vcgencmd","get_camera"], universal_newlines=True, stdout=PIPE, stderr=PIPE)
        return cp.stdout == "supported=1 detected=1\n"