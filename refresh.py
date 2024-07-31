import os
import signal
import subprocess
import time

# Function to find and kill a process
def kill_process(name):
    for line in os.popen("ps ax | grep " + name + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)

# Kill metar.py and led_startup.py
kill_process('metar.py')
kill_process('led_startup.py')
print("Killed metar.py and led_startup.py")

# Wait for the processes to terminate
time.sleep(1)
print("Starting metar.py")
# Start metar.py
process = subprocess.Popen(['sudo', '/home/pi/metar/bin/python3', 'metar.py'])

# Wait for metar.py to finish
time.sleep(5)
#process.wait()
