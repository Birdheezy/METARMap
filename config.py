import datetime
import neopixel
import board

# --------NeoPixel configuration--------
LED_ORDER = neopixel.GRB
LED_COUNT = 30				# Set to the number of LEDs in your installation
LED_PIN = board.D18	  		# Pin used for data for the LEDs
LED_BRIGHTNESS = 0.7  		# Default/daytime brightness
LIGHTNING_BRIGHTNESS = 0.7	# Brightness when flashing white

#--------LED colors--------
COLOR_VFR = [255, 0, 0]
COLOR_MVFR = [0, 0, 255]
COLOR_IFR = [0, 255, 0]
COLOR_LIFR = [0, 125, 125]
COLOR_SNOW = [125, 125, 0]
COLOR_CLEAR = [0, 0, 0]
COLOR_LIGHTNING = [255, 255, 255]

#--------Animation Parameters--------
dim_brightness = 0.1			# Brightness of LEDs after sunset if ACTIVATE_DAYTIME_DIMMING is True
threshold_wind_speed = 15		# Airports with wind speed above this value will animate for wind
windy_animation_dim_pause = 1.5	# Time LED's should stay dim before going bright again
wind_fade_time = 0.5			# Speed of LED fade for wind animation
num_steps = 100					# Amount of steps for dimming animation
animation_pause = 15			# Time between animation sets
lightning_flash_speed = 0.1		# Speed of LED blinking for lightning
snow_fade_time = 0.3			# Snow animation speed

#--------Animation Settings--------
WIND_ANIMATION = True				# Turn wind animation on or off
LIGHTNING_ANIMATION = True			# Turn lightning animation on or off
SNOW_ANIMATION = True				# Turn snow animation on or off
ACTIVATE_DAYTIME_DIMMING = True		# Turn LED dim time of day on or off

#--------Location and time-based settings--------
LOCATION = "Denver"							# Major city location. Visit https://astral.readthedocs.io/en/latest/index.html, scroll down to "cities" to find the cloest one to you
LED_BRIGHTNESS_DIM	= .2					# Led brightness after sunset or DIM_TIME_START
USE_SUNRISE_SUNSET = True					# Use sunrise or sunset times for LED dimming
BRIGHT_TIME_START = datetime.time(7, 0)		# Custom time to set LEDs to bright
DIM_TIME_START = datetime.time(19, 0)		# Custom time to set LEDs to dim

#--------Legend Settings--------
SHOW_LEGEND = False		# Use LEDs to show legend of VFR, MVFR, IFR, and LIFR
OFFSET_LEGEND_BY = 0	# How many LEDs to skip before starting the legend

def flt_cat_color(flight_category, brightness):
	if flight_category == "VFR":
		return (
			int(COLOR_VFR[0] * brightness),
			int(COLOR_VFR[1] * brightness),
			int(COLOR_VFR[2] * brightness)
		)
	elif flight_category == "MVFR":
		return (
			int(COLOR_MVFR[0] * brightness),
			int(COLOR_MVFR[1] * brightness),
			int(COLOR_MVFR[2] * brightness)
		)
	elif flight_category == "IFR":
		return (
			int(COLOR_IFR[0] * brightness),
			int(COLOR_IFR[1] * brightness),
			int(COLOR_IFR[2] * brightness)
		)
	elif flight_category == "LIFR":
		return (
			int(COLOR_LIFR[0] * brightness),
			int(COLOR_LIFR[1] * brightness),
			int(COLOR_LIFR[2] * brightness)
		)
	elif flight_category == "SNOW":
		return (
			int(COLOR_SNOW[0] * brightness),
			int(COLOR_SNOW[1] * brightness),
			int(COLOR_SNOW[2] * brightness)
		)
	else:
		return (
			int(COLOR_CLEAR[0] * brightness),
			int(COLOR_CLEAR[1] * brightness),
			int(COLOR_CLEAR[2] * brightness)
		)
