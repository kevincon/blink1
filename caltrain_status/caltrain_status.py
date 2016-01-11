# coding: latin-1

# Use the blink(1) to communicate the status of incoming Caltrain trains
# Green is local trains, Yellow is express trains, and Red is bullet trains
# The blink(1) blinks slowly when it's time to pack up leave for the station
# It blinks more quickly if you need to hurry to make the train
# When it stops blinking, it's most likely too late to make the train

import atexit
import datetime
import os
import re
import sh
import sys

MAX_MINUTES_I_NEED_TO_GET_READY = 15

CALTRAIN_STATION_SRC_CODE = 'rw'
CALTRAIN_STATION_DEST_CODE = 'pa'
CALTRAIN_DIRECTION = 'sb'

CALTRAIN_CMD = sh.Command('nextcaltrain')
NEXT_CALTRAIN_CMD = CALTRAIN_CMD.bake(CALTRAIN_STATION_SRC_CODE, CALTRAIN_STATION_DEST_CODE)
CALTRAIN_REGEX_PATTERN = re.compile(r'(\d+):(\d+)([ap]m) – .*\n[SN]B \d+ (\w+)')


def get_next_train_info():
    next_train = NEXT_CALTRAIN_CMD()
    next_train_match = CALTRAIN_REGEX_PATTERN.search(str(next_train))
    if next_train_match:
        is_pm = (next_train_match.group(3).lower() == 'pm')
        hour = int(next_train_match.group(1))
        if is_pm:
            hour += 12
        minute = int(next_train_match.group(2))
        second = 0
        train_type = next_train_match.group(4).lower()
        return hour, minute, second, train_type
    else:
        return None


GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
OFF = (0, 0, 0)

# You can create this environment variable to use a specific blink(1), otherwise it will use id 0
BLINK1_ID = int(os.getenv('PEBBLE_CALTRIAN_STATUS_BLINK1_ID', 0))

BLINK1CMD = sh.Command('blink1-tool').bake('-d {}'.format(BLINK1_ID))

blinking_process = None


def get_color_string(r, g, b):
    return '0x{:02x},0x{:02x},0x{:02x}'.format(r, g, b)


def fade_to_color(fade_duration, r, g, b):
    color_string = get_color_string(r, g, b)
    duration_string = '{}'.format(fade_duration)
    BLINK1CMD('--rgb', color_string, '-m', duration_string)


def back_to_black():
    global blinking_process
    if blinking_process:
        blinking_process.wait()
    fade_to_color(0, *OFF)


def blink_color(num_blinks, delay_between_blinks, r, g, b):
    color_string = get_color_string(r, g, b)
    delay_string = '{}'.format(delay_between_blinks)
    num_blinks_string = '{}'.format(num_blinks)
    # This command will be run without blocking
    return BLINK1CMD('--rgb', color_string, '-t', delay_string, '--blink', num_blinks_string, _bg=True)


def get_color_for_train_type(train_type):
    if train_type == 'local':
        return GREEN
    elif train_type == 'limited':
        return YELLOW
    elif train_type == 'bullet':
        return RED
    else:
        # ???
        return PURPLE


def get_blink_delay_ms_for_minutes_until_train(minutes_until_train):
    if minutes_until_train <= 9:
        # too late
        return 0
    elif minutes_until_train <= MAX_MINUTES_I_NEED_TO_GET_READY - 4:
        return 250
    elif minutes_until_train <= MAX_MINUTES_I_NEED_TO_GET_READY - 3:
        # hurry
        return 500
    elif minutes_until_train <= MAX_MINUTES_I_NEED_TO_GET_READY:
        # start getting ready
        return 1000
    else:
        # too early
        return 0


def main():
    global blinking_process
    while True:
        # Try to get the next Caltrain time
        try:
            next_train_info = get_next_train_info()
            if not next_train_info:
                continue
            hour, minute, second, train_type = next_train_info
            color = get_color_for_train_type(train_type)

            # Calculate minutes until the next train
            now = datetime.datetime.now()
            next_train_time = now.replace(hour=hour, minute=minute, second=second)
            if now > next_train_time:
                # adjust for next day
                next_train_time = next_train_time.replace(day=now.day + 1)
            time_delta = next_train_time - now
            minutes_until_train = time_delta.seconds / 60

            num_blinks = 3
            delay_ms_between_blinks = get_blink_delay_ms_for_minutes_until_train(minutes_until_train)
            if delay_ms_between_blinks == 0:
                continue

            # Wait for any previous blinking process to complete
            if blinking_process:
                blinking_process.wait()
                blinking_process = None

            blinking_process = blink_color(num_blinks, delay_ms_between_blinks, *color)
        except KeyboardInterrupt:
            # let atexit handle it
            sys.exit(0)

if __name__ == '__main__':
    # Turn the blink(1) off when script exits
    atexit.register(back_to_black)

    main()
