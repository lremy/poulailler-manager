#!/bin/bash -e

cd /home/pi/poulailler-console

source venv/bin/activate

flask run --host=0.0.0.0
