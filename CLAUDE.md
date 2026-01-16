# Bus Display System

Real-time bus departure display for **Raspberry Pi Zero 2 WH** with Waveshare 2.7" e-Paper.

## Project Structure

```
superbus/
├── bus_display.py      # Main entry point & orchestrator
├── navigation.py       # GPIO button control
├── welcome_screen.py   # Home screen with weather
├── bus_screen.py       # Bus departure display
├── display_utils.py    # Shared fonts & utilities
├── bus_remote.py       # Interactive remote control (SSH)
├── bus_control.sh      # Simple remote control CLI
├── setup_tailscale.sh  # One-time Tailscale setup for remote access
├── update.sh           # Pull latest code from GitHub
├── stop_id_finder.py   # Utility to find IDFM stop IDs
└── bus-display.service # systemd service config
```

## Hardware

- **Display:** Waveshare 2.7" e-Paper V2 (264x176 pixels, B&W, SPI)
- **Library:** `waveshare_epd.epd2in7_V2`
- **Buttons:** 4 GPIO buttons with pull-up resistors

### GPIO Button Mapping

| Button | GPIO Pin | Mode Constant      | Function                       |
|--------|----------|--------------------|---------------------------------|
| KEY1   | 5        | `MODE_BUS`         | Bus 215 → Vincennes (default)  |
| KEY2   | 6        | `MODE_BUS_OPPOSITE`| Bus 215 → Casa Diwan           |
| KEY3   | 13       | `MODE_WELCOME`     | Welcome screen + weather       |
| KEY4   | 19       | `MODE_BLANK`       | Blank white screen             |

## APIs

### IDFM PRIM API (Bus Departures)
- **Endpoint:** `https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring`
- **API Key:** `CK5M767DwRvWjb5MP1KsNSdPrS6RbbnP` (in `bus_screen.py`)
- **Bus Line:** 215 (`STIF:Line::C01229:`)
- **Stop IDs:**
  - Vincennes direction: `STIF:StopPoint:Q:24739:` (Progrès - Armand Carrel)
  - Casa direction: `STIF:StopPoint:Q:24740:` (Valmy - Armand Carrel)

### Open-Meteo API (Weather)
- **Endpoint:** `https://api.open-meteo.com/v1/forecast`
- **No API key required**
- **Location:** Paris (48.8566°N, 2.3522°E)
- **Data:** Hourly temperature, precipitation probability, weather code
- **Sampling:** 9 AM (morning), 2 PM (afternoon), 8 PM (evening)

## Key Constants

```python
# bus_display.py
UPDATE_INTERVAL = 60              # Display update (seconds)
FULL_REFRESH_INTERVAL = 15        # Full refresh every N updates
WEATHER_UPDATE_INTERVAL = 1800    # Weather refresh (30 min)

# navigation.py
DEBOUNCE_DELAY = 0.3              # Button debounce (seconds)
```

## Update Logic

- Display updates synchronized to minute boundaries (when `seconds == 0`)
- **Fast refresh:** Every minute (low power, quick update)
- **Full refresh:** Every 15 minutes (clears ghosting artifacts)
- Weather data fetched every 30 minutes

## Screen Details

### Welcome Screen (`welcome_screen.py`)
- Greeting: "¡Hola Viejo loco!"
- Current time (28pt) and date (20pt)
- 3 weather boxes: morning (Mat), afternoon (Ap-m), evening (Soir)
- Custom weather icons: sun, cloud, rain, snow, storm

### Bus Screen (`bus_screen.py`)
- Header: "BUS 215"
- Direction label: "VINCENNES RER" or "CASA DIWAN"
- Top 2 departure times in minutes
- Shows "Passe" for buses already departed
- Falls back to test data if API unavailable

## Dependencies

```python
import RPi.GPIO           # Button control
from waveshare_epd import epd2in7_V2  # Display
from PIL import Image, ImageDraw, ImageFont
import requests           # API calls
```

## Deployment

```bash
# Copy service file
sudo cp bus-display.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable bus-display.service
sudo systemctl start bus-display.service

# Check logs
journalctl -u bus-display.service -f
```

## Remote Control (SSH)

### Interactive Mode (Recommended)
```bash
python3 bus_remote.py
```
Shows an interactive menu with detailed status (bus times, weather, etc.):
- Press 1-4 to switch screens
- Press r to refresh status
- Press 5 or q to exit

### Simple CLI
```bash
./bus_control.sh status     # See current screen
./bus_control.sh vincennes  # Switch to Vincennes bus (or: 1)
./bus_control.sh casa       # Switch to Casa bus (or: 2)
./bus_control.sh welcome    # Switch to Welcome screen (or: 3)
./bus_control.sh blank      # Switch to Blank screen (or: 4)
```

### How It Works
- **Control file:** `/tmp/bus_control` - Write mode name to switch screens
- **Status file:** `/tmp/bus_status.json` - Service writes detailed JSON status
- Uses `/tmp/` so it works with overlay filesystem (read-only SD card)

## Remote Access from Anywhere (Tailscale)

Tailscale creates a secure VPN mesh so you can SSH to the Pi from anywhere.

### One-time Setup on Pi
```bash
./setup_tailscale.sh
```
Or manually:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Open the URL it prints to authenticate
tailscale ip -4  # Note your Pi's Tailscale IP (e.g., 100.64.0.1)
```

### Setup on Mac
```bash
brew install --cask tailscale
```
Or download from https://tailscale.com/download/mac

Sign in with the same account.

### Connect from Anywhere
```bash
ssh pi@<tailscale-ip>
python3 bus_remote.py
```

Or using MagicDNS: `ssh pi@raspberrypi`

### Dashboard
View all devices at https://login.tailscale.com/admin/machines

## Notes

- Main script path on Pi: `/home/pi/bus_display.py`
- Fonts: DejaVu Sans from `/usr/share/fonts/truetype/dejavu/`
- e-Paper library expected at: `~/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd/`
