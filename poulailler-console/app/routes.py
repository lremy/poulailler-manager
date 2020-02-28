from flask import render_template, flash, redirect, url_for, request
from app import app
from RPi import GPIO
from modules.porte import Porte, Stepper
from modules.abreuvoir import Abreuvoir
from modules.temperature import Temperature
from modules.camera import Camera
from modules.conf import read_conf
from modules.alerte import Alerteur

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

CFG = read_conf("global")

stepper = Stepper(CFG['PORTE_STEPPER_1'],CFG['PORTE_STEPPER_2'],CFG['PORTE_STEPPER_3'],CFG['PORTE_STEPPER_4'])
porte = Porte(stepper,CFG['PORTE_PIN_BAS'],CFG['PORTE_PIN_HAUT'])
abreuvoir = Abreuvoir(CFG['ABREUVOIR_PIN_VIDE'],CFG['ABREUVOIR_PIN_MEDIUM'],CFG['ABREUVOIR_PIN_PLEIN'])
temp_ext = Temperature(CFG['TEMP_ID_EXT'])
temp_int = Temperature(CFG['TEMP_ID_INT'])
camera = Camera(CFG['CAMERA_WIDTH'],CFG['CAMERA_HEIGHT'])

# page par defaut, redirection vers la page principale
@app.route('/')
def index():
    return redirect(url_for('board'))

# page principale
@app.route('/board')
def board():
    return render_template('board.html')

# module porte
@app.route('/porte', methods= ['POST','GET'])
def url_porte():
    porte.read_config()
    img_etat = "ouverte"
    img_etat_title = "Porte ouverte"
    img_action = "fermer"
    img_action_title = "Fermer la porte"
    running = False
    if request.method == 'POST':
        # demande de modification de l'etat de la porte
        if porte.is_closed():
            # la porte est fermee
            porte.open()
        else:
            # la porte est ouverte ou en etat instable
            porte.close()
    if porte.is_closed():
        # la porte est fermee
        img_etat = "fermee"
        img_etat_title = "Porte fermee"
        img_action = "ouvrir"
        img_action_title = "Ouvrir la porte"
    elif not porte.is_opened():
        # la porte n'est pas ouverte = porte en deplacement
        img_etat = "en-cours"
        img_etat_title = "En cours de deplacement..."
        running = True
    template_data = {
        'running' : running,
        'img_etat' : url_for("static", filename="img/porte-" + img_etat + ".png"),
        'img_etat_title' : img_etat_title,
        'img_action' : url_for("static", filename="img/porte-" + img_action + ".png"),
        'img_action_title' : img_action_title,
        'url_porte' : url_for("url_porte"),
        'open_last_date' : porte.open_last_date,
        'open_next_date' : porte.open_next_date,
        'close_last_date' : porte.close_last_date,
        'close_next_date' : porte.close_next_date,
    }
    return render_template('porte.html', **template_data)

# module abreuvoir
@app.route('/abreuvoir', methods= ['GET'])
def url_abreuvoir():
    abreuvoir.read_config()
    levels = [20,80,140]
    level_labels = ['bas','milieu','haut']
    template_data = {
        'last_level' : levels[abreuvoir.last_level],
        'last_level_date' : abreuvoir.last_level_date,
        'last_level_label' : level_labels[abreuvoir.last_level]
    }
    return render_template('abreuvoir.html', **template_data)

# module temperature
@app.route('/temperature', methods= ['GET'])
def url_temperature():
    template_data = {
        'temp_int' : temp_int.read_temperature(),
        'temp_int_activated' : temp_int.activated,
        'temp_ext' : temp_ext.read_temperature(),
        'temp_ext_activated' : temp_ext.activated
    }
    return render_template('temperature.html', **template_data)

# module camera
@app.route('/camera', methods= ['GET'])
def url_camera():
    capture_url = camera.capture()
    template_data = {
        'last_capture' : camera.last_capture,
        'capture_url' : capture_url
    }
    return render_template('camera.html', **template_data)

# module alertes
@app.route('/alertes', methods= ['GET'])
def url_alertes():
    template_data = {
        'alertes' : Alerteur().alertes
    }
    return render_template('alertes.html', **template_data)

