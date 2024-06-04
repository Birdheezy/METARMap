#!/usr/bin/env python3

import urllib.request
import xml.etree.ElementTree as ET
import board
import neopixel
import time
import datetime
try:
	import astral
except ImportError:
	astral = None
try:
	import displaymetar
except ImportError:
	displaymetar = None
#-----------------------
import sys
import os
import signal
from config import *

def cleanup():
	# Perform any cleanup actions here, such as turning off the LEDs
	for i in range(LED_COUNT):
		pixels[i] = (0, 0, 0)
	pixels.show()
	print("Cleanup completed.")

def signal_handler(sig, frame):
	print("Exiting script...")
	cleanup()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)



print("Running metar.py at " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))

# Figure out sunrise/sunset times if astral is being used
if astral is not None and USE_SUNRISE_SUNSET:
	try:
		# For older clients running python 3.5 which are using Astral 1.10.1
		ast = astral.Astral()
		try:
			city = ast[LOCATION]
		except KeyError:
			print("Error: Location not recognized, please check list of supported cities and reconfigure")
		else:
			print(city)
			sun = city.sun(date = datetime.datetime.now().date(), local = True)
			BRIGHT_TIME_START = sun['sunrise'].time()
			DIM_TIME_START = sun['sunset'].time()
	except AttributeError:
		# newer Raspberry Pi versions using Python 3.6+ using Astral 2.2
		import astral.geocoder
		import astral.sun
		try:
			city = astral.geocoder.lookup(LOCATION, astral.geocoder.database())
		except KeyError:
			print("Error: Location not recognized, please check list of supported cities and reconfigure")
		else:
			print(city)
			sun = astral.sun.sun(city.observer, date = datetime.datetime.now().date(), tzinfo=city.timezone)
			BRIGHT_TIME_START = sun['sunrise'].time()
			DIM_TIME_START = sun['sunset'].time()
	print("Sunrise:" + BRIGHT_TIME_START.strftime('%H:%M') + " Sunset:" + DIM_TIME_START.strftime('%H:%M'))

# Initialize the LED strip
bright = BRIGHT_TIME_START < datetime.datetime.now().time() < DIM_TIME_START
print("Wind animation: " + str(WIND_ANIMATION))
print("Lightning animation: " + str(LIGHTNING_ANIMATION))
print("Daytime Dimming: " + str(ACTIVATE_DAYTIME_DIMMING) + (" using Sunrise/Sunset" if USE_SUNRISE_SUNSET and ACTIVATE_DAYTIME_DIMMING else ""))
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness = LED_BRIGHTNESS_DIM if (ACTIVATE_DAYTIME_DIMMING and bright == False) else LED_BRIGHTNESS, pixel_order = LED_ORDER, auto_write = False)

# Read the airports file to retrieve list of airports and use as order for LEDs

with open("airports.txt", "r") as file:
	airports = [line.strip() for line in file if line.strip()]

airports = [x.strip() for x in airports]
if len(airports) > LED_COUNT:
	print()
	print("WARNING: Too many airports in airports file, please increase LED_COUNT or reduce the number of airports")
	print("Airports: " + str(len(airports)) + " LED_COUNT: " + str(LED_COUNT))
	print()
	quit()

# Retrieve METAR from aviationweather.gov data server
# Details about parameters can be found here: https://aviationweather.gov/data/api/#/Dataserver/dataserverMetars
url = "https://aviationweather.gov/cgi-bin/data/dataserver.php?requestType=retrieve&dataSource=metars&stationString=" + ",".join([item for item in airports if item != "SKIP"]) + "&hoursBeforeNow=5&format=xml&mostRecent=true&mostRecentForEachStation=constraint"
print(url)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69'})
content = urllib.request.urlopen(req).read()

