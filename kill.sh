#!/bin/bash

# Stop the metar.py process
sudo pkill -9 -f metar.py 
echo 'Killed metar.py'

# Stop the led_startup.py process
sudo pkill -9 -f led_startup.py
echo 'Killed led_startup.py'

# Run the pixelsoff.py script
cd ~
sudo /home/pi/metar/bin/python3  pixelsoff.py

echo 'Killed metar.py and led_startup.py'
echo 'Script finished!'
