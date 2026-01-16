#!/usr/bin/env python3
"""
Button Navigation Module
Handles GPIO button inputs for screen switching
"""

import time
import logging
import RPi.GPIO as GPIO

# Button GPIO Pins
KEY1 = 5
KEY2 = 6
KEY3 = 13
KEY4 = 19

# Screen modes
MODE_WELCOME = "welcome"
MODE_BUS = "bus"
MODE_BUS_OPPOSITE = "bus_opposite"
MODE_BLANK = "blank"

class Navigation:
    """Handles button navigation and mode switching"""
    
    def __init__(self):
        self.current_mode = MODE_BUS
        self.setup_buttons()
    
    def setup_buttons(self):
        """Initialize GPIO buttons"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(KEY1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(KEY2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(KEY3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(KEY4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        logging.info("✓ Buttons initialized")
    
    def check_buttons(self):
        """Check button states and update mode"""
        mode_changed = False
        
        if GPIO.input(KEY1) == 0:
            logging.info("🚌 KEY1 - BUS (Vincennes)")
            self.current_mode = MODE_BUS
            mode_changed = True
            time.sleep(0.3)  # Debounce

        elif GPIO.input(KEY2) == 0:
            logging.info("🚌 KEY2 - BUS (Casa)")
            self.current_mode = MODE_BUS_OPPOSITE
            mode_changed = True
            time.sleep(0.3)  # Debounce

        elif GPIO.input(KEY3) == 0:
            logging.info("🏠 KEY3 - WELCOME")
            self.current_mode = MODE_WELCOME
            mode_changed = True
            time.sleep(0.3)  # Debounce
        
        elif GPIO.input(KEY4) == 0:
            logging.info("⬜ KEY4 - BLANK SCREEN")
            self.current_mode = MODE_BLANK
            mode_changed = True
            time.sleep(0.3)  # Debounce
        
        return mode_changed
    
    def get_mode(self):
        """Get current mode"""
        return self.current_mode
    
    @staticmethod
    def cleanup():
        """Cleanup GPIO"""
        GPIO.cleanup()
