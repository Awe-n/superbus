#!/usr/bin/env python3
"""
Multi-Screen Bus Display with Button Navigation
- Bus Departures Vincennes (KEY1) - Default on startup
- Bus Departures Casa (KEY2)
- Welcome Screen with Weather Icons (KEY3)
- Blank Screen (KEY4)

Modular version with separate screen modules and minute-synchronized updates
"""

import sys
import os
import time
import json
import logging
import datetime
import argparse

# Add e-Paper library path
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'e-Paper/RaspberryPi_JetsonNano/python/pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'e-Paper/RaspberryPi_JetsonNano/python/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in7_V2

# Import custom modules
from navigation import Navigation, MODE_WELCOME, MODE_BUS, MODE_BUS_OPPOSITE, MODE_BLANK
from welcome_screen import get_weather, parse_weather, create_welcome_screen
from bus_screen import fetch_and_parse_departures, create_bus_screen, api_stats
from display_utils import load_fonts, create_blank_screen

logging.basicConfig(level=logging.INFO)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Parse command line arguments
parser = argparse.ArgumentParser(description='Bus Display')
parser.add_argument('--fast', action='store_true', help='Fast mode: 30s updates instead of 60s')
args = parser.parse_args()

# Refresh mode settings
if args.fast:
    UPDATE_INTERVAL = 30       # Update every 30 seconds
    FULL_REFRESH_INTERVAL = 10  # Full refresh every 5 minutes
else:
    UPDATE_INTERVAL = 60       # Update every 60 seconds
    FULL_REFRESH_INTERVAL = 15  # Full refresh every 15 minutes

WEATHER_UPDATE_INTERVAL = 1800  # Update weather every 30 minutes

# Remote control files (in /tmp so they work with overlay filesystem)
CONTROL_FILE = "/tmp/bus_control"
STATUS_FILE = "/tmp/bus_status.json"

# =============================================================================
# GLOBAL STATE
# =============================================================================

last_bus_data = []
last_bus_opposite_data = []
is_test_data = False
is_test_data_opposite = False
weather_data = None

# =============================================================================
# REMOTE CONTROL
# =============================================================================

def check_remote_control(nav):
    """Check for remote control commands via /tmp/bus_control"""
    try:
        if os.path.exists(CONTROL_FILE):
            with open(CONTROL_FILE, 'r') as f:
                command = f.read().strip()
            os.remove(CONTROL_FILE)  # Clear after reading

            if command in (MODE_WELCOME, MODE_BUS, MODE_BUS_OPPOSITE, MODE_BLANK):
                logging.info(f"📡 Remote command: {command}")
                nav.current_mode = command
                return True
    except Exception as e:
        logging.debug(f"Remote control check error: {e}")
    return False

