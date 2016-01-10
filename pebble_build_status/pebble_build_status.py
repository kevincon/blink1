# Use the blink(1) to communicate the state of our continuous integration system
# Green is OK, Red is :(, Orange is request failed

import atexit
import os
import requests
import sh
from time import sleep

WALTER_MASTER_STATUS_URL = 'http://walter.marlinspike.hq.getpebble.com/ci/status/master'

FADE_DURATION_MS = 1000
STATUS_POLLING_INTERVAL_SECONDS = 5

GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
OFF = (0, 0, 0)

# You can create this environment variable to use a specific blink(1), otherwise it will use id 0
BLINK1_ID = int(os.getenv('PEBBLE_MASTER_BUILD_STATUS_BLINK1_ID', 0))

BLINK1CMD = sh.Command("blink1-tool")
BLINK1CMD.bake('-d {}'.format(BLINK1_ID))

def fade_to_color(fade_duration, r, g, b):
  color_string = '0x{:02x},0x{:02x},0x{:02x}'.format(r, g, b)
  duration_string = '{}'.format(fade_duration)
  BLINK1CMD('--rgb', color_string, '--m', duration_string)

def back_to_black():
  fade_to_color(0, *OFF)

if __name__ == '__main__':
  # Turn the blink(1) off when script exits
  atexit.register(back_to_black)

  while True:
    try:
      build_status_page = requests.get(WALTER_MASTER_STATUS_URL)
      color = GREEN if (build_status_page.text == 'Successful') else RED
    except requests.ConnectionError:
      color = ORANGE
    fade_to_color(FADE_DURATION_MS, *color)
    sleep(STATUS_POLLING_INTERVAL_SECONDS)