# Retrieve flying conditions from the service response and store in a dictionary for each airport
root = ET.fromstring(content)
conditionDict = {"SKIP": {"flightCategory": "", "windDir": "", "windSpeed": 0, "windGustSpeed": 0, "windGust": False, "lightning": False, "tempC": 0, "dewpointC": 0, "vis": 0, "altimHg": 0, "obs": "", "skyConditions": {}, "obsTime": datetime.datetime.now()}}
conditionDict.pop("SKIP")
stationList = []
for metar in root.iter('METAR'):
	stationId = metar.find('station_id').text
	if metar.find('flight_category') is None or metar.find('flight_category').text is None:
		print("Missing flight condition for " + stationId + ", skipping.")
		continue
	flightCategory = metar.find('flight_category').text
	windDir = ""
	windSpeed = 0
	windGustSpeed = 0
	windGust = False
	lightning = False
	tempC = 0
	dewpointC = 0
	vis = 0
	altimHg = 0.0
	precip = ""
	skyConditions = []
	if metar.find('wind_gust_kt') is not None:
		windGustSpeed = int(metar.find('wind_gust_kt').text)
	if metar.find('wind_speed_kt') is not None:
		windSpeed = int(metar.find('wind_speed_kt').text)
	if metar.find('wind_dir_degrees') is not None:
		windDir = metar.find('wind_dir_degrees').text
	if metar.find('temp_c') is not None:
		tempC = int(round(float(metar.find('temp_c').text)))
	if metar.find('dewpoint_c') is not None:
		dewpointC = int(round(float(metar.find('dewpoint_c').text)))
	if metar.find('visibility_statute_mi') is not None:
		vis_str = metar.find('visibility_statute_mi').text
		vis_str = vis_str.replace('+', '')
		vis = int(round(float(vis_str)))
	if metar.find('altim_in_hg') is not None:
		altimHg = float(round(float(metar.find('altim_in_hg').text), 2))
	if metar.find('wx_string') is not None:
		precip = metar.find('wx_string').text
		snow_detected = 'SN' in precip
	if metar.find('observation_time') is not None:
		obsTime = datetime.datetime.fromisoformat(metar.find('observation_time').text.replace("Z","+00:00"))
	for skyIter in metar.iter("sky_condition"):
		skyCond = { "cover" : skyIter.get("sky_cover"), "cloudBaseFt": int(skyIter.get("cloud_base_ft_agl", default=0)) }
		skyConditions.append(skyCond)
	if metar.find('raw_text') is not None:
		rawText = metar.find('raw_text').text
		lightning = False if ((rawText.find('LTG', 4) == -1 and rawText.find('TS', 4) == -1) or rawText.find('TSNO', 4) != -1) else True


	conditionDict[stationId] = { "flightCategory" : flightCategory, "windDir": windDir, "windSpeed" : windSpeed, "windGustSpeed": windGustSpeed, "windGust": windGust, "vis": vis, "precip" : precip, "tempC" : tempC, "dewpointC" : dewpointC, "altimHg" : altimHg, "lightning": lightning, "skyConditions" : skyConditions, "obsTime": obsTime }
	if airports is None or stationId in airports:
		stationList.append(stationId)

for airport in airports:
	if airport == "SKIP":
		continue
	if airport not in conditionDict:
		print(f"Skipping {airport} due to missing data.")
		continue
	flightCategory = conditionDict[airport]["flightCategory"]
	wind_speed = conditionDict[airport]["windSpeed"]
	wind_gust = conditionDict[airport]["windGustSpeed"]
	color = flt_cat_color(flightCategory, LED_BRIGHTNESS)
	print(f"AIRPORT: {airport}, Flight Category: {flightCategory}, Wind Speed: {wind_speed}, Wind Gust: {wind_gust}, LTG: {conditionDict[airport]['lightning']}, Precip: {conditionDict[airport]['precip']}")

disp = None
if displaymetar is not None and ACTIVATE_EXTERNAL_METAR_DISPLAY:
	print("Setting up external display")
	disp = displaymetar.startDisplay()
	displaymetar.clearScreen(disp)
	
lightning_leds = [index for index, airport in enumerate(airports) if airport != "SKIP" and airport in conditionDict and conditionDict[airport]["lightning"]]

snow_leds = [index for index, airport in enumerate(airports) if airport != "SKIP" and airport in conditionDict and 'SN' in conditionDict[airport]["precip"]]

windy_animation_leds = [index for index, airport in enumerate(airports) if airport != "SKIP" and airport in conditionDict and (conditionDict[airport]["windSpeed"] > threshold_wind_speed or conditionDict[airport]["windGustSpeed"] > threshold_wind_speed)]

def show_legend():
	if not SHOW_LEGEND:
		return
	legend_led = LED_COUNT - 1
	for i, color in enumerate(reversed(legend_colors)):
		pixels[legend_led - i] = color
	pixels.show()

legend_colors = [
	COLOR_VFR,
	COLOR_MVFR,
	COLOR_IFR,
	COLOR_LIFR,
	COLOR_SNOW,
	COLOR_LIGHTNING,
	COLOR_WINDY
]


