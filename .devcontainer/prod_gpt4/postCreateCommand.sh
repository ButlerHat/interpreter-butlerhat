#!/bin/bash

# Init VNC
/usr/local/share/desktop-init.sh
xrandr -s 1920x1080

# Start interpreter server. The port is fixed to 8000 due to cloudflare tunnel
cd /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/interpreter-butlerhat
/opt/conda/envs/robotframework/bin/python src/app_gpt4.py
