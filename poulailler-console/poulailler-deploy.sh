#!/bin/bash -e

cd /home/pi/poulailler-console

chmod +x poulailler-service.sh

cp poulailler.service /etc/systemd/system

systemctl enable poulailler.service
systemctl start poulailler.service
