# Use the blink(1) to communicate the state of our continuous integration system
# Green is OK, Red is :(, Orange is request failed
# The vast majority of this code originally written by Kevin Conley (@kevincon)

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import atexit
from lib.blink1_ctypes import Blink1
import os
import requests
from time import sleep

WALTER_MASTER_STATUS_URL = 'http://walter.marlinspike.hq.getpebble.com/ci/status/master'

FADE_DURATION_MS = 1000
STATUS_POLLING_INTERVAL_SECONDS = 5

GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
OFF = (0, 0, 0)

b1 = Blink1()
# You can create this environment variable to use a specific blink(1), otherwise it will use id 0
b1.open_by_id(int(os.getenv('PEBBLE_MASTER_BUILD_STATUS_BLINK1_ID', 0)))

def back_to_black():
  b1.fade_to_rgb(0, *OFF)

if __name__ == '__main__':
  # Turn the blink(1) off when script exits
  atexit.register(back_to_black)

  while True:
    try:
      build_status_page = requests.get(WALTER_MASTER_STATUS_URL)
      color = GREEN if (build_status_page.text == 'Successful') else RED
    except requests.ConnectionError:
      color = ORANGE
    b1.fade_to_rgb(FADE_DURATION_MS, *color)
    sleep(STATUS_POLLING_INTERVAL_SECONDS)
