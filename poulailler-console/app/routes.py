from flask import render_template, flash, redirect, url_for, request
from app import app
from RPi import GPIO
from modules.porte import Porte, Stepper
from modules.abreuvoir import Abreuvoir
from modules.temperature import Temperature

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

stepper = Stepper(5,6,13,19)
porte = Porte(stepper,23,24)
abreuvoir = Abreuvoir(17,27,22)
temp_ext = Temperature("28-05167380edff")
temp_int = Temperature("28-051680729dff")

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
        if porte.is_opened():
            # la porte est ouverte
            porte.close()
        else:
            # la porte est fermee ou en etat instable
            porte.open()
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
        'temp_ext' : temp_ext.read_temperature()
    }
    return render_template('temperature.html', **template_data)