def main_animation_loop():
	while True:
		
		# Initialize lists to track which animations to run for each LED
		windy_animation_leds = []
		snowy_animation_leds = []
		lightning_animation_leds = []

		# Iterate over all airports to determine animations
		for index, airport in enumerate(airports):
			if airport == "SKIP" or airport not in conditionDict:
				continue
			
			flightCategory = conditionDict[airport]["flightCategory"]
			wind_speed = conditionDict[airport]["windSpeed"]
			wind_gust = conditionDict[airport]["windGustSpeed"]
			precip = conditionDict[airport]["precip"]
			lightning = conditionDict[airport]["lightning"]

			# Determine which animations to run for this airport
			if WIND_ANIMATION:
				if wind_speed > threshold_wind_speed or wind_gust > threshold_wind_speed:
					windy_animation_leds.append(index)
			if SNOW_ANIMATION:
				if 'SN' in precip:
					snowy_animation_leds.append(index)
			if LIGHTNING_ANIMATION:
				if lightning:
					lightning_animation_leds.append(index)
			# Set LED color based on flight category
			color = flt_cat_color(flightCategory, LED_BRIGHTNESS)
			pixels[index] = color

		# Perform animations for all LEDs together
		if WIND_ANIMATION and windy_animation_leds:
			windy_animation(windy_animation_leds)
		if SNOW_ANIMATION and snowy_animation_leds:
			snow_animation(snowy_animation_leds)
		if LIGHTNING_ANIMATION and lightning_animation_leds:
			lightning_animation(lightning_animation_leds)
		
		
		# Show the current state of LEDs after animations
		pixels.show()
		
		# Add a delay between animation loops if needed
		time.sleep(animation_pause)




def windy_animation(leds):
	# Perform windy animation for the specified LEDs
	if WIND_ANIMATION:
		#for _ in range(2): #to use this, indent evertying below by 1 tab
		for step in range(num_steps):
			brightness = LED_BRIGHTNESS - (LED_BRIGHTNESS - dim_brightness) * (step / num_steps)
			for led in leds:
				airport = airports[led]
				flightCategory = conditionDict.get(airport, {}).get("flightCategory", "")
				color = flt_cat_color(flightCategory, brightness)
				pixels[led] = color
			pixels.show()
			time.sleep(wind_fade_time / num_steps)
		time.sleep(windy_animation_dim_pause)
		# Gradual fade back to original brightness
		for step in range(num_steps):
			brightness = dim_brightness + (LED_BRIGHTNESS - dim_brightness) * (step / num_steps)
			for led in leds:
				airport = airports[led]
				flightCategory = conditionDict.get(airport, {}).get("flightCategory", "")
				color = flt_cat_color(flightCategory, brightness)
				pixels[led] = color
			pixels.show()
			time.sleep(wind_fade_time / num_steps)
		pass


def snow_animation(leds):
	# Perform snowy animation for the specified LEDs
	if SNOW_ANIMATION:
		for step in range(num_steps):
			brightness = LED_BRIGHTNESS - (LED_BRIGHTNESS - dim_brightness) * (step / num_steps)
			for led in leds:
				airport = airports[led]
				color = flt_cat_color("SNOW", brightness)  # Always use snow color
				pixels[led] = color
			pixels.show()
			time.sleep(snow_fade_time / num_steps)

		# Gradual fade back to original flight category color
		for step in range(num_steps):
			brightness = dim_brightness + (LED_BRIGHTNESS - dim_brightness) * (step / num_steps)
			for led in leds:
				airport = airports[led]
				flightCategory = conditionDict.get(airport, {}).get("flightCategory", "")
				color = flt_cat_color(flightCategory, brightness)
				pixels[led] = color
			pixels.show()
			time.sleep(snow_fade_time / num_steps)
		pass

def lightning_animation(leds):
	# Perform lightning animation for the specified LEDs
	if LIGHTNING_ANIMATION:
		for _ in range(2):	# Flash twice white for LEDs reporting lightning
			for led in leds:
				pixels[led] = [int(color * LED_BRIGHTNESS) for color in COLOR_LIGHTNING]

			pixels.show()
			time.sleep(lightning_flash_speed)  # Adjust the duration of the flash

			# Return to the original colors for LEDs reporting lightning
			for led in leds:
				airport = airports[led]
				flightCategory = conditionDict.get(airport, {}).get("flightCategory", "")
				color = flt_cat_color(flightCategory, LED_BRIGHTNESS)
				pixels[led] = color

			pixels.show()
			time.sleep(lightning_flash_speed)  # Adjust the duration between flashes
		pass
for index, airport in enumerate(airports):
	if airport == "SKIP" or airport not in conditionDict:
		continue
	flightCategory = conditionDict[airport]["flightCategory"]
	color = flt_cat_color(flightCategory, LED_BRIGHTNESS) # Full brightness
	pixels[index] = color
pixels.show()
show_legend()
time.sleep(animation_pause)

# Start the main animation loop
main_animation_loop()
