#!/bin/bash

# Init VNC
/usr/local/share/desktop-init.sh
xrandr -s 1280x720

# Start interpreter server. The port is fixed to 8000 due to cloudflare tunnel
cd src
/opt/conda/envs/robotframework/bin/python app.py
