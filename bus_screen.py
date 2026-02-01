#!/usr/bin/env python3
"""
Bus Departure Screen Module
Displays real-time bus departure information
"""

import time
import random
import logging
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# API Configuration
API_KEY = "CK5M767DwRvWjb5MP1KsNSdPrS6RbbnP"
# Stop IDs for each direction
STOP_ID_VINCENNES = "STIF:StopPoint:Q:24739:"  # Progrès - Armand Carrel (towards Vincennes)
STOP_ID_CASA = "STIF:StopPoint:Q:24740:"      # Valmy - Armand Carrel (towards Casa/Austerlitz)
LINE_ID = "STIF:Line::C01229:"
API_ENDPOINT = "https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring"

# =============================================================================
# API STATS TRACKING
# =============================================================================

class APIStats:
    """Track API request statistics"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.success = 0
        self.failed = 0
        self.last_error = None

    def check_date(self):
        """Reset counters if it's a new day"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.date:
            logging.info(f"📊 New day - resetting API stats (yesterday: {self.success} OK, {self.failed} failed)")
            self.reset()

    def record_success(self):
        self.check_date()
        self.success += 1

    def record_failure(self, error):
        self.check_date()
        self.failed += 1
        self.last_error = str(error)

    def get_summary(self):
        return f"API today: {self.success} OK, {self.failed} failed"

# Global stats instance
api_stats = APIStats()

# =============================================================================
# BUS DATA FETCHING
# =============================================================================

def generate_test_data():
    """Generate test bus data when API is unavailable"""
    times = sorted([random.randint(3, 45) for _ in range(2)])
    departures = []
    for minutes in times:
        time_str = "1 min" if minutes == 1 else f"{minutes} min"
        departures.append({
            'destination': 'Vincennes <RER> - Republique',
            'time': time_str,
            'minutes': minutes
        })
    return departures

