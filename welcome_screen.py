#!/usr/bin/env python3
"""
Welcome Screen Module
Displays greeting, time, date, and weather forecast with enhanced icons
"""

import time
import math
import logging
import requests
from PIL import Image, ImageDraw, ImageFont

# Paris/Montreuil coordinates
LATITUDE = 48.8566
LONGITUDE = 2.3522

# =============================================================================
# ENHANCED WEATHER ICONS
# =============================================================================

def draw_sun_icon(draw, x, y, size=24):
    """Draw a vibrant sun icon with alternating ray lengths"""
    center_x = x + size // 2
    center_y = y + size // 2
    radius = size // 3
    
    # Inner sun circle (filled)
    draw.ellipse((center_x - radius, center_y - radius, 
                  center_x + radius, center_y + radius), fill=0, outline=0)
    
    # Outer glow ring
    draw.ellipse((center_x - radius - 1, center_y - radius - 1, 
                  center_x + radius + 1, center_y + radius + 1), outline=0, width=1)
    
    # Sun rays with alternating lengths (16 rays for smooth look)
    for i, angle in enumerate(range(0, 360, 22.5)):
        rad = math.radians(angle)
        # Alternate between long and short rays
        ray_length = (size // 4) if i % 2 == 0 else (size // 5)
        ray_width = 2 if i % 2 == 0 else 1
        
        x1 = center_x + int((radius + 3) * math.cos(rad))
        y1 = center_y + int((radius + 3) * math.sin(rad))
        x2 = center_x + int((radius + ray_length + 3) * math.cos(rad))
        y2 = center_y + int((radius + ray_length + 3) * math.sin(rad))
        draw.line((x1, y1, x2, y2), fill=0, width=ray_width)
        
        # Add triangular tips to main rays for sparkle effect
        if i % 2 == 0:
            tip_x = center_x + int((radius + ray_length + 4) * math.cos(rad))
            tip_y = center_y + int((radius + ray_length + 4) * math.sin(rad))
            # Draw small triangle tip
            angle_left = math.radians(angle - 8)
            angle_right = math.radians(angle + 8)
            tip_left_x = center_x + int((radius + ray_length + 2) * math.cos(angle_left))
            tip_left_y = center_y + int((radius + ray_length + 2) * math.sin(angle_left))
            tip_right_x = center_x + int((radius + ray_length + 2) * math.cos(angle_right))
            tip_right_y = center_y + int((radius + ray_length + 2) * math.sin(angle_right))
            draw.polygon([(tip_x, tip_y), (tip_left_x, tip_left_y), (tip_right_x, tip_right_y)], fill=0)

def draw_cloud_icon(draw, x, y, size=24):
    """Draw a fluffy, realistic cloud icon"""
    # Cloud made of multiple overlapping circles for natural fluffy look
    r1 = size // 5
    r2 = size // 3
    r3 = size // 5
    r4 = size // 6
    
    # Build cloud from bottom up with white fill and black outline
    # Bottom base rectangle
    base_y = y + r1*2 + r1//2 + 2
    draw.rectangle((x + 3, base_y, x + size - 4, y + size - 2), fill=255, outline=255)
    
    # Bottom left puff
    draw.ellipse((x, y + r1 + 2, x + r1*2, y + r1*3 + 2), fill=255, outline=0, width=2)
    
    # Left-center puff
    draw.ellipse((x + r1//2, y + r1, x + r1//2 + r1*2, y + r1 + r1*2), fill=255, outline=0, width=2)
    
    # Top center puff (largest - the crown of the cloud)
    draw.ellipse((x + r1 - 1, y, x + r1 + r2*2 + 1, y + r2*2), fill=255, outline=0, width=2)
    
    # Right-center puff
    draw.ellipse((x + r1 + r2 - 2, y + r1 + 2, x + r1 + r2 + r3*2 - 2, y + r1 + r3*2 + 2), 
                 fill=255, outline=0, width=2)
    
    # Small puff on far right
    draw.ellipse((x + size - r4*2 - 2, y + r1 + 4, x + size - 2, y + r1 + r4*2 + 4), 
                 fill=255, outline=0, width=2)
    
    # Another small puff for extra fluffiness
    draw.ellipse((x + size//2 + r1, y + r1//2 + 3, x + size//2 + r1 + r4*2, y + r1//2 + r4*2 + 3), 
                 fill=255, outline=0, width=2)
    
    # Clean bottom line
    draw.line((x + 3, base_y, x + size - 4, base_y), fill=0, width=2)

def draw_rain_icon(draw, x, y, size=24):
    """Draw rain with realistic water droplets"""
    # Cloud (darker/grayer cloud for rain)
    draw_cloud_icon(draw, x, y, size - 6)
    
    # Realistic raindrops with varied length, position, and stagger
    drop_y_start = y + size - 9
    drops = [
        (x + 3, drop_y_start, 6, 2),      # left drop - long
        (x + 8, drop_y_start + 3, 5, 2),  # center-left - medium
        (x + 13, drop_y_start + 1, 6, 2), # center-right - long
        (x + 18, drop_y_start + 4, 4, 1), # right drop - short
    ]
    
    for drop_x, drop_y, drop_len, drop_width in drops:
        # Draw raindrop as a line
        draw.line((drop_x, drop_y, drop_x, drop_y + drop_len), fill=0, width=drop_width)
        # Add teardrop shape at bottom
        draw.ellipse((drop_x - 1, drop_y + drop_len - 1, drop_x + 1, drop_y + drop_len + 1), fill=0)
        # Small splash effect at bottom
        if drop_width == 2:
            draw.line((drop_x - 2, drop_y + drop_len + 1, drop_x + 2, drop_y + drop_len + 1), fill=0, width=1)

def draw_snow_icon(draw, x, y, size=24):
    """Draw beautiful crystalline snowflakes"""
    # Cloud
    draw_cloud_icon(draw, x, y, size - 6)
    
    # Detailed snowflakes with different sizes
    snow_y_start = y + size - 9
    flakes = [
        (x + 4, snow_y_start, 3),      # left - large
        (x + 10, snow_y_start + 3, 2),  # center - small
        (x + 16, snow_y_start + 1, 3),  # right - large
    ]
    
    for flake_x, flake_y, flake_size in flakes:
        # Draw 6-armed snowflake crystal
        # Main vertical and horizontal arms
        draw.line((flake_x - flake_size, flake_y, flake_x + flake_size, flake_y), fill=0, width=1)
        draw.line((flake_x, flake_y - flake_size, flake_x, flake_y + flake_size), fill=0, width=1)
        # Diagonal arms
        draw.line((flake_x - flake_size + 1, flake_y - flake_size + 1, 
                   flake_x + flake_size - 1, flake_y + flake_size - 1), fill=0, width=1)
        draw.line((flake_x - flake_size + 1, flake_y + flake_size - 1, 
                   flake_x + flake_size - 1, flake_y - flake_size + 1), fill=0, width=1)
        
        # Add crystalline branches on each arm
        if flake_size >= 3:
            branch_len = 1
            # Branches on horizontal arms
            draw.line((flake_x - 2, flake_y - branch_len, flake_x - 2, flake_y + branch_len), fill=0, width=1)
            draw.line((flake_x + 2, flake_y - branch_len, flake_x + 2, flake_y + branch_len), fill=0, width=1)
            # Branches on vertical arms
            draw.line((flake_x - branch_len, flake_y - 2, flake_x + branch_len, flake_y - 2), fill=0, width=1)
            draw.line((flake_x - branch_len, flake_y + 2, flake_x + branch_len, flake_y + 2), fill=0, width=1)

def draw_storm_icon(draw, x, y, size=24):
    """Draw dramatic storm with bold lightning bolt"""
    # Dark storm cloud
    draw_cloud_icon(draw, x, y, size - 8)
    
    # Dramatic lightning bolt
    bolt_x = x + size // 2
    bolt_y = y + size - 11
    
    # Create a bold, angular lightning bolt shape
    lightning_points = [
        (bolt_x, bolt_y),           # top point
        (bolt_x - 2, bolt_y + 3),   # left turn
        (bolt_x + 1, bolt_y + 3),   # right turn (makes zigzag)
        (bolt_x - 1, bolt_y + 6),   # left again
        (bolt_x + 2, bolt_y + 6),   # right turn
        (bolt_x - 2, bolt_y + 10)   # bottom point
    ]
    
    # Draw main lightning bolt
    for i in range(len(lightning_points) - 1):
        draw.line((lightning_points[i][0], lightning_points[i][1], 
                   lightning_points[i+1][0], lightning_points[i+1][1]), 
                 fill=0, width=3)
    
    # Add thinner outline for emphasis
    for i in range(len(lightning_points) - 1):
        draw.line((lightning_points[i][0] - 1, lightning_points[i][1], 
                   lightning_points[i+1][0] - 1, lightning_points[i+1][1]), 
                 fill=0, width=1)
        draw.line((lightning_points[i][0] + 1, lightning_points[i][1], 
                   lightning_points[i+1][0] + 1, lightning_points[i+1][1]), 
                 fill=0, width=1)
    
    # Add small electric sparks around bolt
    spark_points = [
        (bolt_x - 3, bolt_y + 4, bolt_x - 4, bolt_y + 5),  # left spark
        (bolt_x + 3, bolt_y + 7, bolt_x + 4, bolt_y + 8),  # right spark
    ]
    for x1, y1, x2, y2 in spark_points:
        draw.line((x1, y1, x2, y2), fill=0, width=1)

def draw_weather_icon(draw, x, y, condition, size=24):
    """Draw appropriate weather icon based on condition"""
    if condition == "Soleil":
        draw_sun_icon(draw, x, y, size)
    elif condition == "Nuages":
        draw_cloud_icon(draw, x, y, size)
    elif condition == "Pluie":
        draw_rain_icon(draw, x, y, size)
    elif condition == "Neige":
        draw_snow_icon(draw, x, y, size)
    elif condition == "Orage":
        draw_storm_icon(draw, x, y, size)
    else:  # Couvert or default
        draw_cloud_icon(draw, x, y, size)

# =============================================================================
# WEATHER API
# =============================================================================

def get_weather(retries=2, timeout=15):
    """Fetch weather forecast from Open-Meteo API with retry mechanism"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=temperature_2m,precipitation_probability,weathercode&timezone=Europe/Paris&forecast_days=1"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                logging.info("✓ Donnees meteo recues avec succes")
                return response.json()
            else:
                logging.warning(f"Weather API returned status code: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            if attempt < retries - 1:
                logging.warning(f"Tentative {attempt + 1}/{retries}: Pas de connexion, nouvelle tentative...")
                time.sleep(2)
            else:
                logging.error("Pas de connexion internet - Weather API inaccessible")
            continue
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                logging.warning(f"Tentative {attempt + 1}/{retries}: Timeout, nouvelle tentative...")
                time.sleep(2)
            else:
                logging.error("Weather API timeout apres plusieurs tentatives")
            continue
        except Exception as e:
            if attempt < retries - 1:
                logging.warning(f"Tentative {attempt + 1}/{retries}: Erreur {e}, nouvelle tentative...")
                time.sleep(2)
            else:
                logging.error(f"Weather API Error: {e}")
            continue
    
    return None

def parse_weather(data):
    """Parse weather data for morning, afternoon, and evening"""
    if not data or not isinstance(data, dict):
        logging.warning("Donnees meteo invalides ou absentes")
        return None
    
    try:
        hourly = data.get('hourly', {})
        if not hourly:
            logging.warning("Pas de donnees horaires dans la reponse meteo")
            return None
            
        times = hourly.get('time', [])
        temps = hourly.get('temperature_2m', [])
        codes = hourly.get('weathercode', [])
        
        if not times or not temps or not codes:
            logging.warning("Donnees meteo incompletes")
            return None
        
        morning_idx = None
        afternoon_idx = None
        evening_idx = None
        
        for i, t in enumerate(times):
            hour = int(t.split('T')[1].split(':')[0])
            if hour == 9 and morning_idx is None:
                morning_idx = i
            elif hour == 14 and afternoon_idx is None:
                afternoon_idx = i
            elif hour == 20 and evening_idx is None:
                evening_idx = i
        
        def weather_condition(code):
            """Convert weather code to condition string"""
            if code == 0:
                return "Soleil"
            elif code in [1, 2]:
                return "Nuages"
            elif code == 3:
                return "Couvert"
            elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                return "Pluie"
            elif code in [71, 73, 75, 85, 86]:
                return "Neige"
            elif code in [95, 96, 99]:
                return "Orage"
            else:
                return "Nuages"
        
        result = {}
        
        if morning_idx is not None:
            result['morning'] = {
                'temp': int(temps[morning_idx]),
                'condition': weather_condition(codes[morning_idx])
            }
        
        if afternoon_idx is not None:
            result['afternoon'] = {
                'temp': int(temps[afternoon_idx]),
                'condition': weather_condition(codes[afternoon_idx])
            }
        
        if evening_idx is not None:
            result['evening'] = {
                'temp': int(temps[evening_idx]),
                'condition': weather_condition(codes[evening_idx])
            }
        
        if not result:
            logging.warning("Aucune donnee meteo trouvee pour les heures specifiees")
            return None
            
        return result
    except Exception as e:
        logging.error(f"Erreur lors de l'analyse des donnees meteo: {e}")
        return None

# =============================================================================
# WELCOME SCREEN
# =============================================================================

def create_welcome_screen(epd, fonts, weather):
    """Create welcome screen with greeting, time, date, and weather icons"""
    font_header, font_stop, font_huge, font_large, font_small, font_welcome, font_time, font_date = fonts
    
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    
    # === GREETING - Top left ===
    draw.text((5, 5), "¡Hola", font=font_welcome, fill=0)
    draw.text((5, 40), "Viejo loco!", font=font_welcome, fill=0)
    
    # === DATE & TIME (always available, no internet needed) ===
    current_time = time.strftime("%H:%M")
    current_date = time.strftime("%d/%m/%Y")
    
    draw.text((10, 85), current_time, font=font_time, fill=0)
    draw.text((10, 115), current_date, font=font_date, fill=0)
    
    # === WEATHER WITH ENHANCED ICONS - Bottom ===
    if weather and isinstance(weather, dict) and len(weather) > 0:
        y_weather = 145
        x = 10
        
        # Morning
        if 'morning' in weather:
            w = weather['morning']
            draw_weather_icon(draw, x, y_weather, w['condition'], size=26)
            draw.text((x + 30, y_weather + 2), f"{w['temp']}C", font=font_small, fill=0)
            draw.text((x + 30, y_weather + 13), "Mat", font=font_small, fill=0)
            x += 70
        
        # Afternoon
        if 'afternoon' in weather:
            w = weather['afternoon']
            draw_weather_icon(draw, x, y_weather, w['condition'], size=26)
            draw.text((x + 30, y_weather + 2), f"{w['temp']}C", font=font_small, fill=0)
            draw.text((x + 30, y_weather + 13), "Ap-m", font=font_small, fill=0)
            x += 70
        
        # Evening
        if 'evening' in weather:
            w = weather['evening']
            draw_weather_icon(draw, x, y_weather, w['condition'], size=26)
            draw.text((x + 30, y_weather + 2), f"{w['temp']}C", font=font_small, fill=0)
            draw.text((x + 30, y_weather + 13), "Soir", font=font_small, fill=0)
    else:
        # French fallback messages for no internet/weather data
        draw.text((10, 145), "Pas de connexion", font=font_small, fill=0)
        draw.text((10, 158), "Meteo indisponible", font=font_small, fill=0)
    
    return image
