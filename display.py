from luma.core.interface.serial import i2c
from luma.oled.device import ssd1309
from luma.core.render import canvas
from PIL import ImageFont
import time

class OLEDDisplay:
    def __init__(self, i2c_address=0x3C, i2c_port=1):
        self.serial = i2c(port=i2c_port, address=i2c_address)
        self.device = ssd1309(self.serial)
        self.font = ImageFont.load_default()

    def display_text(self, text):
        """Displays the given text on the OLED screen."""
        with canvas(self.device) as draw:
            draw.text((0, 0), text, font=self.font, fill="white")
    
    def clear_display(self):
        """Clears the display."""
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")
            
    def display_metar_for_duration(self, metar_list, duration=10):
        """Displays each METAR from the list for the specified duration (in seconds)."""
        for metar in metar_list:
            self.display_text(metar)
            time.sleep(duration)
            self.clear_display()

# Example usage if this script is run directly
if __name__ == "__main__":
    oled = OLEDDisplay()
    example_metars = ["METAR 1", "METAR 2", "METAR 3"]
    oled.display_metar_for_duration(example_metars)