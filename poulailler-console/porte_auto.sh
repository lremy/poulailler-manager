#!/bin/bash -e

cd /home/pi/poulailler-console

source venv/bin/activate

python task_porte.py $1
