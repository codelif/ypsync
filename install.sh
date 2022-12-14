#!/bin/sh

DIRECTORY="$(dirname $(readlink -f $0))"
LAUNCHER="#!/usr/bin/env python3\nimport sys\nsys.path.insert(1, '$DIRECTORY')\nfrom ypsync import main\nif __name__ == '__main__':\n\tsys.exit(main())"
LOCAL=~/.local/bin
mkdir -p $LOCAL
echo -e "$LAUNCHER" > $LOCAL/ypsync
chmod +x $LOCAL/ypsync
mkdir -p ~/.config/ypsync
echo "Installing requirements... (requires pip)"
pip install -r $DIRECTORY/requirements.txt
echo -e "\n\nypsync successfully installed. Please ensure ffmpeg is installed for youtube-dl to work. \n\tNext steps:\n\t1. Make sure ~/.local/bin is in PATH environment variable.\n\t2. Add playlists and API key in '~/.config/ypsync/config.ini' to start syncing.\n\t4. If you ever move the folder where this script resides then you have to re-run this script."

