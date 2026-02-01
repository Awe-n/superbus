#!/bin/bash
# Update script for bus display
# Run this on the Pi to pull latest code from GitHub

echo "========================================="
echo "   BUS DISPLAY - UPDATE FROM GITHUB"
echo "========================================="
echo

# Check if we're in the right directory
if [ ! -f /home/pi/bus_display.py ]; then
    echo "Error: Must run from Pi with bus_display.py in /home/pi/"
    exit 1
fi

cd /home/pi

echo "1/5 - Cloning repository..."
rm -rf temp_clone 2>/dev/null
git clone https://github.com/Awe-n/superbus.git temp_clone

if [ ! -d temp_clone ]; then
    echo "Error: Failed to clone repository"
    exit 1
fi

echo "2/5 - Copying Python files..."
cp temp_clone/*.py /home/pi/

echo "3/5 - Copying shell scripts..."
cp temp_clone/*.sh /home/pi/
chmod +x /home/pi/*.sh

echo "4/5 - Copying service file..."
cp temp_clone/bus-display.service /home/pi/

echo "5/6 - Cleaning up..."
rm -rf temp_clone

echo "6/6 - Updating systemd and restarting service..."
sudo cp /home/pi/bus-display.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart bus-display.service

echo
echo "========================================="
echo "   UPDATE COMPLETE!"
echo "========================================="
echo
echo "Check status with: sudo systemctl status bus-display.service"
echo "Or use remote:     python3 bus_remote.py"
