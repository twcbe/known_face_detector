#!/bin/sh -el

v4l2-ctl -d0 -c backlight_compensation=1,sharpness=138,power_line_frequency=1,white_balance_temperature_auto=1,saturation=128,contrast=128,brightness=128,focus_auto=0,zoom_absolute=300
echo "Camera parameters updated successfully!"
