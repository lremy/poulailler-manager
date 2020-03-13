from datetime import datetime
from dateutil.tz import *
from modules.conf import read_conf, write_conf
from os import listdir, remove, system
from subprocess import run, PIPE

class Camera_usb():
    """classe de pilotage de la caméra du Raspberry Pi"""
    def __init__(self, width, height):
        """initialise la camera"""
        self.module_name = "camera_usb"
        self.activated = True
        self.capture_path = "static/img/"
        self.CONF_FILE = "camera"
        self.width = width
        self.height = height
        self.read_config()
    
    def capture(self):
        """capture une image; renvoie la dernière image capturée"""
        date = datetime.now(tzlocal()).strftime("%Y%m%d-%H%M%S")
        img = self.capture_path + "camera-{}.jpg".format(date)
        capture = run(['fswebcam','-r','{}x{}'.format(self.width, self.height),'--no-banner','{}'.format("app/" + img)], universal_newlines=True, stdout=PIPE, stderr=PIPE)
        if "Error opening file for output" in capture.stderr:
            self.activated = False
            return None
        self.activated = True
        self.last_image = img
        self.last_capture = date
        self.write_config()
        self.keep_last_images()
        return self.last_image

    def keep_last_images(self):
        """conserve uniquement les 5 dernières images"""
        images = list(f for f in listdir("app/" + self.capture_path) if f.startswith("camera-"))
        images.sort()
        if len(images) > 5:
            remove("app/" + self.capture_path + images[0])

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
