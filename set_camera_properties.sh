#!/bin/sh -el

ZOOM=${1:-300}
v4l2-ctl -d1 -c backlight_compensation=1,sharpness=138,power_line_frequency=1,white_balance_temperature_auto=1,saturation=128,contrast=128,brightness=128,focus_auto=0,zoom_absolute=$ZOOM
echo "Camera parameters updated successfully!"
