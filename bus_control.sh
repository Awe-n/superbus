#!/bin/bash
# Remote control for bus display
# Usage: ./bus_control.sh <command>

CONTROL_FILE="/tmp/bus_control"
STATUS_FILE="/tmp/bus_status"

case "$1" in
    status)
        if [ -f "$STATUS_FILE" ]; then
            cat "$STATUS_FILE"
        else
            echo "Status unknown (service may not be running)"
        fi
        ;;
    vincennes|bus|1)
        echo "bus" > "$CONTROL_FILE"
        echo "-> Switching to Vincennes bus screen"
        ;;
    casa|2)
        echo "bus_opposite" > "$CONTROL_FILE"
        echo "-> Switching to Casa bus screen"
        ;;
    welcome|3)
        echo "welcome" > "$CONTROL_FILE"
        echo "-> Switching to Welcome screen"
        ;;
    blank|4)
        echo "blank" > "$CONTROL_FILE"
        echo "-> Switching to Blank screen"
        ;;
    *)
        echo "Bus Display Remote Control"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  status     Show current screen"
        echo "  vincennes  Bus to Vincennes (KEY1)"
        echo "  casa       Bus to Casa (KEY2)"
        echo "  welcome    Welcome screen (KEY3)"
        echo "  blank      Blank screen (KEY4)"
        echo ""
        echo "Shortcuts: 1=vincennes, 2=casa, 3=welcome, 4=blank"
        ;;
esac