def write_status(mode, departures=None, weather=None, is_test=False):
    """Write detailed JSON status to /tmp/bus_status.json"""
    try:
        status = {
            'mode': mode,
            'updated': time.strftime('%H:%M:%S'),
            'is_test': is_test,
            'api_stats': {
                'date': api_stats.date,
                'success': api_stats.success,
                'failed': api_stats.failed,
                'last_error': api_stats.last_error
            }
        }

        if mode in (MODE_BUS, MODE_BUS_OPPOSITE) and departures:
            status['departures'] = [d['time'] for d in departures[:2]]

        if mode == MODE_WELCOME:
            status['greeting'] = "Hola Viejo loco!"
            status['time'] = time.strftime('%H:%M')
            status['date'] = time.strftime('%a %d %b')
            if weather:
                status['weather'] = {
                    'morning': f"{weather.get('morning_temp', '?')}C {weather.get('morning_precip', '?')}%",
                    'afternoon': f"{weather.get('afternoon_temp', '?')}C {weather.get('afternoon_precip', '?')}%",
                    'evening': f"{weather.get('evening_temp', '?')}C {weather.get('evening_precip', '?')}%"
                }

        with open(STATUS_FILE, 'w') as f:
            json.dump(status, f)
    except Exception as e:
        logging.debug(f"Status write error: {e}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main loop orchestrating all modules"""
    global last_bus_data, last_bus_opposite_data, is_test_data, is_test_data_opposite, weather_data
    
    logging.info("=" * 60)
    logging.info("🚌 MULTI-SCREEN DISPLAY - Starting...")
    logging.info("=" * 60)
    
    # Initialize display and modules
    epd = epd2in7_V2.EPD()
    fonts = load_fonts(picdir)
    nav = Navigation()
    
    try:
        # Boot sequence
        logging.info("📺 Initializing display...")
        epd.init()
        epd.Clear()
        
        # Give network a moment to stabilize after boot
        logging.info("⏳ Waiting for network stability...")
        time.sleep(3)
        
        logging.info("🌤️ Fetching weather...")
        weather_raw = get_weather()
        weather_data = parse_weather(weather_raw)

        # Fetch initial bus data and show bus screen (KEY1 default)
        logging.info("🚌 Fetching bus departures...")
        last_bus_data, is_test_data = fetch_and_parse_departures(direction_filter="Vincennes")
        bus_image = create_bus_screen(epd, last_bus_data, fonts, is_test_data, direction_name="VINCENNES RER")
        epd.display(epd.getbuffer(bus_image))
        logging.info("✓ Bus screen displayed!")
        
        time.sleep(3)
        
        # Switch to fast refresh mode
        epd.init_Fast()
        logging.info("✓ Fast refresh mode enabled")
        
        # Main loop variables
        refresh_count = 0
        last_weather_update = time.time()
        
        # Calculate seconds until next update boundary for initial sync
        now = datetime.datetime.now()
        if UPDATE_INTERVAL == 30:
            # Sync to :00 or :30 second boundaries
            if now.second < 30:
                seconds_until_next = 30 - now.second
            else:
                seconds_until_next = 60 - now.second
            logging.info(f"⏰ FAST MODE: Syncing to clock, waiting {seconds_until_next} seconds")
        else:
            # Sync to minute boundary
            seconds_until_next = 60 - now.second
            logging.info(f"⏰ Syncing to clock: waiting {seconds_until_next} seconds until next minute")
        next_update_time = time.time() + seconds_until_next
        
        logging.info("\n🎮 Controls: KEY1=Bus (Vincennes) | KEY2=Bus (Casa) | KEY3=Welcome | KEY4=Blank\n")
        
        while True:
            current_time = time.time()
            button_pressed = nav.check_buttons()
            remote_pressed = check_remote_control(nav)
            current_mode = nav.get_mode()

            # Update weather periodically
            if current_time - last_weather_update >= WEATHER_UPDATE_INTERVAL:
                logging.info("🌤️ Updating weather...")
                weather_raw = get_weather()
                weather_data = parse_weather(weather_raw)
                last_weather_update = current_time
            
            # Update display at scheduled time, button press, or remote command
            if current_time >= next_update_time or button_pressed or remote_pressed:
                # Schedule next update
                now = datetime.datetime.now()
                if UPDATE_INTERVAL == 30:
                    # Next :00 or :30 boundary
                    if now.second < 30:
                        next_update_time = current_time + (30 - now.second)
                    else:
                        next_update_time = current_time + (60 - now.second)
                else:
                    # Next minute boundary
                    next_update_time = current_time + (60 - now.second)
                
                # Log the current time for debugging
                now = datetime.datetime.now()
                logging.info(f"🔄 Updating display at {now.strftime('%H:%M:%S')}")
                
                # Fetch fresh bus data on every update
                if current_mode == MODE_BUS:
                    last_bus_data, is_test_data = fetch_and_parse_departures(direction_filter="Vincennes")
                elif current_mode == MODE_BUS_OPPOSITE:
                    last_bus_opposite_data, is_test_data_opposite = fetch_and_parse_departures(direction_filter="Casa")
                
                # Render appropriate screen
                if current_mode == MODE_WELCOME:
                    image = create_welcome_screen(epd, fonts, weather_data)
                elif current_mode == MODE_BUS:
                    image = create_bus_screen(epd, last_bus_data, fonts, is_test_data, direction_name="VINCENNES RER")
                elif current_mode == MODE_BUS_OPPOSITE:
                    image = create_bus_screen(epd, last_bus_opposite_data, fonts, is_test_data_opposite, direction_name="CASA DIWAN")
                elif current_mode == MODE_BLANK:
                    image = create_blank_screen(epd)
                
                # Display with periodic full refresh
                if refresh_count > 0 and refresh_count % FULL_REFRESH_INTERVAL == 0:
                    logging.info("🔄 Full refresh")
                    epd.init()
                    epd.display(epd.getbuffer(image))
                    epd.init_Fast()
                else:
                    epd.display_Fast(epd.getbuffer(image))
                
                refresh_count += 1

                # Write status for remote monitoring
                if current_mode == MODE_BUS:
                    write_status(current_mode, departures=last_bus_data, is_test=is_test_data)
                elif current_mode == MODE_BUS_OPPOSITE:
                    write_status(current_mode, departures=last_bus_opposite_data, is_test=is_test_data_opposite)
                elif current_mode == MODE_WELCOME:
                    write_status(current_mode, weather=weather_data)
                else:
                    write_status(current_mode)

            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logging.info("\n👋 Shutting down gracefully...")
        nav.cleanup()
        epd.init()
        epd.Clear()
        epd.sleep()
        epd2in7_V2.epdconfig.module_exit(cleanup=True)
        
    except Exception as e:
        logging.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            nav.cleanup()
            epd.init()
            epd.Clear()
            epd.sleep()
            epd2in7_V2.epdconfig.module_exit(cleanup=True)
        except:
            pass

if __name__ == '__main__':
    main()
