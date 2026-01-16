#!/usr/bin/env python3
"""Interactive remote control for bus display"""
import json
import os
import time

CONTROL_FILE = "/tmp/bus_control"
STATUS_FILE = "/tmp/bus_status.json"

def clear_screen():
    os.system('clear')

def read_status():
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def send_command(mode):
    with open(CONTROL_FILE, 'w') as f:
        f.write(mode)

def display_status(status):
    if not status:
        print("Status unknown (service may not be running)")
        return

    mode = status.get('mode', 'unknown')
    updated = status.get('updated', '?')
    is_test = status.get('is_test', False)

    print(f"Last update: {updated}" + (" [TEST DATA]" if is_test else ""))
    print("-" * 40)

    if mode == 'bus':
        print("Screen: BUS 215 -> VINCENNES RER")
        departures = status.get('departures', [])
        if departures:
            for i, dep in enumerate(departures, 1):
                print(f"  {i}. {dep}")
        else:
            print("  No departures")

    elif mode == 'bus_opposite':
        print("Screen: BUS 215 -> CASA DIWAN")
        departures = status.get('departures', [])
        if departures:
            for i, dep in enumerate(departures, 1):
                print(f"  {i}. {dep}")
        else:
            print("  No departures")

    elif mode == 'welcome':
        print("Screen: WELCOME")
        print(f"  Greeting: {status.get('greeting', '?')}")
        print(f"  Time: {status.get('time', '?')}")
        print(f"  Date: {status.get('date', '?')}")
        weather = status.get('weather', {})
        if weather:
            print(f"  Weather: Mat {weather.get('morning', '?')} | "
                  f"Ap-m {weather.get('afternoon', '?')} | "
                  f"Soir {weather.get('evening', '?')}")

    elif mode == 'blank':
        print("Screen: BLANK (white)")

def main():
    print("Bus Display Remote Control")
    print("Connecting...")

    while True:
        clear_screen()
        print("=" * 40)
        print("   BUS DISPLAY REMOTE CONTROL")
        print("=" * 40)
        print()

        status = read_status()
        display_status(status)

        print()
        print("-" * 40)
        print("  1) Bus Vincennes    3) Welcome")
        print("  2) Bus Casa         4) Blank")
        print("  5) Exit             r) Refresh")
        print("-" * 40)

        try:
            choice = input("\nChoice: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if choice == '1':
            send_command('bus')
            print("-> Switching to Vincennes...")
            time.sleep(0.5)
        elif choice == '2':
            send_command('bus_opposite')
            print("-> Switching to Casa...")
            time.sleep(0.5)
        elif choice == '3':
            send_command('welcome')
            print("-> Switching to Welcome...")
            time.sleep(0.5)
        elif choice == '4':
            send_command('blank')
            print("-> Switching to Blank...")
            time.sleep(0.5)
        elif choice == '5' or choice == 'q':
            print("Goodbye!")
            break
        elif choice == 'r' or choice == '':
            pass  # Just refresh

if __name__ == '__main__':
    main()
