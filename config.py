import datetime
import neopixel
import board

# --------NeoPixel configuration--------
LED_ORDER = neopixel.GRB
LED_COUNT = 50				# Set to the number of LEDs in your installation
LED_PIN = board.D18  		# Pin used for data for the LEDs
LED_BRIGHTNESS = .6  		# Default/daytime brightness. Value between 0 and 1
LIGHTNING_BRIGHTNESS = 0.7	# Brightness when flashing white for lightning animation. Change in def lightning_animation(leds):

#--------LED colors--------
COLOR_VFR = [255, 0, 0]				#Green
COLOR_MVFR = [0, 0, 255]			#Blue
COLOR_IFR = [0, 255, 0]				#Red
COLOR_LIFR = [0, 125, 125]			#Magenta
COLOR_SNOW = [125, 125, 0]			#Yellow
COLOR_CLEAR = [0, 0, 0]				#Off
COLOR_LIGHTNING = [255, 255, 255]	#White
COLOR_WINDY = [10, 0, 0]			#Dim Green for windy

#--------Animation Parameters--------
dim_brightness = 0.05			# Brightness the LEDs will dim to when doing the windy animation
threshold_wind_speed = 15		# Airports with wind speed above this value will animate for wind
windy_animation_dim_pause = 1.3	# Time LED's should stay dim before going bright again
wind_fade_time = 0.5			# Speed of LED fade for wind animation
num_steps = 100					# Amount of steps for dimming animation
animation_pause = 10			# Time between animation sets
lightning_flash_speed = 0.1		# Speed of LED blinking for lightning
snow_fade_time = 0.3			# Snow animation speed

#--------Animation Settings--------
WIND_ANIMATION = True				# Turn wind animation on or off
LIGHTNING_ANIMATION = True			# Turn lightning animation on or off
SNOW_ANIMATION = True				# Turn snow animation on or off
ACTIVATE_DAYTIME_DIMMING = True		# Turn LED dim time of day on or off

#--------Location and time-based settings--------
LOCATION = "Denver"							# Major city location. Visit https://astral.readthedocs.io/en/latest/index.html, scroll down to "cities" to find the cloest one to you
LED_BRIGHTNESS_DIM = .2						# Led brightness after sunset or DIM_TIME_START
USE_SUNRISE_SUNSET = True					# Use sunrise or sunset times for LED dimming
BRIGHT_TIME_START = datetime.time(7, 0)		# Custom time to set LEDs to be bright
DIM_TIME_START = datetime.time(20, 30)		# Custom time to set LEDs to dim

#--------Legend Settings--------
SHOW_LEGEND = True				# Use LEDs to show legend of VFR, MVFR, IFR, and LIFR
#OFFSET_LEGEND_BY = 1			# How many LEDs to skip before starting the legend

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
