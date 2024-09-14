#!/usr/bin/env python3

from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import config
import importlib
import subprocess

app = Flask(__name__)

@app.route('/settings.css')
def settings_css():
    return send_from_directory('.', 'settings.css')

def validate_float_field(field_name, min_value, max_value, default_value):
    try:
        value = float(request.form[field_name])
        if value < min_value:
            value = min_value
            error_message = f"{field_name.replace('_', ' ').title()} was too low. Set to minimum value of {min_value}."
        elif value > max_value:
            value = max_value
            error_message = f"{field_name.replace('_', ' ').title()} was too high. Set to maximum value of {max_value}."
        else:
            error_message = None
    except ValueError:
        value = default_value
        error_message = f"Invalid input for {field_name.replace('_', ' ').title()}. Please enter a number between {min_value} and {max_value}."
    return value, error_message

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    if request.method == 'POST':
        if 'update' in request.form:

            led_brightness, error_message_led = validate_float_field('LED_BRIGHTNESS', 0.01, 1.0, config.LED_BRIGHTNESS)
            led_brightness_dim, error_message_dim = validate_float_field('LED_BRIGHTNESS_DIM', 0.01, 1.0, config.LED_BRIGHTNESS_DIM)
            dim_brightness, error_message_dim_brightness = validate_float_field('dim_brightness', 0.01, 1.0, config.dim_brightness)

            # Combine error messages if needed
            error_messages = [error_message_led, error_message_dim, error_message_dim_brightness]
            error_message = " ".join([msg for msg in error_messages if msg])
            # Combine error messages if needed
            error_messages = [error_message_led, error_message_dim, error_message_dim_brightness]
            error_message = " ".join([msg for msg in error_messages if msg])
            # Validate other settings
            led_count = request.form['LED_COUNT']
            lightning_brightness = request.form['LIGHTNING_BRIGHTNESS']
            dim_brightness = request.form['dim_brightness']
            threshold_wind_speed = request.form['threshold_wind_speed']
            windy_animation_dim_pause = request.form['windy_animation_dim_pause']
            wind_fade_time = request.form['wind_fade_time']
            animation_pause = request.form['animation_pause']
            lightning_flash_speed = request.form['lightning_flash_speed']
            snow_fade_time = request.form['snow_fade_time']
            wind_animation = request.form.get('WIND_ANIMATION') == 'on'
            lightning_animation = request.form.get('LIGHTNING_ANIMATION') == 'on'
            snow_animation = request.form.get('SNOW_ANIMATION') == 'on'
            activate_daytime_dimming = request.form.get('ACTIVATE_DAYTIME_DIMMING') == 'on'
            led_brightness_dim = request.form['LED_BRIGHTNESS_DIM']
            show_legend = request.form.get('SHOW_LEGEND') == 'on'

            bright_hour = int(request.form['BRIGHT_HOUR'])
            bright_minute = int(request.form['BRIGHT_MINUTE'])
            dim_hour = int(request.form['DIM_HOUR'])
            dim_minute = int(request.form['DIM_MINUTE'])

            # Read the existing config file
            with open('config.py', 'r') as f:
                lines = f.readlines()

            # Update the specific settings
            new_lines = []
            for line in lines:
                if line.strip().startswith('BRIGHT_TIME_START ='):
                    new_lines.append(f"BRIGHT_TIME_START = datetime.time({bright_hour}, {bright_minute})\n")
                elif line.strip().startswith('DIM_TIME_START ='):
                    new_lines.append(f"DIM_TIME_START = datetime.time({dim_hour}, {dim_minute})\n")
                elif line.strip().startswith('LED_BRIGHTNESS ='):
                    new_lines.append(f"LED_BRIGHTNESS = {led_brightness}\n")
                elif line.strip().startswith('LED_BRIGHTNESS_DIM ='):
                    new_lines.append(f"LED_BRIGHTNESS_DIM = {led_brightness_dim}\n")
                elif line.startswith('LOCATION'):
                    new_lines.append(f"LOCATION = \"{request.form['LOCATION']}\"\n")
                elif line.startswith('LED_COUNT'):
                    new_lines.append(f"LED_COUNT = {led_count}\n")
                elif line.startswith('LIGHTNING_BRIGHTNESS'):
                    new_lines.append(f"LIGHTNING_BRIGHTNESS = {lightning_brightness}\n")
                elif line.startswith('dim_brightness'):
                    new_lines.append(f"dim_brightness = {dim_brightness}\n")
                elif line.startswith('threshold_wind_speed'):
                    new_lines.append(f"threshold_wind_speed = {threshold_wind_speed}\n")
                elif line.startswith('windy_animation_dim_pause'):
                    new_lines.append(f"windy_animation_dim_pause = {windy_animation_dim_pause}\n")
                elif line.startswith('wind_fade_time'):
                    new_lines.append(f"wind_fade_time = {wind_fade_time}\n")
                elif line.startswith('animation_pause'):
                    new_lines.append(f"animation_pause = {animation_pause}\n")
                elif line.startswith('lightning_flash_speed'):
                    new_lines.append(f"lightning_flash_speed = {lightning_flash_speed}\n")
                elif line.startswith('snow_fade_time'):
                    new_lines.append(f"snow_fade_time = {snow_fade_time}\n")
                elif line.startswith('WIND_ANIMATION'):
                    new_lines.append(f"WIND_ANIMATION = {wind_animation}\n")
                elif line.startswith('LIGHTNING_ANIMATION'):
                    new_lines.append(f"LIGHTNING_ANIMATION = {lightning_animation}\n")
                elif line.startswith('SNOW_ANIMATION'):
                    new_lines.append(f"SNOW_ANIMATION = {snow_animation}\n")
                elif line.startswith('ACTIVATE_DAYTIME_DIMMING'):
                    new_lines.append(f"ACTIVATE_DAYTIME_DIMMING = {activate_daytime_dimming}\n")
                elif line.startswith('LED_BRIGHTNESS_DIM'):
                    new_lines.append(f"LED_BRIGHTNESS_DIM = {led_brightness_dim}\n")
                elif line.startswith('SHOW_LEGEND'):
                    new_lines.append(f"SHOW_LEGEND = {show_legend}\n")
                

                else:
                    new_lines.append(line)

            # Write the updated settings back to the file
            with open('config.py', 'w') as f:
                f.writelines(new_lines)

            # Reload the config module to reflect changes
            importlib.reload(config)
        elif 'refresh' in request.form:
            # Execute the full command directly
            subprocess.run(["sudo", "/home/pi/metar/bin/python3", "metar.py &"])

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Settings</title>
            <link rel="stylesheet" type="text/css" href="/settings.css">
        </head>
        <body>
            <div class="container">
                <h1>Settings</h1>
                <form method="post">
                    <div class="form-group">
                        <label for="WIND_ANIMATION" title="Turn wind animation on or off">Wind Animation:</label>
                        <input type="checkbox" id="WIND_ANIMATION" name="WIND_ANIMATION" {% if WIND_ANIMATION %}checked{% endif %}>
                    </div>
                    <div class="form-group">
                        <label for="LIGHTNING_ANIMATION" title="Turn lightning animation on or off">Lightning Animation:</label>
                        <input type="checkbox" id="LIGHTNING_ANIMATION" name="LIGHTNING_ANIMATION" {% if LIGHTNING_ANIMATION %}checked{% endif %}>
                    </div>
                    <div class="form-group">
                        <label for="SNOW_ANIMATION" title="Turn snow animation on or off">Snow Animation:</label>
                        <input type="checkbox" id="SNOW_ANIMATION" name="SNOW_ANIMATION" {% if SNOW_ANIMATION %}checked{% endif %}>
                    </div>
                    <div class="form-group">
                        <label for="ACTIVATE_DAYTIME_DIMMING" title="Turn LED dim time of day on or off">Activate Daytime Dimming:</label>
                        <input type="checkbox" id="ACTIVATE_DAYTIME_DIMMING" name="ACTIVATE_DAYTIME_DIMMING" {% if ACTIVATE_DAYTIME_DIMMING %}checked{% endif %}>
                    </div>
                    <div class="form-group">
                        <label for="snow_fade_time" title="Snow animation speed">Snow Fade Time:</label>
                        <input type="text" id="snow_fade_time" name="snow_fade_time" value="{{ snow_fade_time }}">
                    </div>
                    <div class="form-group">
                        <label for="LED_BRIGHTNESS" title="Default/daytime brightness. Value between 0 and 1">LED Brightness:</label>
                        <input type="text" id="LED_BRIGHTNESS" name="LED_BRIGHTNESS" value="{{ LED_BRIGHTNESS }}">
                    </div>
                    <div class="form-group">
                        <label for="LOCATION" title="Major city location. Visit https://astral.readthedocs.io/en/latest/index.html, scroll down to 'cities' to find the closest one to you">Location:</label>
                        <input type="text" id="LOCATION" name="LOCATION" value="{{ LOCATION }}">
                    </div>
                    <div class="form-group">
                        <label for="LED_COUNT" title="Set to the number of LEDs in your installation">LED Count:</label>
                        <input type="text" id="LED_COUNT" name="LED_COUNT" value="{{ LED_COUNT }}">
                    </div>
                    <div class="form-group">
                        <label for="LIGHTNING_BRIGHTNESS" title="Brightness when flashing white for lightning animation">Lightning Brightness:</label>
                        <input type="text" id="LIGHTNING_BRIGHTNESS" name="LIGHTNING_BRIGHTNESS" value="{{ LIGHTNING_BRIGHTNESS }}">
                    </div>
                    <div class="form-group">
                        <label for="dim_brightness" title="Brightness the LEDs will dim to when doing the windy animation">Dim Brightness:</label>
                        <input type="text" id="dim_brightness" name="dim_brightness" value="{{ dim_brightness }}">
                    </div>
                    <div class="form-group">
                        <label for="threshold_wind_speed" title="Airports with wind speed above this value will animate for wind">Threshold Wind Speed:</label>
                        <input type="text" id="threshold_wind_speed" name="threshold_wind_speed" value="{{ threshold_wind_speed }}">
                    </div>
                    <div class="form-group">
                        <label for="windy_animation_dim_pause" title="Time LED's should stay dim before going bright again">Windy Animation Dim Pause:</label>
                        <input type="text" id="windy_animation_dim_pause" name="windy_animation_dim_pause" value="{{ windy_animation_dim_pause }}">
                    </div>
                    <div class="form-group">
                        <label for="wind_fade_time" title="Speed of LED fade for wind animation">Fade Animation Speed</label>
                        <input type="text" id="wind_fade_time" name="wind_fade_time" value="{{ wind_fade_time }}">
                    </div>
                    <div class="form-group">
                        <label for="animation_pause" title="Time between animation sets">Animation Pause:</label>
                        <input type="text" id="animation_pause" name="animation_pause" value="{{ animation_pause }}">
                    </div>
                    <div class="form-group">
                        <label for="lightning_flash_speed" title="Speed of LED blinking for lightning">Lightning Flash Speed:</label>
                        <input type="text" id="lightning_flash_speed" name="lightning_flash_speed" value="{{ lightning_flash_speed }}">
                    </div>
                    
                    <div class="form-group">
                        <label for="LED_BRIGHTNESS_DIM" title="LED brightness after sunset or DIM_TIME_START">LED Brightness Dim:</label>
                        <input type="text" id="LED_BRIGHTNESS_DIM" name="LED_BRIGHTNESS_DIM" value="{{ LED_BRIGHTNESS_DIM }}">
                    </div>
                    <div class="form-group">
                        <label for="SHOW_LEGEND" title="Use LEDs to show legend of VFR, MVFR, IFR, and LIFR">Show Legend:</label>
                        <input type="checkbox" id="SHOW_LEGEND" name="SHOW_LEGEND" {% if SHOW_LEGEND %}checked{% endif %}>
                    </div>

                    <!-- Bright Time Start -->
                    <div class="form-group">
                        <label for="BRIGHT_HOUR">Bright Time Start - Hour:</label>
                        <select id="BRIGHT_HOUR" name="BRIGHT_HOUR">
                            {% for hour in range(24) %}
                                <option value="{{ hour }}" {% if hour == BRIGHT_TIME_START.hour %}selected{% endif %}>{{ hour }}</option>
                            {% endfor %}
                        </select>
                        <label for="BRIGHT_MINUTE">Minute:</label>
                        <select id="BRIGHT_MINUTE" name="BRIGHT_MINUTE">
                            {% for minute in range(0, 60, 5) %}
                                <option value="{{ minute }}" {% if minute == BRIGHT_TIME_START.minute %}selected{% endif %}>{{ minute }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- Dim Time Start -->
                    <div class="form-group">
                        <label for="DIM_HOUR">Dim Time Start - Hour:</label>
                        <select id="DIM_HOUR" name="DIM_HOUR">
                            {% for hour in range(24) %}
                                <option value="{{ hour }}" {% if hour == DIM_TIME_START.hour %}selected{% endif %}>{{ hour }}</option>
                            {% endfor %}
                        </select>
                        <label for="DIM_MINUTE">Minute:</label>
                        <select id="DIM_MINUTE" name="DIM_MINUTE">
                            {% for minute in range(0, 60, 5) %}
                                <option value="{{ minute }}" {% if minute == DIM_TIME_START.minute %}selected{% endif %}>{{ minute }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <input type="submit" name="update" value="Update">
                    <input type="submit" name="refresh" value="Refresh">
                </form>
                {% if error_message %}
                    <p class="error">{{ error_message }}</p>
                {% endif %}
            </div>
        </body>
        </html>
''', LED_BRIGHTNESS=config.LED_BRIGHTNESS, LOCATION=config.LOCATION, LED_COUNT=config.LED_COUNT, LIGHTNING_BRIGHTNESS=config.LIGHTNING_BRIGHTNESS, dim_brightness=config.dim_brightness, threshold_wind_speed=config.threshold_wind_speed, windy_animation_dim_pause=config.windy_animation_dim_pause, wind_fade_time=config.wind_fade_time, animation_pause=config.animation_pause, lightning_flash_speed=config.lightning_flash_speed, snow_fade_time=config.snow_fade_time, WIND_ANIMATION=config.WIND_ANIMATION, LIGHTNING_ANIMATION=config.LIGHTNING_ANIMATION, SNOW_ANIMATION=config.SNOW_ANIMATION, ACTIVATE_DAYTIME_DIMMING=config.ACTIVATE_DAYTIME_DIMMING, LED_BRIGHTNESS_DIM=config.LED_BRIGHTNESS_DIM, BRIGHT_TIME_START=config.BRIGHT_TIME_START, DIM_TIME_START=config.DIM_TIME_START, SHOW_LEGEND=config.SHOW_LEGEND, error_message=error_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)