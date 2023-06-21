#!/bin/bash

# Init Anaconda
conda init bash 
rfbrowser init 
# Init VNC
/usr/local/share/desktop-init.sh
xrandr -s 1280x720


# Assert ~/.cloudflared directory exists
if [ ! -d ~/.cloudflared ]; then
    echo No ~/.cloudflared directory found. The tunnel will not work.
    exit 1
fi
# Assert ~/.cloudflared/cert.pem exists
if [ ! -f ~/.cloudflared/cert.pem ]; then
    echo No ~/.cloudflared/cert.pem file found. The tunnel will not work.
    exit 1
fi

# Start the tunnel
cloudflared tunnel run --config $HOME/.cloudflared/config_interpreter.yml interpreter_bridge &

# Start interpreter server. The port is fixed to 8000 due to cloudflare tunnel
cd src
/opt/conda/bin/python app.py
