#!/bin/bash

sudo mv /home/pi/RPiStatus/RPiStatus.service /etc/systemd/system/ && sudo systemctl daemon-reload
chmod +x -R /home/pi/RPiStatus/*