def get_bus_departures(stop_id=None):
    """Fetch bus departures from IDFM API

    Args:
        stop_id: Stop ID to query (defaults to Vincennes stop)
    """
    headers = {'apikey': API_KEY}
    if stop_id is None:
        stop_id = STOP_ID_VINCENNES
    params = {'MonitoringRef': stop_id, 'LineRef': LINE_ID}

    try:
        response = requests.get(API_ENDPOINT, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            api_stats.record_success()
            logging.info(f"✅ API OK (status 200) | {api_stats.get_summary()}")
            return response.json()
        else:
            api_stats.record_failure(f"HTTP {response.status_code}")
            logging.error(f"❌ API failed: HTTP {response.status_code} | {api_stats.get_summary()}")
            return None
    except requests.exceptions.Timeout:
        api_stats.record_failure("Timeout")
        logging.error(f"❌ API timeout (>10s) | {api_stats.get_summary()}")
        return None
    except requests.exceptions.ConnectionError as e:
        api_stats.record_failure("Connection error")
        logging.error(f"❌ API connection error: {e} | {api_stats.get_summary()}")
        return None
    except Exception as e:
        api_stats.record_failure(str(e))
        logging.error(f"❌ API error: {e} | {api_stats.get_summary()}")
        return None

def parse_departures(data, filter_destination=None, filter_direction=None):
    """Parse bus departure data from API response
    
    Args:
        data: API response JSON
        filter_destination: Optional destination name to filter by (case-insensitive partial match)
        filter_direction: Optional direction to filter by - "Vincennes" for Aller, "Casa" for Retour
    """
    departures = []
    
    try:
        siri = data.get('Siri', {})
        service_delivery = siri.get('ServiceDelivery', {})
        stop_monitoring = service_delivery.get('StopMonitoringDelivery', [])
        
        if not stop_monitoring:
            return []
        
        monitored_visits = stop_monitoring[0].get('MonitoredStopVisit', [])
        
        for visit in monitored_visits[:10]:  # Check more visits to find both directions
            try:
                journey = visit.get('MonitoredVehicleJourney', {})
                monitored_call = journey.get('MonitoredCall', {})
                
                destination = journey.get('DestinationName', [{}])[0].get('value', 'Unknown')
                direction_ref = journey.get('DirectionRef', {}).get('value', '')
                
                # Filter by direction (Aller = Vincennes direction, Retour = opposite/Casa direction)
                if filter_direction:
                    if filter_direction.lower() == "vincennes":
                        # Only show "Aller" direction (towards Vincennes)
                        # Also check destination name as fallback
                        if direction_ref and direction_ref != "Aller":
                            continue
                        if "vincennes" not in destination.lower():
                            continue
                    elif filter_direction.lower() == "casa":
                        # Only show "Retour" direction (towards Casa)
                        # First try DirectionRef
                        if direction_ref:
                            if direction_ref != "Retour":
                                continue
                        else:
                            # Fallback: if no DirectionRef, exclude Vincennes destinations
                            if "vincennes" in destination.lower():
                                continue
                            # Look for Casa/Diwan in destination
                            if "casa" not in destination.lower() and "diwan" not in destination.lower():
                                continue
                
                # Also filter by destination name if specified (for backward compatibility)
                if filter_destination and not filter_direction:
                    if filter_destination.lower() not in destination.lower():
                        continue
                
                expected_time = monitored_call.get('ExpectedDepartureTime')
                
                if expected_time:
                    dt = datetime.fromisoformat(expected_time.replace('Z', '+00:00'))
                    now = datetime.now(dt.tzinfo)
                    delta = dt - now
                    minutes = int(delta.total_seconds() / 60)
                    
                    if minutes < 0:
                        time_str = "Passe"
                    elif minutes == 0:
                        time_str = "0 min"
                    elif minutes == 1:
                        time_str = "1 min"
                    else:
                        time_str = f"{minutes} min"
                    
                    departures.append({
                        'destination': destination,
                        'time': time_str,
                        'minutes': minutes
                    })
            except Exception as e:
                logging.debug(f"Error parsing visit: {e}")
                continue
        
        return departures
    except Exception as e:
        logging.error(f"Error parsing departures: {e}")
        return []

# =============================================================================
# BUS SCREEN
# =============================================================================

def create_bus_screen(epd, departures, fonts, is_test, direction_name="VINCENNES RER"):
    """Create bus departure screen
    
    Args:
        epd: E-Paper display object
        departures: List of departure dictionaries
        fonts: Tuple of font objects
        is_test: Boolean indicating if using test data
        direction_name: Name of the direction to display (default: "VINCENNES RER")
    """
    font_header, font_stop, font_huge, font_large, font_small, font_welcome, font_time, font_date = fonts
    
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    
    # Header - BUS 215
    draw.text((10, 2), "BUS 215", font=font_header, fill=0)
    
    # Direction name in font_header (24pt) - big but not too big
    draw.text((10, 28), direction_name, font=font_header, fill=0)
    draw.line((0, 56, 264, 56), fill=0, width=2)
    
    # Departure times
    y_pos = 64
    if departures:
        for dep in departures[:2]:
            draw.text((10, y_pos), dep['time'], font=font_huge, fill=0)
            y_pos += 38
    else:
        draw.text((10, y_pos), "Aucun bus", font=font_huge, fill=0)
    
    # Footer
    draw.line((0, 152, 264, 152), fill=0, width=1)
    current_time = time.strftime("%H:%M")
    
    if is_test:
        draw.text((10, 158), f"TEST - {current_time}", font=font_large, fill=0)
    else:
        draw.text((10, 158), f"Maj: {current_time}", font=font_large, fill=0)
    
    return image

def fetch_and_parse_departures(direction_filter=None):
    """Fetch bus data and return departures with test flag

    Args:
        direction_filter: Direction to filter by - "Vincennes" for Aller, "Casa" for Retour

    Returns:
        Tuple of (departures list, is_test boolean)
    """
    direction_label = direction_filter.upper() if direction_filter else "ALL"

    # Use the correct stop ID based on direction
    if direction_filter and "casa" in direction_filter.lower():
        stop_id = STOP_ID_CASA
    else:
        stop_id = STOP_ID_VINCENNES

    data = get_bus_departures(stop_id=stop_id)

    if data:
        departures = parse_departures(data, filter_destination=None, filter_direction=None)
    else:
        departures = []

    if not departures:
        logging.warning(f"⚠️  [{direction_label}] No data - using TEST mode")
        if direction_filter and "casa" in direction_filter.lower():
            times = sorted([random.randint(3, 45) for _ in range(2)])
            departures = []
            for minutes in times:
                time_str = "1 min" if minutes == 1 else f"{minutes} min"
                departures.append({
                    'destination': 'Casa del Diwan',
                    'time': time_str,
                    'minutes': minutes
                })
        else:
            departures = generate_test_data()
        is_test = True
    else:
        times_str = ", ".join([d['time'] for d in departures[:2]])
        logging.info(f"🚌 [{direction_label}] Next buses: {times_str}")
        is_test = False

    return departures, is_test
