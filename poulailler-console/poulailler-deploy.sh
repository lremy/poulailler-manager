#!/bin/bash -e

cd /home/pi/poulailler-console

chmod +x poulailler-service.sh

cp poulailler.service /etc/systemd/system
systemctl enable poulailler.service
systemctl start poulailler.service

cp poulailler_porte_auto.service /etc/systemd/system
systemctl enable poulailler_porte_auto.service
systemctl start poulailler_porte_auto.service

cp poulailler-console.log-rotate /etc/logrotate.d
