#!/bin/bash
# Boot update script - pulls latest code from GitHub on startup
# This runs before bus-display.service starts, ensuring fresh code even with overlay filesystem

LOG_TAG="bus-update"

log() {
    echo "$1"
    logger -t "$LOG_TAG" "$1"
}

log "Starting boot update..."

cd /home/pi || exit 0

# Check network connectivity (wait up to 30 seconds)
for i in {1..6}; do
    if ping -c 1 github.com &>/dev/null; then
        log "Network available"
        break
    fi
    log "Waiting for network... ($i/6)"
    sleep 5
done

# Try to update from GitHub
log "Cloning repository..."
rm -rf /tmp/bus_update 2>/dev/null
if git clone --depth 1 https://github.com/Awe-n/superbus.git /tmp/bus_update 2>/dev/null; then
    log "Copying files..."
    cp /tmp/bus_update/*.py /home/pi/ 2>/dev/null
    cp /tmp/bus_update/*.sh /home/pi/ 2>/dev/null
    chmod +x /home/pi/*.sh 2>/dev/null
    rm -rf /tmp/bus_update
    log "Boot update complete!"
else
    log "Update failed (no network?) - using existing code"
fi

exit 0
