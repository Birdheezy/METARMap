# led_startup.py

import board
import neopixel
import time
import subprocess

from config import *

# Initialize the NeoPixel strip
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, pixel_order=LED_ORDER, brightness=LED_BRIGHTNESS)

def cycle_colors():
	colors = [COLOR_VFR, COLOR_MVFR, COLOR_IFR, COLOR_LIFR]
	for color in colors:
		# Set all LEDs to the current color
		pixels.fill(color)
		pixels.show()
		time.sleep(.7)  # Adjust the duration for each color

def main():
	# Turn on all LEDs
	pixels.fill((255, 255, 255))  # White
	pixels.show()
	time.sleep(.7)  # Adjust the duration LEDs stay on

	# Cycle through colors
	cycle_colors()

	# Turn off all LEDs
	pixels.show()

	print("Starting metar.py script...")
	subprocess.run(["python3", "metar.py"]) 

	sys.exit()

if __name__ == "__main__":
	main()
