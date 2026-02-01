#!/bin/bash
# =========================================
#   SWITCH REFRESH MODE
# =========================================
#
#   ./set_mode.sh           # Show current mode
#   ./set_mode.sh normal    # 60s updates (default)
#   ./set_mode.sh fast      # 30s updates
#
# =========================================

SERVICE_FILE="/etc/systemd/system/bus-display.service"

show_current() {
    if grep -q "\-\-fast" "$SERVICE_FILE" 2>/dev/null; then
        echo "Current mode: FAST (30s updates)"
    else
        echo "Current mode: NORMAL (60s updates)"
    fi
}

case "$1" in
    fast)
        echo "Switching to FAST mode (30s updates)..."
        sudo sed -i 's|/usr/bin/python3 /home/pi/bus_display.py.*|/usr/bin/python3 /home/pi/bus_display.py --fast|' "$SERVICE_FILE"
        sudo systemctl daemon-reload
        sudo systemctl restart bus-display.service
        echo "Done! Display now updates every 30 seconds."
        ;;
    normal)
        echo "Switching to NORMAL mode (60s updates)..."
        sudo sed -i 's|/usr/bin/python3 /home/pi/bus_display.py.*|/usr/bin/python3 /home/pi/bus_display.py|' "$SERVICE_FILE"
        sudo systemctl daemon-reload
        sudo systemctl restart bus-display.service
        echo "Done! Display now updates every 60 seconds."
        ;;
    status|"")
        show_current
        echo ""
        echo "Usage: ./set_mode.sh [normal|fast]"
        echo "  normal - 60s updates, full refresh every 15 min"
        echo "  fast   - 30s updates, full refresh every 5 min"
        ;;
    *)
        echo "Unknown mode: $1"
        echo "Usage: ./set_mode.sh [normal|fast]"
        exit 1
        ;;
esac
